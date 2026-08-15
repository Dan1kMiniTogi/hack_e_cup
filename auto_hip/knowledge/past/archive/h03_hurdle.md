# H03 — Hurdle ноль/ненуль

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: P(y>0)*E[y|y>0] HGB clf+reg на агрегатах
Метрики: primary rmsle 2.070 vs H04 1.708; holdout 2.031 vs 1.746
Вердикт: отклонить
Почему:
- persist=17592, fixed=7408, regress=29209 vs H04 на primary
- двухэтапность хуже прямого log1p HGB
Repro: run_id=h03_hurdle, arm=hurdle
Next: не повторять hurdle без другой clf-схемы
