# 074 — H70 + RFM cohortknn peers

**Тип:** explore
**Линия:** H70 / Peer features on hurdle
**Исследование:** [`../investigate/007_h70_next.md`](../investigate/007_h70_next.md) — H69 ❌ на log1p-H65; у друга kNN сработал на blend+hurdle

**Идея:**
Baseline H70. Добавить `COHORTKNN_FEATURES` (уже в `ltv_data`) в классификатор и channel-регрессоры hurdle-logmix c=0: arm `hurdle_logmix_c0_knn` с `need_cohortknn=True`. Не менять формулу сборки и не добавлять dual. Ожидаемый эффект — peer-норма помогает mid/nonzero при уже чистых нулях от hurdle (как H76 у друга поверх стека).

**Почему:**
H69 на чистом log1p не дал сигнала; research друга показал, что kNN выигрывает именно nonzero/low/mid при живом hurdle на нулях. Риск — RAM на кэш cutoff и шум на cold; кэш parquet уже есть для train/holdout/primary.

**Acceptance:** лучше H70 RMSLE на primary и holdout.

**Избегать:** cohortknn на log1p без hurdle (H69), GNN, RFM TE по y.
