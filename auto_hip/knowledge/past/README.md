# past — история экспериментов

Сюда пишутся отчёты после прогонов.

## Как читать

1. [`INDEX.md`](INDEX.md) — полный scorecard (читай первым).
2. [`SYNTHESIS.md`](SYNTHESIS.md) — путь метрики, cemetery, дыры champion.
3. [`lines/`](lines/) — свёртка старых эпох (H00–H46+) и [`lines/cemetery.md`](lines/cemetery.md).
4. В корне `past/` — **активное окно ~15** полных отчётов (`hxx_slug.md`). Сейчас: H74–H87.

## Правило окна (~15)

- Новый прогон: строка в INDEX + полный отчёт `past/hxx_slug.md`.
- Если полных отчётов в корне **>15** — самый старый свернуть в 1–3 буллета в соответствующий `lines/*.md` и удалить индивидуальный файл.
- INDEX **не укорачивать** (нужен для anti-loop и статусов всех id).

## Обязательные поля отчёта

```markdown
# Hxx — название
Статус: ✅/⚠️/❌ | Primary: <split> | Holdout: … | N: …
Идея: 1–2 предложения (механизм, без id)
Метрики: primary (+ holdout) vs champion — имена из METRICS.md
Вердикт: принять / отклонить / доработать
Почему:
- persist=…, fixed=…, regress=… vs champion
- топ срезы: …
Repro: run_id, arm, путь к meta/логу
Next: что в brief / future
```

Отчёт без persist/fixed/regress (или эквивалента из METRICS) — **невалиден**.

## Статусы

- ✅ — acceptance + holdout (если требуется config).
- ⚠️ — прогресс на primary без подтверждённого holdout / частичный критерий.
- ❌ — hard-constraint / чистый regress / провал идеи.
