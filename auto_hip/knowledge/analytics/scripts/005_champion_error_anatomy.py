"""Detailed error anatomy and slice breakdown for the champion model.

Usage:
    python auto_hip/knowledge/analytics/scripts/005_champion_error_anatomy.py
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import polars as pl

REPO_ROOT = Path(__file__).resolve().parents[4]
WORKSPACE = REPO_ROOT / "auto_hip" / "workspace"
sys.path.insert(0, str(WORKSPACE))

from ltv_data import load_named
from ltv_metrics import add_slices, hist_gmv_quantiles, rmsle


def analyze_champion(run_id: str = "h78_stack_h3") -> dict:
    run_dir = WORKSPACE / "runs" / run_id
    if not run_dir.exists():
        print(f"Run dir not found: {run_dir}")
        return {}

    train = pl.concat([load_named(n) for n in ("train_a", "train_b", "inner_train")])
    q50, q90 = hist_gmv_quantiles(train)

    report = {"run_id": run_id, "splits": {}}

    for split in ("primary", "holdout"):
        pred_path = run_dir / f"preds_{split}.parquet"
        if not pred_path.exists():
            continue
        preds_df = pl.read_parquet(pred_path)
        eval_df = add_slices(load_named(split).sort("user_id"), q50, q90)
        eval_df = eval_df.join(preds_df.select("user_id", "predict"), on="user_id")

        y = eval_df["y"].to_numpy()
        pred = eval_df["predict"].to_numpy()

        log_err_sq = (np.log1p(y) - np.log1p(np.clip(pred, 0, None))) ** 2
        total_rmsle = float(np.sqrt(np.mean(log_err_sq)))

        # Breakdown by zero vs positive true labels
        is_zero = y == 0
        is_pos = y > 0
        zero_sse = float(np.sum(log_err_sq[is_zero]))
        pos_sse = float(np.sum(log_err_sq[is_pos]))
        total_sse = float(np.sum(log_err_sq))

        zero_share = float(np.mean(is_zero))
        zero_sse_share = zero_sse / max(total_sse, 1e-9)
        pos_sse_share = pos_sse / max(total_sse, 1e-9)

        # Analysis by slices
        slice_breakdowns = {}
        for col in ("hist_gmv_bucket", "recency_bucket", "channel_mix", "activity_days_bucket"):
            rows = []
            for val, grp in eval_df.group_by(col):
                gy = grp["y"].to_numpy()
                gpred = grp["predict"].to_numpy()
                g_err_sq = (np.log1p(gy) - np.log1p(np.clip(gpred, 0, None))) ** 2
                rows.append({
                    "slice": str(val[0] if isinstance(val, tuple) else val),
                    "n": int(len(gy)),
                    "rmsle": float(np.sqrt(np.mean(g_err_sq))),
                    "mean_y": float(np.mean(gy)),
                    "mean_pred": float(np.mean(gpred)),
                    "zero_true_share": float(np.mean(gy == 0)),
                    "sse_share": float(np.sum(g_err_sq) / max(total_sse, 1e-9)),
                })
            rows.sort(key=lambda x: x["rmsle"], reverse=True)
            slice_breakdowns[col] = rows

        # Error tail analysis (top 10% worst predictions)
        q90_err = float(np.percentile(log_err_sq, 90))
        tail_mask = log_err_sq >= q90_err
        tail_y = y[tail_mask]
        tail_pred = pred[tail_mask]

        # False alarms (predicted high when true is 0) vs missed buyers (predicted ~0 when true is high)
        false_alarms = (tail_y == 0) & (tail_pred > 10.0)
        missed_buyers = (tail_y > 50.0) & (tail_pred < 5.0)

        report["splits"][split] = {
            "total_rmsle": total_rmsle,
            "zero_true_share": zero_share,
            "zero_sse_share": zero_sse_share,
            "pos_sse_share": pos_sse_share,
            "slice_breakdowns": slice_breakdowns,
            "error_tail": {
                "q90_err_threshold": q90_err,
                "n_tail": int(np.sum(tail_mask)),
                "n_false_alarms_pred_gt_10_true_0": int(np.sum(false_alarms)),
                "n_missed_buyers_pred_lt_5_true_gt_50": int(np.sum(missed_buyers)),
                "mean_y_in_tail": float(np.mean(tail_y)),
                "mean_pred_in_tail": float(np.mean(tail_pred)),
            }
        }

    out_path = REPO_ROOT / "auto_hip" / "knowledge" / "analytics" / "results" / "005_champion_error_anatomy.json"
    out_path.write_text(json.dumps(report, indent=2))
    print(f"Saved analysis to {out_path}")
    return report


if __name__ == "__main__":
    analyze_champion()
