# 088 — 4-member mixed hurdle на чемпионе H87 (clf-intent)

**Тип:** explore
**Линия:** H87 / H84 holdout CB на clf-intent
**Исследование:** [`../investigate/011_h87_next.md`](../investigate/011_h87_next.md) — забрать holdout H84 без отката изоляции intent

**Идея:**
Baseline H87 (0.30 H65 + 0.70 hurdle3, intent только в clf, 1.689383 / 1.738805). H84 дал holdout 1.738575 при полном 3×LGB+CB, но без intent-изоляции и с микро-регрессом primary. Arm `stack_h87_hurdle4_mixed`: те же clf_cols = H65+INTENT, μ-cols = H65; hurdle-bag = LGB(42,43,44)+CatBoost(45). H65-голова без intent, веса 0.30/0.70, c=0. Ожидаемый эффект — holdout H84 плюс primary-страховка H87.

**Почему:**
H84 и H87 ортогональны: разнообразие деревьев vs маршрутизация фич. Склейка H85 в лог-пространстве не дотянула primary. Риск — CB на расширенном clf-пространстве; фиксированный один CB-член без сетки.

**Acceptance:** лучше H87 на primary и holdout.

**Избегать:** intent в μ, dual-channel, T<1, сетка весов стека.
