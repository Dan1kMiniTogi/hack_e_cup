# H12 — Вес нулевого таргета

Статус: ⚠️ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: channel_gaps, sample_weight=2 на y=0
Метрики: primary 1.6904 vs H07 1.6987; holdout 1.7817 vs 1.7430
Вердикт: не продвигать (holdout регресс)
Почему:
- primary persist=18458, fixed=6542, regress=7624 — много обмена
- holdout хуже: вес нулей не переносится между окнами
Repro: h12_zero_w, arm=channel_zero_w
Next: не усиливать zero-weight без сезонного guard
