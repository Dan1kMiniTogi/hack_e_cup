# auto_hip — цикл гипотез (E-CUP 2026, задача 3)

Инстанс knowledge-протокола под предсказание 30-дневного GMV (Поиск/Каталог, метрика RMSLE). Правила цикла те же, что у шаблона: **investigate → future → experiment → past**. Факты задачи, KPI и пороги — не в `AGENTS.md`, а в профиле ниже.

## Профиль этого инстанса

- Задача и ловушки данных: [`knowledge/CONTEXT.md`](knowledge/CONTEXT.md)
- Определения метрик: [`knowledge/METRICS.md`](knowledge/METRICS.md)
- Сплиты, acceptance, workers, preflight: [`config.yaml`](config.yaml)
- Протокол агента: [`AGENTS.md`](AGENTS.md)
- Код и артефакты прогонов: [`workspace/`](workspace/)
- Сырые данные: [`../data/train.parquet`](../data/train.parquet) + [`../data/README.md`](../data/README.md)

## Каркас

| Файл / папка | Роль |
|--------------|------|
| [`AGENTS.md`](AGENTS.md) | Протокол одного цикла для агента |
| [`config.yaml`](config.yaml) | SoT порогов, baselines, workers, preflight |
| [`knowledge/`](knowledge/) | CONTEXT, METRICS, investigate → future → past |
| [`workspace/`](workspace/) | Раннер, pred, meta (не knowledge) |

Порядок работы: **investigate → future → experiment → past**.

## Чего здесь нет (пока)

- Готового раннера и воспроизведённого champion_run (control описан как наивный авторегресс).
- Brief в `investigate/` и очереди в `future/` — цикл ещё не стартовал.
