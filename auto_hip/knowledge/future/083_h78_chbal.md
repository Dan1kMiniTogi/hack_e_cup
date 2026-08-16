# 083 — H78 + channel balance interaction features

**Тип:** refine
**Линия:** H78 / Cross-channel balance on H65 stack
**Исследование:** [`../investigate/009_h78_next.md`](../investigate/009_h78_next.md) — паразитный вклад y_cat и mid-ошибка

**Идея:**
Baseline H78. Arm `stack_h65_hurdle3_chbal`: к H65-стеку (BTYD+IPI+chlag) добавляем CHANNEL_BALANCE_FEATURES — `cat_gmv_dominance_30d`, `channel_entropy_30d`, `search_to_cat_ord_ratio_90d` — в обе головы стека (H65 3-seed и hurdle 3-seed). Веса 0.30/0.70, формула c=0, без temperature и без intent. Ожидаемый эффект — голова y_cat меньше завышает прогноз на search-dominant пользователях, mid/SSE на both/search_only чуть ниже.

**Почему:**
Deep EDA и H76: независимый dual-channel хуже, но относительный микс каналов как фичи ещё не пробовали на H78. Абсолютные лаги уже есть; относительные доли — другой сигнал для регуляризации двух голов. Риск — коллинеарность с gmv_*_sum; если holdout хуже H78 → ❌.

**Acceptance:** лучше H78 на primary и holdout.

**Избегать:** dual-channel hurdle, bucket c, funnel-v3 как промоут.
