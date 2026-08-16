# H78 — Стек 0.30 H65 + 0.70 hurdle 3-seed
Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Как H73, но hurdle-голова = 3-seed bagging (42/43/44) с усреднением p и μ до logmix.
Метрики:
- Primary: **1.689400** vs H73 1.690065 (−0.000665)
- Holdout: **1.738825** vs H73 1.739049 (−0.000224)
Вердикт: принять как **нового чемпиона (H78)**
Почему:
- Совмещает holdout-страховку H73 и primary-сигнал H75.
- Оба сплита строго лучше H73; holdout впервые уверенно ниже 1.739.
Repro: h78_stack_h3, arm=stack_h65_hurdle3seed, `workspace/runs/h78_stack_h3/`
Next: сабмит H78 на LB; лёгкий вес 0.15 (H79) как ⚠️; не сетка весов.
