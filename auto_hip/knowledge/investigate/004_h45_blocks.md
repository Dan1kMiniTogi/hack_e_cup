# 004 — Блоки H45: почему плато и какие оси живы

**Дата / split:** local_val_cutoff_2026-01-14
**Опорный run:** `workspace/runs/h48_btyd` · arm `lgb_btyd` vs H45 `h45_blend`
**Статус:** closed

## Вопрос

Почему офлайн RMSLE H45 застрял на 1.696, какие блоки ещё дают сигнал, и какие оси champion не трогал?

## Наблюдения

Цифры H45: [`../analytics/results/004_h45_debug.md`](../analytics/results/004_h45_debug.md). H47/H48: [`../past/h47_funnel.md`](../past/h47_funnel.md), [`../past/h48_btyd.md`](../past/h48_btyd.md).

- H45 плато подтверждено: слой `H26_COLS` выжат (Spearman |ρ|<0.08). Mix библиотек −0.000012.
- **H47 funnel ❌:** primary 1.696525 / holdout 1.741538 vs H45 1.696101 / 1.74135. persist/fixed/regress 24263/737/790. Воронка коллинеарна `to_ord`.
- **H48 BTYD ✅ champion:** primary **1.693588** / holdout **1.740301**. persist/fixed/regress 23342/1658/1601 на primary (holdout 23454/1546/1607). Первый скачок не из оконных сумм (−0.0025). mid 1.8803 vs 1.8846; recency 0_7 1.7131 vs 1.7164.
- Живые оси: календарь целевого окна (holdout mean_true 101 vs primary 84); disjoint 30d лаги GMV.

Код champion: `fit_arm("lgb_btyd")` в [`../../workspace/ltv_arms.py`](../../workspace/ltv_arms.py).

## Гипотезы-кандидаты (не окончательные)

| # | Тип | Суть | Риск hard-constraint |
|---|-----|------|----------------------|
| 1 | explore | Воронка — закрыто H47 ❌ | — |
| 2 | pivot | BTYD-фичи — закрыто H48 ✅ | — |
| 3 | explore | Календарь следующих 30d (праздники/месяц), известен на cutoff | подгонка под НГ-holdout |
| 4 | explore | Disjoint 30d лаги GMV `[-30,0]`, `[-60,-30]`, `[-90,-60]` к H48 | коллинеарность с `gmv_sum_*` |

В очередь `future/`: #3–#4 (049–050) плюс 051–057 (канальный BTYD, IPI заказов, канальные лаги, mix LGB+HGB на BTYD, ресенси канала, якорь 2025-11-08, недавние заказные дни).

## Анти-паттерны

hurdle · funnel windows (H47) · MLP · poisson/tweedie · quantile · MAE · post-hoc c · mix naive · densify · zero-weight · extra early cutoff · single-head · last-K · weekday · vol · RFM TE · refine HGB/LGB на голом H26_COLS

## Следующий шаг

Календарь целевого окна и disjoint 30d лаги vs H48; не повторять funnel.
