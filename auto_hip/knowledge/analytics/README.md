# analytics — данные для гипотез

Сюда складываем **скрипты** (в целевом проекте или локально) и **результаты** (md/json), на которых строятся investigate briefs и `future/`. Не дублирует `past/` (вердикты) и `METRICS.md` (KPI SoT).

```
knowledge/analytics/
  README.md
  scripts/eda_snapshot.py
  scripts/h07_residual.py
  scripts/003_champion_deep_eda.py
  scripts/004_h45_debug.py
  results/001_eda_snapshot.md
  results/002_h07_residual.md
  results/003_line_scorecard.md
  results/003_champion_deep_eda.md
  results/004_h45_debug.md
  results/chatgpt_seed_hypotheses_prompt.md
  results/chatgpt_gap_hypotheses_prompt.md
```

Пересчёт снимка naive-выборки: `python auto_hip/knowledge/analytics/scripts/eda_snapshot.py` из корня репо.
Deep EDA champion H26: `python auto_hip/knowledge/analytics/scripts/003_champion_deep_eda.py`.
Debug champion H45: `python auto_hip/knowledge/analytics/scripts/004_h45_debug.py`.
Промпт после H26 (разрыв с LB): `results/chatgpt_gap_hypotheses_prompt.md` (копировать блок между BEGIN/END). Старый seed-промпт — `chatgpt_seed_hypotheses_prompt.md`.

## Когда обязательно запускать (до `future/`)

| Ситуация | Действие |
|----------|----------|
| Brief без цифр по нужному слою | снять snapshot слоя → `results/*.md` |
| Серия ❌ по одной линии и непонятно *что* ломается | breakdown + распределения pred/ref / ошибок |
| Новая ось без baseline snapshot | сначала baseline analytics → brief → future |
| Очередь пуста / explore вне champion | минимум distribution / error anatomy по METRICS |

Порядок: **analytics → investigate brief → future/**. Ссылка в гипотезе: `Исследование:` + путь к `results/*.md` или brief.

## Снимки для этой задачи (когда цикл стартует)

Не запускать «на всякий случай»: только если brief без цифр. Агрегировать по `user_id` / cutoff, **без** dense calendar.

| Слой | Зачем |
|------|--------|
| sparsity | доля пользователей/дней с записью; не заполнять нули |
| zero-GMV | доля y=0 в 30d окне; как RMSLE бьёт по нулям vs хвосту |
| recency | давность последней активности/заказа vs будущий GMV |
| channel mix | Поиск vs Каталог vs оба vs ни одного |
| hist GMV / activity days | срезы из METRICS для persist/fixed/regress |

## Правила

- Не хардкодить id кейсов в results для подбора treatment.
- Results — навигация для brief; acceptance всё равно vs champion по `config.yaml`.
- Старые results не удалять без нужды; для нового цикла — новый файл.

На старте шаблона `scripts/` и `results/` можно создать по мере надобности — обязателен только этот README.
