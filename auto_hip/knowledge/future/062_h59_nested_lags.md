# 062 — H59 + nested GMV лаги

**Тип:** explore
**Линия:** H59 / H50
**Исследование:** [`../investigate/006_h59_next.md`](../investigate/006_h59_next.md) — H50 микро-✅ vs H48; на стеке IPI+chlag не проверено

**Идея:**
Baseline H59: IPI + канальные disjoint лаги + BTYD. Добавляем nested total-GMV блоки из 30/60/90 (H50) и отношения. Две LGB-головы, clip≥0. Ожидаемый эффект: тренд total GMV сверх канала; если коллинеарно chlag — RMSLE не лучше H59.

**Почему:**
H50 и H53 оба микро vs H48 порознь; H59 взял только канал. Риск коллинеарности `gmv_lag*` с `gmv_search_lag*`+`gmv_cat_lag*`.

**Acceptance:** лучше H59 RMSLE на primary и holdout; pred≥0; 250k; без densify.

**Избегать:** calendar стек (H58), bucket c (H60)
