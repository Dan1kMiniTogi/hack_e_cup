# H85 — Log-blend H78 ⊕ H82 (0.70 / 0.30)
Статус: ⚠️ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Один fit: общая H65-голова + hurdle3 LGB и hurdle mixed; log-blend 0.70 H78-сборки + 0.30 H82-сборки.
Метрики:
- Primary: **1.689415** vs H78 1.689400 (+0.000015)
- Holdout: **1.738712** vs H78 1.738825 (−0.000113)
Вердикт: не промоутить (primary чуть хуже)
Почему:
- Смесь тянет holdout вниз, но не до H82 (1.738559); primary всё ещё над H78.
- Фиксированные 0.70/0.30 слишком консервативны для CB-сигнала и всё равно бьют primary.
Repro: h85_blend, arm=blend_h78_h82, `workspace/runs/h85_blend/`
Next: не сетка весов; комбинировать CB только внутри hurdle чемпиона.
