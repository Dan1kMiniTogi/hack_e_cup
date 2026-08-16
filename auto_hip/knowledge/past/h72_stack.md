# H72 — Стек 0.70 dual-blend + 0.30 hurdle-logmix
Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Смесь в GMV: 0.70·dual_capacity + 0.30·hurdle_logmix_c0 на фичах H65.
Метрики:
- Primary: **1.690623** vs H70 1.690181 (+0.00044); vs H65 1.691493 (−0.00087)
- Holdout: **1.739754** vs H70 1.739575 (+0.00018); vs H65 1.739622 (+0.00013)
Вердикт: отклонить vs H70 (лучше H65 только на primary → не promote)
Почему:
- Dual-голова тянет стек назад относительно чистого hurdle-logmix; веса 0.70/0.30 из research друга не оптимальны на нашем стеке.
- Primary лучше H65, но holdout хуже обоих — нельзя промоутить.
Repro: h72_stack, arm=stack_blend_hurdle, `workspace/runs/h72_stack/`
Next: refine веса в сторону hurdle (например 0.3/0.7) или dual заменить на H65 3-seed blend.
