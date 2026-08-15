# H33 — Одна голова total GMV

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: один sklearn HGB на log1p(y) с фичами и ёмкостью H26 (depth 8, 320, lr 0.04, L2, 3 seed), без суммы двух канальных голов.
Метрики: primary rmsle 1.70543 vs H31 1.69611; holdout 1.74467 vs 1.74146; также хуже H26 и H05-канала
Вердикт: отклонить
Почему:
- persist=23989, fixed=1011, regress=1584 vs H31 на primary; holdout persist=23959, fixed=1041, regress=1391
- mid rmsle 1.8978 хуже двух голов; канальная декомпозиция на богатых фичах всё ещё нужна
- mean_pred выше (48.96), но RMSLE хуже — калибровка среднего не KPI
Repro: run_id=h33_single, arm=single_head_ens, champion-run=h31_lgb, `workspace/runs/h33_single/`
Next: не откатывать к одной голове; CatBoost/last-K уже в очереди
