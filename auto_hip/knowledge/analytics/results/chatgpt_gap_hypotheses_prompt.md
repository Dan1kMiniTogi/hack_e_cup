# Промпт для браузерного ChatGPT (разрыв с LB, после H26)

Скопируй **всё между** линиями `===== BEGIN PROMPT =====` и `===== END PROMPT =====` в чат. Ответ принеси обратно в Cursor. Этот чат **не** кладёт гипотезы в `future/`.

===== BEGIN PROMPT =====

Ты помогаешь с гипотезами для табличного хакатона. Нужны формулировки механизмов под метрику RMSLE, не код и не обучение моделей. Не выдумывай статистики: опирайся только на цифры ниже. Если чего-то нет в тексте — напиши «неизвестно», не оценивай «на глаз».

## Задача

E-CUP 2026, задача 3. Предсказать суммарный GMV пользователя в Поиске и Каталоге за следующие 30 дней (прокси LTV «здесь и сейчас»).

- История: 2025-01-01 … 2026-02-13, train.parquet, 30 631 006 строк, 250 000 user_id, 409 календарных дней с записями.
- Тест соревнования: сумма GMV за 2026-02-14 … 2026-03-15. Сабмит: CSV `user_id, predict` на всех 250k. Отрицательные predict клипаются в 0.
- Метрика (↓ лучше): RMSLE = sqrt(mean( (log1p(y) − log1p(max(0, yhat)))^2 )).
- Public/private лидерборд 20/80 по клиентам (50k / 200k). Офлайн-сплит ≠ лидерборд.
- Строка = один день активности. Nulls в колонках: 0. Среднее ~122.5 строки на пользователя. Не densify календарь нулями (оценка dense fill ≈ 102.25M строк).
- Запрещено правила «если user_id = …». Фичи только из дат ≤ cutoff.

Колонки дня: event_date, user_id, search, cat, has_search_to_cart, has_search_to_ord, has_cat_to_cart, has_cat_to_ord, search_to_cart, search_to_ord, cat_to_cart, cat_to_ord, gmv_search, gmv_cat, to_cart, to_ord, gmv, searches.

## Как оцениваем офлайн

- primary: cutoff 2026-01-14, y = сумма gmv за 2026-01-15 … 2026-02-13. mean_true = 84.034, y_zero = 0.4593, n = 250000.
- holdout (не для подгонки): cutoff 2025-12-15, y = 2025-12-16 … 2026-01-14. mean_true = 101.426, y_zero = 0.4369.
- Fit модели: три якоря cutoff 2025-10-18, 2025-11-01, 2025-11-15 (лейблы holdout/primary не в fit).
- Дня нет в parquet → вклад в сумму GMV = 0.
- Constraints: pred ≥ 0; все 250k; без dense zero-fill. Регресс RMSLE vs champion на primary — сразу отказ; для промоута нужен holdout не хуже.

## Разрыв с лидербордом (осторожно)

- Офлайн champion RMSLE primary **1.696510**, holdout **1.741716**.
- Первое место public LB: **1.6466974773**. Своего public score нет (сабмит ещё не залит).
- Public — 50k клиентов, не тот же split, что cutoff 2026-01-14. Не предлагай «выбить −0.05 на primary тем же HGB». После перехода на HGB (H04 1.708) весь путь до H26 дал только **−0.01175**. Гипотезы должны бить в наблюдаемые дыры ниже, а не в магическое число 1.6467.

## Champion H26 — архитектура

Arm `channel_ens`: среднее трёх независимых моделей (random_state 42, 7, 99). Каждая: две головы HistGradientBoostingRegressor sklearn, target log1p(y_search) и log1p(y_cat), pred = clip(expm1(s),0) + clip(expm1(c),0). Гиперпараметры: max_depth=8, max_iter=320, learning_rate=0.04, min_samples_leaf=30, l2_regularization=1.0, loss=squared_error на log1p.

Фичи (без densify):

- BASE: gmv_sum_{7,14,30,60,90}d; gmv_search_sum_{7,30,90}d; gmv_cat_sum_{7,30,90}d; searches_sum_{7,30,90}d; to_ord_sum_{7,30,90}d; to_cart_sum_{7,30}d; active_days_{7,14,30,90}d; activity_days; hist_gmv / hist_gmv_search / hist_gmv_cat; hist_orders; hist_searches; any_search; any_cat; recency_days (null→9999).
- GAP: last_gap, mean_gap, max_gap, n_gaps_gt_7, n_gaps_gt_14 (разности дат существующих строк).
- RATIO: intensity_30d/90d = gmv_sum / (active_days+1); ord_rate_30d, cart_rate_30d; search_gmv_share_30d; gmv_per_ord_90d.
- ORDER: recency_order_days — дни от cutoff до последней строки с to_ord>0 (null→9999).

H25 добавляла decay_gmv30 = gmv_sum_30d/(1+recency); на одном дереве чуть лучше H19, в 3-seed (H27) уже нет.

Калибровка H26 primary: mean_pred=45.835 vs mean_true=84.034 (ratio 0.545); holdout mean_pred=45.561 vs 101.426 (ratio 0.449). zero_pred_share ≈ 0.00004 при y_zero 0.46. corr(pred,y)=0.496. mae_log1p primary 1.3477.

## Scorecard: что сработало и что нет

Скачок: naive 2.195 → H04 HGB log1p 1.708 (−0.487). Дальше микро:

- H05 две головы search+cat: 1.6993
- H07 +gaps: 1.6987
- H11 +ratios: 1.6981
- H13 depth8/220/lr0.05: 1.6976
- H15 +L2: 1.6975
- H17 +order recency: 1.6970
- H19 max_iter 320 lr 0.04: 1.6967
- H25 decay (не champ): 1.6966
- H26 3-seed: 1.6965 / holdout 1.7417 — **champion**

Не предлагать снова (проверено, вред или ноль):

- hurdle P(y>0)*E[y|y>0] (H03)
- маленький MLP CPU (H08, holdout mean_pred 798)
- Poisson identity (H18, RMSLE 2.53)
- quantile 0.6 (H16, 1.90)
- MAE/absolute_error на log1p (H21, 1.81)
- глобальный или bucket множитель c после модели (H09 c=1.05, H14 mid/high c=1.1)
- mix с naive last-30d (H10, alpha=1)
- sample_weight на y=0 (H12 primary 1.690, holdout 1.782)
- четвёртый ранний fit-якорь 2025-10-04 (H22, holdout лучше, primary хуже)
- ord_lag = recency_order − recency (H20)
- min_samples_leaf=20 (H23), monotonic_cst на GMV (H24), ens+decay (H27), depth=7 (H28)
- densify календарь; hardcode user_id; подгонка c на primary labels

Gaps на едином GMV (H06) хуже канальных голов. Naive scale c=0.4 (H01) лучше naive, но далеко от HGB.

## Deep EDA H26, полный 250k (не hash-выборка)

Масса squared-log-error (SSE), не «rmsle среза»:

Primary:

- **52.34% SSE на y=0** (n=114835, 45.93% пользователей). На нулях mean_pred=8.25, rmsle_y0=1.8109, log_bias=+1.475. Модель ставит мелкий плюс мёртвым.
- y>0: 47.66% SSE. Квинтили y>0: q1 mean_y 10 pred 22 (переоценка); q5 mean_y 541 pred 201 (ratio 0.373, rmsle 2.05, 15.8% SSE).
- hist_gmv mid: 36.3% людей, **44.8% SSE**, rmsle 1.885, ratio 0.463. low: 38.6% людей, 39.7% SSE. high только 10.4% SSE при rmsle 1.613. hist_gmv=zero почти здоров (5.0% SSE, rmsle 1.033).
- recency 0–7 дней: 82.5% людей и **84.5% SSE**. Бакетов 31+ / never на этих cutoff нет (все 250k активны за 30д? нет: recency только 0_7 и 8_30).
- activity 61+: 65.5% людей, 69.6% SSE.
- channel both: 91.8% людей, 93.8% SSE. cat_share_of_y = 0.0668; y_cat zero 0.923. Pred — сумма голов, отдельно y_cat не калиброван (если мерить total pred vs y_cat, rmsle 2.79 — это не метрика модели, только напоминание что cat маленький).
- order recency 8–30д: 29.4% людей, **36.7% SSE**, rmsle 1.897, ratio 0.422. 31–90: 18.1% людей, 22.0% SSE, rmsle 1.873, ratio 0.196. never_ord = hist_gmv zero.

Калибровка по децилям pred (primary): везде mean_pred < mean_y; худший rmsle в средних децилях d5–d7 (~2.02). Верхний дециль pred: mean_y 378 vs pred 290, rmsle 1.31 (лучше). По децилям истинного y: низкие y переоценены (y_d1 ratio 3.34), хвост недооценён (y_d10 mean_y 814 pred 273, rmsle 2.22).

Хвост q90 sq-log (n=25000): 56.3% из них y=0; mean_y 152 vs mean_pred 32. Не только «большие GMV».

Spearman фича vs log_bias (log1p(pred)−log1p(y)): все |ρ| < 0.08. Нет одной линейной дыры в текущих агрегатах. Топ: gmv_sum_90d −0.056, to_ord_sum_30d −0.056, mean_gap +0.051.

Holdout vs primary (сдвиг сезона):

- mean_true 101.4 vs 84.0; дневной GMV в окне holdout-target 845216 vs primary-target 700284 (те же 30 календарных дней, разные месяцы). Январь–середина февраля тише, чем середина декабря–середина января.
- SSE share y=0 на holdout 44.5% (не 52%). mean_log_bias holdout +0.064 vs primary +0.257.
- Тест 14.02–15.03: лейблов нет. last 30d до теста = primary-target (уже более тихое окно). Неизвестно, будет ли март ближе к 700k/день или к 845k.

## Что сдать

Ровно **8 гипотез на русском: 2 refine, 3 pivot, 3 explore**. Не делай все про «ещё чуть HGB / ещё один seed / ещё одна ratio». Каждая опирается на конкретную цифру выше. Поля Идея и Почему — связные абзацы по 3–5 предложений, не телеграф. Объём каждой ≤350 слов.

Типы:

- refine — тот же механизм H26, 1–2 параметра или узкий guard (не повтор banned scale/leaf/depth7).
- pivot — тот же KPI, другой механизм (другая табличная модель/loss/целевая декомпозиция, не hurdle/poisson/quantile/MAE как уже ломали).
- explore — другая ось данных: сезонность окон, last-K событий без densify, вероятность покупки иначе чем hurdle, срез mid/order 8–30, и т.п.

Шаблон:

# NNN — короткое имя
**Тип:** refine | pivot | explore
**Линия:** H26 / new
**Идея:** от какого baseline; что меняется; при каком условии срабатывает; что не меняем (clip ≥0, все user_id, без densify, без hardcode id). Ожидаемый эффект на RMSLE — одно предложение.
**Почему:** причинно-следственная цепочка из цифр; почему предыдущие попытки не закрыли дыру; главный риск регресса RMSLE и как его ограничиваем.
**Acceptance:** лучше H26 RMSLE на primary и на holdout.

Можно предлагать: LightGBM/CatBoost того же табличного класса; last-K событий / gap-последовательность без explode календаря; сезонность/сдвиг уровня окна; аккуратная работа с y=0 если не повтор H03/H12; срез mid hist_gmv или order-recency 8–30.

Не предлагай: тяжёлые нейронки, трансформеры, токенизацию рядов в BERT/LLM, GPU-DL, «просто MLP побольше», LSTM/GRU как главный путь; densify; golden user_id; оптимизировать MAE/RMSE вместо RMSLE как primary; повтор banned-линий списком выше.

===== END PROMPT =====

После ответа ChatGPT вставь его в чат Cursor. Дальше разберём, что годится в investigate/future.
