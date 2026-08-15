# H59 — IPI + канальные disjoint лаги

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: три 30d блока gmv_search/gmv_cat/to_ord и отношения lag2/lag1 поверх H52 IPI+BTYD.
Метрики: primary **1.691937** vs H52 1.692618; holdout **1.739946** vs 1.740169
Вердикт: принять, новый champion
Почему:
- persist=24269, fixed=731, regress=607 vs H52 на primary; holdout persist=24455, fixed=545, regress=528 — net fixed>regress
- mid 1.8776 vs 1.8787; каденс + тренд канала ортогональны
Repro: h59_ipi_chlag, arm=lgb_ipi_chlag, `workspace/runs/h59_ipi_chlag/`
Next: не calendar на этом стеке; не bucket c
