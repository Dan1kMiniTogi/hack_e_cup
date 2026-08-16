# H80 — H78 + intent dynamics в hurdle 3-seed
Статус: ⚠️ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Стек 0.30 H65 + 0.70 hurdle3; INTENT_DYNAMICS только в hurdle-голове, H65 без изменений.
Метрики:
- Primary: **1.689363** vs H78 1.689400 (−0.000037)
- Holdout: **1.738863** vs H78 1.738825 (+0.000038)
Вердикт: не промоутить (holdout регресс на уровне шума; primary микро-выигрыш)
Почему:
- Intent в стеке H78 почти нейтрален: primary чуть лучше, holdout чуть хуже.
- Сигнал H77 primary не переносится в holdout даже под страховкой H65 0.30.
Repro: h80_intent, arm=stack_h65_hurdle3_intent, `workspace/runs/h80_intent/`
Next: не добавлять полный intent-блок; опционально intent только в clf; приоритет holdout-сигнал H82.
