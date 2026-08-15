# 003 — Что осталось у champion (H45)

**Дата / split:** local_val_cutoff_2026-01-14
**Опорный run:** `workspace/runs/h45_blend` · arm `blend_lgb_hgb` (предыдущие `h31_lgb`, `h26_ens`)
**Статус:** closed

## Вопрос

Почему офлайн RMSLE застрял ~1.696, если public top ~1.65, и какие оси ещё живы?

## Наблюдения

- H45 primary **1.696101**, holdout **1.74135** (оба лучше H31 1.696113 / 1.74146). persist/fixed/regress vs H31: 24642 / 358 / 364.
- После H04 (−0.49 vs naive) все бустеры/фичи/калибровки дали ≤0.001. H38 Tweedie 2.49; H37/H33 single-head ~1.705; H44 isotonic 1.707; H29 zero-guard 1.700; H40 snap 1.6965; H41 RFM TE ⚠️ holdout хуже.
- Структура ошибки H26/H31: ~52% SSE на y=0, mid 45% SSE, две головы лучше одной. Смесь библиотек — единственный ✅ этого пакета, микро.

## Гипотезы-кандидаты

Очередь `future/` пуста по стоп-запросу. Дальше вне этой сессии: другой признаковый слой (не оконные суммы), не refine HGB/LGB.

## Анти-паттерны

- hurdle, MLP, poisson/tweedie identity, quantile, MAE, c/bucket/isotonic, mix naive, densify, hard-zero hist_gmv=0, weekend cutoff, single-head, leaf 20/50

## Следующий шаг

Закрыто аудитом H45: [`../analytics/results/004_h45_debug.md`](../analytics/results/004_h45_debug.md). Живые оси — [`004_h45_blocks.md`](004_h45_blocks.md), не refine HGB/LGB на H26_COLS.
