# 081 — Температура логита P(y>0) в hurdle 3-seed стека

**Тип:** pivot
**Линия:** H78 / Clf calibration temperature
**Исследование:** [`../investigate/008_h73_next.md`](../investigate/008_h73_next.md) — калибровка границы нулей без post-hoc c и без bucket scale

**Идея:**
Baseline H78. Вместо сырого `p = clf.predict` применяем температуру на логите: \(p_T = \sigma(\mathrm{logit}(p)/T)\) с фиксированным \(T \in \{0.9, 1.1\}\) (один прогон, T=0.9 как primary choice — чуть острее нули). Меняется только сборка hurdle-головы внутри `stack_h65_hurdle3seed`; веса 0.30/0.70 и фичи те же. Это не global scale c и не bucket c (cemetery H09/H14/H60). Ожидаемый эффект — тонкая калибровка zero/low без сдвига mean на high.

**Почему:**
H70/H78 выигрывают за счёт формы logmix; остаточный зазор часто в калибровке p, не в μ. Post-hoc c ломал RMSLE; температура логита — другой механизм. Риск — T≠1 ухудшит holdout; один фиксированный T без сетки по holdout.

**Acceptance:** лучше H78 на primary и holdout.

**Избегать:** bucket c, isotonic, Platt fit на val, T-сетка по holdout.
