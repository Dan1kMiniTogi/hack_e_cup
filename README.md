# hack_e_cup — E-CUP 2026, задача 3 (Search/Catalog LTV)

Репозиторий цикла гипотез (`auto_hip/`) и кода прогонов для предсказания 30-дневного GMV (метрика RMSLE).

## После клона

1. Установи зависимости:

```bash
pip install -r requirements.txt
```

2. Положи датасет соревнования в `data/train.parquet` (~172 MB).  
   Описание колонок и формата сабмита — [`data/README.md`](data/README.md).  
   Файл **не** в git (лимит GitHub / размер). Без него `runner.py` и analytics не стартуют.

3. (Опционально) создай venv и активируй его перед `pip install`.

## Работа с гипотезами

- Протокол агента: [`auto_hip/AGENTS.md`](auto_hip/AGENTS.md)
- Пороги / champion / splits: [`auto_hip/config.yaml`](auto_hip/config.yaml)
- Knowledge-цикл: [`auto_hip/knowledge/`](auto_hip/knowledge/) (`investigate` → `future` → experiment → `past`)
- Обзор инстанса: [`auto_hip/README.md`](auto_hip/README.md)

## Прогоны

```bash
cd auto_hip/workspace
python runner.py cache
python runner.py run --arm naive --run-id h00_naive
python runner.py submit --arm <champion_arm> --run-id submit_champ
```

Подробнее: [`auto_hip/workspace/README.md`](auto_hip/workspace/README.md).

Тяжёлые артефакты (`runs/`, `cache/`, модели) локальные и в `.gitignore`.
