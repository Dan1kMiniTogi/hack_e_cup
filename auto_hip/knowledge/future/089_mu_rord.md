# 089 — H87 + недавние дни заказа только в μ-регрессорах

**Тип:** pivot
**Линия:** H87 / Feature routing (rord in μ, not clf)
**Исследование:** [`../investigate/011_h87_next.md`](../investigate/011_h87_next.md) — mid hist_gmv и H63 holdout-сигнал без возврата полного joint

**Идея:**
Baseline H87. H63 (H59 + ord_days 30/90) дал holdout лучше при чуть худшем primary на старом стеке; H66 joint lags+rord ❌. Arm `stack_h87_mu_rord`: RECENT_ORD_FEATURES (`ord_days_30d`, `ord_days_90d`, `ord_days_ratio_30_90`) добавляются **только** в channel-регрессоры μ hurdle 3-seed (и опционально в H65-голову — нет: только μ, как зеркало H87). Классификатор остаётся H65+INTENT. Веса 0.30/0.70, c=0. Ожидаемый эффект — каденс покупок чинит mid-чеки, не ломая P(y>0).

**Почему:**
H87 показал, что краткосрочный интент принадлежит clf. Каденс заказа (H52/H57/H63) — про размер/частоту μ. Полный joint в H66 шумел. Риск — коллинеарность с IPI; если holdout хуже H87 → ❌.

**Acceptance:** лучше H87 на primary и holdout.

**Избегать:** nested lags jointly (H62/H66), intent в μ, calendar.
