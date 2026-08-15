# H49 — Календарь целевого окна

Статус: ⚠️ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: к H48 добавлены признаки следующих 30 дней (месяц, выходные, праздники РФ/14.02), одинаковые для всех user_id на cutoff; две LGB-головы, clip≥0.
Метрики: primary 1.693343 vs H48 1.693588; holdout 1.740312 vs 1.740301
Вердикт: не промоутить (holdout не лучше); primary сдвиг есть
Почему:
- persist=24593, fixed=407, regress=432 vs H48 на primary; holdout persist=24662, fixed=338, regress=377 — обмен хвоста в шуме
- mid 1.8796 vs 1.8803; recency 0_7 1.7129 vs 1.7131
- holdout с НГ чуть хуже: дерево не выиграло на сезоне, ради которого фичи заводили
Repro: h49_cal, arm=lgb_btyd_cal, `workspace/runs/h49_cal/`
Next: календарь только в стеке с H52, не соло
