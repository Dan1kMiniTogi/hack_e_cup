# 010 — После H80–H83: holdout-сигнал mixed CatBoost

**Дата / split:** local_val_cutoff_2026-01-14
**Опорный run:** `workspace/runs/h78_stack_h3` (champ) + `workspace/runs/h82_mixed`
**Статус:** open

## Вопрос

Как забрать holdout-выигрыш H82 (−0.00027) без primary-регресса (+0.00019)?

## Наблюдения

- H78 остаётся чемпионом: **1.689400 / 1.738825**.
- H80 intent ⚠️ 1.689363 / 1.738863 — шум.
- H81 T=0.9 ❌ 1.692937 / 1.740194 — cemetery для заострения p.
- H82 mixed ⚠️ **1.689586 / 1.738559** — holdout лучший в серии.
- H83 chbal ❌ 1.689551 / 1.738817.

## Гипотезы-кандидаты

| # | Тип | Суть | Файл |
|---|-----|------|------|
| 1 | explore | hurdle bag = 3 LGB + 1 CatBoost (084) | [`../future/084_hurdle4_lgb_cb.md`](../future/084_hurdle4_lgb_cb.md) |
| 2 | pivot | log-blend 0.70 H78 + 0.30 H82-arm (085) | [`../future/085_blend_h78_h82.md`](../future/085_blend_h78_h82.md) |

## Анти-паттерны

T<1 на логитах · dual-channel · сетка весов 0.15/0.85 · channel balance refine · полный intent-блок

## Следующий шаг

084 + 085; чемпион пока H78.
