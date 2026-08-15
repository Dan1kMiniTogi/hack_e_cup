#!/usr/bin/env python3
"""Debug champion H45 (blend_lgb_hgb): SSE anatomy, unused parquet cols, block deltas.

Usage:
    python auto_hip/knowledge/analytics/scripts/004_h45_debug.py

Inputs:
    workspace/runs/h45_blend/preds_{primary,holdout}.parquet
    cached cutoff tables via ltv_data.load_named
    data/train.parquet (lazy schema + unused-col aggregates, no densify)

Outputs:
    auto_hip/knowledge/analytics/results/004_h45_debug.md
    auto_hip/knowledge/analytics/results/004_h45_debug.json

Example:
    python auto_hip/knowledge/analytics/scripts/004_h45_debug.py
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import polars as pl

WS = Path(__file__).resolve().parents[3] / "workspace"
RESULTS = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(WS))

from ltv_arms import BASE_FEATURES, GAP_FEATURES, H26_COLS, ORDER_FEATURES, RATIO_FEATURES  # noqa: E402
from ltv_data import CUTOFFS, PARQUET_PATH, VALUE_COLS, load_named  # noqa: E402
from ltv_metrics import ERROR_Q, add_slices, hist_gmv_quantiles  # noqa: E402

ID_COLS = {"event_date", "user_id"}
FLAG_COLS = {"search", "cat"}
UNUSED_COUNTS = (
    "has_search_to_cart",
    "has_search_to_ord",
    "has_cat_to_cart",
    "has_cat_to_ord",
    "search_to_cart",
    "search_to_ord",
    "cat_to_cart",
    "cat_to_ord",
)

# Sequential primary RMSLE from past/INDEX and 003_line_scorecard (not orthogonal ablation).
BLOCK_DELTAS = [
    {"block": "naive last-30d", "hyp": "H00", "primary": 2.195065, "delta": None, "note": "control"},
    {"block": "HGB log1p on window sums (BASE)", "hyp": "H04", "primary": 1.708261, "delta": -0.4868, "note": "единственный большой скачок"},
    {"block": "two heads y_search+y_cat", "hyp": "H05", "primary": 1.699272, "delta": -0.0090, "note": "обязателен; single-head ~1.705"},
    {"block": "GAP features", "hyp": "H07", "primary": 1.698668, "delta": -0.0006, "note": "мелочь; на одной голове вред (H06)"},
    {"block": "RATIO intensity/conv", "hyp": "H11", "primary": 1.698140, "delta": -0.0005, "note": "мелочь"},
    {"block": "depth8 / L2", "hyp": "H15", "primary": 1.697504, "delta": -0.0006, "note": "H13+H15 vs H11; насыщение ёмкости"},
    {"block": "recency_order_days", "hyp": "H17", "primary": 1.697047, "delta": -0.0005, "note": "vs H15; последний полезный агрегат"},
    {"block": "max_iter 320 / lr 0.04", "hyp": "H19", "primary": 1.696721, "delta": -0.0003, "note": "vs H17"},
    {"block": "3-seed HGB", "hyp": "H26", "primary": 1.696510, "delta": -0.0002, "note": "vs H19"},
    {"block": "3-seed LightGBM two-head", "hyp": "H31", "primary": 1.696113, "delta": -0.0004, "note": "vs H26"},
    {"block": "0.5 LGB + 0.5 HGB same H26_COLS", "hyp": "H45", "primary": 1.696101, "delta": -0.000012, "note": "champion; разнообразие сплитта, не данных"},
]


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman rank correlation; NaN-safe, no scipy.

    Args:
        a, b: 1-d arrays of equal length.

    Returns:
        Spearman rho or NaN if fewer than 50 finite pairs.

    Example:
        rho = _spearman(feat, log_bias)
    """
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() < 50:
        return float("nan")
    ra = a[mask].argsort().argsort().astype(np.float64)
    rb = b[mask].argsort().argsort().astype(np.float64)
    ra -= ra.mean()
    rb -= rb.mean()
    den = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / den) if den else float("nan")


def _md_table(rows: list[dict], cols: list[str]) -> list[str]:
    """Markdown table from list of dicts."""
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return lines


def attach(split: str, q50: float, q90: float) -> pl.DataFrame:
    """Join H45 preds with features, slices, and squared-log error.

    Args:
        split: primary | holdout
        q50, q90: hist_gmv quantiles from train-fit

    Returns:
        One row per user_id with y, predict, slices, se, log_bias, order_bucket.

    Example:
        df = attach("primary", q50, q90)
    """
    preds = pl.read_parquet(WS / "runs/h45_blend" / f"preds_{split}.parquet").sort("user_id")
    feats = add_slices(load_named(split).sort("user_id"), q50, q90)
    y = preds["y"].to_numpy()
    p = np.clip(preds["predict"].to_numpy(), 0, None)
    se = (np.log1p(np.clip(y, 0, None)) - np.log1p(p)) ** 2
    log_bias = np.log1p(p) - np.log1p(np.clip(y, 0, None))
    rec_ord = feats["recency_order_days"] if "recency_order_days" in feats.columns else pl.lit(None)
    df = feats.with_columns(
        predict=pl.Series(p),
        y=pl.Series(y),
        se=pl.Series(se),
        log_bias=pl.Series(log_bias),
        recency_order_days=rec_ord,
    )
    return df.with_columns(
        order_bucket=pl.when(pl.col("recency_order_days").is_null())
        .then(pl.lit("never_ord"))
        .when(pl.col("recency_order_days") <= 7)
        .then(pl.lit("0_7"))
        .when(pl.col("recency_order_days") <= 30)
        .then(pl.lit("8_30"))
        .when(pl.col("recency_order_days") <= 90)
        .then(pl.lit("31_90"))
        .otherwise(pl.lit("91_plus")),
    )


def mass_rows(df: pl.DataFrame, col: str) -> list[dict]:
    """Share of total squared-log-error by a categorical column.

    Args:
        df: Table with se, y, predict and ``col``.
        col: Grouping column.

    Returns:
        One dict per slice with n, sse_share, rmsle, means.

    Example:
        rows = mass_rows(df, "hist_gmv_bucket")
    """
    tot = float(df["se"].sum())
    g = (
        df.group_by(col)
        .agg(
            n=pl.len(),
            se_sum=pl.col("se").sum(),
            rmsle=pl.col("se").mean().sqrt(),
            mean_y=pl.col("y").mean(),
            mean_pred=pl.col("predict").mean(),
            y_zero=pl.col("y").eq(0).mean(),
        )
        .sort(col)
    )
    out = []
    for r in g.iter_rows(named=True):
        share = float(r["se_sum"]) / tot if tot else 0.0
        my, mp = float(r["mean_y"]), float(r["mean_pred"])
        out.append(
            {
                "slice": str(r[col]),
                "n": int(r["n"]),
                "n_share": round(int(r["n"]) / df.height, 4),
                "sse_share": round(share, 4),
                "rmsle": round(float(r["rmsle"]), 4),
                "mean_y": round(my, 2),
                "mean_pred": round(mp, 2),
                "ratio": round(mp / my, 3) if my else 0.0,
                "y_zero": round(float(r["y_zero"]), 4),
            }
        )
    return out


def y_quantile_mass(df: pl.DataFrame) -> list[dict]:
    """SSE share by y=0 vs positive y quintiles."""
    pos = df.filter(pl.col("y") > 0)
    qs = [float(pos["y"].quantile(q) or 0.0) for q in (0.2, 0.4, 0.6, 0.8)]
    y = df["y"].to_numpy()
    bucket = np.full(df.height, "y=0", dtype=object)
    pos_mask = y > 0
    yp = y[pos_mask]
    labels = np.array(["q1", "q2", "q3", "q4", "q5"], dtype=object)
    idx = np.clip(np.digitize(yp, qs, right=True), 0, 4)
    bucket[pos_mask] = labels[idx]
    return mass_rows(df.with_columns(yq=pl.Series(bucket)), "yq")


def tail_block(df: pl.DataFrame) -> dict:
    """q90 sq-log-error anatomy on this split's own H45 preds."""
    se = df["se"].to_numpy()
    y = df["y"].to_numpy()
    p = df["predict"].to_numpy()
    thr = float(np.quantile(se, ERROR_Q))
    tail = se >= thr
    return {
        "threshold": round(thr, 4),
        "n_tail": int(tail.sum()),
        "tail_y_zero": round(float((y[tail] == 0).mean()), 4),
        "tail_mean_y": round(float(y[tail].mean()), 2),
        "tail_mean_pred": round(float(p[tail].mean()), 2),
        "tail_under": round(float((p[tail] < y[tail]).mean()), 4),
    }


def unused_schema() -> dict:
    """Compare parquet schema vs VALUE_COLS / H26 feature construction.

    Returns:
        Dict with raw columns, used value cols, unused funnel cols, H26 feature groups.

    Example:
        info = unused_schema()
    """
    schema = pl.scan_parquet(PARQUET_PATH).collect_schema()
    raw = list(schema.names())
    unused = [c for c in raw if c not in ID_COLS | FLAG_COLS | set(VALUE_COLS)]
    return {
        "raw_columns": raw,
        "value_cols_aggregated": list(VALUE_COLS),
        "flags_as_any": sorted(FLAG_COLS),
        "unused_in_aggregates": unused,
        "h26_n": len(H26_COLS),
        "h26_groups": {
            "BASE": len(BASE_FEATURES),
            "GAP": len(GAP_FEATURES),
            "RATIO": len(RATIO_FEATURES),
            "ORDER": len(ORDER_FEATURES),
        },
        "h45_uses_only_H26_COLS": True,
        "h45_not_using": ["DECAY", "WEEKDAY", "LASTK", "VOL", "RFM_TE"],
    }


def unused_spearman(primary: pl.DataFrame) -> list[dict]:
    """Lifetime sums of unused funnel columns vs H45 log_bias on primary cutoff.

    Args:
        primary: H45-attached primary table with user_id and log_bias.

    Returns:
        Spearman rows for each unused count/flag (hist ≤ cutoff, no densify).

    Example:
        rows = unused_spearman(primary)
    """
    cutoff = CUTOFFS["primary"]
    lf = pl.scan_parquet(PARQUET_PATH).filter(pl.col("event_date") <= cutoff)
    aggs = []
    for c in UNUSED_COUNTS:
        if c.startswith("has_"):
            aggs.append(pl.max(c).alias(f"hist_{c}"))
        else:
            aggs.append(pl.sum(c).alias(f"hist_{c}"))
    extra = lf.group_by("user_id").agg(aggs).collect()
    joined = primary.select("user_id", "log_bias").join(extra, on="user_id", how="left")
    resid = joined["log_bias"].to_numpy()
    rows = []
    for c in extra.columns:
        if c == "user_id":
            continue
        x = joined[c].fill_null(0).to_numpy().astype(np.float64)
        rows.append(
            {
                "feature": c,
                "nonzero_share": round(float((x > 0).mean()), 4),
                "mean": round(float(x.mean()), 4),
                "spearman_vs_log_bias": round(_spearman(x, resid), 4),
            }
        )
    rows.sort(key=lambda r: abs(r["spearman_vs_log_bias"]), reverse=True)
    return rows


def existing_spearman(df: pl.DataFrame) -> list[dict]:
    """Spearman of current H26-ish features vs log residual."""
    resid = df["log_bias"].to_numpy()
    cols = [
        "gmv_sum_30d",
        "gmv_sum_90d",
        "hist_gmv",
        "to_ord_sum_30d",
        "searches_sum_30d",
        "last_gap",
        "mean_gap",
        "recency_days",
        "recency_order_days",
    ]
    work = df.with_columns(pl.col("recency_days").fill_null(9999))
    if "recency_order_days" in work.columns:
        work = work.with_columns(pl.col("recency_order_days").fill_null(9999))
    rows = []
    for c in cols:
        if c not in work.columns:
            continue
        x = work[c].to_numpy().astype(np.float64)
        rows.append({"feature": c, "spearman_vs_log_bias": round(_spearman(x, resid), 4)})
    rows.sort(key=lambda r: abs(r["spearman_vs_log_bias"]), reverse=True)
    return rows


def split_payload(df: pl.DataFrame) -> dict:
    """Scalar + slice SSE packs for one split."""
    y = df["y"].to_numpy()
    p = df["predict"].to_numpy()
    se = df["se"].to_numpy()
    tot = float(se.sum())
    z = y == 0
    return {
        "n": df.height,
        "rmsle": round(float(np.sqrt(se.mean())), 6),
        "mean_y": round(float(y.mean()), 3),
        "mean_pred": round(float(p.mean()), 3),
        "corr": round(float(np.corrcoef(y, p)[0, 1]), 4),
        "zero_pred_share": round(float((p == 0).mean()), 6),
        "y_zero_share": round(float(z.mean()), 4),
        "sse_share_y0": round(float(se[z].sum() / tot), 4),
        "sse_share_ypos": round(float(se[~z].sum() / tot), 4),
        "rmsle_y0": round(float(np.sqrt(se[z].mean())), 4),
        "rmsle_ypos": round(float(np.sqrt(se[~z].mean())), 4),
        "under_share": round(float((p < y).mean()), 4),
        "mean_log_bias": round(float(df["log_bias"].mean()), 4),
        "mean_pred_on_y0": round(float(p[z].mean()), 3),
        "y_quantiles": y_quantile_mass(df),
        "hist_gmv": mass_rows(df, "hist_gmv_bucket"),
        "recency": mass_rows(df, "recency_bucket"),
        "activity": mass_rows(df, "activity_days_bucket"),
        "channel": mass_rows(df, "channel_mix"),
        "order_recency": mass_rows(df, "order_bucket"),
        "tail": tail_block(df),
        "spearman_existing": existing_spearman(df),
    }


def fmt_mass(title: str, rows: list[dict]) -> list[str]:
    lines = [f"### {title}", ""]
    lines += _md_table(
        rows,
        ["slice", "n", "n_share", "sse_share", "rmsle", "mean_y", "mean_pred", "ratio", "y_zero"],
    )
    lines.append("")
    return lines


def split_md(name: str, payload: dict) -> list[str]:
    lines = [
        f"## {name}",
        "",
        f"- n={payload['n']} rmsle={payload['rmsle']} mean_y={payload['mean_y']} mean_pred={payload['mean_pred']} corr={payload['corr']}",
        f"- y_zero={payload['y_zero_share']} zero_pred={payload['zero_pred_share']} under={payload['under_share']} mean_log_bias={payload['mean_log_bias']}",
        f"- **SSE share y=0: {payload['sse_share_y0']}** (rmsle_y0={payload['rmsle_y0']}, mean_pred_on_y0={payload['mean_pred_on_y0']}); "
        f"y>0 share {payload['sse_share_ypos']} (rmsle_ypos={payload['rmsle_ypos']})",
        "",
    ]
    lines += fmt_mass("Масса SSE по y-квантилям (y=0 отдельно, затем quintiles y>0)", payload["y_quantiles"])
    lines += fmt_mass("hist_gmv_bucket", payload["hist_gmv"])
    lines += fmt_mass("recency_bucket", payload["recency"])
    lines += fmt_mass("activity_days_bucket", payload["activity"])
    lines += fmt_mass("channel_mix", payload["channel"])
    lines += fmt_mass("order_recency (last to_ord>0)", payload["order_recency"])
    t = payload["tail"]
    lines += [
        "### Хвост sq-log q90 (свой split)",
        "",
        f"threshold={t['threshold']} n={t['n_tail']} y_zero_in_tail={t['tail_y_zero']} "
        f"mean_y={t['tail_mean_y']} mean_pred={t['tail_mean_pred']} under_in_tail={t['tail_under']}",
        "",
        "### Spearman текущих фич vs log_bias",
        "",
    ]
    lines += _md_table(payload["spearman_existing"], ["feature", "spearman_vs_log_bias"])
    lines.append("")
    return lines


def main() -> None:
    """Write H45 debug markdown + json. No model refit."""
    train = pl.concat([load_named(n) for n in ("train_a", "train_b", "inner_train")], how="vertical_relaxed")
    q50, q90 = hist_gmv_quantiles(train)
    primary = attach("primary", q50, q90)
    holdout = attach("holdout", q50, q90)
    p_json = split_payload(primary)
    h_json = split_payload(holdout)
    schema = unused_schema()
    funnel_rho = unused_spearman(primary)

    block_rows = []
    for b in BLOCK_DELTAS:
        d = "" if b["delta"] is None else f"{b['delta']:+.6f}".rstrip("0").rstrip(".")
        block_rows.append({**b, "delta": d if d else "—"})

    lines = [
        "# 004 — Debug champion H45 (blend_lgb_hgb)",
        "",
        "Pred: `workspace/runs/h45_blend`. Без densify, без user_id, без ретрейна 12 моделей. "
        "Квантили hist_gmv с train-fit. Блочный вклад — последовательные Δ из INDEX/scorecard, не ортогональная абляция.",
        "",
        "## Факты",
        "",
        f"- Primary RMSLE {p_json['rmsle']}: **{p_json['sse_share_y0']*100:.1f}%** SSE на y=0 "
        f"(доля пользователей {p_json['y_zero_share']}); rmsle_y0={p_json['rmsle_y0']}, mean_pred на нулях={p_json['mean_pred_on_y0']}.",
        f"- mean_pred/mean_y primary = {p_json['mean_pred']/p_json['mean_y']:.3f}; holdout = {h_json['mean_pred']/h_json['mean_y']:.3f}. "
        f"mean_true holdout {h_json['mean_y']} vs primary {p_json['mean_y']}.",
        f"- zero_pred_share primary {p_json['zero_pred_share']} при y_zero {p_json['y_zero_share']}; модель почти не предсказывает ноль.",
        f"- mean_log_bias primary {p_json['mean_log_bias']} (>0 ⇒ в log-пространстве типичный пользователь переоценён).",
        "- Структура ошибки совпадает с H26: y=0 ≈52% SSE, hist_gmv mid ≈45% SSE. Смесь LGB+HGB не сдвинула массу ошибок.",
        "",
        "## Вклад блоков (последовательные прогоны H00→H45)",
        "",
        "Не абляция: каждый шаг включает предыдущие фичи. Δ — primary RMSLE vs предыдущая строка чемпиона/якоря в таблице.",
        "",
    ]
    lines += _md_table(block_rows, ["block", "hyp", "primary", "delta", "note"])
    lines += [
        "",
        "H04→H45 = **−0.012** на той же таблице оконных сумм. После H05 каждый шаг ≤0.0006.",
        "",
        "## Неиспользованные колонки parquet",
        "",
        f"- Raw: `{', '.join(schema['raw_columns'])}`",
        f"- Агрегируются в окна (`VALUE_COLS`): `{', '.join(schema['value_cols_aggregated'])}`",
        f"- Флаги как `any_*`: `{', '.join(schema['flags_as_any'])}`",
        f"- **Не входят в агрегаты H26/H45:** `{', '.join(schema['unused_in_aggregates'])}`",
        f"- H45 фичи: {schema['h26_n']} колонок H26_COLS "
        f"(BASE {schema['h26_groups']['BASE']}, GAP {schema['h26_groups']['GAP']}, "
        f"RATIO {schema['h26_groups']['RATIO']}, ORDER {schema['h26_groups']['ORDER']}). "
        f"Не используются: {', '.join(schema['h45_not_using'])}.",
        "",
        "Spearman lifetime-сумм неиспользованных колонок vs log_bias H45 на primary "
        "(история ≤ 2026-01-14, без densify). Для сравнения: у текущих фич |ρ|<0.08.",
        "",
    ]
    lines += _md_table(funnel_rho, ["feature", "nonzero_share", "mean", "spearman_vs_log_bias"])
    lines += [
        "",
        "Если |ρ| сопоставим с текущими фичами — колонка коллинеарна остатку так же слабо; "
        "если выше — есть невыжатый линейный сигнал. Даже при низком ρ деревья могут взять взаимодействия воронки с каналом.",
        "",
    ]
    lines += split_md("primary (cutoff 2026-01-14)", p_json)
    lines += split_md("holdout (cutoff 2025-12-15)", h_json)
    lines += [
        "## Критические дыры (сводка)",
        "",
        "1. Воронка по каналам (`search_to_ord` / `cat_to_ord` / `has_*`) не в таблице фич — единственный сырой слой parquet вне H26.",
        "2. 52% SSE на y=0 при mean_pred~8 и zero_pred≈0; split-specific zero-hack не переносится (H12 holdout).",
        "3. Нет календаря целевого окна: holdout-target включает НГ, primary тише, тест Feb–Mar — третий сезон.",
        "4. Окна 7/14/30/60/90 вложенные, нет disjoint 30d лагов таргета.",
        "5. Пользователь×cutoff как iid, без BTYD/P(alive). H03 hurdle — другой механизм.",
        "6. mid hist_gmv держит ~45% SSE; RFM TE / mid-residual не закрыли.",
        "",
    ]

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "004_h45_debug.md").write_text("\n".join(lines) + "\n")
    (RESULTS / "004_h45_debug.json").write_text(
        json.dumps(
            {
                "q50": q50,
                "q90": q90,
                "primary": p_json,
                "holdout": h_json,
                "schema": schema,
                "unused_spearman": funnel_rho,
                "block_deltas": BLOCK_DELTAS,
            },
            indent=2,
        )
    )
    print(f"wrote {RESULTS / '004_h45_debug.md'}")


if __name__ == "__main__":
    main()
