# H08 — MLP CPU (32,16)

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: sklearn MLPRegressor log1p, StandardScaler, без GPU
Метрики: primary rmsle 1.714 vs H05 1.699; holdout 1.750 vs 1.743; holdout mean_pred 798 (сломанная калибровка)
Вердикт: отклонить
Почему:
- persist=23352, fixed=1648, regress=2683 vs H05
- лёгкий MLP хуже HGB и нестабилен по среднему
Repro: h08_mlp
Next: не углублять нейросети на CPU
