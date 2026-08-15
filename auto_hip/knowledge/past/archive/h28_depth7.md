# H28 — Depth 7 вместо 8

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: один H19-пайплайн, max_depth=7
Метрики: primary 1.69654 vs H26 1.69651; holdout 1.74202 vs 1.74172
Вердикт: отклонить
Почему:
- persist=24436, fixed=564, regress=525 vs H26 на primary; holdout persist=24552, fixed=448, regress=468
- мельче дерево не бьёт 3-seed
Repro: h28_d7, arm=channel_d7
Next: не depth-tweak vs bagging
