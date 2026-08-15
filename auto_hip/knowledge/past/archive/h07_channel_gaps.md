# H07 — Channel sum + gap-фичи

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: H05 + last/mean/max gap и n_gaps>7/14 на обеих канальных HGB
Метрики: primary rmsle 1.6987 vs H05 1.6993; holdout 1.7430 vs 1.7432
Вердикт: принять, новый champion (микроулучшение на обоих сплитах)
Почему:
- persist=24170, fixed=830, regress=695 vs H05 на primary
- gaps на канальном механизме чуть полезнее, чем на едином GMV (H06)
Repro: h07_channel_gaps, arm=channel_gaps
Next: плато; сабмит от H07
