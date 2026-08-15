"""RMSLE, slices, persist/fixed/regress vs champion."""

from __future__ import annotations

from typing import Any

import numpy as np
import polars as pl

ERROR_Q = 0.9


def rmsle(y: np.ndarray, yhat: np.ndarray) -> float:
    """Competition RMSLE with log1p and clip at 0."""
    yp = np.clip(yhat, 0, None)
    yt = np.clip(y, 0, None)
    return float(np.sqrt(np.mean((np.log1p(yt) - np.log1p(yp)) ** 2)))


def mae_log1p(y: np.ndarray, yhat: np.ndarray) -> float:
    """Mean |log1p(y) - log1p(clip(yhat))|."""
    yp = np.clip(yhat, 0, None)
    yt = np.clip(y, 0, None)
    return float(np.mean(np.abs(np.log1p(yt) - np.log1p(yp))))


def summary_metrics(y: np.ndarray, yhat: np.ndarray) -> dict[str, float]:
    """Primary + secondary scalars from METRICS.md."""
    yp = np.clip(yhat, 0, None)
    return {
        "n": int(len(y)),
        "rmsle": rmsle(y, yp),
        "mae_log1p": mae_log1p(y, yp),
        "zero_pred_share": float(np.mean(yp == 0)),
        "mean_pred": float(np.mean(yp)),
        "mean_true": float(np.mean(y)),
        "y_zero_share": float(np.mean(y == 0)),
    }


def add_slices(df: pl.DataFrame, gmv_q50: float, gmv_q90: float) -> pl.DataFrame:
    """Attach slice columns using hist_gmv quantiles from inner_train."""
    return df.with_columns(
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
        .when(pl.col("hist_gmv") <= gmv_q50)
        .then(pl.lit("low"))
        .when(pl.col("hist_gmv") <= gmv_q90)
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


def slice_rmsle(df: pl.DataFrame, pred_col: str) -> dict[str, list[dict[str, Any]]]:
    """RMSLE and y stats per METRICS slice_dim."""
    tmp = df.with_columns(
        pred=pl.col(pred_col).clip(lower_bound=0),
    ).with_columns(
        sqerr=((pl.col("y").log1p() - pl.col("pred").log1p()) ** 2),
    )
    out: dict[str, list[dict[str, Any]]] = {}
    for col in ("recency_bucket", "hist_gmv_bucket", "activity_days_bucket", "channel_mix"):
        g = tmp.group_by(col).agg(
            pl.len().alias("n"),
            (pl.col("y") == 0).mean().alias("y_zero_share"),
            pl.col("y").mean().alias("mean_y"),
            pl.col("pred").mean().alias("mean_pred"),
            pl.col("sqerr").mean().sqrt().alias("rmsle"),
        )
        out[col] = [
            {
                "slice": str(r[col]),
                "n": int(r["n"]),
                "y_zero_share": round(float(r["y_zero_share"]), 4),
                "mean_y": round(float(r["mean_y"]), 4),
                "mean_pred": round(float(r["mean_pred"]), 4),
                "rmsle": round(float(r["rmsle"]), 4),
            }
            for r in g.sort(col).iter_rows(named=True)
        ]
    return out


def error_sets(y: np.ndarray, pred_t: np.ndarray, pred_c: np.ndarray, q: float = ERROR_Q) -> dict[str, int]:
    """persist/fixed/regress vs champion using champion squared-log-error quantile."""
    se_c = (np.log1p(np.clip(y, 0, None)) - np.log1p(np.clip(pred_c, 0, None))) ** 2
    se_t = (np.log1p(np.clip(y, 0, None)) - np.log1p(np.clip(pred_t, 0, None))) ** 2
    thr = float(np.quantile(se_c, q))
    err_c = se_c >= thr
    err_t = se_t >= thr
    return {
        "threshold": thr,
        "persist": int(np.sum(err_c & err_t)),
        "fixed": int(np.sum(err_c & ~err_t)),
        "regress": int(np.sum(~err_c & err_t)),
        "n_error_champion": int(np.sum(err_c)),
    }


def hist_gmv_quantiles(train_df: pl.DataFrame) -> tuple[float, float]:
    """q50/q90 of positive hist_gmv on the fitting set."""
    pos = train_df.filter(pl.col("hist_gmv") > 0)["hist_gmv"]
    return float(pos.quantile(0.5) or 0.0), float(pos.quantile(0.9) or 0.0)
