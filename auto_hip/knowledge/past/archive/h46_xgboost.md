# H46 — XGBoost две головы

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: XGB hist, две log1p-головы, фичи H26, 3 seed.
Метрики: primary 1.69745 vs H31 1.69611; holdout 1.74251
Вердикт: отклонить
Почему:
- persist=23928, fixed=1072, regress=1072 vs H31
- третья библиотека бустинга хуже LGB на той же таблице
Repro: h46_xgb, arm=xgb_channel
Next: не менять бустер без новых фич
