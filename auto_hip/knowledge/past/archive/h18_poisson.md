# H18 — Poisson на каналах

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Poisson identity на y_channel+ε, гиперпараметры H15
Метрики: primary 2.527 vs H15 1.698; holdout 2.438 vs 1.743
Вердикт: отклонить
Почему:
- persist=15168, fixed=9832, regress=64210 на primary
- mean_pred завышен, RMSLE хуже naive-диапазона
Repro: h18_poisson, arm=channel_poisson_deeper
Next: не poisson identity
