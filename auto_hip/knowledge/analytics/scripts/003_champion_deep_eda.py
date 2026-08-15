#!/usr/bin/env python3
"""Deep EDA of champion H26 (channel_ens) on full 250k splits.

Usage:
    python auto_hip/knowledge/analytics/scripts/003_champion_deep_eda.py

Inputs:
    workspace/runs/h26_ens/preds_{primary,holdout}.parquet
    cached cutoff tables via ltv_data.load_named
    data/train.parquet (lazy daily GMV only, no densify)

Outputs:
    auto_hip/knowledge/analytics/results/003_champion_deep_eda.md
    auto_hip/knowledge/analytics/results/003_champion_deep_eda.json
"""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import polars as pl

WS = Path(__file__).resolve().parents[3] / "workspace"
RESULTS = Path(__file__).resolve().parents[1] / "results"
sys.path.insert(0, str(WS))

from ltv_data import PARQUET_PATH, load_named  # noqa: E402
from ltv_metrics import ERROR_Q, add_slices, hist_gmv_quantiles  # noqa: E402

HORIZON = 30
WINDOWS = {
    "holdout_target": (date(2025, 12, 16), date(2026, 1, 14)),
    "primary_target": (date(2026, 1, 15), date(2026, 2, 13)),
    "pre_test_30d": (date(2026, 1, 15), date(2026, 2, 13)),  # same as primary; last hist before test
    "last30_to_test": (date(2026, 1, 15), date(2026, 2, 13)),
}


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman rank correlation; NaN-safe, no scipy required."""
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
    """Join H26 preds with features and slice/error columns.

    Args:
        split: primary | holdout
        q50, q90: hist_gmv quantiles from train-fit

    Returns:
        One row per user_id with y, predict, slices, sq-log error.
    """
    preds = pl.read_parquet(WS / "runs/h26_ens" / f"preds_{split}.parquet").sort("user_id")
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
        y_pos=pl.col("y") > 0,
    )


def mass_rows(df: pl.DataFrame, col: str) -> list[dict]:
    """Share of total squared-log-error by a categorical column."""
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
    idx = np.digitize(yp, qs, right=True)
    idx = np.clip(idx, 0, 4)
    bucket[pos_mask] = labels[idx]
    tmp = df.with_columns(yq=pl.Series(bucket))
    return mass_rows(tmp, "yq")


def deciles(df: pl.DataFrame, col: str) -> list[dict]:
    """Calibration by decile of col (pred or y). Zero-y kept as own bin if col==y."""
    x = df[col].to_numpy()
    p = df["predict"].to_numpy()
    y = df["y"].to_numpy()
    se = df["se"].to_numpy()
    lb = df["log_bias"].to_numpy()
    rows = []
    if col == "y":
        z = y <= 0
        rows.append(_bin_row("y=0", z, y, p, se, lb))
        pos = ~z
        xp = x[pos]
        edges = np.quantile(xp, np.linspace(0.1, 0.9, 9))
        b = np.digitize(xp, edges, right=True)
        for i in range(10):
            m = np.zeros(len(x), dtype=bool)
            m[np.where(pos)[0][b == i]] = True
            rows.append(_bin_row(f"y_d{i+1}", m, y, p, se, lb))
        return rows
    edges = np.quantile(x, np.linspace(0.1, 0.9, 9))
    b = np.digitize(x, edges, right=True)
    for i in range(10):
        rows.append(_bin_row(f"d{i+1}", b == i, y, p, se, lb))
    return rows


def _bin_row(name: str, m: np.ndarray, y, p, se, lb) -> dict:
    n = int(m.sum())
    if n == 0:
        return {"bin": name, "n": 0}
    my, mp = float(y[m].mean()), float(p[m].mean())
    return {
        "bin": name,
        "n": n,
        "mean_y": round(my, 2),
        "mean_pred": round(mp, 2),
        "ratio": round(mp / my, 3) if my else 0.0,
        "rmsle": round(float(np.sqrt(se[m].mean())), 4),
        "log_bias": round(float(lb[m].mean()), 4),
        "y_zero": round(float((y[m] == 0).mean()), 4),
    }


def channel_block(df: pl.DataFrame) -> list[dict]:
    """Error of total pred vs y_search / y_cat / y (pred is sum of heads)."""
    y = df["y"].to_numpy()
    ys = df["y_search"].to_numpy()
    yc = df["y_cat"].to_numpy()
    p = df["predict"].to_numpy()
    rows = []
    for name, t in (("y", y), ("y_search", ys), ("y_cat", yc)):
        se = (np.log1p(np.clip(t, 0, None)) - np.log1p(p)) ** 2
        rows.append(
            {
                "target": name,
                "mean_true": round(float(t.mean()), 3),
                "mean_pred_total": round(float(p.mean()), 3),
                "rmsle_if_pred_is_total": round(float(np.sqrt(se.mean())), 4),
                "corr": round(float(np.corrcoef(t, p)[0, 1]), 4),
                "true_zero": round(float((t == 0).mean()), 4),
            }
        )
    cat_share = float(np.clip(yc, 0, None).sum() / max(np.clip(y, 0, None).sum(), 1e-9))
    rows.append({"target": "cat_share_of_y", "mean_true": round(cat_share, 4)})
    return rows


def tail_block(df: pl.DataFrame) -> dict:
    """q90 sq-log-error anatomy on this split's own champion preds."""
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
        "notail_under": round(float((p[~tail] < y[~tail]).mean()), 4),
    }


def spearman_block(df: pl.DataFrame) -> list[dict]:
    """Spearman of features vs log residual (log1p(pred)-log1p(y))."""
    resid = df["log_bias"].to_numpy()
    cols = [
        "gmv_sum_30d",
        "gmv_sum_90d",
        "hist_gmv",
        "recency_days",
        "recency_order_days",
        "activity_days",
        "searches_sum_30d",
        "to_ord_sum_30d",
        "naive_30d",
        "last_gap",
        "mean_gap",
    ]
    rows = []
    work = df.with_columns(pl.col("recency_days").fill_null(9999))
    if "recency_order_days" in work.columns:
        work = work.with_columns(pl.col("recency_order_days").fill_null(9999))
    for c in cols:
        if c not in work.columns:
            continue
        x = work[c].to_numpy().astype(np.float64)
        rows.append({"feature": c, "spearman_vs_log_bias": round(_spearman(x, resid), 4)})
    rows.sort(key=lambda r: abs(r["spearman_vs_log_bias"]), reverse=True)
    return rows


def seasonality() -> dict:
    """Daily GMV sums in labeled windows and last 30d before test. No densify."""
    lf = pl.scan_parquet(PARQUET_PATH)
    daily = (
        lf.group_by("event_date")
        .agg(gmv=pl.sum("gmv"), n=pl.len(), users=pl.col("user_id").n_unique())
        .collect()
        .sort("event_date")
    )
    windows = {
        "holdout_target": (date(2025, 12, 16), date(2026, 1, 14)),
        "primary_target": (date(2026, 1, 15), date(2026, 2, 13)),
        "last30_before_test": (date(2026, 1, 15), date(2026, 2, 13)),
        "prev30_before_primary": (date(2025, 12, 16), date(2026, 1, 14)),
    }
    out = {}
    for name, (a, b) in windows.items():
        w = daily.filter(pl.col("event_date").is_between(a, b))
        g = w["gmv"].to_numpy()
        out[name] = {
            "start": str(a),
            "end": str(b),
            "n_days": w.height,
            "gmv_sum": round(float(g.sum()), 1),
            "gmv_mean_day": round(float(g.mean()), 1),
            "gmv_median_day": round(float(np.median(g)), 1),
            "rows_mean_day": round(float(w["n"].mean()), 1),
        }
    # extra: first 30d of train vs last 30d of train
    first = daily.filter(pl.col("event_date").is_between(date(2025, 1, 1), date(2025, 1, 30)))
    last = daily.filter(pl.col("event_date").is_between(date(2026, 1, 15), date(2026, 2, 13)))
    out["train_first30"] = {
        "gmv_mean_day": round(float(first["gmv"].mean()), 1),
        "n_days": first.height,
    }
    out["note"] = (
        "last30_before_test == primary_target calendar; test horizon 2026-02-14..2026-03-15 has no labels."
    )
    return out


def fmt_mass(title: str, rows: list[dict]) -> list[str]:
    lines = [f"### {title}", ""]
    lines += _md_table(
        rows,
        ["slice", "n", "n_share", "sse_share", "rmsle", "mean_y", "mean_pred", "ratio", "y_zero"],
    )
    lines.append("")
    return lines


def split_report(name: str, df: pl.DataFrame) -> tuple[list[str], dict]:
    y = df["y"].to_numpy()
    p = df["predict"].to_numpy()
    se = df["se"].to_numpy()
    tot = float(se.sum())
    z = y == 0
    payload = {
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
        "y_quantiles": y_quantile_mass(df),
        "hist_gmv": mass_rows(df, "hist_gmv_bucket"),
        "recency": mass_rows(df, "recency_bucket"),
        "activity": mass_rows(df, "activity_days_bucket"),
        "channel": mass_rows(df, "channel_mix"),
        "order_recency": mass_rows(df, "order_bucket"),
        "pred_deciles": deciles(df, "predict"),
        "y_deciles": deciles(df, "y"),
        "channel_heads": channel_block(df),
        "tail": tail_block(df),
        "spearman": spearman_block(df),
    }
    lines = [
        f"## {name}",
        "",
        f"- n={payload['n']} rmsle={payload['rmsle']} mean_y={payload['mean_y']} mean_pred={payload['mean_pred']} corr={payload['corr']}",
        f"- y_zero={payload['y_zero_share']} zero_pred={payload['zero_pred_share']} under={payload['under_share']} mean_log_bias={payload['mean_log_bias']}",
        f"- **SSE share y=0: {payload['sse_share_y0']}** (rmsle_y0={payload['rmsle_y0']}); y>0 share {payload['sse_share_ypos']} (rmsle_ypos={payload['rmsle_ypos']})",
        "",
    ]
    lines += fmt_mass("Масса SSE по y-квантилям (y=0 отдельно, затем quintiles y>0)", payload["y_quantiles"])
    lines += fmt_mass("hist_gmv_bucket", payload["hist_gmv"])
    lines += fmt_mass("recency_bucket", payload["recency"])
    lines += fmt_mass("activity_days_bucket", payload["activity"])
    lines += fmt_mass("channel_mix", payload["channel"])
    lines += fmt_mass("order_recency (last to_ord>0)", payload["order_recency"])
    lines += ["### Калибровка по децилям pred", ""]
    lines += _md_table(payload["pred_deciles"], ["bin", "n", "mean_y", "mean_pred", "ratio", "rmsle", "log_bias", "y_zero"])
    lines += ["", "### Калибровка по y (ноль + децили y>0)", ""]
    lines += _md_table(payload["y_deciles"], ["bin", "n", "mean_y", "mean_pred", "ratio", "rmsle", "log_bias", "y_zero"])
    lines += ["", "### Pred-сумма vs y / y_search / y_cat", ""]
    lines += _md_table(payload["channel_heads"], ["target", "mean_true", "mean_pred_total", "rmsle_if_pred_is_total", "corr", "true_zero"])
    t = payload["tail"]
    lines += [
        "",
        "### Хвост sq-log q90 (свой split)",
        "",
        f"threshold={t['threshold']} n={t['n_tail']} y_zero_in_tail={t['tail_y_zero']} "
        f"mean_y={t['tail_mean_y']} mean_pred={t['tail_mean_pred']} under_in_tail={t['tail_under']} under_out={t['notail_under']}",
        "",
        "### Spearman фича vs log_bias (log1p(pred)-log1p(y))",
        "",
    ]
    lines += _md_table(payload["spearman"], ["feature", "spearman_vs_log_bias"])
    lines.append("")
    return lines, payload


def main() -> None:
    """Write markdown + json deep EDA for H26."""
    train = pl.concat([load_named(n) for n in ("train_a", "train_b", "inner_train")], how="vertical_relaxed")
    q50, q90 = hist_gmv_quantiles(train)
    primary = attach("primary", q50, q90)
    holdout = attach("holdout", q50, q90)
    sea = seasonality()

    p_lines, p_json = split_report("primary (cutoff 2026-01-14)", primary)
    h_lines, h_json = split_report("holdout (cutoff 2025-12-15)", holdout)

    bullets = [
        "# 003 — Deep EDA champion H26 (channel_ens), полный 250k",
        "",
        "Pred: `workspace/runs/h26_ens`. Без densify, без user_id. Квантили hist_gmv с train-fit.",
        "",
        "## Факты",
        "",
        f"- Primary RMSLE {p_json['rmsle']}: **{p_json['sse_share_y0']*100:.1f}%** суммарного squared-log-error приходится на y=0 "
        f"(доля таких пользователей {p_json['y_zero_share']}); rmsle_y0={p_json['rmsle_y0']}, rmsle_y>0={p_json['rmsle_ypos']}.",
        f"- mean_pred/mean_y primary = {p_json['mean_pred']/p_json['mean_y']:.3f}; holdout = {h_json['mean_pred']/h_json['mean_y']:.3f}. "
        f"mean_true holdout {h_json['mean_y']} vs primary {p_json['mean_y']} (сдвиг окна).",
        f"- zero_pred_share primary {p_json['zero_pred_share']} при y_zero {p_json['y_zero_share']}; модель почти не предсказывает ноль.",
        f"- mean_log_bias primary {p_json['mean_log_bias']} (>0 ⇒ в log-пространстве типичный пользователь переоценён).",
        f"- Сезонность дневного GMV: holdout-target mean_day={sea['holdout_target']['gmv_mean_day']}, "
        f"primary-target/last30_before_test mean_day={sea['primary_target']['gmv_mean_day']}, "
        f"train_first30 mean_day={sea['train_first30']['gmv_mean_day']}. Тестовое окно 14.02–15.03 без лейблов.",
        "- Масса SSE на primary: смотри sse_share в таблицах (не rmsle среза). Охотиться туда, где sse_share высокий при большом n.",
        "",
    ]
    sea_rows = [
        {"window": k, **{kk: vv for kk, vv in v.items() if kk != "note"}}
        for k, v in sea.items()
        if isinstance(v, dict) and "gmv_mean_day" in v
    ]
    bullets += ["## Сезонность окон (сумма GMV по дням, не densify)", ""]
    bullets += _md_table(
        sea_rows,
        ["window", "start", "end", "n_days", "gmv_sum", "gmv_mean_day", "gmv_median_day", "rows_mean_day"],
    )
    bullets += ["", sea["note"], ""]
    bullets += p_lines + h_lines

    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "003_champion_deep_eda.md").write_text("\n".join(bullets) + "\n")
    (RESULTS / "003_champion_deep_eda.json").write_text(
        json.dumps({"q50": q50, "q90": q90, "primary": p_json, "holdout": h_json, "seasonality": sea}, indent=2)
    )
    print(f"wrote {RESULTS / '003_champion_deep_eda.md'}")


if __name__ == "__main__":
    main()
