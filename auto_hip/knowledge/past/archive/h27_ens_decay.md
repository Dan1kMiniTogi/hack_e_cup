# H27 — Ensemble + decay

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: три seed H26 на фичах H25 (decay_gmv30)
Метрики: primary 1.69664 vs H26 1.69651; holdout 1.74178 vs 1.74172
Вердикт: отклонить (оба сплита чуть хуже)
Почему:
- persist=24516, fixed=484, regress=508 vs H26 на primary; holdout persist=24546, fixed=454, regress=459
- сложение двух ✅ не дало плюса
Repro: h27_ens_decay, arm=channel_ens_decay
Next: не клеить decay поверх bagging без новой оси
