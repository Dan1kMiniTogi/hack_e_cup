# H17 — Давность последнего заказа

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: H15 + recency_order_days (последний to_ord>0), без densify
Метрики: primary 1.69705 vs H15 1.69750; holdout 1.74230 vs 1.74270
Вердикт: принять, новый champion
Почему:
- persist=24232, fixed=768, regress=732 vs H15 на primary; holdout persist=24257, fixed=743, regress=698
- recency заказа отделяет поиск без покупки
Repro: h17_order, arm=channel_order; cache v2
Next: не Poisson; refine H17 осторожно
