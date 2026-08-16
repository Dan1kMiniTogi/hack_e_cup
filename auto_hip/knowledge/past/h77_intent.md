# H77 — Hurdle + intent dynamics features
Статус: ⚠️ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: INTENT_DYNAMICS (search accel, cart→ord, hot cart, search/cat shift) в hurdle-logmix c=0.
Метрики:
- Primary: **1.689251** vs H73 1.690065 (−0.000814)
- Holdout: **1.739621** vs H73 1.739049 (+0.000572)
Вердикт: не промоутить (holdout регресс); primary сигнал сильный
Почему:
- Intent фичи помогают primary (похоже на H75), но holdout не держит.
- Не добавлять intent в champion без holdout-safe стека / регуляризации.
Repro: h77_intent, arm=hurdle_intent_dynamics, `workspace/runs/h77_intent/`
Next: опционально intent только в clf или в стеке с малым весом; приоритет H75×H73 stack.
