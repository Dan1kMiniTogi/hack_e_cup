# H48 — BTYD-фичи в канальные головы

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: RFM/AOV с дней `to_ord>0` плюс p_alive / E[purch 30d] / E[gmv] (моменты BG-NBD + эмпирика); те же две LGB log1p-головы 3-seed; pred = сумма clip(expm1), не hurdle.
Метрики: primary 1.693588 vs H45 1.696101; holdout 1.740301 vs 1.74135
Вердикт: принять, новый champion
Почему:
- persist=23342, fixed=1658, regress=1601 vs H45 на primary; holdout persist=23454, fixed=1546, regress=1607 — первый обмен хвоста не в шуме 300
- mid 1.8803 vs 1.8846; recency 0_7 1.7131 vs 1.7164; процесс покупок, не оконные суммы
- не clf×reg (H03) и не zero-weight (H12); mean_pred 45.35 vs true 84 — RMSLE, не калибровка среднего
Repro: h48_btyd, arm=lgb_btyd, `workspace/runs/h48_btyd/`
Next: календарь целевого окна и disjoint 30d лаги vs H48; не funnel
