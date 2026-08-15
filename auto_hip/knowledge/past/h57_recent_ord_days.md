# H57 — Недавние заказные дни

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: число дней с to_ord>0 за 30d/90d и отношение 30/90 поверх H48.
Метрики: primary 1.693444 vs H48 1.693588; holdout 1.740113 vs 1.740301
Вердикт: принять vs H48, не champion (хуже H52)
Почему:
- persist=24475, fixed=525, regress=547 vs H48 на primary; holdout persist=24474, fixed=526, regress=496
- mid 1.8800 vs 1.8803; слабее IPI (каденс ≠ cardinality недавних дней)
- to_ord_sum_* уже несёт похожий сигнал
Repro: h57_rord, arm=lgb_btyd_rord, `workspace/runs/h57_rord/`
Next: не refine счётчиков заказных дней; стек IPI с лагом/календарём
