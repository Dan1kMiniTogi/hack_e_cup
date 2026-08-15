# H31 — LightGBM две головы

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: те же фичи H26 (BASE+GAP+RATIO+ORDER), две log1p-головы search/cat, среднее трёх seed; бустер LightGBM leaf-wise (depth 8, 320 раундов, min_data_in_leaf 30, L2).
Метрики: primary rmsle 1.69611 vs H26 1.69651; holdout 1.74146 vs 1.74172; mean_pred primary 45.89 vs true 84.03
Вердикт: принять, новый champion
Почему:
- persist=24284, fixed=716, regress=767 vs H26 на primary; holdout persist=24347, fixed=653, regress=643
- mid по-прежнему топ rmsle (1.8846); recency 0–7 несёт массу ошибки
- leaf-wise чуть лучше sklearn HGB на обоих сплитах без densify и без banned loss
Repro: run_id=h31_lgb, arm=lgb_channel_ens, champion-run=h26_ens, `workspace/runs/h31_lgb/`
Next: не крутить sklearn HGB depth/leaf на той же таблице; проверить single-head и last-K vs новый champion
