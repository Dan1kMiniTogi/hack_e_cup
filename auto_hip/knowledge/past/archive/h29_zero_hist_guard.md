# H29 — Guard pred=0 при hist_gmv=0

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: LGB как H31, затем pred=0 если lifetime GMV=0.
Метрики: primary 1.69963 vs H31 1.69611; holdout 1.75130
Вердикт: отклонить
Почему:
- persist=25000, fixed=0, regress=540 — редкие покупки never_ord стали ошибкой
- срез 5% SSE не стоил регресса
Repro: h29_zguard, arm=zero_hist_guard
Next: не hard-zero never_ord
