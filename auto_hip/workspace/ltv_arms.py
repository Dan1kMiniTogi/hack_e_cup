"""Prediction arms. Fit only on train-fit tables, never on primary/holdout labels.

Usage:
    model = fit_arm("hgb_log1p", train_df)
    pred = predict_arm("hgb_log1p", model, eval_df)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import polars as pl
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor

from ltv_metrics import rmsle

HGB_REG = dict(max_depth=6, max_iter=120, learning_rate=0.08, min_samples_leaf=40, random_state=42)
HGB_CLF = dict(max_depth=5, max_iter=80, learning_rate=0.08, min_samples_leaf=40, random_state=42)

BASE_FEATURES = [
    "gmv_sum_7d",
    "gmv_sum_14d",
    "gmv_sum_30d",
    "gmv_sum_60d",
    "gmv_sum_90d",
    "gmv_search_sum_7d",
    "gmv_search_sum_30d",
    "gmv_search_sum_90d",
    "gmv_cat_sum_7d",
    "gmv_cat_sum_30d",
    "gmv_cat_sum_90d",
    "searches_sum_7d",
    "searches_sum_30d",
    "searches_sum_90d",
    "to_ord_sum_7d",
    "to_ord_sum_30d",
    "to_ord_sum_90d",
    "to_cart_sum_7d",
    "to_cart_sum_30d",
    "active_days_7d",
    "active_days_14d",
    "active_days_30d",
    "active_days_90d",
    "activity_days",
    "hist_gmv",
    "hist_gmv_search",
    "hist_gmv_cat",
    "hist_orders",
    "hist_searches",
    "any_search",
    "any_cat",
    "recency_days",
]
GAP_FEATURES = ["last_gap", "mean_gap", "max_gap", "n_gaps_gt_7", "n_gaps_gt_14"]
RATIO_FEATURES = [
    "intensity_30d",
    "intensity_90d",
    "ord_rate_30d",
    "cart_rate_30d",
    "search_gmv_share_30d",
    "gmv_per_ord_90d",
]
DECAY_FEATURES = ["decay_gmv30"]
ORDER_FEATURES = ["recency_order_days"]
WEEKDAY_FEATURES = ["weekend_gmv_share", "weekend_day_share"]
LASTK_FEATURES = [
    "last_k_gap_1",
    "last_k_gap_2",
    "last_k_gap_3",
    "last_ord_gmv",
    "last_ord_to_ord",
    "searches_after_last_ord",
]
VOL_FEATURES = ["gmv_day_std", "gmv_day_max", "n_active_weeks", "gmv_concentration"]
H26_COLS = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES + ORDER_FEATURES
DEEPER_L2 = dict(max_depth=8, max_iter=220, learning_rate=0.05, min_samples_leaf=30, l2_regularization=1.0)
H26_HGB = {**DEEPER_L2, "max_iter": 320, "learning_rate": 0.04}
LGB_PARAMS = {
    "objective": "regression",
    "metric": "rmse",
    "max_depth": 8,
    "num_leaves": 63,
    "learning_rate": 0.04,
    "min_data_in_leaf": 30,
    "lambda_l2": 1.0,
    "verbosity": -1,
    "feature_pre_filter": False,
    "num_threads": 4,
}
LGB_ROUNDS = 320


def with_derived(df: pl.DataFrame) -> pl.DataFrame:
    """Intensity and conversion ratios from existing window sums (no extra scan).

    Args:
        df: Cutoff feature table.

    Returns:
        Same rows with RATIO_FEATURES added.

    Example:
        X = _X(with_derived(df), BASE_FEATURES + RATIO_FEATURES)
    """
    out = df.with_columns(
        intensity_30d=pl.col("gmv_sum_30d") / (pl.col("active_days_30d") + 1.0),
        intensity_90d=pl.col("gmv_sum_90d") / (pl.col("active_days_90d") + 1.0),
        ord_rate_30d=pl.col("to_ord_sum_30d") / (pl.col("searches_sum_30d") + 1.0),
        cart_rate_30d=pl.col("to_cart_sum_30d") / (pl.col("searches_sum_30d") + 1.0),
        search_gmv_share_30d=pl.col("gmv_search_sum_30d") / (pl.col("gmv_sum_30d") + 1.0),
        gmv_per_ord_90d=pl.col("gmv_sum_90d") / (pl.col("to_ord_sum_90d") + 1.0),
        decay_gmv30=pl.col("gmv_sum_30d") / (pl.col("recency_days").fill_null(9999) + 1.0),
    )
    if "recency_order_days" in df.columns:
        out = out.with_columns(
            ord_lag=pl.col("recency_order_days").fill_null(9999) - pl.col("recency_days").fill_null(9999)
        )
    return out


def _X(df: pl.DataFrame, cols: list[str]) -> np.ndarray:
    """Numeric matrix; null recency filled with large value (never-seen)."""
    work = df
    if any(c in RATIO_FEATURES or c in DECAY_FEATURES or c == "ord_lag" for c in cols) and "intensity_30d" not in df.columns:
        work = with_derived(work)
    work = work.with_columns(pl.col("recency_days").fill_null(9999))
    if "recency_order_days" in work.columns:
        work = work.with_columns(pl.col("recency_order_days").fill_null(9999))
    return work.select(cols).to_numpy().astype(np.float64)


def _clip(p: np.ndarray) -> np.ndarray:
    return np.clip(p, 0, None)


@dataclass
class ArmModel:
    name: str
    payload: dict[str, Any]


def fit_scale_c(train_df: pl.DataFrame) -> ArmModel:
    """Grid-search multiplicative c on naive_30d minimizing RMSLE."""
    y = train_df["y"].to_numpy()
    naive = train_df["naive_30d"].to_numpy()
    grid = np.concatenate(
        [np.linspace(0.4, 1.4, 21), np.array([0.75, 0.8, 0.836, 0.85, 0.9, 1.0])]
    )
    best_c, best = 1.0, 1e9
    for c in grid:
        s = rmsle(y, c * naive)
        if s < best:
            best, best_c = s, float(c)
    return ArmModel("scale", {"c": best_c, "inner_rmsle": best})


def fit_scale_high(train_df: pl.DataFrame, q50: float, q90: float) -> ArmModel:
    """Fit c_high only on hist_gmv high bucket; others stay naive."""
    high = train_df.filter(pl.col("hist_gmv") > q90)
    y = high["y"].to_numpy()
    naive = high["naive_30d"].to_numpy()
    best_c, best = 1.0, 1e9
    for c in np.linspace(0.5, 1.2, 15):
        s = rmsle(y, c * naive)
        if s < best:
            best, best_c = s, float(c)
    return ArmModel("scale_high", {"c_high": best_c, "q90": q90, "inner_rmsle_high": best})


def fit_hgb(
    train_df: pl.DataFrame,
    cols: list[str],
    y_col: str = "y",
    *,
    sample_weight: np.ndarray | None = None,
    hgb_kw: dict | None = None,
    loss: str = "squared_error",
    y_transform: str = "log1p",
) -> HistGradientBoostingRegressor:
    """HGB on transformed target.

    Args:
        train_df: Fit rows.
        cols: Feature names.
        y_col: Target column.
        sample_weight: Optional per-row weights.
        hgb_kw: Overrides for HGB_REG.
        loss: sklearn HGB loss.
        y_transform: log1p | identity | log1p_eps (y+1e-3 before log1p for poisson-like).

    Returns:
        Fitted regressor. Inverse transform is applied in predict helpers.
    """
    raw = np.clip(train_df[y_col].to_numpy(), 0, None)
    if y_transform == "log1p":
        y = np.log1p(raw)
    elif y_transform == "identity":
        y = raw
    else:
        y = np.log1p(raw + 1e-3)
    kw = {**HGB_REG, **(hgb_kw or {})}
    kw.setdefault("loss", loss)
    m = HistGradientBoostingRegressor(**kw)
    m.fit(_X(train_df, cols), y, sample_weight=sample_weight)
    return m


def _best_c(y: np.ndarray, pred: np.ndarray, grid: np.ndarray) -> float:
    """Multiplicative c minimizing RMSLE on a labeled set."""
    best_c, best = 1.0, 1e9
    for c in grid:
        s = rmsle(y, c * pred)
        if s < best:
            best, best_c = s, float(c)
    return best_c


def _best_alpha(y: np.ndarray, pred_m: np.ndarray, pred_n: np.ndarray) -> float:
    """Convex blend alpha*model + (1-alpha)*naive minimizing RMSLE."""
    best_a, best = 1.0, 1e9
    for a in np.linspace(0.0, 1.0, 21):
        s = rmsle(y, a * pred_m + (1.0 - a) * pred_n)
        if s < best:
            best, best_a = s, float(a)
    return best_a


def _fit_channel(train_df: pl.DataFrame, cols: list[str], **hgb_extra) -> dict[str, Any]:
    """Two log1p HGB heads for search and catalog."""
    return {
        "reg_s": fit_hgb(train_df, cols, "y_search", **hgb_extra),
        "reg_c": fit_hgb(train_df, cols, "y_cat", **hgb_extra),
        "cols": cols,
    }


def _fit_lgb_head(
    train_df: pl.DataFrame,
    cols: list[str],
    y_col: str,
    seed: int,
    *,
    weight: np.ndarray | None = None,
    extra_params: dict | None = None,
    y_transform: str = "log1p",
    num_rounds: int | None = None,
):
    """One LightGBM booster.

    Args:
        train_df: Fit rows.
        cols: Feature names.
        y_col: Raw GMV column (clipped ≥0).
        seed: Booster RNG seed.
        weight: Optional per-row weights.
        extra_params: Overrides for LGB_PARAMS (e.g. tweedie).
        y_transform: log1p | identity.
        num_rounds: Boosting rounds, default LGB_ROUNDS.

    Returns:
        Fitted ``lightgbm.Booster``.

    Example:
        bst = _fit_lgb_head(train, H26_COLS, "y_search", 42)
    """
    import lightgbm as lgb

    raw = np.clip(train_df[y_col].to_numpy(), 0, None)
    y = np.log1p(raw) if y_transform == "log1p" else raw
    params = {
        **LGB_PARAMS,
        **(extra_params or {}),
        "seed": seed,
        "feature_fraction_seed": seed,
        "bagging_seed": seed,
    }
    dtrain = lgb.Dataset(_X(train_df, cols), label=y, weight=weight, feature_name=cols, free_raw_data=False)
    return lgb.train(params, dtrain, num_boost_round=num_rounds or LGB_ROUNDS)


def _fit_lgb_channel(train_df: pl.DataFrame, cols: list[str], seed: int, **head_kw) -> dict[str, Any]:
    """Two LightGBM log1p heads for search and catalog."""
    return {
        "reg_s": _fit_lgb_head(train_df, cols, "y_search", seed, **head_kw),
        "reg_c": _fit_lgb_head(train_df, cols, "y_cat", seed, **head_kw),
        "cols": cols,
    }


def _pred_two_log_heads(reg_s, reg_c, xs: np.ndarray) -> np.ndarray:
    """expm1 clip sum of two log-heads (sklearn or LightGBM)."""
    ps = np.expm1(np.clip(reg_s.predict(xs), -1, 20))
    pc = np.expm1(np.clip(reg_c.predict(xs), -1, 20))
    return _clip(ps) + _clip(pc)


def _rfm_bins(hist: np.ndarray, rec: np.ndarray, q50: float, q90: float) -> np.ndarray:
    """Integer cell id: 4 hist buckets × 4 recency buckets."""
    h = np.zeros(len(hist), dtype=np.int32)
    h[hist <= 0] = 0
    h[(hist > 0) & (hist <= q50)] = 1
    h[(hist > q50) & (hist <= q90)] = 2
    h[hist > q90] = 3
    r = np.zeros(len(rec), dtype=np.int32)
    r[rec <= 7] = 0
    r[(rec > 7) & (rec <= 30)] = 1
    r[(rec > 30) & (rec <= 90)] = 2
    r[rec > 90] = 3
    return h * 4 + r


def _rfm_te_map(train_df: pl.DataFrame) -> tuple[dict[int, float], tuple[float, float]]:
    """Mean y per RFM cell on the full fit set (for eval join).

    Args:
        train_df: Labeled fit rows with hist_gmv, recency_days, y.

    Returns:
        cell_id → mean y, and (q50, q90) of positive hist_gmv.

    Example:
        te, edges = _rfm_te_map(train)
    """
    from ltv_metrics import hist_gmv_quantiles

    q50, q90 = hist_gmv_quantiles(train_df)
    hist = train_df["hist_gmv"].to_numpy()
    rec = train_df["recency_days"].fill_null(9999).to_numpy()
    y = train_df["y"].to_numpy()
    cells = _rfm_bins(hist, rec, q50, q90)
    te: dict[int, float] = {}
    for c in range(16):
        m = cells == c
        te[c] = float(y[m].mean()) if m.any() else float(y.mean())
    return te, (q50, q90)


def _add_rfm_te(df: pl.DataFrame, source: pl.DataFrame, *, oof: bool) -> pl.DataFrame:
    """Attach rfm_te. If oof, cell means from other cutoffs only.

    Args:
        df: Rows to annotate.
        source: Fit rows for means.
        oof: Leave-one-cutoff-out on df (must equal source).

    Returns:
        df plus column rfm_te.

    Example:
        train = _add_rfm_te(train, train, oof=True)
    """
    from ltv_metrics import hist_gmv_quantiles

    q50, q90 = hist_gmv_quantiles(source)
    gmean = float(source["y"].mean())
    if not oof:
        te, _ = _rfm_te_map(source)
        hist = df["hist_gmv"].to_numpy()
        rec = df["recency_days"].fill_null(9999).to_numpy()
        cells = _rfm_bins(hist, rec, q50, q90)
        vals = np.array([te.get(int(c), gmean) for c in cells])
        return df.with_columns(rfm_te=pl.Series(vals))
    parts = []
    for co in df["cutoff"].unique().to_list():
        part = df.filter(pl.col("cutoff") == co)
        other = source.filter(pl.col("cutoff") != co)
        te, _ = _rfm_te_map(other) if other.height > 1000 else _rfm_te_map(source)
        hist = part["hist_gmv"].to_numpy()
        rec = part["recency_days"].fill_null(9999).to_numpy()
        cells = _rfm_bins(hist, rec, q50, q90)
        vals = np.array([te.get(int(c), gmean) for c in cells])
        parts.append(part.with_columns(rfm_te=pl.Series(vals)))
    return pl.concat(parts, how="vertical_relaxed")


def fit_hurdle(train_df: pl.DataFrame, cols: list[str]) -> ArmModel:
    """P(y>0) * E[y | y>0] with HGB classifier + log1p regressor."""
    y = train_df["y"].to_numpy()
    X = _X(train_df, cols)
    clf = HistGradientBoostingClassifier(**HGB_CLF)
    clf.fit(X, (y > 0).astype(np.int32))
    pos = train_df.filter(pl.col("y") > 0)
    reg = HistGradientBoostingRegressor(**HGB_REG)
    reg.fit(_X(pos, cols), np.log1p(pos["y"].to_numpy()))
    return ArmModel("hurdle", {"clf": clf, "reg": reg, "cols": cols})


def fit_arm(name: str, train_df: pl.DataFrame, q50: float, q90: float) -> ArmModel:
    """Fit named arm on train-fit rows.

    Args:
        name: naive|scale|scale_high|hurdle|hgb_log1p|channel_sum|hgb_gaps.
        train_df: Concatenated fit anchors.
        q50, q90: Positive hist_gmv quantiles from the same fit set.

    Returns:
        ArmModel for predict_arm.
    """
    if name == "naive":
        return ArmModel("naive", {})
    if name == "scale":
        return fit_scale_c(train_df)
    if name == "scale_high":
        return fit_scale_high(train_df, q50, q90)
    if name == "hurdle":
        return fit_hurdle(train_df, BASE_FEATURES)
    if name == "hgb_log1p":
        return ArmModel("hgb_log1p", {"reg": fit_hgb(train_df, BASE_FEATURES), "cols": BASE_FEATURES})
    if name == "channel_sum":
        return ArmModel("channel_sum", _fit_channel(train_df, BASE_FEATURES))
    if name == "channel_gaps":
        cols = BASE_FEATURES + GAP_FEATURES
        return ArmModel("channel_sum", _fit_channel(train_df, cols))
    if name == "channel_gaps_cal":
        cols = BASE_FEATURES + GAP_FEATURES
        payload = _fit_channel(train_df, cols)
        tmp = ArmModel("channel_sum", payload)
        pred = predict_arm(tmp, train_df)
        c = _best_c(train_df["y"].to_numpy(), pred, np.linspace(0.7, 2.2, 31))
        payload = {**payload, "c": c}
        return ArmModel("channel_cal", payload)
    if name == "channel_naive_blend":
        cols = BASE_FEATURES + GAP_FEATURES
        payload = _fit_channel(train_df, cols)
        tmp = ArmModel("channel_sum", payload)
        pred = predict_arm(tmp, train_df)
        naive = train_df["naive_30d"].to_numpy()
        a = _best_alpha(train_df["y"].to_numpy(), pred, naive)
        payload = {**payload, "alpha": a}
        return ArmModel("channel_blend", payload)
    if name == "channel_ratios":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES
        return ArmModel("channel_sum", _fit_channel(train_df, cols))
    if name == "channel_ratios_deeper":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES
        kw = dict(max_depth=8, max_iter=220, learning_rate=0.05, min_samples_leaf=30)
        return ArmModel("channel_sum", _fit_channel(train_df, cols, hgb_kw=kw))
    if name == "channel_deeper_l2":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES
        return ArmModel("channel_sum", _fit_channel(train_df, cols, hgb_kw=DEEPER_L2))
    if name == "channel_order":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES + ORDER_FEATURES
        return ArmModel("channel_sum", _fit_channel(train_df, cols, hgb_kw=DEEPER_L2))
    if name == "channel_order_more":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES + ORDER_FEATURES
        kw = {**DEEPER_L2, "max_iter": 320, "learning_rate": 0.04}
        return ArmModel("channel_sum", _fit_channel(train_df, cols, hgb_kw=kw))
    if name == "channel_order_lag":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES + ORDER_FEATURES + ["ord_lag"]
        return ArmModel("channel_sum", _fit_channel(train_df, cols, hgb_kw=DEEPER_L2))
    if name == "channel_order_leaf":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES + ORDER_FEATURES
        kw = {**DEEPER_L2, "max_iter": 320, "learning_rate": 0.04, "min_samples_leaf": 20}
        return ArmModel("channel_sum", _fit_channel(train_df, cols, hgb_kw=kw))
    if name == "channel_mono":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES + ORDER_FEATURES
        cst = [0] * len(cols)
        for i, c in enumerate(cols):
            if c.startswith("gmv_sum_") or c in ("hist_gmv", "gmv_search_sum_30d", "gmv_cat_sum_30d"):
                cst[i] = 1
        kw = {**DEEPER_L2, "max_iter": 320, "learning_rate": 0.04, "monotonic_cst": cst}
        return ArmModel("channel_sum", _fit_channel(train_df, cols, hgb_kw=kw))
    if name == "channel_abs":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES + ORDER_FEATURES
        kw = {**DEEPER_L2, "max_iter": 320, "learning_rate": 0.04, "loss": "absolute_error"}
        return ArmModel("channel_sum", _fit_channel(train_df, cols, hgb_kw=kw))
    if name == "channel_more_data":
        from ltv_data import load_named

        extra = load_named("train_c")
        train_df = pl.concat([train_df, extra], how="vertical_relaxed")
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES + ORDER_FEATURES
        kw = {**DEEPER_L2, "max_iter": 320, "learning_rate": 0.04}
        return ArmModel("channel_sum", _fit_channel(train_df, cols, hgb_kw=kw))
    if name == "channel_decay":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES + ORDER_FEATURES + DECAY_FEATURES
        kw = {**DEEPER_L2, "max_iter": 320, "learning_rate": 0.04}
        return ArmModel("channel_sum", _fit_channel(train_df, cols, hgb_kw=kw))
    if name == "channel_ens":
        cols = H26_COLS
        members = []
        for seed in (42, 7, 99):
            kw = {**H26_HGB, "random_state": seed}
            members.append(_fit_channel(train_df, cols, hgb_kw=kw))
        return ArmModel("channel_ens", {"members": members})
    if name == "lgb_channel_ens":
        members = [_fit_lgb_channel(train_df, H26_COLS, seed) for seed in (42, 7, 99)]
        return ArmModel("lgb_channel_ens", {"members": members})
    if name == "channel_ens_weekday":
        from ltv_data import attach_extras

        train_df = attach_extras(train_df)
        cols = H26_COLS + WEEKDAY_FEATURES
        members = []
        for seed in (42, 7, 99):
            kw = {**H26_HGB, "random_state": seed}
            members.append(_fit_channel(train_df, cols, hgb_kw=kw))
        return ArmModel("channel_ens", {"members": members, "need_extras": True})
    if name == "channel_ens_lastk":
        from ltv_data import attach_extras

        train_df = attach_extras(train_df)
        cols = H26_COLS + LASTK_FEATURES
        members = []
        for seed in (42, 7, 99):
            kw = {**H26_HGB, "random_state": seed}
            members.append(_fit_channel(train_df, cols, hgb_kw=kw))
        return ArmModel("channel_ens", {"members": members, "need_extras": True})
    if name == "single_head_ens":
        members = []
        for seed in (42, 7, 99):
            kw = {**H26_HGB, "random_state": seed}
            members.append({"reg": fit_hgb(train_df, H26_COLS, "y", hgb_kw=kw), "cols": H26_COLS})
        return ArmModel("single_head_ens", {"members": members})
    if name == "catboost_channel":
        from catboost import CatBoostRegressor

        xs = _X(train_df, H26_COLS)
        members = []
        for seed in (42, 7, 99):
            kw = dict(
                loss_function="RMSE",
                depth=8,
                iterations=320,
                learning_rate=0.04,
                l2_leaf_reg=3.0,
                random_seed=seed,
                verbose=0,
            )
            rs = CatBoostRegressor(**kw)
            rc = CatBoostRegressor(**kw)
            rs.fit(xs, np.log1p(np.clip(train_df["y_search"].to_numpy(), 0, None)))
            rc.fit(xs, np.log1p(np.clip(train_df["y_cat"].to_numpy(), 0, None)))
            members.append({"reg_s": rs, "reg_c": rc, "cols": H26_COLS})
        return ArmModel("lgb_channel_ens", {"members": members})
    if name == "residual_mid_order":
        base = _fit_lgb_channel(train_df, H26_COLS, 42)
        xs = _X(train_df, H26_COLS)
        base_pred = _pred_two_log_heads(base["reg_s"], base["reg_c"], xs)
        hist = train_df["hist_gmv"].to_numpy()
        ro = train_df["recency_order_days"].fill_null(9999).to_numpy() if "recency_order_days" in train_df.columns else np.full(len(hist), 9999.0)
        mask = (hist > q50) & (hist <= q90) & (ro > 7) & (ro <= 30)
        y = np.clip(train_df["y"].to_numpy(), 0, None)
        resid = np.log1p(y) - np.log1p(np.clip(base_pred, 0, None))
        reg = HistGradientBoostingRegressor(**{**H26_HGB, "random_state": 42, "max_iter": 120})
        if mask.sum() >= 1000:
            reg.fit(xs[mask], resid[mask])
        else:
            reg.fit(xs, resid)
        return ArmModel("residual_mid_order", {"base": base, "resid": reg, "q50": q50, "q90": q90, "cols": H26_COLS})
    if name == "channel_leaf50":
        cols = H26_COLS
        kw = {**H26_HGB, "min_samples_leaf": 50}
        members = []
        for seed in (42, 7, 99):
            members.append(_fit_channel(train_df, cols, hgb_kw={**kw, "random_state": seed}))
        return ArmModel("channel_ens", {"members": members})
    if name == "lgb_total":
        members = [_fit_lgb_head(train_df, H26_COLS, "y", seed) for seed in (42, 7, 99)]
        return ArmModel("lgb_total", {"members": members, "cols": H26_COLS})
    if name == "lgb_tweedie":
        extra = {"objective": "tweedie", "tweedie_variance_power": 1.3}
        members = []
        for seed in (42, 7, 99):
            members.append(
                {
                    "reg_s": _fit_lgb_head(train_df, H26_COLS, "y_search", seed, extra_params=extra, y_transform="identity"),
                    "reg_c": _fit_lgb_head(train_df, H26_COLS, "y_cat", seed, extra_params=extra, y_transform="identity"),
                    "cols": H26_COLS,
                }
            )
        return ArmModel("lgb_tweedie", {"members": members})
    if name == "moe_hist":
        hist = train_df["hist_gmv"].to_numpy()
        low_df = train_df.filter(pl.col("hist_gmv") <= q50)
        high_df = train_df.filter(pl.col("hist_gmv") > q50)
        return ArmModel(
            "moe_hist",
            {
                "low": _fit_lgb_channel(low_df, H26_COLS, 42),
                "high": _fit_lgb_channel(high_df, H26_COLS, 42),
                "q50": q50,
            },
        )
    if name == "zero_snap":
        mem = _fit_lgb_channel(train_df, H26_COLS, 42)
        pred = _pred_two_log_heads(mem["reg_s"], mem["reg_c"], _X(train_df, H26_COLS))
        y = train_df["y"].to_numpy()
        best_t, best = 0.0, rmsle(y, pred)
        for t in (0.5, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 16.0):
            p2 = pred.copy()
            p2[p2 < t] = 0.0
            s = rmsle(y, p2)
            if s < best:
                best, best_t = s, float(t)
        return ArmModel("zero_snap", {"mem": mem, "tau": best_t, "inner_rmsle": best})
    if name == "rfm_te":
        work = _add_rfm_te(train_df, train_df, oof=True)
        cols = H26_COLS + ["rfm_te"]
        members = [_fit_lgb_channel(work, cols, seed) for seed in (42, 7)]
        te_map, edges = _rfm_te_map(train_df)
        return ArmModel("rfm_te", {"members": members, "te_map": te_map, "edges": edges, "cols": cols})
    if name == "vol_burst":
        from ltv_data import attach_vol

        train_df = attach_vol(train_df)
        cols = H26_COLS + VOL_FEATURES
        members = [_fit_lgb_channel(train_df, cols, seed) for seed in (42, 7, 99)]
        return ArmModel("lgb_channel_ens", {"members": members, "need_vol": True})
    if name == "time_decay_w":
        from datetime import date as _date

        inner = _date(2025, 11, 15)
        cuts = train_df["cutoff"].to_list()
        w = np.array([np.exp(-(inner - (c.date() if hasattr(c, "date") else c)).days / 21.0) for c in cuts])
        members = [_fit_lgb_channel(train_df, H26_COLS, seed, weight=w) for seed in (42, 7, 99)]
        return ArmModel("lgb_channel_ens", {"members": members})
    if name == "isotonic_log":
        from sklearn.isotonic import IsotonicRegression

        members = [_fit_lgb_channel(train_df, H26_COLS, seed) for seed in (42, 7, 99)]
        acc = None
        for mem in members:
            part = _pred_two_log_heads(mem["reg_s"], mem["reg_c"], _X(train_df, H26_COLS))
            acc = part if acc is None else acc + part
        pred = acc / len(members)
        iso = IsotonicRegression(out_of_bounds="clip", increasing=True)
        iso.fit(np.log1p(np.clip(pred, 0, None)), np.log1p(np.clip(train_df["y"].to_numpy(), 0, None)))
        return ArmModel("isotonic_log", {"members": members, "iso": iso})
    if name == "blend_lgb_hgb":
        lgb_m = [_fit_lgb_channel(train_df, H26_COLS, seed) for seed in (42, 7, 99)]
        hgb_m = []
        for seed in (42, 7, 99):
            hgb_m.append(_fit_channel(train_df, H26_COLS, hgb_kw={**H26_HGB, "random_state": seed}))
        return ArmModel("blend_lgb_hgb", {"lgb": lgb_m, "hgb": hgb_m})
    if name == "xgb_channel":
        import xgboost as xgb

        xs = _X(train_df, H26_COLS)
        members = []
        for seed in (42, 7, 99):
            kw = dict(max_depth=8, n_estimators=320, learning_rate=0.04, min_child_weight=30, reg_lambda=1.0, subsample=1.0, n_jobs=4, random_state=seed, tree_method="hist")
            rs = xgb.XGBRegressor(**kw)
            rc = xgb.XGBRegressor(**kw)
            rs.fit(xs, np.log1p(np.clip(train_df["y_search"].to_numpy(), 0, None)))
            rc.fit(xs, np.log1p(np.clip(train_df["y_cat"].to_numpy(), 0, None)))
            members.append({"reg_s": rs, "reg_c": rc, "cols": H26_COLS})
        return ArmModel("lgb_channel_ens", {"members": members})
    if name == "zero_hist_guard":
        members = [_fit_lgb_channel(train_df, H26_COLS, seed) for seed in (42, 7, 99)]
        return ArmModel("zero_hist_guard", {"members": members})
    if name == "channel_ens_decay":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES + ORDER_FEATURES + DECAY_FEATURES
        members = []
        for seed in (42, 7, 99):
            kw = {**DEEPER_L2, "max_iter": 320, "learning_rate": 0.04, "random_state": seed}
            members.append(_fit_channel(train_df, cols, hgb_kw=kw))
        return ArmModel("channel_ens", {"members": members})
    if name == "channel_d7":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES + ORDER_FEATURES
        kw = {**DEEPER_L2, "max_iter": 320, "learning_rate": 0.04, "max_depth": 7}
        return ArmModel("channel_sum", _fit_channel(train_df, cols, hgb_kw=kw))
    if name == "channel_poisson_deeper":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES
        extra = dict(loss="poisson", y_transform="identity", hgb_kw=DEEPER_L2)
        train_p = train_df.with_columns(
            y_search=pl.col("y_search") + 1e-4,
            y_cat=pl.col("y_cat") + 1e-4,
        )
        return ArmModel("channel_poisson", _fit_channel(train_p, cols, **extra))
    if name == "channel_quantile":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES
        kw = dict(max_depth=8, max_iter=220, learning_rate=0.05, min_samples_leaf=30, loss="quantile", quantile=0.6)
        return ArmModel("channel_sum", _fit_channel(train_df, cols, hgb_kw=kw))
    if name == "channel_ratios_l2":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES
        return ArmModel("channel_sum", _fit_channel(train_df, cols, hgb_kw=dict(l2_regularization=1.0)))
    if name == "channel_ratios_bucket_cal":
        cols = BASE_FEATURES + GAP_FEATURES + RATIO_FEATURES
        payload = _fit_channel(train_df, cols)
        tmp = ArmModel("channel_sum", payload)
        pred = predict_arm(tmp, train_df)
        y = train_df["y"].to_numpy()
        hist = train_df["hist_gmv"].to_numpy()
        buckets = {
            "zero": hist <= 0,
            "low": (hist > 0) & (hist <= q50),
            "mid": (hist > q50) & (hist <= q90),
            "high": hist > q90,
        }
        cs = {}
        grid = np.linspace(0.7, 2.2, 31)
        for b, mask in buckets.items():
            cs[b] = 1.0 if mask.sum() < 100 else _best_c(y[mask], pred[mask], grid)
        payload = {**payload, "c_buckets": cs, "q50": q50, "q90": q90}
        return ArmModel("channel_bucket_cal", payload)
    if name == "channel_zero_w":
        cols = BASE_FEATURES + GAP_FEATURES
        y = train_df["y"].to_numpy()
        w = np.where(y <= 0, 2.0, 1.0)
        return ArmModel("channel_sum", _fit_channel(train_df, cols, sample_weight=w))
    if name == "channel_deeper":
        cols = BASE_FEATURES + GAP_FEATURES
        kw = dict(max_depth=8, max_iter=220, learning_rate=0.05, min_samples_leaf=30)
        return ArmModel("channel_sum", _fit_channel(train_df, cols, hgb_kw=kw))
    if name == "channel_poisson":
        cols = BASE_FEATURES + GAP_FEATURES
        extra = dict(loss="poisson", y_transform="identity", hgb_kw=dict(max_iter=120, max_depth=6, learning_rate=0.08, min_samples_leaf=40))
        # Poisson needs y >= 0; sklearn forbids all-zero in some versions — add tiny eps in identity.
        train_p = train_df.with_columns(
            y_search=pl.col("y_search") + 1e-4,
            y_cat=pl.col("y_cat") + 1e-4,
        )
        return ArmModel("channel_poisson", _fit_channel(train_p, cols, **extra))
    if name == "channel_l2":
        cols = BASE_FEATURES + GAP_FEATURES
        kw = dict(l2_regularization=1.0)
        return ArmModel("channel_sum", _fit_channel(train_df, cols, hgb_kw=kw))
    if name == "channel_bucket_cal":
        cols = BASE_FEATURES + GAP_FEATURES
        payload = _fit_channel(train_df, cols)
        tmp = ArmModel("channel_sum", payload)
        pred = predict_arm(tmp, train_df)
        y = train_df["y"].to_numpy()
        hist = train_df["hist_gmv"].to_numpy()
        q50, q90 = q50, q90
        buckets = {
            "zero": hist <= 0,
            "low": (hist > 0) & (hist <= q50),
            "mid": (hist > q50) & (hist <= q90),
            "high": hist > q90,
        }
        cs = {}
        grid = np.linspace(0.7, 2.2, 31)
        for b, mask in buckets.items():
            if mask.sum() < 100:
                cs[b] = 1.0
                continue
            cs[b] = _best_c(y[mask], pred[mask], grid)
        payload = {**payload, "c_buckets": cs, "q50": q50, "q90": q90}
        return ArmModel("channel_bucket_cal", payload)
    if name == "hgb_gaps":
        cols = BASE_FEATURES + GAP_FEATURES
        return ArmModel("hgb_gaps", {"reg": fit_hgb(train_df, cols), "cols": cols})
    if name == "mlp":
        from sklearn.neural_network import MLPRegressor
        from sklearn.preprocessing import StandardScaler

        cols = BASE_FEATURES
        X = _X(train_df, cols)
        scaler = StandardScaler()
        Xs = scaler.fit_transform(X)
        y = np.log1p(np.clip(train_df["y"].to_numpy(), 0, None))
        mlp = MLPRegressor(
            hidden_layer_sizes=(32, 16),
            max_iter=40,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1,
        )
        mlp.fit(Xs, y)
        return ArmModel("mlp", {"mlp": mlp, "scaler": scaler, "cols": cols})
    raise ValueError(name)


def predict_arm(model: ArmModel, eval_df: pl.DataFrame) -> np.ndarray:
    """Non-negative predictions aligned with eval_df row order."""
    name = model.name
    p = model.payload
    if name == "naive":
        return _clip(eval_df["naive_30d"].to_numpy())
    if name == "scale":
        return _clip(p["c"] * eval_df["naive_30d"].to_numpy())
    if name == "scale_high":
        pred = eval_df["naive_30d"].to_numpy().copy()
        high = eval_df["hist_gmv"].to_numpy() > p["q90"]
        pred[high] *= p["c_high"]
        return _clip(pred)
    if name == "hurdle":
        X = _X(eval_df, p["cols"])
        p_pos = p["clf"].predict_proba(X)[:, 1]
        mag = np.expm1(np.clip(p["reg"].predict(X), -1, 20))
        return _clip(p_pos * mag)
    if name in ("hgb_log1p", "hgb_gaps"):
        pred = np.expm1(np.clip(p["reg"].predict(_X(eval_df, p["cols"])), -1, 20))
        return _clip(pred)
    if name in ("channel_sum", "channel_cal", "channel_blend", "channel_bucket_cal", "channel_poisson"):
        xs = _X(eval_df, p["cols"])
        if name == "channel_poisson":
            ps = np.clip(p["reg_s"].predict(xs), 0, None)
            pc = np.clip(p["reg_c"].predict(xs), 0, None)
        else:
            ps = np.expm1(np.clip(p["reg_s"].predict(xs), -1, 20))
            pc = np.expm1(np.clip(p["reg_c"].predict(xs), -1, 20))
        pred = _clip(ps) + _clip(pc)
        if name == "channel_cal":
            pred = _clip(p["c"] * pred)
        elif name == "channel_blend":
            naive = eval_df["naive_30d"].to_numpy()
            pred = _clip(p["alpha"] * pred + (1.0 - p["alpha"]) * naive)
        elif name == "channel_bucket_cal":
            hist = eval_df["hist_gmv"].to_numpy()
            cs = p["c_buckets"]
            scale = np.ones_like(pred)
            scale[hist <= 0] = cs["zero"]
            scale[(hist > 0) & (hist <= p["q50"])] = cs["low"]
            scale[(hist > p["q50"]) & (hist <= p["q90"])] = cs["mid"]
            scale[hist > p["q90"]] = cs["high"]
            pred = _clip(scale * pred)
        return pred
    if name == "channel_ens":
        work = eval_df
        if p.get("need_extras"):
            from ltv_data import attach_extras

            work = attach_extras(eval_df)
        acc = None
        for mem in p["members"]:
            part = predict_arm(ArmModel("channel_sum", mem), work)
            acc = part if acc is None else acc + part
        return _clip(acc / len(p["members"]))
    if name == "lgb_channel_ens":
        work = eval_df
        if p.get("need_vol"):
            from ltv_data import attach_vol

            work = attach_vol(eval_df)
        acc = None
        for mem in p["members"]:
            xs = _X(work, mem["cols"])
            part = _pred_two_log_heads(mem["reg_s"], mem["reg_c"], xs)
            acc = part if acc is None else acc + part
        return _clip(acc / len(p["members"]))
    if name == "lgb_total":
        acc = None
        for bst in p["members"]:
            part = np.expm1(np.clip(bst.predict(_X(eval_df, p["cols"])), -1, 20))
            acc = part if acc is None else acc + part
        return _clip(acc / len(p["members"]))
    if name == "lgb_tweedie":
        acc = None
        for mem in p["members"]:
            xs = _X(eval_df, mem["cols"])
            part = _clip(mem["reg_s"].predict(xs)) + _clip(mem["reg_c"].predict(xs))
            acc = part if acc is None else acc + part
        return _clip(acc / len(p["members"]))
    if name == "moe_hist":
        hist = eval_df["hist_gmv"].to_numpy()
        xs = _X(eval_df, H26_COLS)
        pl_ = _pred_two_log_heads(p["low"]["reg_s"], p["low"]["reg_c"], xs)
        ph = _pred_two_log_heads(p["high"]["reg_s"], p["high"]["reg_c"], xs)
        pred = np.where(hist <= p["q50"], pl_, ph)
        return _clip(pred)
    if name == "zero_snap":
        pred = _pred_two_log_heads(p["mem"]["reg_s"], p["mem"]["reg_c"], _X(eval_df, H26_COLS))
        pred = pred.copy()
        pred[pred < p["tau"]] = 0.0
        return _clip(pred)
    if name == "rfm_te":
        hist = eval_df["hist_gmv"].to_numpy()
        rec = eval_df["recency_days"].fill_null(9999).to_numpy()
        q50, q90 = p["edges"]
        cells = _rfm_bins(hist, rec, q50, q90)
        gmean = float(np.mean(list(p["te_map"].values())))
        te = np.array([p["te_map"].get(int(c), gmean) for c in cells])
        work = eval_df.with_columns(rfm_te=pl.Series(te))
        acc = None
        for mem in p["members"]:
            part = _pred_two_log_heads(mem["reg_s"], mem["reg_c"], _X(work, p["cols"]))
            acc = part if acc is None else acc + part
        return _clip(acc / len(p["members"]))
    if name == "isotonic_log":
        acc = None
        for mem in p["members"]:
            part = _pred_two_log_heads(mem["reg_s"], mem["reg_c"], _X(eval_df, H26_COLS))
            acc = part if acc is None else acc + part
        pred = acc / len(p["members"])
        cal = p["iso"].predict(np.log1p(np.clip(pred, 0, None)))
        return _clip(np.expm1(cal))
    if name == "blend_lgb_hgb":
        acc_l = None
        for mem in p["lgb"]:
            part = _pred_two_log_heads(mem["reg_s"], mem["reg_c"], _X(eval_df, H26_COLS))
            acc_l = part if acc_l is None else acc_l + part
        acc_h = None
        for mem in p["hgb"]:
            part = predict_arm(ArmModel("channel_sum", mem), eval_df)
            acc_h = part if acc_h is None else acc_h + part
        return _clip(0.5 * (acc_l / len(p["lgb"])) + 0.5 * (acc_h / len(p["hgb"])))
    if name == "residual_mid_order":
        xs = _X(eval_df, p["cols"])
        base = _pred_two_log_heads(p["base"]["reg_s"], p["base"]["reg_c"], xs)
        hist = eval_df["hist_gmv"].to_numpy()
        ro = eval_df["recency_order_days"].fill_null(9999).to_numpy()
        mask = (hist > p["q50"]) & (hist <= p["q90"]) & (ro > 7) & (ro <= 30)
        out = np.log1p(np.clip(base, 0, None))
        if mask.any():
            out[mask] = out[mask] + p["resid"].predict(xs[mask])
        return _clip(np.expm1(out))
    if name == "zero_hist_guard":
        acc = None
        for mem in p["members"]:
            part = _pred_two_log_heads(mem["reg_s"], mem["reg_c"], _X(eval_df, H26_COLS))
            acc = part if acc is None else acc + part
        pred = acc / len(p["members"])
        pred = pred.copy()
        pred[eval_df["hist_gmv"].to_numpy() <= 0] = 0.0
        return _clip(pred)
    if name == "single_head_ens":
        acc = None
        for mem in p["members"]:
            part = np.expm1(np.clip(mem["reg"].predict(_X(eval_df, mem["cols"])), -1, 20))
            acc = part if acc is None else acc + part
        return _clip(acc / len(p["members"]))
    if name == "mlp":
        Xs = p["scaler"].transform(_X(eval_df, p["cols"]))
        pred = np.expm1(np.clip(p["mlp"].predict(Xs), -1, 20))
        return _clip(pred)
    raise ValueError(name)
