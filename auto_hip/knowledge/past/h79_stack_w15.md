# H79 — Стек 0.15 H65 + 0.85 hurdle 3-seed
Статус: ⚠️ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Та же архитектура H78, веса 0.15/0.85 в сторону hurdle 3-seed.
Метрики:
- Primary: **1.689218** vs H78 1.689400 (−0.000182); vs H73 лучше
- Holdout: **1.738941** vs H78 1.738825 (+0.000116); vs H73 лучше
Вердикт: лучше H73 на обоих, но vs H78 holdout хуже → не промоутить
Почему:
- Больше веса на hurdle улучшает primary, чуть бьёт holdout относительно H78.
- Оставить H78 чемпионом; не крутить веса дальше без нового механизма.
Repro: h79_stack_w15, arm=stack_h65_hurdle3seed_w85, `workspace/runs/h79_stack_w15/`
Next: стоп по весам стека; искать новую ось (mid/features/arch).
