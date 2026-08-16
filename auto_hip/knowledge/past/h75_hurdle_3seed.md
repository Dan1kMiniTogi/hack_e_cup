# H75 — Hurdle-logmix 3-seed bagging
Статус: ⚠️ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Три сида (42/43/44) hurdle-logmix c=0; усреднение p и μ до сборки expm1(p·log1p(μ)).
Метрики:
- Primary: **1.689143** vs H73 1.690065 (−0.000922); vs H70 1.690181 лучше
- Holdout: **1.739171** vs H73 1.739049 (+0.000122); vs H70 1.739575 лучше
Вердикт: не промоутить vs H73 (holdout); лучший primary в серии — кандидат в стек
Почему:
- 3-seed сильно бьёт primary и бьёт H70 holdout, но тонко проигрывает H73 holdout.
- Логичный next: заменить hurdle-голову в H73 на 3-seed (0.30 H65 + 0.70 hurdle_3seed).
Repro: h75_hurdle_3seed, arm=hurdle_logmix_3seed, `workspace/runs/h75_hurdle_3seed/`
Next: stack_h65_hurdle3seed; не крутить веса сидов.
