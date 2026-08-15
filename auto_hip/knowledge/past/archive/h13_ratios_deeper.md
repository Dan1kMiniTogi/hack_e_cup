# H13 — Глубже HGB на ratios

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: H11 + depth=8, 220 итер, lr=0.05
Метрики: primary 1.69764 vs H11 1.69814; holdout 1.74272 vs 1.74277
Вердикт: принять, новый champion
Почему:
- persist=24242, fixed=758, regress=751 vs H11 на primary; holdout persist=24374, fixed=626, regress=690
- ёмкость чуть помогает без ломки holdout
Repro: h13_deeper, arm=channel_ratios_deeper
Next: регуляризация той же ёмкости; не bucket-c
