# H62 — H59 + nested GMV лаги
Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: К фичам H59 (IPI + channel lags + BTYD) добавлены непересекающиеся total-GMV лаги 30/60/90 (H50) и отношения лагов.
Метрики: primary 1.692303 vs H59 1.691937; holdout 1.740054 vs 1.739946
Вердикт: отклонить
Почему:
- Регрессия на обоих сплитах из-за сильной коллинеарности `gmv_lag*` с суммой канальных лагов `gmv_search_lag*` + `gmv_cat_lag*`.
- Дополнительные сплиты по избыточным колонкам ухудшили обобщающую способность.
Repro: h62_nested_lags, arm=lgb_h59_nested_lags, `workspace/runs/h62_nested_lags/`
Next: избегать дублирования канальных и тотальных оконных лагов.
