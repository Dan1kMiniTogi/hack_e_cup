# H37 — LightGBM одна голова total y

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: LGB 3-seed на log1p(y) суммарного GMV, фичи H26.
Метрики: primary 1.70473 vs H31 1.69611; holdout 1.74428 vs 1.74146
Вердикт: отклонить
Почему:
- persist=24112, fixed=888, regress=1603 vs H31 на primary
- как H33, RMSLE-native target хуже канальной суммы даже на LightGBM
- mean_pred 48.98 выше, метрика хуже
Repro: h37_lgbtot, arm=lgb_total
Next: две головы оставлять
