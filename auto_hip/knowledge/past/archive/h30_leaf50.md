# H30 — min_samples_leaf=50

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: H26 3-seed, только leaf 50 вместо 30.
Метрики: primary 1.69650 vs H31 1.69611; holdout 1.74165 vs 1.74146
Вердикт: отклонить
Почему:
- persist=24254, fixed=746, regress=720 vs H31
- как H23, край листа не бьёт LGB-champion
Repro: h30_leaf50, arm=channel_leaf50
Next: не крутить min_samples_leaf HGB
