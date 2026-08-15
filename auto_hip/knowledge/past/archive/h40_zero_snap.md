# H40 — Порог мелкий pred → 0

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: LGB две головы + τ на train-fit, pred<τ ⇒ 0.
Метрики: primary 1.69649 vs H31 1.69611; holdout 1.74181 vs 1.74146
Вердикт: отклонить (микрорегресс, не скачок по нулям)
Почему:
- persist=24594, fixed=406, regress=427 vs H31
- inner_rmsle fit 1.699; порог не перенёсся на eval лучше champion
Repro: h40_snap, arm=zero_snap
Next: не snap/hurdle/H12
