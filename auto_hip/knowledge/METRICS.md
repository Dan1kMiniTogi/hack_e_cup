# METRICS

Источник истины для **смысла** метрик. Числовые пороги и флаги acceptance — в корневом [`config.yaml`](../config.yaml). Не копировать пороги сюда дубликатом, который разъедется с config.

Имена метрик совпадают с `config.metrics`.

### Метрики

| Имя | Направление | Определение |
|-----|-------------|-------------|
| rmsle | ↓ лучше | \(\sqrt{\frac{1}{n}\sum_i(\log(1+y_i)-\log(1+\hat{y}_i))^2}\); \(\hat{y}_i=\max(0,\hat{y}_i)\); \(y_i\) — сумма `gmv` пользователя за 30 дней после cutoff |
| mae_log1p | ↓ лучше | среднее \(\lvert\log(1+y_i)-\log(1+\hat{y}_i)\rvert\); разбор, не primary |
| zero_pred_share | — | доля пользователей с \(\hat{y}_i=0\); диагностика калибровки нулей |
| mean_pred | — | среднее \(\hat{y}\) после клипа |
| mean_true | — | среднее \(y\) на том же сплите |

Primary KPI соревнования — **rmsle**. Сабмит: все клиенты из train (`all_users_predicted`).

### Acceptance (прозой)

- Champion / control: `baselines.*` в config. На старте оба = наивный авторегресс; после первого прогона заполнить `champion_run`.
- Hard-constraint (сразу ❌, если нарушено vs правила config):
  - регресс **rmsle** vs champion на primary, если `no_regression_vs_champion`;
  - отрицательные pred без клипа в артефакте оценки, либо оценка не на полном множестве user_id;
  - dense zero-fill фичевой таблицы как часть treatment.
- Soft progress: улучшение rmsle на primary; срезы; mae_log1p; калибровка mean_pred vs mean_true.
- ✅ — лучше champion по rmsle на primary **и** holdout (если `require_holdout_for_promote`), constraints ок.
- ⚠️ — лучше на primary, holdout не подтверждён или не гонялся.
- ❌ — hard-constraint / чистый regress rmsle без выгоды / сломанный прогон.

### Research buckets

Для регрессии «ошибка» — пользователь, у которого squared log-error \(\bigl(\log(1+y)-\log(1+\hat{y})\bigr)^2\) не ниже квантиля `metrics.error_sq_log_quantile` **на предсказаниях champion** (порог из config). Сравнение множеств treatment vs champion:

- **persist** — в хвосте ошибок и у champion, и у treatment;
- **fixed** — в хвосте у champion, у treatment нет;
- **regress** — не в хвосте у champion, у treatment есть.

Дополнительно смотреть знак ошибки в хвосте: занижение нулей vs переоценка крупных GMV (RMSLE чувствителен к обоим).

### Срезы

`slice_dims` (как в config), считаются **на истории до cutoff**:

- `recency_bucket` — давность последней активности / последнего заказа;
- `hist_gmv_bucket` — накопленный GMV (в т.ч. нулевой);
- `activity_days_bucket` — число дней с записью в parquet;
- `channel_mix` — только Поиск / только Каталог / оба / ни одного флага в истории.
