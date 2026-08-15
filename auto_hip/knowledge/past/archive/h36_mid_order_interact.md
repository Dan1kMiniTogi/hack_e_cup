# H36 — Residual mid × order 8–30

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: LGB-база + HGB на log-residual только на mid ∩ recency_order 8–30.
Метрики: primary 1.69877 vs H31 1.69611; holdout 1.74246 vs 1.74146
Вердикт: отклонить
Почему:
- persist=24539, fixed=461, regress=757 vs H31
- точечная поправка mid дала регресс, не скачок
Repro: h36_midres, arm=residual_mid_order
Next: не residual на маске primary-среза
