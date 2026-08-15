# H35 — Last-K событий без densify

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: к фичам H26 добавлены gap последних 1–3 визитов, GMV/to_ord последней заказанной строки и searches после неё; модель H26 3-seed HGB.
Метрики: primary rmsle 1.69660 vs H31 1.69611 (хуже); holdout 1.74154 vs 1.74146 (чуть хуже)
Вердикт: отклонить
Почему:
- persist=24129, fixed=871, regress=867 vs H31 на primary; holdout persist=24198, fixed=802, regress=812
- mid 1.8853 ≈ H31 1.8846; last-K почти коллинеарен last_gap/recency_order
- densify не использовался; эффект в шуме bagging
Repro: run_id=h35_lastk, arm=channel_ens_lastk, champion-run=h31_lgb, `workspace/runs/h35_lastk/`
Next: не наращивать K на тех же окнах; другая ось (CatBoost / mid×order) vs H31
