# H38 — LightGBM Tweedie

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: две головы Tweedie (p=1.3) на сыром y_search/y_cat.
Метрики: primary 2.488 vs H31 1.696; holdout 2.405; mean_pred ~110
Вердикт: отклонить
Почему:
- persist=15256, fixed=9744, regress=61831 vs H31 на primary
- масса нулей не компенсировала разъезд шкалы; mean_pred > mean_true
- подтверждает banned poisson-like на identity
Repro: h38_tweedie, arm=lgb_tweedie
Next: не Tweedie/Poisson identity
