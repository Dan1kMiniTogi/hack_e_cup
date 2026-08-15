# H11 — Intensity и conversion ratios

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: H07 + intensity/conversion ratios из оконных сумм
Метрики: primary 1.69814 vs H07 1.69867; holdout 1.74277 vs 1.74299
Вердикт: принять, новый champion (микро, оба сплита)
Почему:
- persist=24420, fixed=580, regress=619 vs H07 на primary; holdout persist=24456, fixed=544, regress=564
- ratios чуть двигают mid/intensity без ломки нулей
Repro: h11_ratios, arm=channel_ratios
Next: refine H11 осторожно; zero-weight не переносить на holdout
