# 058 — IPI + календарь целевого окна

**Тип:** explore
**Линия:** H52 / H49
**Исследование:** [`../investigate/005_h52_stack.md`](../investigate/005_h52_stack.md) — календарь улучшил primary, не holdout; IPI улучшил оба

**Идея:**
Baseline — champion H52: H26+BTYD плюс mean/std/last/n интервалов между заказными днями. H49 добавил календарь следующих 30 дней соло и проиграл holdout на 0.00001. Кладём те же calendar-фичи в стек H52, не убирая IPI. Две LGB-головы, clip≥0, без densify. Ожидаемый эффект: primary как у H49 или лучше за счёт IPI, holdout не хуже H52.

**Почему:**
H52 −0.001 vs H48 за счёт каденса; H49 сдвинул primary без процесса покупок и не закрыл НГ на holdout. Признаки ортогональны: IPI — пользователь, календарь — окно, одинаковое для всех. Риск — снова регресс holdout; тогда ❌, календарь не тащим.

**Acceptance:** лучше H52 RMSLE на primary и holdout; pred≥0; все 250k; без densify.

**Избегать:** calendar соло без IPI, time-decay якорей, extra cutoff
