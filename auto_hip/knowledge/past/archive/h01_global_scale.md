# H01 — Глобальная RMSLE-калибровка

Статус: ⚠️ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: pred = c * naive_30d, c подобран по RMSLE на fit-якорях (c=0.4, упёрся в низ сетки)
Метрики: primary rmsle 2.037 vs naive 2.195; holdout 2.108 vs 2.214
Вердикт: доработать / не champion — лучше naive на обоих сплитах, но слабее H04; mean_pred 40.6 vs true 84
Почему:
- persist=16557, fixed=8443, regress=761 vs naive на primary
- c=0.4 — край сетки; holdout mean ломается (40 vs 101)
Repro: run_id=h01_scale, arm=scale, workspace/runs/h01_scale
Next: не промоутить над H04; refine c ниже 0.4 низкий приоритет
