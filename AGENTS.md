# hack_e_cup

Протокол гипотез: [`auto_hip/AGENTS.md`](auto_hip/AGENTS.md). Пороги и splits: [`auto_hip/config.yaml`](auto_hip/config.yaml).

## Cursor Cloud specific instructions

Датасет **не** в git. Если нет `data/train.parquet` (или файл меньше ~100 MB):

```bash
python scripts/download_dataset.py
```

Файл на Google Drive должен быть доступен по ссылке (Anyone with the link). Cloud Build также вызывает этот скрипт из [`.cursor/environment.json`](.cursor/environment.json) (`install`). Не читать parquet целиком в чат.

Дальше — preflight и цикл в [`auto_hip/AGENTS.md`](auto_hip/AGENTS.md).
