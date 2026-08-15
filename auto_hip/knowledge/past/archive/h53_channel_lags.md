# H53 — Disjoint лаги search/cat/to_ord

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: три 30d блока gmv_search/gmv_cat/to_ord и отношения lag2/lag1 поверх H48.
Метрики: primary 1.693417 vs H48 1.693588; holdout 1.740132 vs 1.740301
Вердикт: принять vs H48, не champion (хуже H52)
Почему:
- persist=24440, fixed=560, regress=748 vs H48 на primary; holdout persist=24455, fixed=545, regress=580
- mid 1.8803 = H48; holdout чуть лучше H50 (канальный тренд, не total GMV)
- слабее IPI
Repro: h53_chlag, arm=lgb_btyd_chlag, `workspace/runs/h53_chlag/`
Next: стек с H52, не соло-лаг-панель
