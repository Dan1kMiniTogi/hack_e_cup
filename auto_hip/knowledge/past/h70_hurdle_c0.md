# H70 — Hurdle-logmix c=0 на стеке H65
Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Классификатор P(y>0) + channel log1p-регрессоры на покупателях; сборка \(\mathrm{expm1}(p\cdot\log(1+\mu))\) с c=0 (не p×μ). Фичи = H65 (IPI+chlag+BTYD+reg).
Метрики:
- Primary: **1.690181** vs H65 1.691493 (−0.00131)
- Holdout: **1.739575** vs H65 1.739622 (−0.00005)
- vs H65 primary: fixed=1158, regress=1399
Вердикт: принять как **нового чемпиона (H70)**
Почему:
- Строго лучше на primary и holdout; первый шаг порядка тысячных после H65.
- Правильная лог-смесь закрывает banned `hurdle_zero_positive` (H03) и даёт выигрыш там, где сырой p×μ ломал метрику.
- Holdout улучшение тонкое — следить за public; не добавлять c>0 / Platt.
Repro: h70_hurdle_c0, arm=hurdle_logmix_c0, `workspace/runs/h70_hurdle_c0/`
Next: dual-capacity и stack 0.7/0.3 поверх этой головы; cohortknn на hurdle-базе.
