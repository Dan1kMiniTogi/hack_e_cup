"""User-level aggregates at a cutoff. No dense calendar fill.

Usage:
    from ltv_data import build_cutoff_table, CUTOFFS
    df = build_cutoff_table(date(2026, 1, 14), with_target=True)
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[2]
PARQUET_PATH = REPO_ROOT / "data" / "train.parquet"
CACHE_DIR = Path(__file__).resolve().parent / "cache"

HORIZON_DAYS = 30
WINDOWS = [("7d", 7), ("14d", 14), ("30d", 30), ("60d", 60), ("90d", 90)]
VALUE_COLS = ["gmv", "gmv_search", "gmv_cat", "searches", "to_ord", "to_cart"]

CUTOFFS = {
    "inner_train": date(2025, 11, 15),
    "train_b": date(2025, 11, 1),
    "train_a": date(2025, 10, 18),
    "train_c": date(2025, 10, 4),
    "holdout": date(2025, 12, 15),
    "primary": date(2026, 1, 14),
    "test": date(2026, 2, 13),
}

TRAIN_FIT_NAMES = ("train_a", "train_b", "inner_train")
EVAL_NAMES = ("holdout", "primary")


def _window_exprs(cutoff: date) -> list[pl.Expr]:
    """Sum/count expressions for rolling windows ending at cutoff (inclusive)."""
    exprs: list[pl.Expr] = []
    for w_name, n_days in WINDOWS:
        start = cutoff - timedelta(days=n_days - 1)
        mask = pl.col("event_date").is_between(start, cutoff)
        for col in VALUE_COLS:
            exprs.append(
                pl.when(mask).then(pl.col(col)).otherwise(0).sum().alias(f"{col}_sum_{w_name}")
            )
        exprs.append(pl.when(mask).then(1).otherwise(0).sum().alias(f"active_days_{w_name}"))
    return exprs


def _hist_exprs(cutoff: date) -> list[pl.Expr]:
    """Lifetime-to-cutoff aggregates and recency (sparse rows only)."""
    return [
        pl.len().alias("activity_days"),
        pl.col("event_date").max().alias("last_activity"),
        pl.sum("gmv").alias("hist_gmv"),
        pl.sum("gmv_search").alias("hist_gmv_search"),
        pl.sum("gmv_cat").alias("hist_gmv_cat"),
        pl.max("search").alias("any_search"),
        pl.max("cat").alias("any_cat"),
        pl.sum("to_ord").alias("hist_orders"),
        pl.sum("searches").alias("hist_searches"),
        pl.col("event_date").filter(pl.col("to_ord") > 0).max().alias("last_order"),
    ]


def _gap_table(lf_hist: pl.LazyFrame) -> pl.LazyFrame:
    """Gap stats from existing event dates only (no calendar explode)."""
    return (
        lf_hist.select("user_id", "event_date")
        .sort(["user_id", "event_date"])
        .with_columns(gap=pl.col("event_date").diff().over("user_id").dt.total_days())
        .group_by("user_id")
        .agg(
            last_gap=pl.col("gap").drop_nulls().last(),
            mean_gap=pl.col("gap").mean(),
            max_gap=pl.col("gap").max(),
            n_gaps_gt_7=(pl.col("gap") > 7).sum(),
            n_gaps_gt_14=(pl.col("gap") > 14).sum(),
        )
    )


def build_cutoff_table(
    cutoff: date,
    *,
    with_target: bool,
    cache: bool = True,
) -> pl.DataFrame:
    """Build one row per user at ``cutoff``.

    Args:
        cutoff: Last date allowed in features.
        with_target: If True, add y / y_search / y_cat for the next 30 days.
        cache: Read/write parquet under workspace/cache.

    Returns:
        DataFrame with user_id, naive_30d (= gmv_sum_30d), features, optional targets.
        Users with no history get zeros / null recency.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tag = f"{cutoff.isoformat()}_{'y' if with_target else 'notarget'}_v2"
    path = CACHE_DIR / f"features_{tag}.parquet"
    if cache and path.exists():
        return pl.read_parquet(path)

    lf = pl.scan_parquet(PARQUET_PATH)
    users = lf.select(pl.col("user_id").unique()).collect()
    lf_hist = lf.filter(pl.col("event_date") <= cutoff)

    feats = lf_hist.group_by("user_id").agg(_window_exprs(cutoff) + _hist_exprs(cutoff))
    gaps = _gap_table(lf_hist)
    out = (
        users.lazy()
        .join(feats, on="user_id", how="left")
        .join(gaps, on="user_id", how="left")
    )

    if with_target:
        t0 = cutoff + timedelta(days=1)
        t1 = cutoff + timedelta(days=HORIZON_DAYS)
        tgt = (
            lf.filter(pl.col("event_date").is_between(t0, t1))
            .group_by("user_id")
            .agg(
                pl.sum("gmv").alias("y"),
                pl.sum("gmv_search").alias("y_search"),
                pl.sum("gmv_cat").alias("y_cat"),
            )
        )
        out = out.join(tgt, on="user_id", how="left")

    df = out.collect()
    fill_zero = [
        c
        for c in df.columns
        if c not in ("user_id", "last_activity", "last_order") and df.schema[c].is_numeric()
    ]
    df = df.with_columns([pl.col(c).fill_null(0) for c in fill_zero])
    df = df.with_columns(
        recency_days=pl.when(pl.col("last_activity").is_null())
        .then(None)
        .otherwise((pl.lit(cutoff) - pl.col("last_activity")).dt.total_days()),
        recency_order_days=pl.when(pl.col("last_order").is_null())
        .then(None)
        .otherwise((pl.lit(cutoff) - pl.col("last_order")).dt.total_days()),
        naive_30d=pl.col("gmv_sum_30d"),
        cutoff=pl.lit(cutoff),
    )
    if cache:
        df.write_parquet(path)
    return df


def build_extra_features(cutoff: date, *, cache: bool = True) -> pl.DataFrame:
    """Weekday mix and last-K event stats from sparse rows (no calendar densify).

    Args:
        cutoff: Last date allowed in history.
        cache: Read/write ``features_{cutoff}_extra_v1.parquet``.

    Returns:
        One row per user with weekend shares, last-3 gaps, last-order GMV/to_ord,
        searches after last order. Missing gaps filled with 9999; other nulls 0.

    Example:
        extra = build_extra_features(date(2026, 1, 14))
        df = load_named("primary").join(extra, on="user_id", how="left")
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"features_{cutoff.isoformat()}_extra_v1.parquet"
    if cache and path.exists():
        return pl.read_parquet(path)

    lf = pl.scan_parquet(PARQUET_PATH)
    users = lf.select(pl.col("user_id").unique())
    lf_hist = lf.filter(pl.col("event_date") <= cutoff)

    weekday = (
        lf_hist.select("user_id", "event_date", "gmv")
        .with_columns(wd=pl.col("event_date").dt.weekday())
        .group_by("user_id")
        .agg(
            weekend_gmv=pl.when(pl.col("wd") >= 6).then(pl.col("gmv")).otherwise(0).sum(),
            weekend_days=pl.when(pl.col("wd") >= 6).then(1).otherwise(0).sum(),
            n_hist_rows=pl.len(),
            hist_gmv_wd=pl.sum("gmv"),
        )
        .with_columns(
            weekend_gmv_share=pl.col("weekend_gmv") / (pl.col("hist_gmv_wd") + 1.0),
            weekend_day_share=pl.col("weekend_days") / (pl.col("n_hist_rows") + 1.0),
        )
        .select("user_id", "weekend_gmv_share", "weekend_day_share")
    )

    with_gap = lf_hist.sort(["user_id", "event_date"]).with_columns(
        gap=pl.col("event_date").diff().over("user_id").dt.total_days()
    )
    lastk_gaps = with_gap.group_by("user_id").agg(
        last_k_gap_1=pl.col("gap").drop_nulls().last(),
        last_k_gap_2=pl.col("gap").drop_nulls().slice(-2, 1).first(),
        last_k_gap_3=pl.col("gap").drop_nulls().slice(-3, 1).first(),
    )
    last_ord = (
        lf_hist.filter(pl.col("to_ord") > 0)
        .sort(["user_id", "event_date"])
        .group_by("user_id")
        .agg(
            last_ord_gmv=pl.col("gmv").last(),
            last_ord_to_ord=pl.col("to_ord").last(),
            last_ord_date=pl.col("event_date").last(),
        )
    )
    searches_after = (
        lf_hist.join(last_ord.select("user_id", "last_ord_date"), on="user_id", how="inner")
        .filter(pl.col("event_date") > pl.col("last_ord_date"))
        .group_by("user_id")
        .agg(searches_after_last_ord=pl.col("searches").sum())
    )

    df = (
        users.join(weekday, on="user_id", how="left")
        .join(lastk_gaps, on="user_id", how="left")
        .join(last_ord.drop("last_ord_date"), on="user_id", how="left")
        .join(searches_after, on="user_id", how="left")
        .collect()
    )
    gap_cols = ["last_k_gap_1", "last_k_gap_2", "last_k_gap_3"]
    zero_cols = [
        c
        for c in df.columns
        if c != "user_id" and c not in gap_cols and df.schema[c].is_numeric()
    ]
    df = df.with_columns([pl.col(c).fill_null(0) for c in zero_cols])
    df = df.with_columns([pl.col(c).fill_null(9999) for c in gap_cols])
    if cache:
        df.write_parquet(path)
    return df


def attach_extras(df: pl.DataFrame) -> pl.DataFrame:
    """Left-join extra_v1 features per cutoff already present on ``df``.

    Args:
        df: Cutoff table with ``user_id`` and ``cutoff``.

    Returns:
        Same rows with weekend and last-K columns (idempotent if already joined).

    Example:
        train = attach_extras(concat_train_fit())
    """
    if "weekend_gmv_share" in df.columns:
        return df
    parts: list[pl.DataFrame] = []
    for co in df["cutoff"].unique().to_list():
        part = df.filter(pl.col("cutoff") == co)
        extra = build_extra_features(co)
        parts.append(part.join(extra, on="user_id", how="left"))
    return pl.concat(parts, how="vertical_relaxed")


def build_vol_features(cutoff: date, *, cache: bool = True) -> pl.DataFrame:
    """Burstiness stats from sparse daily GMV (no calendar densify).

    Args:
        cutoff: Last date in history.
        cache: ``features_{cutoff}_vol_v1.parquet``.

    Returns:
        user_id, gmv_day_std, gmv_day_max, n_active_weeks, gmv_concentration.

    Example:
        vol = build_vol_features(date(2026, 1, 14))
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"features_{cutoff.isoformat()}_vol_v1.parquet"
    if cache and path.exists():
        return pl.read_parquet(path)
    lf = pl.scan_parquet(PARQUET_PATH)
    users = lf.select(pl.col("user_id").unique())
    lf_hist = lf.filter(pl.col("event_date") <= cutoff)
    vol = lf_hist.group_by("user_id").agg(
        gmv_day_std=pl.col("gmv").std(),
        gmv_day_max=pl.col("gmv").max(),
        n_active_weeks=pl.col("event_date").dt.truncate("1w").n_unique(),
        gmv_sum_hist=pl.col("gmv").sum(),
    ).with_columns(
        gmv_concentration=pl.col("gmv_day_max") / (pl.col("gmv_sum_hist") + 1.0),
    ).select("user_id", "gmv_day_std", "gmv_day_max", "n_active_weeks", "gmv_concentration")
    df = users.join(vol, on="user_id", how="left").collect()
    nums = [c for c in df.columns if c != "user_id"]
    df = df.with_columns([pl.col(c).fill_null(0) for c in nums])
    if cache:
        df.write_parquet(path)
    return df


FUNNEL_WINDOWS = [("7d", 7), ("30d", 30), ("90d", 90)]
FUNNEL_SUM_COLS = ["search_to_ord", "cat_to_ord", "search_to_cart", "cat_to_cart"]
FUNNEL_HAS_COLS = [
    "has_search_to_ord",
    "has_cat_to_ord",
    "has_search_to_cart",
    "has_cat_to_cart",
]


def build_funnel_features(cutoff: date, *, cache: bool = True) -> pl.DataFrame:
    """Channel funnel window sums and lifetime has_* flags (no densify).

    Args:
        cutoff: Last date allowed in history.
        cache: ``features_{cutoff}_funnel_v1.parquet``.

    Returns:
        One row per user_id: ``{search,cat}_to_{ord,cart}_sum_{7,30,90}d`` and
        ``hist_has_*`` lifetime max flags. Missing users filled with 0.

    Example:
        extra = build_funnel_features(date(2026, 1, 14))
        df = load_named("primary").join(extra, on="user_id", how="left")
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"features_{cutoff.isoformat()}_funnel_v1.parquet"
    if cache and path.exists():
        return pl.read_parquet(path)

    lf = pl.scan_parquet(PARQUET_PATH)
    users = lf.select(pl.col("user_id").unique())
    lf_hist = lf.filter(pl.col("event_date") <= cutoff)
    exprs: list[pl.Expr] = []
    for w_name, n_days in FUNNEL_WINDOWS:
        start = cutoff - timedelta(days=n_days - 1)
        mask = pl.col("event_date").is_between(start, cutoff)
        for col in FUNNEL_SUM_COLS:
            exprs.append(
                pl.when(mask).then(pl.col(col)).otherwise(0).sum().alias(f"{col}_sum_{w_name}")
            )
    for col in FUNNEL_HAS_COLS:
        exprs.append(pl.max(col).alias(f"hist_{col}"))
    funnel = lf_hist.group_by("user_id").agg(exprs)
    df = users.join(funnel, on="user_id", how="left").collect()
    nums = [c for c in df.columns if c != "user_id"]
    df = df.with_columns([pl.col(c).fill_null(0) for c in nums])
    if cache:
        df.write_parquet(path)
    return df


def attach_funnel(df: pl.DataFrame) -> pl.DataFrame:
    """Left-join funnel_v1 per cutoff already on ``df``.

    Args:
        df: Table with user_id and cutoff.

    Returns:
        Same rows plus funnel columns (idempotent).

    Example:
        train = attach_funnel(concat_train_fit())
    """
    if "search_to_ord_sum_30d" in df.columns:
        return df
    parts: list[pl.DataFrame] = []
    for co in df["cutoff"].unique().to_list():
        part = df.filter(pl.col("cutoff") == co)
        parts.append(part.join(build_funnel_features(co), on="user_id", how="left"))
    return pl.concat(parts, how="vertical_relaxed")


def build_btyd_features(cutoff: date, *, cache: bool = True) -> pl.DataFrame:
    """Purchase-process RFM/AOV from sparse order days (no densify, no labels).

    Args:
        cutoff: Last date in history.
        cache: ``features_{cutoff}_btyd_v1.parquet``.

    Returns:
        user_id plus btyd_frequency (repeat order-days), btyd_recency_tx (first→last
        order days), btyd_T (first order→cutoff), btyd_aov, btyd_n_purch,
        btyd_days_since_last (9999 if never ordered).

    Example:
        btyd = build_btyd_features(date(2026, 1, 14))
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"features_{cutoff.isoformat()}_btyd_v1.parquet"
    if cache and path.exists():
        return pl.read_parquet(path)

    lf = pl.scan_parquet(PARQUET_PATH)
    users = lf.select(pl.col("user_id").unique())
    purch = (
        lf.filter((pl.col("event_date") <= cutoff) & (pl.col("to_ord") > 0))
        .group_by("user_id")
        .agg(
            btyd_n_purch=pl.len(),
            first_purch=pl.col("event_date").min(),
            last_purch=pl.col("event_date").max(),
            purch_gmv=pl.sum("gmv"),
        )
    )
    df = users.join(purch, on="user_id", how="left").collect()
    cutoff_lit = pl.lit(cutoff)
    df = df.with_columns(
        btyd_n_purch=pl.col("btyd_n_purch").fill_null(0),
        purch_gmv=pl.col("purch_gmv").fill_null(0.0),
        btyd_frequency=pl.max_horizontal(pl.col("btyd_n_purch").fill_null(0) - 1, pl.lit(0)),
        btyd_recency_tx=pl.when(pl.col("first_purch").is_null())
        .then(0)
        .otherwise((pl.col("last_purch") - pl.col("first_purch")).dt.total_days()),
        btyd_T=pl.when(pl.col("first_purch").is_null())
        .then(0)
        .otherwise((cutoff_lit - pl.col("first_purch")).dt.total_days()),
        btyd_days_since_last=pl.when(pl.col("last_purch").is_null())
        .then(9999)
        .otherwise((cutoff_lit - pl.col("last_purch")).dt.total_days()),
        btyd_aov=pl.col("purch_gmv").fill_null(0.0) / (pl.col("btyd_n_purch").fill_null(0) + 1e-9),
    ).select(
        "user_id",
        "btyd_n_purch",
        "btyd_frequency",
        "btyd_recency_tx",
        "btyd_T",
        "btyd_aov",
        "btyd_days_since_last",
    )
    if cache:
        df.write_parquet(path)
    return df


def attach_btyd(df: pl.DataFrame) -> pl.DataFrame:
    """Join btyd_v1 per cutoff already on ``df``.

    Args:
        df: Table with user_id and cutoff.

    Returns:
        Rows plus RFM/AOV columns (idempotent).

    Example:
        train = attach_btyd(concat_train_fit())
    """
    if "btyd_frequency" in df.columns:
        return df
    parts: list[pl.DataFrame] = []
    for co in df["cutoff"].unique().to_list():
        part = df.filter(pl.col("cutoff") == co)
        parts.append(part.join(build_btyd_features(co), on="user_id", how="left"))
    return pl.concat(parts, how="vertical_relaxed")


def bgnbd_moments(frequency: np.ndarray, T: np.ndarray) -> dict[str, float]:
    """Rough BG-NBD params from purchase rates (no labels).

    Args:
        frequency: Repeat purchase counts (x).
        T: Observation age in days from first purchase (0 if never).

    Returns:
        Dict r, alpha, a, b for p_alive / expected purchases.

    Example:
        params = bgnbd_moments(freq, T)
    """
    import numpy as np

    freq = np.asarray(frequency, dtype=np.float64)
    t = np.asarray(T, dtype=np.float64)
    rates = (freq + 1.0) / (t + 1.0)
    mu = float(rates.mean())
    var = float(rates.var())
    alpha = float(mu / max(var, 1e-8))
    r = float(max(mu * alpha, 1e-3))
    alpha = float(max(alpha, 1e-3))
    long = t > 60
    p0 = float(((long) & (freq == 0)).mean()) if long.any() else float((freq == 0).mean())
    p0 = min(max(p0, 0.05), 0.9)
    a = 0.5
    b = float(max(0.5, (1.0 - p0) / p0))
    return {"r": r, "alpha": alpha, "a": a, "b": b}


def add_bgnbd_derived(df: pl.DataFrame, params: dict[str, float]) -> pl.DataFrame:
    """Add p_alive, E[purchases 30d], E[gmv] from BG-NBD-like closed forms.

    Args:
        df: Rows with btyd_frequency, btyd_recency_tx, btyd_T, btyd_aov, btyd_days_since_last.
        params: r, alpha, a, b from ``bgnbd_moments``.

    Returns:
        df plus btyd_p_alive, btyd_e_purch_30, btyd_e_gmv.

    Example:
        work = add_bgnbd_derived(attach_btyd(df), params)
    """
    import numpy as np

    if "btyd_p_alive" in df.columns:
        return df
    r, alpha, a, b = params["r"], params["alpha"], params["a"], params["b"]
    x = df["btyd_frequency"].to_numpy().astype(np.float64)
    t_x = df["btyd_recency_tx"].to_numpy().astype(np.float64)
    T = df["btyd_T"].to_numpy().astype(np.float64)
    aov = df["btyd_aov"].to_numpy().astype(np.float64)
    dsl = df["btyd_days_since_last"].to_numpy().astype(np.float64)
    never = T <= 0
    t_x = np.minimum(t_x, T)
    ratio = np.power((alpha + T + 1e-9) / (alpha + t_x + 1e-9), r + x)
    p_alive = 1.0 / (1.0 + (a / (b + x + 1e-9)) * ratio)
    mean_ip = np.where(x > 0, t_x / np.maximum(x, 1.0), np.maximum(T, 1.0))
    p_emp = 1.0 / (1.0 + dsl / (mean_ip + 7.0))
    p_alive = np.where(never, 0.0, 0.5 * p_alive + 0.5 * p_emp)
    lam = (r + x) / (alpha + T + 1e-9)
    e_purch = np.where(never, 0.0, lam * 30.0 * p_alive)
    e_gmv = e_purch * np.clip(aov, 0, None)
    return df.with_columns(
        btyd_p_alive=pl.Series(p_alive),
        btyd_e_purch_30=pl.Series(e_purch),
        btyd_e_gmv=pl.Series(e_gmv),
    )


def attach_vol(df: pl.DataFrame) -> pl.DataFrame:
    """Join vol_v1 per cutoff already on ``df``.

    Args:
        df: Table with user_id and cutoff.

    Returns:
        Rows plus burstiness columns (idempotent).

    Example:
        train = attach_vol(concat_train_fit())
    """
    if "gmv_day_std" in df.columns:
        return df
    parts: list[pl.DataFrame] = []
    for co in df["cutoff"].unique().to_list():
        part = df.filter(pl.col("cutoff") == co)
        parts.append(part.join(build_vol_features(co), on="user_id", how="left"))
    return pl.concat(parts, how="vertical_relaxed")


def load_named(name: str) -> pl.DataFrame:
    """Load cached/build table for a named split in CUTOFFS.

    Args:
        name: Key in CUTOFFS.

    Returns:
        Feature table; target columns present except for ``test``.
    """
    cutoff = CUTOFFS[name]
    return build_cutoff_table(cutoff, with_target=name != "test")


def concat_train_fit() -> pl.DataFrame:
    """Stack TRAIN_FIT_NAMES rows for model fitting (no holdout/primary labels)."""
    return pl.concat([load_named(n) for n in TRAIN_FIT_NAMES], how="vertical_relaxed")
