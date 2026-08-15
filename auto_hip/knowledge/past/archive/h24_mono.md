# H24 — Монотонность GMV

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: H19 + monotonic_cst на GMV-суммах
Метрики: primary 1.69693 vs 1.69672; holdout 1.74204 vs 1.74218
Вердикт: отклонить (primary)
Почему:
- persist=24435, fixed=565, regress=655
- constraint чуть помогает holdout, не primary
Repro: h24_mono
Next: seed-ensemble / decay feature
