# H19 — Больше итераций H17

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: H17, max_iter=320, lr=0.04
Метрики: primary 1.69672 vs H17 1.69705; holdout 1.74218 vs 1.74230
Вердикт: принять, новый champion
Почему:
- persist=24427, fixed=573, regress=625 vs H17 на primary; holdout persist=24461, fixed=539, regress=559
- ещё чуть ёмкости при меньшем lr
Repro: h19_more, arm=channel_order_more
Next: не refine H19 подряд
