# H04 — Регрессия log1p на агрегатах (HGB)

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: HistGradientBoosting на log1p(y) по оконным/lifetime агрегатам до cutoff; pred=expm1 clip≥0
Метрики: primary rmsle 1.708 vs naive 2.195; holdout 1.746 vs 2.214
Вердикт: принять, новый champion
Почему:
- persist=4501, fixed=20499, regress=939 vs naive на primary
- mid/high срезы сильно лучше naive; mean_pred 49.5 всё ещё ниже mean_true 84 (RMSLE это прощает)
Repro: run_id=h04_hgb, arm=hgb_log1p, workspace/runs/h04_hgb
Next: hurdle, channel_sum, gaps vs этот champion
