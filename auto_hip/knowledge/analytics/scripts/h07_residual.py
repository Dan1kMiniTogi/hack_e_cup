#!/usr/bin/env python3
"""Residual anatomy of champion H07 (channel_gaps) on primary split.

Usage:
    python auto_hip/knowledge/analytics/scripts/h07_residual.py

Outputs:
    auto_hip/knowledge/analytics/results/002_h07_residual.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

WS = Path(__file__).resolve().parents[3] / "workspace"
sys.path.insert(0, str(WS))

from ltv_data import load_named  # noqa: E402
from ltv_metrics import add_slices, hist_gmv_quantiles  # noqa: E402


def main() -> None:
    """Write slice-wise bias and tail-error counts for H07 primary preds."""
    preds = pl.read_parquet(WS / "runs/h07_channel_gaps/preds_primary.parquet").sort("user_id")
    feats = load_named("primary").sort("user_id")
    train = pl.concat(
        [load_named(n) for n in ("train_a", "train_b", "inner_train")],
        how="vertical_relaxed",
    )
    q50, q90 = hist_gmv_quantiles(train)
    df = add_slices(feats, q50, q90).with_columns(
        predict=preds["predict"],
        y=preds["y"],
    )
    y = df["y"].to_numpy()
    p = df["predict"].to_numpy()
    se = (np.log1p(np.clip(y, 0, None)) - np.log1p(np.clip(p, 0, None))) ** 2
    thr = float(np.quantile(se, 0.9))
    df = df.with_columns(
        se=pl.Series(se),
        in_tail=pl.Series(se >= thr),
        under=pl.Series(p < y),
        log_bias=pl.Series(np.log1p(np.clip(p, 0, None)) - np.log1p(np.clip(y, 0, None))),
    )

    lines = [
        "# 002 — H07 residual anatomy (primary)",
        "",
        f"threshold sq-log q90={thr:.4f}; mean_pred={p.mean():.3f} mean_true={y.mean():.3f};",
        f"share underpred={(p < y).mean():.4f}; corr(pred,y)={np.corrcoef(p, y)[0,1]:.4f}",
        "",
        "## Slices (rmsle, mean_pred/mean_y, tail share)",
        "",
    ]
    for col in ("hist_gmv_bucket", "recency_bucket", "activity_days_bucket", "channel_mix"):
        g = (
            df.group_by(col)
            .agg(
                n=pl.len(),
                rmsle=pl.col("se").mean().sqrt(),
                mean_y=pl.col("y").mean(),
                mean_pred=pl.col("predict").mean(),
                tail=pl.col("in_tail").mean(),
                under=pl.col("under").mean(),
                mean_log_bias=pl.col("log_bias").mean(),
                y_zero=pl.col("y").eq(0).mean(),
            )
            .sort(col)
        )
        lines.append(f"### {col}")
        lines.append("")
        lines.append("| slice | n | rmsle | mean_y | mean_pred | ratio | tail | under | log_bias | y_zero |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|")
        for r in g.iter_rows(named=True):
            my, mp = r["mean_y"], r["mean_pred"]
            ratio = mp / my if my else 0.0
            lines.append(
                f"| {r[col]} | {r['n']} | {r['rmsle']:.4f} | {my:.2f} | {mp:.2f} | "
                f"{ratio:.3f} | {r['tail']:.3f} | {r['under']:.3f} | {r['mean_log_bias']:.3f} | {r['y_zero']:.3f} |"
            )
        lines.append("")

    out = Path(__file__).resolve().parents[1] / "results" / "002_h07_residual.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
