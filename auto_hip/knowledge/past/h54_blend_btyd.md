# H54 — LGB+HGB mix на BTYD

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: 0.5 LGB + 0.5 HGB, оба на H26+BTYD, 3 сида, две log1p-головы (H45 на новом слое).
Метрики: primary 1.693688 vs H48 1.693588; holdout 1.740029 vs 1.740301
Вердикт: отклонить (регресс primary)
Почему:
- persist=24599, fixed=401, regress=417 vs H48 на primary; holdout persist=24622, fixed=378, regress=337
- holdout лучший в пакете, primary нет — H45-механизм не переносится на BTYD
- mid 1.8806 чуть хуже
Repro: h54_blend, arm=blend_lgb_hgb_btyd, `workspace/runs/h54_blend/`
Next: не mix библиотек на BTYD; IPI важнее
