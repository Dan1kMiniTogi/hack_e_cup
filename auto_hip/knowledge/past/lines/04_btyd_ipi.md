# Линия: BTYD / IPI (H47–H61)

Champion-path: H45 → **H48** BTYD (−0.0025) → **H52** order IPI (−0.0010) → **H59** IPI+канальные лаги (−0.0007). Индивидуальные отчёты свёрнуты сюда.

## Keep (вехи)

- **H48 ✅:** RFM/AOV + BG-NBD моменты (`p_alive`, E[purch], E[gmv]) в две LGB log1p-головы. Первый скачок после плато ~1.696. Repro: `workspace/runs/h48_btyd/`.
- **H52 ✅:** inter-purchase interval (каденс дней заказа) поверх BTYD.
- **H59 ✅:** IPI + disjoint 30d лаги `gmv_search` / `gmv_cat` / `to_ord` и lag2/lag1. Primary **1.691937** / holdout **1.739946**. Дальше регуляризация → H65.
- Полезные ✅ ниже чемпиона той эпохи: **H50** nested GMV lags, **H53** channel lags, **H57** recent ord days 30/90.
- **H49 / H58 ⚠️:** календарь целевого окна — primary чуть лучше, holdout нет. Не стековать calendar с IPI для промоута.

## Dead here

- **H47** funnel windows, **H51** channel BTYD, **H54** LGB+HGB на BTYD, **H55** channel recency, **H56** якорь 2025-11-08.
- **H60** bucket c на IPI (повтор H14), **H61** `log1p(y+1)` на головах (transform ≠ eval RMSLE).
