# Линия: BTYD / IPI (H47–H61)

Champion-path: H45 → **H48** BTYD (−0.0025) → **H52** order IPI (−0.0010) → **H59** IPI+канальные лаги (−0.0007). Полные отчёты активного окна — в корне [`../`](../) (`h47_*.md` … `h61_*.md`).

## Keep (вехи)

- **H48 ✅:** RFM/AOV + BG-NBD моменты (`p_alive`, E[purch], E[gmv]) в две LGB log1p-головы. Первый скачок после плато ~1.696. Repro: `workspace/runs/h48_btyd/`.
- **H52 ✅:** inter-purchase interval (каденс дней заказа) поверх BTYD. Repro: order IPI.
- **H59 ✅ champion:** IPI + disjoint 30d лаги `gmv_search` / `gmv_cat` / `to_ord` и lag2/lag1. Primary **1.691937** / holdout **1.739946**.
- Полезные ✅ ниже чемпиона (ортогональные куски стека): **H50** nested GMV lags, **H53** channel lags, **H57** recent ord days 30/90.
- **H49 / H58 ⚠️:** календарь целевого окна — primary чуть лучше, holdout нет. Не стековать calendar с IPI для промоута.

## Dead here

- **H47** funnel windows, **H51** channel BTYD, **H54** LGB+HGB на BTYD, **H55** channel recency, **H56** якорь 2025-11-08.
- **H60** bucket c на IPI (повтор H14), **H61** `log1p(y+1)` на головах (transform ≠ eval RMSLE).

## Дыры текущего champion (H59)

1. mid ~1.878 — худший срез; y=0 держит массу SSE.
2. Календарь не стекуется с IPI на holdout.
3. Nested total-GMV лаги (H50) со стеком H59 не проверены.
4. Public ~1.65 — другой split; офлайн шаг после H52 микро.
