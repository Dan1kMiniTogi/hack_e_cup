# H58 — IPI + календарь целевого окна

Статус: ⚠️ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: календарь следующих 30d поверх H52 (IPI+BTYD), две LGB-головы.
Метрики: primary 1.692532 vs H52 1.692618; holdout 1.740267 vs 1.740169
Вердикт: не промоутить (holdout хуже, как H49 соло)
Почему:
- persist=24525, fixed=475, regress=419 vs H52 на primary; holdout persist=24632, fixed=368, regress=369
- mid 1.8784 vs 1.8787; календарь снова не переносится на НГ-окно
Repro: h58_ipi_cal, arm=lgb_ipi_cal, `workspace/runs/h58_ipi_cal/`
Next: не стековать календарь соло с IPI
