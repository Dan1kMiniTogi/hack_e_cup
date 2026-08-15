# 047 — Канальная воронка в окна

**Тип:** explore
**Линия:** new / parquet funnel
**Исследование:** [`../investigate/004_h45_blocks.md`](../investigate/004_h45_blocks.md) — неиспользованные колонки parquet при выжатом слое H26_COLS

**Идея:**
Отталкиваемся от champion H45 / runner-up H31: две log1p-головы search+cat, pred = clip(expm1)+clip(expm1), фичи `H26_COLS`. Сейчас в окна попадают только суммарные `to_ord` и `to_cart`; сырые `search_to_ord`, `cat_to_ord`, `search_to_cart`, `cat_to_cart` и флаги `has_search_to_*` / `has_cat_to_*` в [`ltv_data.VALUE_COLS`](../../workspace/ltv_data.py) нет. Добавляем те же окна 7/30/90 (без densify, без last-K) и lifetime-max флагов, оставляем две головы, clip≥0, все user_id. Ожидаемый эффект: RMSLE чуть ниже H45 за счёт канальной конверсии, которую дерево не восстанавливает из суммы `to_ord`.

**Почему:**
Аудит H45 ([`../analytics/results/004_h45_debug.md`](../analytics/results/004_h45_debug.md)) показывает, что после H04 все твики агрегатов дали −0.012 суммарно, а Spearman остатка vs текущих фич |ρ|<0.08. Last-K (H35) и weekday (H34) коллинеарны recency/gaps и не сработали; воронка — другой слой колонок, не последовательность визитов. Линейный Spearman lifetime `hist_search_to_ord` vs log_bias ≈ −0.05, как у `to_ord_sum_30d`: ставка не на линейный остаток, а на взаимодействие канала с головой. Главный риск — шум редкого cat (y_cat zero 0.92) и регресс vs H45; ограничиваем окна 7/30/90 и не трогаем loss/калибровку/hurdle.

**Acceptance:** лучше H45 RMSLE на primary и holdout; pred≥0; все 250k; без densify.

**Избегать:** last-K gaps, weekend, vol, RFM TE, post-hoc c, single-head, densify, hardcode user_id
