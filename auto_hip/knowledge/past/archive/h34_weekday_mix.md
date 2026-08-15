# H34 — Доля выходных в истории

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: к фичам H26 добавлены weekend_gmv_share и weekend_day_share по существующим строкам (сб/вс), модель как H26 3-seed.
Метрики: primary rmsle 1.69703 vs H26 1.69651 (хуже); holdout 1.74163 vs 1.74172 (чуть лучше)
Вердикт: отклонить
Почему:
- persist=24480, fixed=520, regress=588 vs H26 на primary; holdout persist=24493, fixed=507, regress=535
- календарный mix пользователя не сдвинул mid (rmsle 1.8857) и дал регресс primary
- cutoff weekday не использовался; densify не было
Repro: run_id=h34_weekday, arm=channel_ens_weekday, `workspace/runs/h34_weekday/`
Next: не добавлять cutoff-календарь; last-K / другая ось данных
