# H88 — 4-мемберный hurdle (3×LGB + 1×CB) на clf-intent H87
Статус: ⚠️ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Стек 0.30 H65 + 0.70 hurdle; hurdle = LGB(42,43,44)+CatBoost(45); INTENT_DYNAMICS только в clf, μ на H65, c=0.
Метрики:
- Primary: **1.689445** vs H87 1.689383 (+0.000062)
- Holdout: **1.738558** vs H87 1.738805 (−0.000247); ≈ H82 1.738559
Вердикт: не промоутить (регресс primary); holdout лучший среди 4-bag на H87
Почему:
- persist=24791, fixed=209, regress=210 на primary; holdout persist=24770, fixed=230, regress=151
- mid RMSLE 1.8764 vs H87 1.8762 — CB не поднял μ в mid (mean_pred 41.75 vs 41.70)
- Паттерн H84: holdout забирается, primary чуть хуже clf-intent LGB
Repro: h88_hurdle4, arm=stack_h87_hurdle4_mixed, `workspace/runs/h88_hurdle4/`
Next: не соло-CB без калибровки p; проверить 4-bag уже на H91 (T=1.05)
