# H71 — Dual-capacity LGB blend (47 vs 95 leaves)
Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Две channel-пары с разной ёмкостью (leaves 47@lr0.08 и 95@lr0.06), усреднение в рублях 0.5/0.5 на фичах H65 вместо 3 одинаковых сидов.
Метрики:
- Primary: **1.691743** vs H70 1.690181 (+0.00156); vs H65 1.691493 (+0.00025)
- Holdout: **1.740804** vs H70 1.739575 (+0.00123); vs H65 1.739622 (+0.00118)
Вердикт: отклонить
Почему:
- Хуже и нового чемпиона H70, и H65 на обоих сплитах.
- Асимметрия листьев без hurdle не дала diversity-выигрыша в нашей схеме двух channel-голов.
Repro: h71_dual, arm=lgb_dual_capacity, `workspace/runs/h71_dual/`
Next: не продвигать dual соло; в стеке с hurdle смотреть H72.
