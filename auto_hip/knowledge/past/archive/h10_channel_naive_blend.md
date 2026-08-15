# H10 — Blend channel_gaps и naive_30d

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: alpha * H07-pred + (1-alpha) * naive_30d, alpha по RMSLE на train-fit
Метрики: primary 1.6987 / holdout 1.7430 — совпало с H07; alpha=1.0
Вердикт: отклонить
Почему:
- persist=25000, fixed=0, regress=0 — вырождение в champion
- naive не улучшает RMSLE ни на какой смеси на fit-якорях
Repro: h10_blend, arm=channel_naive_blend
Next: ratios / веса нулей, не mix с naive
