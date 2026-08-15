# H25 — Recency-decay GMV

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: H19 + gmv_sum_30d/(1+recency)
Метрики: primary 1.69661 vs H19 1.69672; holdout 1.74211 vs 1.74218
Вердикт: принять vs H19; не champion (H26 лучше)
Почему:
- persist=24304, fixed=696, regress=674 vs H19
- decay чуть полезен
Repro: h25_decay
Next: совместить с ensemble
