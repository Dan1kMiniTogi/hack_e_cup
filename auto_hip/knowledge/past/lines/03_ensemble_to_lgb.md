# Линия: ensemble → LightGBM (H20–H46)

Champion-path: H19 → **H25** decay → **H26** 3-seed HGB → **H31** LightGBM → **H45** LGB+HGB mix (~1.6961). Дальше скачок дал уже BTYD (см. [`04_btyd_ipi.md`](04_btyd_ipi.md)).

## Keep

- **H25 ✅:** recency-decay GMV-фичи — полезный слой поверх order.
- **H26 ✅:** среднее трёх seed HGB — стабилизация без новых фич.
- **H31 ✅:** LightGBM leaf-wise, те же BASE+GAP+RATIO+ORDER, две головы, 3-seed. Лучше sklearn HGB на обоих сплитах. Repro: `workspace/runs/h31_lgb/`.
- **H45 ✅:** 0.5 LGB + 0.5 HGB на одних фичах — микро, но оба сплита; ошибки leaf-/level-wise частично ортогональны. Repro: `workspace/runs/h45_blend/`.
- **H41 ⚠️:** OOF RFM TE ≈ H31 primary, holdout хуже — не промоутить.
- Урок: две головы обязательны даже на богатых фичах; смена бустера без новых фич почти не даёт.

## Dead here (сжато)

- Микро-тюны HGB без механизма: **H23** leaf20, **H28** depth7, **H30** leaf50, **H27** ens+decay.
- **H20** ord_lag, **H22** 4-й cutoff, **H24** mono GMV, **H29** zero-hist guard, **H34** weekend share, **H35** last-K (коллинеарно gap/recency), **H36** mid residual на маске среза, **H42** burstiness (holdout↑ primary↓), **H43** time-decay weights.
- Другие бустеры/loss: **H32** CatBoost, **H46** XGBoost, **H38** Tweedie (~2.5), **H21** abs loss.
- Архитектура: **H33/H37** single-head total y, **H39** MoE по hist_gmv, **H40** zero-snap τ.
- Калибровка: **H44** isotonic log (как H09/H14 — ломает сезон).
