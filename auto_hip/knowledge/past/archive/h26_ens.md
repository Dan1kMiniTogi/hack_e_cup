# H26 — Среднее трёх seed

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: три H19 с разными random_state, среднее pred
Метрики: primary 1.69651 vs H19 1.69672; holdout 1.74172 vs 1.74218
Вердикт: принять, новый champion
Почему:
- persist=24537, fixed=463, regress=466 vs H19; holdout persist=24545, fixed=455, regress=412
- bagging стабилизирует микрошум листьев
Repro: h26_ens, arm=channel_ens
Next: ens+decay; не 5 seeds без нужды
