# H15 — L2 на глубоком H11

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: H13 + l2_regularization=1.0
Метрики: primary 1.69750 vs H13 1.69764; holdout 1.74270 vs 1.74272
Вердикт: принять, новый champion
Почему:
- persist=24522, fixed=478, regress=447 vs H13 на primary; holdout persist=24588, fixed=412, regress=420
- слабая L2 чуть стабилизирует ёмкость
Repro: h15_l2, arm=channel_deeper_l2
Next: не refine этой линии подряд; order-recency / другая loss
