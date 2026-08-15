# H14 — Bucket-множители на H11

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: отдельные c по hist_gmv bucket после H11
Метрики: primary 1.7093 vs H11 1.6981; holdout 1.7460 vs 1.7428; c mid/high=1.1
Вердикт: отклонить
Почему:
- up-scale бакетов снова бьёт RMSLE (как H09)
- mid не лечится множителем
Repro: h14_bucket, arm=channel_ratios_bucket_cal
Next: не post-hoc scale
