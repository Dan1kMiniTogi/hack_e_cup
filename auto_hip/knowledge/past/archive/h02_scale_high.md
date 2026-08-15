# H02 — Сжатие high-GMV naive

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: c_high на hist_gmv>q90, иначе naive
Метрики: primary rmsle 2.187 vs H05 1.699; holdout 2.210 vs 1.743
Вердикт: отклонить vs champion (vs naive почти нейтрально)
Почему: механизм остаётся naive; табличный champion уже закрыл этот хвост
Repro: h02_scale_high
Next: не refine naive scale
