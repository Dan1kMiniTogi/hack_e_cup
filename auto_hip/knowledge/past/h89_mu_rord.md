# H89 — RECENT_ORD только в μ-регрессорах hurdle
Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: На базе H87 маршрутизация rord (`ord_days_30/90`, ratio) только в μ_search/μ_cat; clf остаётся H65+intent; H65-голова без rord.
Метрики:
- Primary: **1.689425** vs H87 1.689383 (+0.000042)
- Holdout: **1.738816** vs H87 1.738805 (+0.000011)
Вердикт: отклонить (регресс обоих сплитов; mid не починился)
Почему:
- persist=24847, fixed=153, regress=144 на primary; holdout persist=24853, fixed=147, regress=123
- mid RMSLE 1.8763 vs цель <1.8700; mean_pred mid **41.70** — как у H87, деревья не взяли rord поверх IPI
- H63 (rord сквозной) был ⚠️; изоляция в μ не дала ни mid-lift, ни holdout
Repro: h89_mu_rord, arm=stack_h87_mu_rord, `workspace/runs/h89_mu_rord/`
Next: не повторять rord-routing без нового сигнала; cemetery-кандидат
