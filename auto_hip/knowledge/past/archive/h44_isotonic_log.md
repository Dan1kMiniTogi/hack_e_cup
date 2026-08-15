# H44 — Isotonic в log1p

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: H31-стек + IsotonicRegression log1p(pred)→log1p(y) на train-fit.
Метрики: primary 1.70670 vs H31 1.69611; holdout 1.74514; mean_pred 50.8
Вердикт: отклонить
Почему:
- persist=24516, fixed=484, regress=1172 vs H31
- калибровка под осенний y разъехалась на январском primary
Repro: h44_iso, arm=isotonic_log
Next: не H09/H14/isotonic на fit mean
