# H06 — HGB + gap-агрегаты

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: HGB log1p как H04 плюс last/mean/max gap и n_gaps>7/14
Метрики: primary rmsle 1.707 vs H05 1.699; holdout 1.746 vs 1.743
Вердикт: отклонить (на уровне H04, хуже channel champion)
Почему: gap-фичи не улучшили единый GMV относительно канальной суммы
Repro: h06_gaps
Next: проверить gaps на channel_sum; иначе стоп по этой оси
