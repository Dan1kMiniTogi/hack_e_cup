# Линия: foundation (H00–H05)

Champion-path: H00 naive → **H04** HGB log1p (−0.487) → **H05** dual head (−0.009).

## Keep

- **H00 control:** last-30d GMV naive, primary ~2.195 / holdout ~2.214.
- **H04 ✅:** HistGradientBoosting на `log1p(y)` по оконным/lifetime агрегатам; `pred=expm1` clip≥0. Главный скачок метрики (−0.487). mean_pred ≪ mean_true — нормально для RMSLE. Repro: `workspace/runs/h04_hgb`.
- **H05 ✅:** две головы `y_search` + `y_cat`, сумма clip≥0. Канальная декомпозиция лучше единого GMV (−0.009). Repro: channel_sum.
- **H01 ⚠️:** глобальный `c * naive` (c=0.4) лучше naive, но слабее H04; не champion.
- Урок: прямой log1p-бустинг бьёт naive/scale; mean-matching не KPI.

## Dead here

- **H02** — scale high-GMV naive: механизм всё ещё naive, табличный champion уже закрыл хвост.
- **H03** — hurdle clf×reg: двухэтапность хуже прямого log1p; массовый regress vs H04.
