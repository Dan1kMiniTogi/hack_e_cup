# 010 — После H80–H83: holdout-сигнал mixed CatBoost и декомпозиция ошибок

**Дата / split:** local_val_cutoff_2026-01-14
**Опорный run:** `workspace/runs/h78_stack_h3` (champ) + `workspace/runs/h82_mixed`
**Статус:** open

## Вопрос

Как забрать holdout-выигрыш H82 (−0.00027) и primary-сигнал intent без регресса метрик на противоположном сплите?

## Наблюдения

- H78 остаётся чемпионом: **1.689400 / 1.738825**.
- H80 intent ⚠️ 1.689363 / 1.738863 — primary лучше чемпиона, но регрессоры переобучились на краткосрочном шуме на holdout.
- H81 T=0.9 ❌ 1.692937 / 1.740194 — cemetery для заострения $p$ (завышает mean_pred и квадратичную ошибку).
- H82 mixed ⚠️ **1.689586 / 1.738559** — лучший holdout в серии за счет разнообразия деревьев CatBoost.
- H83 chbal ❌ 1.689551 / 1.738817 — коллинеарность с channel lags.

## Портфель гипотез-кандидатов (future/)

| # | Id | Тип | Суть | Файл |
|---|----|-----|------|------|
| 1 | 084 | explore | Hurdle bag 3×LGB + 1×CatBoost на стеке H78 | [`../future/084_hurdle4_lgb_cb.md`](../future/084_hurdle4_lgb_cb.md) |
| 2 | 085 | pivot | Log-blend чемпиона H78 с mixed-стеком H82 (0.70 / 0.30) | [`../future/085_blend_h78_h82.md`](../future/085_blend_h78_h82.md) |
| 3 | 086 | explore | Двухмасштабная глубина (Multi-depth 31/63/95) в hurdle 3-seed | [`../future/086_hurdle3_multidepth.md`](../future/086_hurdle3_multidepth.md) |
| 4 | 087 | pivot | Изолированные динамические фичи только в классификаторе P(y>0) | [`../future/087_clf_only_intent.md`](../future/087_clf_only_intent.md) |

## Анти-паттерны

$T < 1$ на логитах · dual-channel hurdle · сетка весов стека $0.15/0.85$ · channel balance ratios · добавление intent в регрессоры $\mu$

## Следующий шаг

Прогнать гипотезы 084–087 на связке Primary + Holdout; чемпион на текущий момент — H78.
