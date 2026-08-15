# H43 — Веса якорей по давности

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: LGB H31 с sample_weight exp(−Δdays/21) к inner_train.
Метрики: primary 1.69681 vs H31 1.69611; holdout 1.74159 vs 1.74146
Вердикт: отклонить
Почему:
- persist=24173, fixed=827, regress=856 vs H31
- перевзвешивание сезона не закрыло разрыв RMSLE
Repro: h43_timew, arm=time_decay_w
Next: не H22-стиль переразметки якорей
