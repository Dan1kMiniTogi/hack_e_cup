# H84 — Hurdle bag 3×LGB + 1×CatBoost
Статус: ⚠️ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Как H78, но hurdle = LGB(42,43,44)+CatBoost(45), равное усреднение p и μ, веса стека 0.30/0.70.
Метрики:
- Primary: **1.689420** vs H78 1.689400 (+0.000020)
- Holdout: **1.738575** vs H78 1.738825 (−0.000250)
Вердикт: не промоутить (primary регресс); holdout близок к H82
Почему:
- Третий LGB вернул primary почти к H78 (лучше H82 1.689586), holdout всё ещё лучше чемпиона.
- persist/fixed/regress vs H78 не считались (нет `h78_stack_h3` preds в этом env).
Repro: h84_hurdle4, arm=stack_h65_hurdle4_mixed, `workspace/runs/h84_hurdle4/`
Next: 4-bag на clf-intent чемпионе, не соло CB.
