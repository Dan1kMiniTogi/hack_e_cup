# H39 — MoE по hist_gmv

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: два LGB-эксперта (две головы) ниже/выше q50 hist_gmv.
Метрики: primary 1.69877 vs H31 1.69611; holdout 1.74314
Вердикт: отклонить
Почему:
- persist=23765, fixed=1235, regress=1509 vs H31
- раздельные деревья не побили единый бустер
Repro: h39_moe, arm=moe_hist
Next: не gate по hist_gmv
