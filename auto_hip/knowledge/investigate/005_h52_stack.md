# 005 — После H52: что ещё живое

**Дата / split:** local_val_cutoff_2026-01-14
**Опорный run:** `workspace/runs/h52_ipi` · arm `lgb_btyd_ipi` vs H48 `h48_btyd`
**Статус:** closed

## Вопрос

Какие оси из пакета H49–H57 независимы от IPI и стоит стековать, а какие закрыты?

## Наблюдения

- H52 champion: primary **1.692618** / holdout **1.740169**. persist/fixed/regress 24291/709/807 vs H48; mid 1.8787 vs 1.8803.
- Микро-✅ vs H48, слабее H52: H50 lags, H53 channel lags, H57 recent ord days.
- ⚠️ H49 calendar: primary 1.693343 лучше H48, holdout 1.740312 нет.
- ❌ H51 channel BTYD, H54 mix HGB, H55 channel recency, H56 cutoff 8.11.

## Гипотезы-кандидаты (не окончательные)

| # | Тип | Суть | Риск hard-constraint |
|---|-----|------|----------------------|
| 1 | explore | IPI + календарь целевого окна | подгонка под НГ-holdout |
| 2 | explore | IPI + канальные disjoint лаги | коллинеарность с окнами |

## Анти-паттерны

канальный BTYD · channel recency · mix LGB+HGB на BTYD · extra cutoff Oct–Nov · funnel · hurdle

## Следующий шаг

Стек победителей (IPI+cal, IPI+chlag) vs H52; не новые RFM.
