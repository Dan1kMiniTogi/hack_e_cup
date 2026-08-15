# SYNTHESIS — H00–H61

Champion: **H59** `lgb_ipi_chlag`, primary RMSLE **1.691937**, holdout **1.739946**. Предыдущий H52 1.692618 / 1.740169.

Scorecard — [`INDEX.md`](INDEX.md). Линии — [`lines/`](lines/). Активное окно (~15 отчётов) — `h47_*.md` … `h61_*.md` в корне. Cemetery — [`lines/cemetery.md`](lines/cemetery.md).

## Что реально сдвинуло метрику

| Шаг | Δ primary | Смысл |
|-----|-----------|--------|
| H00 → H04 | **−0.487** | HGB log1p на оконных/lifetime суммах. |
| H04 → H05 | **−0.009** | Две головы `y_search`+`y_cat`. |
| H05 → H45 | **−0.003** | Gaps, ratios, depth/L2, order recency, 3-seed, mix. Шаг ≤0.0006. |
| H45 → H48 | **−0.0025** | BTYD RFM/AOV как фичи. |
| H48 → H52 | **−0.0010** | IPI между днями заказа. |
| H52 → H59 | **−0.0007** | IPI + disjoint 30d лаги search/cat/to_ord. |

mean_pred ≈ 45 при mean_true 84 / 101 — не баг для RMSLE: post-hoc scale (H60) и `log1p(y+ε)` (H61) ломают метрику.

## Линии (навигация)

| Файл | Эпоха |
|------|--------|
| [`lines/01_foundation.md`](lines/01_foundation.md) | H00–H05 |
| [`lines/02_hgb_features.md`](lines/02_hgb_features.md) | H06–H19 |
| [`lines/03_ensemble_to_lgb.md`](lines/03_ensemble_to_lgb.md) | H20–H46 |
| [`lines/04_btyd_ipi.md`](lines/04_btyd_ipi.md) | H47–H61 (+ дыры H59) |

## Cemetery (сводка)

Не повторять без нового механизма: hurdle · post-hoc/bucket c · Poisson/Tweedie · single-head · MLP/Cat/XGB без новых фич · zero-weight/snap · isotonic · MoE/mid-residual · calendar как промоут · funnel/channel-BTYD · extra cutoff.

Полный список — [`lines/cemetery.md`](lines/cemetery.md).

## Дыры H59

1. mid ~1.878 всё ещё худший срез; y=0 держит массу SSE.
2. Календарь не стекуется с IPI на holdout (H49/H58).
3. Nested total-GMV лаги (H50) со стеком H59 не проверены.
4. Public ~1.65 — другой split; офлайн шаг после H52 микро.
