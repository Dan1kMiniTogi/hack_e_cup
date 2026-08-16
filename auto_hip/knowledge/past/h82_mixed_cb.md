# H82 — H78 + mixed LGBM/CatBoost hurdle bag
Статус: ⚠️ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Hurdle-bag = 2×LGB (42,43) + 1×CatBoost (44); H65 3-seed и веса 0.30/0.70 как у H78.
Метрики:
- Primary: **1.689586** vs H78 1.689400 (+0.000186)
- Holdout: **1.738559** vs H78 1.738825 (−0.000266)
Вердикт: не промоутить (primary регресс), но **лучший holdout в серии после H78**
Почему:
- CatBoost-член стабилизирует holdout (−0.00027), но чуть портит primary.
- Разнообразие деревьев работает на сезонном сдвиге; не выкидывать линию — искать holdout-safe склейку с H78.
Repro: h82_mixed, arm=stack_h65_hurdle3_mixed, `workspace/runs/h82_mixed/`
Next: 4-member bag (3 LGB + CB) или log-blend H78⊕H82 с фиксированным малым весом CB-стека.
