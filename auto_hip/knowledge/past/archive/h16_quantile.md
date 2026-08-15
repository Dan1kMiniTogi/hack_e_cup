# H16 — Quantile 0.6

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: H13-фичи, quantile loss 0.6 на log1p каналов
Метрики: primary 1.8987 vs H13 1.6976; holdout 1.8894 vs 1.7427
Вердикт: отклонить
Почему:
- persist=21321, fixed=3679, regress=21103 на primary — массовый regress
- mean_pred ближе к true, RMSLE сильно хуже
Repro: h16_quantile, arm=channel_quantile
Next: не quantile/mean-matching как primary objective
