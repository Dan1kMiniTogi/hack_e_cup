# H60 — Bucket c на H52

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: после H52 умножить pred на c∈[0.8,1.2] по hist_gmv бакетам, сетка только на train-fit.
Метрики: primary 1.702081 vs H52 1.692618; holdout 1.743058 vs 1.740169
Вердикт: отклонить
Почему:
- persist=24384, fixed=616, regress=1117 vs H52 на primary; holdout persist=24279, fixed=721, regress=873
- fit c: zero=1.0, low=1.06, mid=1.08, high=1.08 — среднее поднялось (48.6), RMSLE вырос, как H14
- mid 1.8916 vs 1.8787
Repro: h60_bucket_c, arm=lgb_ipi_bucket_c, `workspace/runs/h60_bucket_c/`
Next: не post-hoc c на H52
