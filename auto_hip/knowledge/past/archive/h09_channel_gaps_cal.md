# H09 — RMSLE-калибровка множителем

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: channel_gaps + множитель c по RMSLE на train-fit
Метрики: primary 1.7055 vs H07 1.6987; holdout 1.7449 vs 1.7430; c=1.05
Вердикт: отклонить
Почему:
- persist=24526, fixed=474, regress=777 vs H07 на primary
- слабый up-scale ухудшает нули сильнее, чем помогает хвосту
Repro: h09_cal, arm=channel_gaps_cal
Next: не глобальный c; bucket или новые фичи
