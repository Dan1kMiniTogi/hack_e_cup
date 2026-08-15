# H22 — Четвёртый fit-якорь 2025-10-04

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: H19 + extra cutoff train_c
Метрики: primary 1.69736 vs H19 1.69672; holdout 1.74151 vs 1.74218
Вердикт: отклонить (primary регресс; holdout лучше)
Почему:
- persist=24164, fixed=836, regress=942 vs H19
- ранний сезон помогает holdout, чуть вредит январю
Repro: h22_data, arm=channel_more_data
Next: не мешать октябрь в fit без reweight
