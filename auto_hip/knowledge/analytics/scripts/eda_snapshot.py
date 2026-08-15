#!/usr/bin/env python3
"""EDA snapshot for E-CUP 2026 task 3 (30d GMV / RMSLE).

Reads ``data/train.parquet`` via Polars lazy scan (no dense calendar fill).
Writes markdown + JSON under ``knowledge/analytics/results/``.

Usage:
    python auto_hip/knowledge/analytics/scripts/eda_snapshot.py

Inputs:
    data/train.parquet (repo root).

Outputs:
    auto_hip/knowledge/analytics/results/001_eda_snapshot.md
    auto_hip/knowledge/analytics/results/001_eda_snapshot.json
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[4]
PARQUET_PATH = REPO_ROOT / "data" / "train.parquet"
RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"

CUTOFF = date(2026, 1, 14)
HORIZON_DAYS = 30
TARGET_START = CUTOFF + timedelta(days=1)
TARGET_END = CUTOFF + timedelta(days=HORIZON_DAYS)
NAIVE_START = CUTOFF - timedelta(days=HORIZON_DAYS - 1)
USER_MOD = 12


def _rmsle(y: pl.Series, yhat: pl.Series) -> float:
    """Root mean squared log1p error; clips predictions at 0.

    Args:
        y: True 30d GMV.
        yhat: Predicted 30d GMV.

    Returns:
        Scalar RMSLE.
    """
    yt = y.to_numpy()
    yp = yhat.clip(lower_bound=0).to_numpy()
    import numpy as np

    return float(np.sqrt(np.mean((np.log1p(yt) - np.log1p(yp)) ** 2)))


def _mae_log1p(y: pl.Series, yhat: pl.Series) -> float:
    """Mean absolute log1p error; clips predictions at 0."""
    import numpy as np

    yt = y.to_numpy()
    yp = yhat.clip(lower_bound=0).to_numpy()
    return float(np.mean(np.abs(np.log1p(yt) - np.log1p(yp))))


def _pct(series: pl.Series, p: float) -> float:
    """Percentile of a numeric series (0–100)."""
    v = series.quantile(p / 100.0)
    return float(v) if v is not None else float("nan")


def collect_global(lf: pl.LazyFrame) -> dict:
    """Cheap full-table aggregates: size, dates, nulls, daily activity.

    Args:
        lf: Lazy scan of train.parquet.

    Returns:
        JSON-serializable dict with global stats.
    """
    n_rows = lf.select(pl.len().alias("n")).collect().item()
    n_users = lf.select(pl.col("user_id").n_unique()).collect().item()
    date_bounds = lf.select(
        pl.col("event_date").min().alias("min_d"),
        pl.col("event_date").max().alias("max_d"),
    ).collect()
    nulls = lf.null_count().collect()
    null_total = int(nulls.sum_horizontal().item())
    daily = (
        lf.group_by("event_date")
        .agg(
            pl.len().alias("n_rows"),
            pl.sum("gmv").alias("gmv_sum"),
            pl.col("user_id").n_unique().alias("n_users"),
        )
        .sort("event_date")
        .collect()
    )
    n_days = daily.height
    return {
        "n_rows": int(n_rows),
        "n_users": int(n_users),
        "min_date": str(date_bounds["min_d"].item()),
        "max_date": str(date_bounds["max_d"].item()),
        "n_calendar_span_days": (
            date_bounds["max_d"].item() - date_bounds["min_d"].item()
        ).days
        + 1,
        "n_days_with_rows": int(n_days),
        "null_cells_total": null_total,
        "daily_n_rows": {
            "min": int(daily["n_rows"].min()),
            "p50": int(_pct(daily["n_rows"], 50)),
            "p90": int(_pct(daily["n_rows"], 90)),
            "max": int(daily["n_rows"].max()),
            "mean": float(daily["n_rows"].mean()),
        },
        "daily_gmv_sum": {
            "min": float(daily["gmv_sum"].min()),
            "p50": float(_pct(daily["gmv_sum"], 50)),
            "p90": float(_pct(daily["gmv_sum"], 90)),
            "max": float(daily["gmv_sum"].max()),
            "mean": float(daily["gmv_sum"].mean()),
        },
        "daily_n_users": {
            "min": int(daily["n_users"].min()),
            "p50": int(_pct(daily["n_users"], 50)),
            "p90": int(_pct(daily["n_users"], 90)),
            "max": int(daily["n_users"].max()),
            "mean": float(daily["n_users"].mean()),
        },
        "first_3_days": [
            {
                "event_date": str(r["event_date"]),
                "n_rows": int(r["n_rows"]),
                "gmv_sum": float(r["gmv_sum"]),
            }
            for r in daily.head(3).iter_rows(named=True)
        ],
        "last_3_days": [
            {
                "event_date": str(r["event_date"]),
                "n_rows": int(r["n_rows"]),
                "gmv_sum": float(r["gmv_sum"]),
            }
            for r in daily.tail(3).iter_rows(named=True)
        ],
        "sparsity_note": (
            "rows_per_user_mean = n_rows/n_users; dense fill would be "
            "n_users * n_calendar_span_days"
        ),
        "rows_per_user_mean": float(n_rows) / float(n_users),
        "dense_row_estimate": int(n_users) * int(
            (date_bounds["max_d"].item() - date_bounds["min_d"].item()).days + 1
        ),
    }


def collect_sample_user_table(lf: pl.LazyFrame) -> tuple[pl.DataFrame, dict]:
    """User-level features/target on a hash sample for primary cutoff.

    Args:
        lf: Lazy scan of train.parquet.

    Returns:
        Tuple of (user table, sample meta). Sample: ``user_id % USER_MOD == 0``.
        Users with no rows in a window get 0 / null recency (no densify of days).
    """
    sample_ids = (
        lf.select(pl.col("user_id").unique())
        .filter((pl.col("user_id") % USER_MOD) == 0)
        .collect()
        .get_column("user_id")
    )
    n_sample = sample_ids.len()
    sample_lf = lf.filter(pl.col("user_id").is_in(sample_ids.to_list()))
    sample_df = sample_lf.collect()

    hist = sample_df.filter(pl.col("event_date") <= CUTOFF)
    tgt = sample_df.filter(
        pl.col("event_date").is_between(TARGET_START, TARGET_END, closed="both")
    )
    naive = sample_df.filter(
        pl.col("event_date").is_between(NAIVE_START, CUTOFF, closed="both")
    )

    hist_u = hist.group_by("user_id").agg(
        pl.len().alias("activity_days"),
        pl.col("event_date").max().alias("last_activity"),
        pl.col("event_date")
        .filter(pl.col("gmv") > 0)
        .max()
        .alias("last_order_date"),
        pl.sum("gmv").alias("hist_gmv"),
        pl.sum("gmv_search").alias("hist_gmv_search"),
        pl.sum("gmv_cat").alias("hist_gmv_cat"),
        pl.sum("searches").alias("hist_searches"),
        pl.max("search").alias("any_search"),
        pl.max("cat").alias("any_cat"),
        pl.sum("to_ord").alias("hist_orders"),
    )
    y_u = tgt.group_by("user_id").agg(pl.sum("gmv").alias("y"))
    pred_u = naive.group_by("user_id").agg(pl.sum("gmv").alias("pred_naive"))

    users = pl.DataFrame({"user_id": sample_ids})
    users = (
        users.join(hist_u, on="user_id", how="left")
        .join(y_u, on="user_id", how="left")
        .join(pred_u, on="user_id", how="left")
        .with_columns(
            pl.col("y").fill_null(0.0),
            pl.col("pred_naive").fill_null(0.0),
            pl.col("hist_gmv").fill_null(0.0),
            pl.col("hist_gmv_search").fill_null(0.0),
            pl.col("hist_gmv_cat").fill_null(0.0),
            pl.col("hist_searches").fill_null(0),
            pl.col("hist_orders").fill_null(0),
            pl.col("activity_days").fill_null(0),
            pl.col("any_search").fill_null(0),
            pl.col("any_cat").fill_null(0),
        )
    )
    users = users.with_columns(
        recency_days=(
            pl.when(pl.col("last_activity").is_null())
            .then(None)
            .otherwise((pl.lit(CUTOFF) - pl.col("last_activity")).dt.total_days())
        ),
        recency_order_days=(
            pl.when(pl.col("last_order_date").is_null())
            .then(None)
            .otherwise((pl.lit(CUTOFF) - pl.col("last_order_date")).dt.total_days())
        ),
    )
    pos_gmv = users.filter(pl.col("hist_gmv") > 0)["hist_gmv"]
    q50 = float(pos_gmv.quantile(0.5) or 0.0)
    q90 = float(pos_gmv.quantile(0.9) or 0.0)

    users = users.with_columns(
        recency_bucket=pl.when(pl.col("recency_days").is_null())
        .then(pl.lit("never"))
        .when(pl.col("recency_days") <= 7)
        .then(pl.lit("0_7"))
        .when(pl.col("recency_days") <= 30)
        .then(pl.lit("8_30"))
        .when(pl.col("recency_days") <= 90)
        .then(pl.lit("31_90"))
        .otherwise(pl.lit("91_plus")),
        hist_gmv_bucket=pl.when(pl.col("hist_gmv") <= 0)
        .then(pl.lit("zero"))
        .when(pl.col("hist_gmv") <= q50)
        .then(pl.lit("low"))
        .when(pl.col("hist_gmv") <= q90)
        .then(pl.lit("mid"))
        .otherwise(pl.lit("high")),
        activity_days_bucket=pl.when(pl.col("activity_days") == 0)
        .then(pl.lit("0"))
        .when(pl.col("activity_days") <= 5)
        .then(pl.lit("1_5"))
        .when(pl.col("activity_days") <= 20)
        .then(pl.lit("6_20"))
        .when(pl.col("activity_days") <= 60)
        .then(pl.lit("21_60"))
        .otherwise(pl.lit("61_plus")),
        channel_mix=pl.when((pl.col("any_search") > 0) & (pl.col("any_cat") > 0))
        .then(pl.lit("both"))
        .when(pl.col("any_search") > 0)
        .then(pl.lit("search_only"))
        .when(pl.col("any_cat") > 0)
        .then(pl.lit("cat_only"))
        .otherwise(pl.lit("neither")),
    )
    meta = {
        "user_mod": USER_MOD,
        "n_sample_users": int(n_sample),
        "n_sample_rows": int(sample_df.height),
        "cutoff": str(CUTOFF),
        "target_window": [str(TARGET_START), str(TARGET_END)],
        "naive_window": [str(NAIVE_START), str(CUTOFF)],
        "hist_gmv_positive_q50": q50,
        "hist_gmv_positive_q90": q90,
    }
    return users, meta


def _slice_table(users: pl.DataFrame, col: str) -> list[dict]:
    """Aggregate y vs naive pred by a slice column.

    Args:
        users: User-level frame with y, pred_naive, slice col.
        col: Slice dimension name.

    Returns:
        Rows sorted by slice label.
    """
    g = users.group_by(col).agg(
        pl.len().alias("n"),
        (pl.col("y") == 0).mean().alias("y_zero_share"),
        pl.col("y").mean().alias("mean_y"),
        pl.col("y").median().alias("median_y"),
        pl.col("pred_naive").mean().alias("mean_pred"),
        (pl.col("pred_naive") == 0).mean().alias("zero_pred_share"),
    )
    sq = users.with_columns(
        sqerr=((pl.col("y").log1p() - pl.col("pred_naive").clip(lower_bound=0).log1p()) ** 2)
    )
    rms = sq.group_by(col).agg(pl.col("sqerr").mean().sqrt().alias("rmsle"))
    out = g.join(rms, on=col).sort(col)
    rows = []
    for r in out.iter_rows(named=True):
        rows.append(
            {
                "slice": str(r[col]),
                "n": int(r["n"]),
                "share": round(int(r["n"]) / users.height, 4),
                "y_zero_share": round(float(r["y_zero_share"]), 4),
                "mean_y": round(float(r["mean_y"]), 4),
                "median_y": round(float(r["median_y"]), 4),
                "mean_pred": round(float(r["mean_pred"]), 4),
                "zero_pred_share": round(float(r["zero_pred_share"]), 4),
                "rmsle": round(float(r["rmsle"]), 4),
            }
        )
    return rows


def collect_sample_stats(users: pl.DataFrame, meta: dict) -> dict:
    """Target, naive RMSLE, channel GMV mix, and METRICS slices on the sample."""
    y = users["y"]
    pred = users["pred_naive"]
    y_pos = users.filter(pl.col("y") > 0)["y"]
    hist_sum = float(users["hist_gmv"].sum())
    search_sum = float(users["hist_gmv_search"].sum())
    cat_sum = float(users["hist_gmv_cat"].sum())
    return {
        **meta,
        "y_zero_share": float((y == 0).mean()),
        "y_mean": float(y.mean()),
        "y_median": float(y.median()),
        "y_p90": float(_pct(y, 90)),
        "y_p99": float(_pct(y, 99)),
        "y_positive": {
            "n": int(y_pos.len()),
            "mean": float(y_pos.mean()) if y_pos.len() else None,
            "median": float(y_pos.median()) if y_pos.len() else None,
            "p90": float(_pct(y_pos, 90)) if y_pos.len() else None,
            "p99": float(_pct(y_pos, 99)) if y_pos.len() else None,
        },
        "naive_metrics": {
            "scope": "hash sample, not full 250k",
            "rmsle": _rmsle(y, pred),
            "mae_log1p": _mae_log1p(y, pred),
            "zero_pred_share": float((pred == 0).mean()),
            "mean_pred": float(pred.mean()),
            "mean_true": float(y.mean()),
        },
        "channel_gmv_hist": {
            "gmv_search_share": (search_sum / hist_sum) if hist_sum else None,
            "gmv_cat_share": (cat_sum / hist_sum) if hist_sum else None,
            "hist_gmv_sum": hist_sum,
        },
        "slices": {
            "recency_bucket": _slice_table(users, "recency_bucket"),
            "hist_gmv_bucket": _slice_table(users, "hist_gmv_bucket"),
            "activity_days_bucket": _slice_table(users, "activity_days_bucket"),
            "channel_mix": _slice_table(users, "channel_mix"),
        },
    }


def _md_table(rows: list[dict], keys: list[str]) -> str:
    header = "| " + " | ".join(keys) + " |"
    sep = "| " + " | ".join("---" for _ in keys) + " |"
    lines = [header, sep]
    for r in rows:
        lines.append("| " + " | ".join(str(r[k]) for k in keys) + " |")
    return "\n".join(lines)


def render_markdown(global_stats: dict, sample: dict) -> str:
    """Build the human-readable snapshot (no user ids)."""
    g, s = global_stats, sample
    nm = s["naive_metrics"]
    yp = s["y_positive"]
    ch = s["channel_gmv_hist"]
    slice_keys = [
        "slice",
        "n",
        "share",
        "y_zero_share",
        "mean_y",
        "median_y",
        "mean_pred",
        "zero_pred_share",
        "rmsle",
    ]
    parts = [
        "# 001 — EDA snapshot (sample_fast)",
        "",
        "Источник: `data/train.parquet` через Polars lazy scan. **Без** dense calendar.",
        "Выборка пользователей: `user_id % 12 == 0` на cutoff `2026-01-14`.",
        "Naive pred = сумма `gmv` за `[2025-12-16, 2026-01-14]`; y = сумма `gmv` за `[2026-01-15, 2026-02-13]`.",
        "Метрики naive — **только на выборке**, не полный 250k и не лидерборд.",
        "",
        "## Global",
        "",
        f"- rows: `{g['n_rows']}` · users: `{g['n_users']}` · days with rows: `{g['n_days_with_rows']}` · calendar span: `{g['n_calendar_span_days']}`",
        f"- dates: `{g['min_date']}` … `{g['max_date']}` · null cells: `{g['null_cells_total']}`",
        f"- rows/user mean: `{g['rows_per_user_mean']:.2f}` · dense fill estimate: `{g['dense_row_estimate']}` rows",
        "",
        "Daily `n_rows`: "
        f"min `{g['daily_n_rows']['min']}`, p50 `{g['daily_n_rows']['p50']}`, "
        f"p90 `{g['daily_n_rows']['p90']}`, max `{g['daily_n_rows']['max']}`, "
        f"mean `{g['daily_n_rows']['mean']:.1f}`.",
        "",
        "Daily `gmv_sum`: "
        f"min `{g['daily_gmv_sum']['min']:.2f}`, p50 `{g['daily_gmv_sum']['p50']:.2f}`, "
        f"p90 `{g['daily_gmv_sum']['p90']:.2f}`, max `{g['daily_gmv_sum']['max']:.2f}`, "
        f"mean `{g['daily_gmv_sum']['mean']:.2f}`.",
        "",
        "Daily active users (unique `user_id` that day): "
        f"min `{g['daily_n_users']['min']}`, p50 `{g['daily_n_users']['p50']}`, "
        f"p90 `{g['daily_n_users']['p90']}`, max `{g['daily_n_users']['max']}`, "
        f"mean `{g['daily_n_users']['mean']:.1f}`.",
        "",
        "First days: " + ", ".join(
            f"{d['event_date']} (rows={d['n_rows']}, gmv={d['gmv_sum']:.1f})"
            for d in g["first_3_days"]
        ),
        "",
        "Last days: " + ", ".join(
            f"{d['event_date']} (rows={d['n_rows']}, gmv={d['gmv_sum']:.1f})"
            for d in g["last_3_days"]
        ),
        "",
        "## Sample (primary split)",
        "",
        f"- n_users: `{s['n_sample_users']}` · n_rows in sample: `{s['n_sample_rows']}`",
        f"- hist_gmv > 0 quantiles used for buckets: q50 `{s['hist_gmv_positive_q50']:.4f}`, q90 `{s['hist_gmv_positive_q90']:.4f}`",
        f"- y=0 share: `{s['y_zero_share']:.4f}` · y mean `{s['y_mean']:.4f}` · median `{s['y_median']:.4f}` · p90 `{s['y_p90']:.4f}` · p99 `{s['y_p99']:.4f}`",
        f"- y>0 only (n={yp['n']}): mean `{yp['mean']:.4f}` · median `{yp['median']:.4f}` · p90 `{yp['p90']:.4f}` · p99 `{yp['p99']:.4f}`",
        "",
        "## Naive champion proxy (sample)",
        "",
        f"- rmsle: `{nm['rmsle']:.6f}`",
        f"- mae_log1p: `{nm['mae_log1p']:.6f}`",
        f"- zero_pred_share: `{nm['zero_pred_share']:.4f}`",
        f"- mean_pred: `{nm['mean_pred']:.4f}` · mean_true: `{nm['mean_true']:.4f}`",
        "",
        "## Channel GMV (history ≤ cutoff, sample)",
        "",
        f"- gmv_search share: `{ch['gmv_search_share']:.4f}` · gmv_cat share: `{ch['gmv_cat_share']:.4f}` · hist_gmv_sum `{ch['hist_gmv_sum']:.2f}`",
        "",
        "## Slices",
        "",
        "### recency_bucket (days since last activity ≤ cutoff)",
        "",
        _md_table(s["slices"]["recency_bucket"], slice_keys),
        "",
        "### hist_gmv_bucket",
        "",
        _md_table(s["slices"]["hist_gmv_bucket"], slice_keys),
        "",
        "### activity_days_bucket",
        "",
        _md_table(s["slices"]["activity_days_bucket"], slice_keys),
        "",
        "### channel_mix",
        "",
        _md_table(s["slices"]["channel_mix"], slice_keys),
        "",
        "## Caveats",
        "",
        "- Hash sample, not a probability sample of the public LB 20%.",
        "- Baseline notebook naive submit uses this last-30d GMV as predict for the *test* horizon, not scored here.",
        "- No user_id listed.",
        "",
    ]
    return "\n".join(parts)


def main() -> None:
    if not PARQUET_PATH.exists():
        raise FileNotFoundError(PARQUET_PATH)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    lf = pl.scan_parquet(PARQUET_PATH)
    global_stats = collect_global(lf)
    users, meta = collect_sample_user_table(lf)
    sample = collect_sample_stats(users, meta)
    payload = {"global": global_stats, "sample": sample}
    json_path = RESULTS_DIR / "001_eda_snapshot.json"
    md_path = RESULTS_DIR / "001_eda_snapshot.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    md_path.write_text(render_markdown(global_stats, sample))
    print(f"wrote {md_path}")
    print(f"wrote {json_path}")
    print(f"sample_rmsle={sample['naive_metrics']['rmsle']:.6f} n={sample['n_sample_users']}")


if __name__ == "__main__":
    main()
