# H21 — MAE на log1p

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: H19-фичи, absolute_error на log1p
Метрики: primary 1.806 vs H19 1.697; holdout 1.858 vs 1.742
Вердикт: отклонить
Почему:
- persist=23439, fixed=1561, regress=14345 на primary
- MAE не RMSLE
Repro: h21_abs, arm=channel_abs
Next: не abs/quantile/poisson
