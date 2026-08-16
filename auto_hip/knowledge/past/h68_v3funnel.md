# H68 — v3 gap_ratio + platform-relative GMV + funnel2
Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: На стек H65 добавить gap_ratio, user/platform GMV (7/30/90d), AOV каналов, abandoned search-cart и отношение конверсий 30/90 без смены голов.
Метрики:
- Primary: **1.691886** vs H65 1.691493 (+0.00039)
- Holdout: **1.739839** vs H65 1.739622 (+0.00022)
- vs H65 primary: fixed=672, regress=725
Вердикт: отклонить
Почему:
- Оба сплита чуть хуже чемпиона; пакет не дал ортогонального сигнала поверх IPI+chlag+BTYD.
- Вероятна коллинеарность gap_ratio / funnel с уже имеющимися gaps и channel lags.
Repro: h68_v3funnel, arm=lgb_h65_v3funnel, `workspace/runs/h68_v3funnel/`
Next: не стековать v3funnel на H65 соло; пробовать только вместе с другим механизмом (hurdle), если brief покажет дыру.
