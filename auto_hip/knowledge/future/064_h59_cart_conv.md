# 064 — H59 + метрики корзины и воронки добавления
 
**Тип:** explore
**Линия:** H59 / Cart-Conversion
**Исследование:** [`../investigate/006_h59_next.md`](../investigate/006_h59_next.md) — конверсии корзины (`cart_to_ord`) на коротких горизонтах (7d/30d) и незавершенные корзины (`to_cart - to_ord`) ортогональны каденсу IPI и GMV-лагам.

**Идея:**
Baseline H59 (IPI + channel lags + BTYD). Добавляем производные фичи конверсии и отложенного спроса из оконных агрегатов без создания dense-календаря:
1. `cart_to_ord_ratio_7d = to_cart_sum_7d / (to_ord_sum_7d + 1.0)`
2. `cart_to_ord_ratio_30d = to_cart_sum_30d / (to_ord_sum_30d + 1.0)`
3. `abandoned_cart_30d = max(0, to_cart_sum_30d - to_ord_sum_30d)`
4. `abandoned_cart_7d = max(0, to_cart_sum_7d - to_ord_sum_7d)`
Две LightGBM log1p-головы (3 seeds), таргет `y_search` + `y_cat`.

**Почему:**
Пользователь, накопивший корзину за последние 7–30 дней, но не успевший выкупить её до даты cutoff, имеет высокий шанс конвертироваться в первые недели целевого 30d-окна. Это дает опережающий сигнал о покупке, отличный от ретроспективного GMV.

**Acceptance:** лучше H59 RMSLE на primary (1.691937) и holdout (1.739946); non_negative_preds; 250k.
