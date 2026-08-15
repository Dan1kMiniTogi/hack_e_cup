# workspace

Сюда кладём **исполнение** гипотез. Knowledge-цикл (`investigate` / `future` / `past`) сюда не пишем.

## Запуск

```
python runner.py cache
python runner.py run --arm naive --run-id h00_naive
python runner.py run --arm hgb_log1p --run-id h04_hgb --champion-run h00_naive
python runner.py submit --arm <champion_arm> --run-id submit_champ
```

Сабмит: [`submit.csv`](submit.csv) (`user_id,predict`).

## Что здесь будет

| Путь | Назначение |
|------|------------|
| скрипты / ноутбуки | фичи до cutoff, модель, оценка RMSLE, сабмит |
| `runs/<run_id>/` | pred (`user_id, predict`), `metrics.json`, `meta.yaml` (hypothesis, split, параметры, git commit если есть) |

Один прогон = один `run_id`. Сравнение treatment vs champion — по именам из [`../knowledge/METRICS.md`](../knowledge/METRICS.md) и порогам [`../config.yaml`](../config.yaml).

## Ограничения

- Не densify дневной календарь нулями.
- Предсказания неотрицательные; все `user_id` из train.
- Тяжёлые артефакты (`runs/`, модели, кэш агрегатов) в `.gitignore` репозитория.
