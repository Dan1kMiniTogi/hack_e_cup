# 004 — Блоки H45: почему плато и какие оси живы

**Дата / split:** local_val_cutoff_2026-01-14
**Опорный run:** `workspace/runs/h45_blend` · arm `blend_lgb_hgb` vs H31 `h31_lgb`
**Статус:** open

## Вопрос

Почему офлайн RMSLE H45 застрял на 1.696101 (holdout 1.74135), какие блоки пайплайна ещё что-то дают, и какие оси данных champion не трогал?

## Наблюдения

Цифры: [`../analytics/results/004_h45_debug.md`](../analytics/results/004_h45_debug.md). Синтез H00–H46: [`../past/SYNTHESIS.md`](../past/SYNTHESIS.md).

- Primary: 52.3% SSE на y=0 (n=114835, y_zero=0.4593), mean_pred на нулях=8.243, zero_pred_share=2.4e-05, rmsle_y0=1.8102. mid hist_gmv: 36.3% людей, **44.8% SSE**, rmsle 1.8846. order recency 8–30д: 29.4% людей, 36.7% SSE.
- Holdout: SSE на y=0 падает до 44.5%; mean_true 101.4 vs 84.0; mean_log_bias 0.064 vs 0.256. Сезон окна, не «недоученность» H45.
- Блоки (последовательные Δ, не абляция): H04 BASE log1p −0.487; H05 две головы −0.009; H07–H45 суммарно −0.003. Mix LGB+HGB на тех же 44 колонках: −0.000012. persist/fixed/regress vs H31: 24642 / 358 / 364.
- Не в агрегатах H26/H45: `has_search_to_cart/ord`, `has_cat_to_cart/ord`, `search_to_cart/ord`, `cat_to_cart/ord`. Lifetime Spearman vs log_bias |ρ|≤0.05 (как у текущих фич) — линейного остатка нет, но канальная декомпозиция `to_ord` не подавалась в дерево.
- Spearman текущих фич vs log_bias: max |ρ|=0.056 (gmv_sum_90d). Слой оконных сумм выжат.

Код champion: `fit_arm("blend_lgb_hgb")` / `predict_arm` в [`../../workspace/ltv_arms.py`](../../workspace/ltv_arms.py); фичи — `H26_COLS` из [`../../workspace/ltv_data.py`](../../workspace/ltv_data.py). Extra/vol кэш H45 не использует.

## Гипотезы-кандидаты (не окончательные)

| # | Тип | Суть (1–2 информативных предложения) | Риск hard-constraint |
|---|-----|--------------------------------------|----------------------|
| 1 | explore | Оконные суммы воронки search/cat (`*_to_ord`, `*_to_cart`, `has_*`) к H26_COLS, две головы как H31/H45 | шум редкого cat; коллинеарность с `to_ord` |
| 2 | pivot | BG-NBD + AOV как фичи (`p_alive`, `e_purch_30`, `e_gmv_btyd`) в LGB-головы, не clf×reg hurdle | плохая калибровка частоты; не заменять pred на сырой BTYD |
| 3 | explore | Календарь целевого окна (праздники/месяц следующих 30d) — бэклог, не слот workers | подгонка под НГ-holdout |
| 4 | explore | Disjoint 30d лаги GMV вместо вложенных 7/14/30/60/90 — бэклог | коллинеарность с `gmv_sum_*` |

В очередь `future/` сейчас только #1 и #2 (`workers: 2`).

## Анти-паттерны

hurdle · MLP · poisson/tweedie identity · quantile · MAE · post-hoc c/bucket/isotonic · mix naive · densify · zero-weight · extra early cutoff · single-head · last-K gaps · weekday · vol · RFM TE · time-decay якорей · CatBoost/XGB на H26_COLS · MoE hist · leaf 20/50 · depth 7 · refine HGB/LGB на том же векторе

## Следующий шаг

Прогнать воронку (#1) и BTYD-фичи (#2) против H45; не добавлять refine деревьев, пока эти две оси не закрыты.
