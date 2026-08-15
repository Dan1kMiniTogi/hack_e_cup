# 059 — IPI + канальные disjoint лаги

**Тип:** explore
**Линия:** H52 / H53
**Исследование:** [`../investigate/005_h52_stack.md`](../investigate/005_h52_stack.md) — H53 микро-✅ vs H48 на обоих сплитах, слабее IPI; стек не проверен

**Идея:**
Baseline H52. H53 добавил три 30d блока gmv_search/gmv_cat/to_ord и отношения lag2/lag1 — holdout 1.740132, primary 1.693417 vs H48. Добавляем тот же канал-лаг к IPI+BTYD, гиперпараметры LGB не трогаем, clip≥0. Ожидаемый эффект: тренд канала плюс каденс, RMSLE ниже H52 на mid.

**Почему:**
H50 total-GMV лаги слабее H53; H52 не смотрит на сдвиг search vs cat. Механизмы разные: интервалы заказов vs уровень GMV в прошлых 30d-таргетах. Риск коллинеарности с `gmv_search_sum_*`; нет прироста на обоих сплитах — ❌.

**Acceptance:** лучше H52 RMSLE на primary и holdout; pred≥0; все 250k; без densify.

**Избегать:** funnel (H47), channel BTYD (H51), extra cutoff
