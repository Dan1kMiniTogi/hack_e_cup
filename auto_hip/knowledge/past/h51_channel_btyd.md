# H51 — Канальный BTYD

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: RFM/AOV отдельно по дням search_to_ord и cat_to_ord поверх глобального BTYD H48.
Метрики: primary 1.694336 vs H48 1.693588; holdout 1.740368 vs 1.740301
Вердикт: отклонить
Почему:
- persist=24129, fixed=871, regress=940 vs H48 на primary; holdout persist=24242, fixed=758, regress=760
- mid 1.8815 хуже 1.8803; канальный RFM шумит относительно общего процесса
- не то же, что H47 (окна воронки), но тот же урок: канал уже в двух головах
Repro: h51_chbtyd, arm=lgb_btyd_chbtyd, `workspace/runs/h51_chbtyd/`
Next: не плодить RFM на канал; каденс заказов (H52) живой
