# H90 — Dual routing (intent в clf, rord в μ) + 4-bag CB
Статус: ⚠️ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Синергия H88 и H89: 3×LGB+1×CB hurdle, clf=H65+intent, μ=H65+rord, стек 0.30/0.70, c=0.
Метрики:
- Primary: **1.689457** vs H87 1.689383 (+0.000074)
- Holdout: **1.738551** vs H87 1.738805 (−0.000254) — лучший holdout цикла
Вердикт: не промоутить (primary хуже H87 и H88); holdout чуть лучше H88/H82
Почему:
- persist=24742, fixed=258, regress=229 на primary; holdout persist=24720, fixed=280, regress=189
- mid mean_pred 41.74 — rord снова не сдвинул чек; выигрыш holdout = CatBoost, не routing
- Ортогональность «не сложилась»: rord добавил шум к уже слабому primary 4-bag
Repro: h90_dual_routing, arm=stack_h87_dual_routing_cb, `workspace/runs/h90_dual_routing/`
Next: CB-диверсификация только вместе с T>1 чемпиона H91, без rord
