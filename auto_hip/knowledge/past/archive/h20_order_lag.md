# H20 — Лаг заказ vs активность

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: H17 + ord_lag = recency_order - recency
Метрики: primary 1.69737 vs H17 1.69705; holdout 1.74223 vs 1.74230
Вердикт: отклонить (регресс primary)
Почему:
- persist=24532, fixed=468, regress=605 vs H17
- разность recency коллинеарна, primary чуть хуже
Repro: h20_lag, arm=channel_order_lag
Next: не лаг; больше данных или другая loss
