# H05 — Search + Catalog сумма

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: две HGB log1p на y_search и y_cat, сумма clip≥0
Метрики: primary rmsle 1.699 vs H04 1.708; holdout 1.743 vs 1.746
Вердикт: принять, новый champion (небольшой, но оба сплита)
Почему:
- persist=23312, fixed=1688, regress=1007 vs H04 на primary
- канальная декомпозиция чуть лучше единого GMV
Repro: run_id=h05_channel, arm=channel_sum
Next: gaps и scale_high vs H05
