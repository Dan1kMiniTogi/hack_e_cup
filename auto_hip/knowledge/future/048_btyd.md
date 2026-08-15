# 048 — BTYD-фичи в канальные головы

**Тип:** pivot
**Линия:** new / BTYD-as-features
**Исследование:** [`../investigate/004_h45_blocks.md`](../investigate/004_h45_blocks.md) — 52% SSE на y=0 и отсутствие P(alive) без hurdle

**Идея:**
Baseline — H31/H45: две LightGBM log1p-головы на `H26_COLS`, pred = сумма clip(expm1). Hurdle clf×reg (H03), вес нулей (H12), snap (H40) и hard-zero hist_gmv (H29) либо ломают holdout, либо не бьют RMSLE, потому что доля y=0 сезонная (holdout 43.7% vs primary 45.9%). По sparse дням с `to_ord>0` считаем recency/frequency/T до cutoff и оцениваем BG-NBD: `p_alive` и E[покупок на 30d]; AOV — среднее gmv/заказ на тех же sparse строках (Gamma-Gamma или простой mean). Эти три числа подаём как фичи в те же две головы; итоговый pred по-прежнему clip-сумма голов, не сырой BTYD. Ожидаемый эффект: меньше мелкого плюса на «мёртвых» без split-specific порога, ниже RMSLE на y=0 при удержании holdout.

**Почему:**
На primary 52.3% SSE сидит на y=0 при mean_pred≈8.24 и zero_pred≈0 ([`../analytics/results/004_h45_debug.md`](../analytics/results/004_h45_debug.md)); постановка соревнования прямо предлагает BTYD, и это не классификатор×регрессор H03. Пользователь×три cutoff сейчас iid, дерево не моделирует процесс покупок. Риск — смещённая частота и регресс mid/high; поэтому BTYD только как признаки, без замены RMSLE-loss и без умножения P(y>0)×E[y|y>0]. Если BG-NBD численно нестабилен на коротких рядах — те же recency/frequency/T и эмпирический P(повтор за 30d) по walk-forward якорям, всё ещё не hurdle.

**Acceptance:** лучше H45 RMSLE на primary и holdout; pred≥0; все 250k; без densify.

**Избегать:** hurdle clf×reg, zero-weight, zero-snap, hard-zero hist_gmv, poisson/tweedie identity, калибровка c
