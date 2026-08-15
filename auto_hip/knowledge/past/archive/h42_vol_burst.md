# H42 — Burstiness std/max/недели

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: gmv_day_std, max, n_weeks, concentration + LGB H31-стек.
Метрики: primary 1.69653 vs H31 1.69611 (хуже); holdout 1.74086 vs 1.74146 (лучше)
Вердикт: отклонить по primary
Почему:
- persist=23895, fixed=1105, regress=1191 vs H31
- holdout улучшился, primary нет — типичный сезон/сплит разъезд
Repro: h42_vol, arm=vol_burst
Next: не волатильность как единственная ось
