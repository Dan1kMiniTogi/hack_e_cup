# 001 — EDA snapshot (sample_fast)

Источник: `data/train.parquet` через Polars lazy scan. **Без** dense calendar.
Выборка пользователей: `user_id % 12 == 0` на cutoff `2026-01-14`.
Naive pred = сумма `gmv` за `[2025-12-16, 2026-01-14]`; y = сумма `gmv` за `[2026-01-15, 2026-02-13]`.
Метрики naive — **только на выборке**, не полный 250k и не лидерборд.

## Global

- rows: `30631006` · users: `250000` · days with rows: `409` · calendar span: `409`
- dates: `2025-01-01` … `2026-02-13` · null cells: `0`
- rows/user mean: `122.52` · dense fill estimate: `102250000` rows

Daily `n_rows`: min `43516`, p50 `69960`, p90 `94669`, max `103617`, mean `74892.4`.

Daily `gmv_sum`: min `374066.47`, p50 `661632.10`, p90 `823997.29`, max `1093028.44`, mean `665285.02`.

Daily active users (unique `user_id` that day): min `43516`, p50 `69960`, p90 `94669`, max `103617`, mean `74892.4`.

First days: 2025-01-01 (rows=43516, gmv=374066.5), 2025-01-02 (rows=52556, gmv=489228.0), 2025-01-03 (rows=53609, gmv=473332.5)

Last days: 2026-02-11 (rows=95601, gmv=721942.5), 2026-02-12 (rows=94450, gmv=757756.4), 2026-02-13 (rows=91293, gmv=750104.8)

## Sample (primary split)

- n_users: `20866` · n_rows in sample: `2563785`
- hist_gmv > 0 quantiles used for buckets: q50 `482.9291`, q90 `2873.2211`
- y=0 share: `0.4627` · y mean `83.8059` · median `7.4907` · p90 `210.6296` · p99 `1016.7949`
- y>0 only (n=11212): mean `155.9663` · median `62.6965` · p90 `356.0574` · p99 `1405.8787`

## Naive champion proxy (sample)

- rmsle: `2.196794`
- mae_log1p: `1.446952`
- zero_pred_share: `0.4340`
- mean_pred: `100.2554` · mean_true: `83.8059`

## Channel GMV (history ≤ cutoff, sample)

- gmv_search share: `0.9281` · gmv_cat share: `0.0719` · hist_gmv_sum `20969481.09`

## Slices

### recency_bucket (days since last activity ≤ cutoff)

| slice | n | share | y_zero_share | mean_y | median_y | mean_pred | zero_pred_share | rmsle |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0_7 | 17212 | 0.8249 | 0.4084 | 95.7532 | 15.0842 | 116.2908 | 0.3686 | 2.2116 |
| 8_30 | 3654 | 0.1751 | 0.7184 | 27.529 | 0.0 | 24.7211 | 0.7422 | 2.1255 |

### hist_gmv_bucket

| slice | n | share | y_zero_share | mean_y | median_y | mean_pred | zero_pred_share | rmsle |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| high | 1800 | 0.0863 | 0.0733 | 402.1126 | 206.1068 | 522.0167 | 0.0533 | 1.9989 |
| low | 9001 | 0.4314 | 0.5792 | 28.9331 | 0.0 | 23.5456 | 0.5302 | 2.2964 |
| mid | 7200 | 0.3451 | 0.2346 | 104.3775 | 43.8988 | 130.6062 | 0.1837 | 2.4454 |
| zero | 2865 | 0.1373 | 0.9145 | 4.519 | 0.0 | 0.0 | 1.0 | 1.0207 |

### activity_days_bucket

| slice | n | share | y_zero_share | mean_y | median_y | mean_pred | zero_pred_share | rmsle |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1_5 | 198 | 0.0095 | 0.8687 | 6.4928 | 0.0 | 9.1166 | 0.9141 | 1.48 |
| 21_60 | 5296 | 0.2538 | 0.6839 | 30.0511 | 0.0 | 32.366 | 0.6596 | 2.1855 |
| 61_plus | 13602 | 0.6519 | 0.3236 | 115.1645 | 27.611 | 138.8926 | 0.289 | 2.2611 |
| 6_20 | 1770 | 0.0848 | 0.8243 | 12.3113 | 0.0 | 16.6643 | 0.8198 | 1.7509 |

### channel_mix

| slice | n | share | y_zero_share | mean_y | median_y | mean_pred | zero_pred_share | rmsle |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| both | 19109 | 0.9158 | 0.4347 | 89.8529 | 11.4694 | 107.3443 | 0.4042 | 2.2193 |
| cat_only | 23 | 0.0011 | 0.7826 | 42.2333 | 0.0 | 22.9109 | 0.6957 | 1.8981 |
| neither | 42 | 0.002 | 0.9762 | 0.1709 | 0.0 | 0.0 | 1.0 | 0.3243 |
| search_only | 1692 | 0.0811 | 0.7618 | 18.1538 | 0.0 | 23.7345 | 0.7535 | 1.9585 |

## Caveats

- Hash sample, not a probability sample of the public LB 20%.
- Baseline notebook naive submit uses this last-30d GMV as predict for the *test* horizon, not scored here.
- No user_id listed.
