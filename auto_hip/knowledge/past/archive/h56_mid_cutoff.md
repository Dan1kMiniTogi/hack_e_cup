# H56 — Якорь 2025-11-08

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: к fit H48 добавлен cutoff 2025-11-08 (между 1.11 и 15.11), без раннего 4.10.
Метрики: primary 1.694647 vs H48 1.693588; holdout 1.740583 vs 1.740301
Вердикт: отклонить
Почему:
- persist=24295, fixed=705, regress=924 vs H48 на primary; holdout persist=24310, fixed=690, regress=726
- mid 1.8820 хуже; лишние iid-строки того же сезона вредят, как и ранний якорь H22
- плотность walk-forward в Oct–Nov исчерпана
Repro: h56_midcut, arm=lgb_btyd_midcut, `workspace/runs/h56_midcut/`
Next: не добавлять якоря в Oct–Nov
