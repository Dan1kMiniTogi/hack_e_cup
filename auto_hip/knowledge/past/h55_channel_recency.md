# H55 — Ресенси канала

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: дни до последней search/cat активности и search/cat заказа поверх H48 (null→9999).
Метрики: primary 1.693671 vs H48 1.693588; holdout 1.740102 vs 1.740301
Вердикт: отклонить
Почему:
- persist=24444, fixed=556, regress=679 vs H48 на primary; holdout persist=24481, fixed=519, regress=561
- mid 1.8807 / recency 0_7 1.7134 хуже; коллинеарно recency_order_days и btyd_days_since_last
- близко к H20 (грубая разность ресенси)
Repro: h55_chrec, arm=lgb_btyd_chrec, `workspace/runs/h55_chrec/`
Next: не дробить recency по каналу
