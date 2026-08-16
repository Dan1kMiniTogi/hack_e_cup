# SYNTHESIS — H00–H72

Champion: **H70** `hurdle_logmix_c0`, primary RMSLE **1.690181**, holdout **1.739575**. Предыдущий H65 1.691493 / 1.739622.

Scorecard — [`INDEX.md`](INDEX.md). Линии — [`lines/`](lines/). Активное окно (~15 отчётов) — `h58_*.md` … `h72_*.md` в корне. Cemetery — [`lines/cemetery.md`](lines/cemetery.md).

## Что реально сдвинуло метрику

| Шаг | Δ primary | Смысл |
|-----|-----------|--------|
| H00 → H04 | **−0.487** | HGB log1p на оконных/lifetime суммах. |
| H04 → H05 | **−0.009** | Две головы `y_search`+`y_cat`. |
| H05 → H45 | **−0.003** | Gaps, ratios, depth/L2, order recency, 3-seed, mix. Шаг ≤0.0006. |
| H45 → H48 | **−0.0025** | BTYD RFM/AOV как фичи. |
| H48 → H52 | **−0.0010** | IPI между днями заказа. |
| H52 → H59 | **−0.0007** | IPI + disjoint 30d лаги search/cat/to_ord. |
| H59 → H65 | **−0.00044** | Регуляризация (min_data_in_leaf 60, feature_fraction 0.8, L2 3.0) на широком признаковом стеке. |
| H65 → H70 | **−0.00131** | Hurdle-logmix c=0: \(\mathrm{expm1}(p\log(1+\mu))\), не p×μ. |

mean_pred ≈ 45–46 при mean_true 84 / 101 — не баг для RMSLE: post-hoc scale (H60) и `log1p(y+ε)` (H61) ломают метрику.

Friend-transfer H68/H69 (v3funnel, cohortknn) на соло-H65 ❌; dual (H71) и 0.70/0.30 stack (H72) хуже чистого hurdle.

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

## Дыры H70

1. mid hist_gmv всё ещё ~1.878; hurdle чуть улучшил zero/low, mid почти как у H65.
2. Holdout выигрыш H70 тонкий (−0.00005) — нужен public check / submit.
3. cohortknn и v3funnel не стекуются на log1p-H65; пробовать на hurdle-базе.
4. Dual 0.70 в стеке вреден — refine веса в сторону hurdle или заменить dual на H65 3-seed.
