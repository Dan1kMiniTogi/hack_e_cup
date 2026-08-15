# H32 — CatBoost две головы

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: две log1p-головы search/cat на фичах H26, CatBoost RMSE, 3 seed.
Метрики: primary 1.69627 vs H31 1.69611; holdout 1.74155 vs 1.74146
Вердикт: отклонить (микрорегресс)
Почему:
- persist=23796, fixed=1204, regress=1184 vs H31 на primary
- другой бустер двигает хвост ошибок, но RMSLE чуть хуже
Repro: h32_catboost, arm=catboost_channel, `workspace/runs/h32_catboost/`
Next: LGB total / Tweedie
