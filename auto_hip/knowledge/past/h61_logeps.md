# H61 — log1p(y+1) на головах H52

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: две головы H52 учат log1p(y+1), inverse clip(expm1−1); фичи те же.
Метрики: primary 1.729107 vs H52 1.692618; holdout 1.757207 vs 1.740169
Вердикт: отклонить
Почему:
- persist=22504, fixed=2496, regress=3406 vs H52 на primary; holdout persist=22102, fixed=2898, regress=2655
- mid 1.9094; transform ≠ RMSLE log1p(y), как чужие loss
Repro: h61_logeps, arm=lgb_ipi_logeps, `workspace/runs/h61_logeps/`
Next: не менять log1p голов
