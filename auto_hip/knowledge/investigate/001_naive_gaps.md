# 001 — Разрывы naive на полном 250k

**Дата / split:** local_val_cutoff_2026-01-14
**Опорный run:** `auto_hip/workspace/runs/h00_naive` · arms: naive
**Статус:** closed

## Вопрос

Почему naive last-30d GMV даёт RMSLE 2.195 на primary при завышении среднего (101.4 vs 84.0), и в каких срезах ошибка persist?

## Наблюдения

- Primary n=250000: rmsle=2.195065, mae_log1p=1.4418, y_zero=0.4593, zero_pred=0.4369, mean_pred=101.43, mean_true=84.03.
- Holdout: rmsle=2.214254, mean_pred≈mean_true (102.08 vs 101.43) — bias среднего почти только на primary (сдвиг окна).
- hist_gmv mid: rmsle 2.4787 (худший); high: mean_pred 466.6 vs mean_y 349.5; zero: y_zero 0.908, rmsle 1.074, pred всегда 0.
- recency только 0_7 (n=206319, rmsle 2.222) и 8_30 (n=43681, rmsle 2.062).
- Hash-EDA (~20k) совпала по порядку величины с полным naive.

## Гипотезы-кандидаты (не окончательные)

| # | Тип | Суть (1–2 информативных предложения) | Риск hard-constraint |
|---|-----|--------------------------------------|----------------------|
| 1 | refine | Глобальный множитель c на naive | c с primary не переносится на holdout |
| 2 | refine | c только на hist_gmv=high | узкий срез, регресс mid |
| 3 | pivot | Hurdle ноль/ненуль | ошибка классификации нуля |
| 4 | pivot | HGB на log1p агрегатов | переобучение vs holdout |
| 5 | explore | Отдельно search и cat GMV | шум малого канала |
| 6 | explore | Gap-фичи последовательности | шум, densify запрещён |

## Анти-паттерны

- Dense calendar; hardcode user_id; подгонка c на primary labels.

## Следующий шаг

Закрыто: naive разобран; скачок H04/H05. Актуальный champion H45 — [`004_h45_blocks.md`](004_h45_blocks.md).
