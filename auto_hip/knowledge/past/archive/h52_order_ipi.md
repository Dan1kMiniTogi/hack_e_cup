# H52 — Каденс покупок (IPI)

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: mean/std/last интервала и число интервалов между днями с to_ord>0 (без densify) поверх H48.
Метрики: primary **1.692618** vs H48 1.693588; holdout **1.740169** vs 1.740301
Вердикт: принять, новый champion
Почему:
- persist=24291, fixed=709, regress=807 vs H48 на primary; holdout persist=24416, fixed=584, regress=610 — RMSLE лучше при шумном хвосте q90
- mid 1.8787 vs 1.8803; recency 0_7 1.7120 vs 1.7131 — регулярность покупок, не оконные суммы
- не last-K activity (H35) и не vol GMV (H42): только заказные дни
Repro: h52_ipi, arm=lgb_btyd_ipi, `workspace/runs/h52_ipi/`
Next: IPI + календарь / канальные лаги; не канальный BTYD
