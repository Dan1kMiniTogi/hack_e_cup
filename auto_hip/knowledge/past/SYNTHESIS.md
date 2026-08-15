# SYNTHESIS — H00–H46

Champion: **H45** `blend_lgb_hgb`, primary RMSLE **1.696101**, holdout **1.74135**. Scorecard — [`INDEX.md`](INDEX.md). Отчёты — [`archive/`](archive/). Цифры H45 — [`../analytics/results/004_h45_debug.md`](../analytics/results/004_h45_debug.md).

## Что реально сдвинуло метрику

| Шаг | Δ primary | Смысл |
|-----|-----------|--------|
| H00 → H04 | **−0.487** | HGB log1p на оконных/lifetime суммах. Почти весь выигрыш цикла. |
| H04 → H05 | **−0.009** | Две головы `y_search`+`y_cat`, pred = clip(expm1)+clip(expm1). Обязательно (H33/H37 ~1.705). |
| H05 → H45 | **−0.003** | Gaps, ratios, depth/L2, order recency, 3-seed, mix LGB+HGB. Шаг ≤0.0006. |

После H04 оптимизируется **одна таблица** (~44 колонки `H26_COLS`). Spearman остатка vs фич |ρ|<0.08. Деревья слой выжали.

mean_pred ≈ 46 при mean_true 84 (primary) / 101 (holdout) — не баг для RMSLE: post-hoc scale ломает метрику.

## Линии

- **Naive/scale (H00–H02, H09–H10, H14):** last-30d и множитель `c` далеки от HGB. Bucket/global c и mix с naive — ❌.
- **Hurdle / zero (H03, H12, H29, H40):** clf×reg, вес нулей, snap, guard hist_gmv=0. Primary иногда лучше, holdout нет (H12 1.690 / 1.782). Доля y=0 сезонная.
- **Канальные головы + агрегаты (H04–H07, H11, H17):** рабочий каркас champion. Gaps на одной голове хуже (H06).
- **Ёмкость дерева (H13, H15, H19, H23, H24, H28, H30):** depth 8 / L2 / 320 iter — мелкий плюс; leaf 20/50, depth 7, monotonic — нет.
- **Loss (H16, H18, H21, H38):** quantile, poisson, MAE, Tweedie — сильно хуже log1p+RMSE.
- **Данные якорей (H22, H43):** четвёртый ранний cutoff и time-decay веса — primary не лучше.
- **Другой бустер на тех же фичах (H31–H32, H45–H46):** LGB чуть лучше HGB; mix H45 микро; CatBoost/XGB нет.
- **Коллинеарные фичи (H20, H25, H27, H34, H35, H41, H42):** ord_lag, decay, weekday, last-K, RFM TE, burstiness — шум или holdout-регресс.
- **Калибровка/смесь голов (H33, H36, H37, H39, H44):** single-head, mid-residual, MoE hist, isotonic — хуже двух голов без калибровки.

## Cemetery (не повторять)

hurdle_zero_positive · mlp_cpu_small · poisson/tweedie identity · quantile · MAE · post-hoc c / bucket c / isotonic · mix с naive · densify · zero-weight без сезонного guard · extra early cutoff · single-head total y · last-K gaps · weekday mix · vol/burst · RFM TE · time-decay весов якорей · CatBoost/XGB на H26_COLS · MoE hist · leaf 20/50 · depth 7 · monotonic GMV · ord_lag · hard-zero hist_gmv=0 · zero-snap τ

## Дыры H45 (куда смотреть дальше)

1. Сырые колонки воронки (`search_to_ord`, `cat_to_ord`, `has_*`) не в агрегатах — единственный нетронутый слой parquet.
2. 52% SSE на y=0, zero_pred≈0, mean_pred на нулях ≈8. Split-specific zero-hack не переносится.
3. Нет календаря целевого окна (НГ vs январь vs Feb–Mar).
4. Нет disjoint 30d лагов; окна вложенные.
5. Нет BTYD/P(alive); пользователь×cutoff как iid. H03 ≠ BG-NBD.
6. mid hist_gmv ≈45% SSE.

Гнаться за public ~1.65 на этом primary тем же слоем нереалистично (офлайн после H04: −0.012; public — другие 50k клиентов).
