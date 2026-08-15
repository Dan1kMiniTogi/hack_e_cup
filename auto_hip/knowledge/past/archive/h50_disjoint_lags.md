# H50 — Disjoint 30d лаги GMV

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: три непересекающихся блока GMV из вложенных 30/60/90 и отношения соседей; стек H48, без densify.
Метрики: primary 1.693554 vs H48 1.693588; holdout 1.740184 vs 1.740301
Вердикт: принять vs H48, не champion (хуже H52)
Почему:
- persist=24494, fixed=506, regress=671 vs H48 на primary; holdout persist=24502, fixed=498, regress=529
- mid 1.8805 ≈ 1.8803 — тренд total GMV почти не двигает худший срез
- оба сплита лучше, шаг микро
Repro: h50_lags, arm=lgb_btyd_lags, `workspace/runs/h50_lags/`
Next: лаги канала (H53) сильнее на holdout; не наращивать только total GMV
