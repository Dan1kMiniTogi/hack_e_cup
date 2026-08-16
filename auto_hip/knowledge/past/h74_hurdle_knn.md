# H74 — H70 + RFM cohortknn peers
Статус: ⚠️ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Добавить COHORTKNN_FEATURES в clf/reg hurdle-logmix c=0 (arm `hurdle_logmix_c0_knn`).
Метрики:
- Primary: **1.689840** vs H70 1.690181 (−0.000341); vs H73 1.690065 лучше primary
- Holdout: **1.739585** vs H70 1.739575 (+0.000010); vs H73 1.739049 хуже
Вердикт: не промоутить (holdout регресс vs H70/H73); primary сигнал есть
Почему:
- На primary knn помогает mid/nonzero; holdout не подтверждает.
- Не повторять knn как solo-промоут без holdout-guard; возможен лёгкий вес в стеке позже.
Repro: h74_hurdle_knn, arm=hurdle_logmix_c0_knn, `workspace/runs/h74_hurdle_knn/`
Next: не refine knn без нового механизма; приоритет 075/076/077.
