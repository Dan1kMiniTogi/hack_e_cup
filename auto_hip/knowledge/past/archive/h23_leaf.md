# H23 — Мельче лист

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: H19, min_samples_leaf=20
Метрики: primary 1.69690 vs H19 1.69672; holdout 1.74208 vs 1.74218
Вердикт: отклонить (primary)
Почему:
- persist=24588, fixed=412, regress=403 vs H19
- holdout чуть лучше, primary нет
Repro: h23_leaf
Next: без refine линии H19
