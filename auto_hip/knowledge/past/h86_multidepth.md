# H86 — Multi-depth hurdle (leaves 31 / 63 / 95)
Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Три сида hurdle с разной ёмкостью (31/90/0.05, 63/60/0.04, 95/40/0.03) вместо одинаковых деревьев.
Метрики:
- Primary: **1.689650** vs H78 1.689400 (+0.000250)
- Holdout: **1.738790** vs H78 1.738825 (−0.000035)
Вердикт: отклонить
Почему:
- Primary заметно хуже; holdout в шуме. Асимметрия листьев без hurdle уже падала в H71.
- Глубокий член 95 листьев, похоже, тянет mid/primary, мелкий не компенсирует.
Repro: h86_multidepth, arm=stack_h65_hurdle3_multidepth, `workspace/runs/h86_multidepth/`
Next: cemetery для multi-depth на том же стеке без нового механизма.
