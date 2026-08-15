#!/usr/bin/env python3
"""Run an LTV arm, write metrics under workspace/runs/.

Usage:
    python runner.py cache
    python runner.py run --arm naive --run-id h00_naive
    python runner.py run --arm hgb_log1p --run-id h04_hgb --champion-run h00_naive
    python runner.py submit --arm hgb_log1p --run-id submit_champ
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import polars as pl

from ltv_arms import fit_arm, predict_arm
from ltv_data import CUTOFFS, EVAL_NAMES, concat_train_fit, load_named
from ltv_metrics import (
    add_slices,
    error_sets,
    hist_gmv_quantiles,
    slice_rmsle,
    summary_metrics,
)

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"


def cache_all() -> None:
    """Materialize feature tables for every named cutoff."""
    for name in CUTOFFS:
        df = load_named(name)
        print(f"{name}: {df.height} rows, cols={len(df.columns)}")


def _write_run(run_id: str, payload: dict) -> Path:
    d = RUNS / run_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "metrics.json").write_text(json.dumps(payload["metrics"], indent=2, default=str))
    (d / "meta.json").write_text(json.dumps(payload["meta"], indent=2, default=str))
    return d


def run_arm(arm: str, run_id: str, champion_run: str | None) -> None:
    """Fit on TRAIN_FIT_NAMES, score holdout+primary, optional vs champion preds."""
    train = concat_train_fit()
    q50, q90 = hist_gmv_quantiles(train)
    model = fit_arm(arm, train, q50, q90)
    champ_preds: dict[str, np.ndarray] = {}
    if champion_run:
        for split in EVAL_NAMES:
            p = RUNS / champion_run / f"preds_{split}.parquet"
            champ_preds[split] = pl.read_parquet(p).sort("user_id")["predict"].to_numpy()

    metrics: dict = {"arm": arm, "q50": q50, "q90": q90, "splits": {}}
    extra = {
        k: v
        for k, v in model.payload.items()
        if k in ("c", "c_high", "inner_rmsle", "inner_rmsle_high", "q90", "alpha", "c_buckets")
    }
    metrics["fit"] = extra
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    for split in EVAL_NAMES:
        df = add_slices(load_named(split).sort("user_id"), q50, q90)
        pred = predict_arm(model, df)
        y = df["y"].to_numpy()
        sm = summary_metrics(y, pred)
        sl = slice_rmsle(df.with_columns(predict=pl.Series(pred)), "predict")
        pack = {"summary": sm, "slices": sl}
        if split in champ_preds:
            pack["vs_champion"] = error_sets(y, pred, champ_preds[split])
        metrics["splits"][split] = pack
        pl.DataFrame({"user_id": df["user_id"], "predict": pred, "y": y}).write_parquet(
            run_dir / f"preds_{split}.parquet"
        )
        print(f"{run_id} {split} rmsle={sm['rmsle']:.6f} mean_pred={sm['mean_pred']:.3f} mean_true={sm['mean_true']:.3f}")

    _write_run(run_id, {"metrics": metrics, "meta": {"arm": arm, "run_id": run_id, "champion_run": champion_run}})


def make_submit(arm: str, run_id: str) -> None:
    """Refit on all labeled cutoffs except test; predict test cutoff."""
    labeled = pl.concat(
        [load_named(n) for n in ("train_a", "train_b", "inner_train", "holdout", "primary")],
        how="vertical_relaxed",
    )
    q50, q90 = hist_gmv_quantiles(labeled)
    model = fit_arm(arm, labeled, q50, q90)
    test = load_named("test").sort("user_id")
    pred = predict_arm(model, test)
    out = pl.DataFrame({"user_id": test["user_id"], "predict": pred})
    csv_path = ROOT / "submit.csv"
    out.write_csv(csv_path)
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    out.write_parquet(run_dir / "preds_test.parquet")
    meta = {"arm": arm, "n": out.height, "mean_pred": float(pred.mean()), "zero_share": float((pred == 0).mean())}
    (run_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"wrote {csv_path} n={out.height} mean_pred={meta['mean_pred']:.4f}")


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("cache")
    r = sub.add_parser("run")
    r.add_argument("--arm", required=True)
    r.add_argument("--run-id", required=True)
    r.add_argument("--champion-run", default=None)
    s = sub.add_parser("submit")
    s.add_argument("--arm", required=True)
    s.add_argument("--run-id", default="submit")
    args = p.parse_args()
    if args.cmd == "cache":
        cache_all()
    elif args.cmd == "run":
        run_arm(args.arm, args.run_id, args.champion_run)
    else:
        make_submit(args.arm, args.run_id)


if __name__ == "__main__":
    main()
