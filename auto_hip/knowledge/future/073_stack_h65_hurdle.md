# 073 — Стек 0.30 H65-reg + 0.70 hurdle-logmix

**Тип:** refine
**Линия:** H70 / Stack weights
**Исследование:** [`../investigate/007_h70_next.md`](../investigate/007_h70_next.md) — dual 0.70 тянул H72 назад; нужно сместить массу на hurdle

**Идея:**
Baseline H70 (hurdle-logmix c=0, primary 1.690181) и H72 (0.70 dual + 0.30 hurdle → 1.690623, хуже). Arm `stack_h65_hurdle`: смешать в GMV **0.30·lgb_h59_reg (H65 3-seed)** + **0.70·hurdle_logmix_c0** на общих фичах H65, без dual-capacity и без новых признаков. Константы весов фиксированы; не подбирать сеткой только по holdout. Ожидаемый эффект — чуть лучше калибровка покупателей, чем соло-hurdle, без отката H72.

**Почему:**
H72 показал, что сильная dual-голова с весом 0.70 портит hurdle; у друга 0.70 был на сильном blend, у нас соло-hurdle уже чемпион. Замена dual на стабильный H65 с малым весом 0.30 — минимальный refine. Риск — holdout у H70 тонкий; если holdout регресснет >0 vs H70 → ❌.

**Acceptance:** строго лучше H70 RMSLE на primary и holdout.

**Избегать:** dual 0.70, подгонка весов только под primary, c>0.
