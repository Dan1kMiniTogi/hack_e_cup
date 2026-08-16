# H73 — Стек 0.30 H65-reg + 0.70 hurdle-logmix
Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Смесь в GMV 0.30·lgb_h59_reg (3-seed) + 0.70·hurdle_logmix_c0 на фичах H65 без dual-capacity.
Метрики:
- Primary: **1.690065** vs H70 1.690181 (−0.000116)
- Holdout: **1.739049** vs H70 1.739575 (−0.000526)
Вердикт: принять как **нового чемпиона (H73)**
Почему:
- Строго лучше H70 на обоих сплитах; holdout выигрыш заметнее primary.
- Замена dual (H72) на стабильный H65 3-seed с малым весом 0.30 подтвердила гипотезу из brief 007.
- mid hist_gmv всё ещё ~1.88 — стек не закрыл mid-дыру.
Repro: h73_stack_h65, arm=stack_h65_hurdle, `workspace/runs/h73_stack_h65/`
Next: 3-seed hurdle, dual-channel hurdle, intent features; сабмит H73 на LB (офлайн ≠ public).
