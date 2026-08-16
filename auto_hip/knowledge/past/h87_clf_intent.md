# H87 — Intent только в классификаторе P(y>0)
Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: INTENT_DYNAMICS (accel/cart/hot-cart) только на clf hurdle 3-seed; μ-головы и H65 без intent. Стек 0.30/0.70, c=0.
Метрики:
- Primary: **1.689383** vs H78 1.689400 (−0.000017)
- Holdout: **1.738805** vs H78 1.738825 (−0.000020)
Вердикт: принять как **нового чемпиона (H87)**
Почему:
- Оба сплита строго лучше H78 (тонкий шаг). H80 клал intent и в μ — holdout падал; изоляция clf это чинит.
- Шаг меньше H78←H73, но проходит acceptance (no regression + holdout).
Repro: h87_clf_intent, arm=stack_h65_hurdle3_clf_intent, `workspace/runs/h87_clf_intent/`
Next: сабмит H87; 4-bag CB на этой clf-intent базе (holdout H84) без возврата intent в μ.
