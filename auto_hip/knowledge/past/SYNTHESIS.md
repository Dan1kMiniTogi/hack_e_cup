# SYNTHESIS — H00–H72

Champion: **H87** `stack_h65_hurdle3_clf_intent`, primary RMSLE **1.689383**, holdout **1.738805**. Предыдущий H78 1.689400 / 1.738825.

Scorecard — [`INDEX.md`](INDEX.md). Линии — [`lines/`](lines/). Активное окно (~15 отчётов) — `h74_*.md` … `h87_*.md` в корне. Cemetery — [`lines/cemetery.md`](lines/cemetery.md).

## Что реально сдвинуло метрику

| Шаг | Δ primary | Смысл |
|-----|-----------|--------|
| H00 → H04 | **−0.487** | HGB log1p на оконных/lifetime суммах. |
| H04 → H05 | **−0.009** | Две головы `y_search`+`y_cat`. |
| H05 → H45 | **−0.003** | Gaps, ratios, depth/L2, order recency, 3-seed, mix. Шаг ≤0.0006. |
| H45 → H48 | **−0.0025** | BTYD RFM/AOV как фичи. |
| H48 → H52 | **−0.0010** | IPI между днями заказа. |
| H52 → H59 | **−0.0007** | IPI + disjoint 30d лаги search/cat/to_ord. |
| H59 → H65 | **−0.00044** | Регуляризация на широком признаковом стеке. |
| H65 → H70 | **−0.00131** | Hurdle-logmix c=0. |
| H70 → H73 | **−0.00012** | Stack 0.30 H65 + 0.70 hurdle (holdout −0.00053). |
| H73 → H78 | **−0.00067** | Тот же стек, hurdle → 3-seed bagging (holdout −0.00022). |
| H78 → H87 | **−0.000017** | Intent dynamics только в clf P(y>0), не в μ. |

H79 веса 0.15/0.85 ⚠️. H82 mixed ⚠️ holdout **1.738559**. H84 4-bag ⚠️ holdout 1.738575. H86 multi-depth ❌. **H87 ✅ champion**. Public LB H65 ≈ 1.6619 — грузить `submit_87.csv`.

## Дыры H87

1. mid hist_gmv всё ещё тяжёлый.
2. Holdout H84 (−0.00025) не забран — 4-bag на clf-intent.
3. Веса стека исчерпаны; T<1 и intent-в-μ cemetery.

## Линии (навигация)

| Файл | Эпоха |
|------|--------|
| [`lines/01_foundation.md`](lines/01_foundation.md) | H00–H05 |
| [`lines/02_hgb_features.md`](lines/02_hgb_features.md) | H06–H19 |
| [`lines/03_ensemble_to_lgb.md`](lines/03_ensemble_to_lgb.md) | H20–H46 |
| [`lines/04_btyd_ipi.md`](lines/04_btyd_ipi.md) | H47–H61 (+ дыры H59) |
| [`lines/05_hurdle_stack.md`](lines/05_hurdle_stack.md) | H70–H73 |

## Cemetery (сводка)

Не повторять без нового механизма: hurdle · post-hoc/bucket c · Poisson/Tweedie · single-head · MLP/Cat/XGB без новых фич · zero-weight/snap · isotonic · MoE/mid-residual · calendar как промоут · funnel/channel-BTYD · extra cutoff.

Полный список — [`lines/cemetery.md`](lines/cemetery.md).

## Дыры H70

1. mid hist_gmv всё ещё ~1.878; hurdle чуть улучшил zero/low, mid почти как у H65.
2. Holdout выигрыш H70 тонкий (−0.00005) — нужен public check / submit.
3. cohortknn и v3funnel не стекуются на log1p-H65; пробовать на hurdle-базе.
4. Dual 0.70 в стеке вреден — refine веса в сторону hurdle или заменить dual на H65 3-seed.
