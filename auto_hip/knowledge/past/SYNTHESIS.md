# SYNTHESIS — H00–H57

Champion: **H52** `lgb_btyd_ipi`, primary RMSLE **1.692618**, holdout **1.740169**. Предыдущий H48 1.693588 / 1.740301. Scorecard — [`INDEX.md`](INDEX.md). Отчёты — [`archive/`](archive/).

## Что реально сдвинуло метрику

| Шаг | Δ primary | Смысл |
|-----|-----------|--------|
| H00 → H04 | **−0.487** | HGB log1p на оконных/lifetime суммах. Почти весь выигрыш цикла. |
| H04 → H05 | **−0.009** | Две головы `y_search`+`y_cat`, pred = clip(expm1)+clip(expm1). Обязательно (H33/H37 ~1.705). |
| H05 → H45 | **−0.003** | Gaps, ratios, depth/L2, order recency, 3-seed, mix LGB+HGB. Шаг ≤0.0006. |
| H45 → H48 | **−0.0025** | BTYD RFM/AOV + p_alive как фичи в те же две LGB-головы. |
| H48 → H52 | **−0.0010** | Интервалы между днями заказа (IPI), не activity gaps и не lifetime RFM. |

После H04 оптимизируется таблица оконных сумм. Spearman остатка vs фич |ρ|<0.08. Деревья этот слой выжали; живой слой — процесс покупок (BTYD + каденс).

mean_pred ≈ 45 при mean_true 84 (primary) / 101 (holdout) — не баг для RMSLE: post-hoc scale ломает метрику.

## Линии

- **Naive/scale (H00–H02, H09–H10, H14):** last-30d и множитель `c` далеки от HGB. Bucket/global c и mix с naive — ❌.
- **Hurdle / zero (H03, H12, H29, H40):** clf×reg, вес нулей, snap, guard hist_gmv=0. Primary иногда лучше, holdout нет (H12 1.690 / 1.782). Доля y=0 сезонная.
- **Канальные головы + агрегаты (H04–H07, H11, H17):** рабочий каркас champion. Gaps на одной голове хуже (H06).
- **Ёмкость дерева (H13, H15, H19, H23, H24, H28, H30):** depth 8 / L2 / 320 iter — мелкий плюс; leaf 20/50, depth 7, monotonic — нет.
- **Loss (H16, H18, H21, H38):** quantile, poisson, MAE, Tweedie — сильно хуже log1p+RMSE.
- **Данные якорей (H22, H43, H56):** ранний cutoff, time-decay веса, якорь 8.11 — primary хуже. Три якоря Oct–Nov достаточно.
- **Другой бустер на тех же фичах (H31–H32, H45–H46, H54):** LGB чуть лучше HGB; mix H45 микро на H26; mix на BTYD (H54) регресс primary.
- **Коллинеарные фичи (H20, H25, H27, H34, H35, H41, H42, H47, H51, H55):** ord_lag, decay, weekday, last-K, RFM TE, burstiness, канальная воронка, канальный BTYD, channel recency — шум или holdout-регресс.
- **BTYD (H48):** процесс покупок как фичи, не hurdle.
- **Каденс заказов (H52):** IPI по дням `to_ord>0` — champion. H57 cardinality недавних заказных дней слабее. H50/H53 лаги — микро vs H48.
- **Календарь (H49):** primary лучше, holdout нет — ⚠️.
- **Калибровка/смесь голов (H33, H36, H37, H39, H44):** single-head, mid-residual, MoE hist, isotonic — хуже двух голов без калибровки.

## Cemetery (не повторять)

hurdle_zero_positive · mlp_cpu_small · poisson/tweedie identity · quantile · MAE · post-hoc c / bucket c / isotonic · mix с naive · densify · zero-weight без сезонного guard · extra early cutoff · extra mid cutoff 2025-11-08 (H56) · single-head total y · last-K gaps · weekday mix · vol/burst · RFM TE · time-decay весов якорей · CatBoost/XGB на H26_COLS · MoE hist · leaf 20/50 · depth 7 · monotonic GMV · ord_lag · hard-zero hist_gmv=0 · zero-snap τ · funnel search/cat to_ord windows (H47) · channel BTYD RFM (H51) · channel recency (H55) · LGB+HGB mix на BTYD (H54)

## Дыры H52 (куда смотреть дальше)

1. IPI закрыл каденс; y=0 и mid (~1.879) всё ещё держат массу SSE.
2. Календарь соло не перенёсся на holdout; стек с IPI не проверен.
3. Канальные/nested лаги микро vs H48; стек с IPI не проверен.
4. Воронка и канальный BTYD коллинеарны уже имеющемуся процессу.
5. Public ~1.65 — другой split/слой; офлайн после H48 ещё −0.001.

Гнаться за public ~1.65 на этом primary тем же слоем оконных сумм нереалистично.
