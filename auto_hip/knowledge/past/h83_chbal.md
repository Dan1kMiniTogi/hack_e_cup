# H83 — H78 + channel balance features
Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: CHANNEL_BALANCE (cat dominance, entropy, search/cat ord ratio) в обе головы стека H78.
Метрики:
- Primary: **1.689551** vs H78 1.689400 (+0.000151)
- Holdout: **1.738817** vs H78 1.738825 (−0.000008)
Вердикт: отклонить
Почему:
- Относительный микс каналов не дал выигрыша на primary; holdout в шуме.
- Коллинеарность с уже имеющимися channel lags / gmv shares.
Repro: h83_chbal, arm=stack_h65_hurdle3_chbal, `workspace/runs/h83_chbal/`
Next: не refine balance-фич; holdout-линия H82 приоритетнее.
