# H69 — RFM MiniBatchKMeans + kNN peer-норма
Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Peer-статы когорты (k=8) и kNN-соседей (индекс ≤50k, 20 peers) по истории ≤ cutoff на стеке H65.
Метрики:
- Primary: **1.691916** vs H65 1.691493 (+0.00042)
- Holdout: **1.739830** vs H65 1.739622 (+0.00021)
- vs H65 primary: fixed=668, regress=675
Вердикт: отклонить
Почему:
- Оба сплита хуже H65; mean_pred чуть занижен (44.6 vs 45.2) без выигрыша RMSLE.
- В отличие от друга (kNN поверх богатого blend+hurdle), у нас добавление peers на чистый log1p-H65 не сдвинуло mid.
Repro: h69_cohortknn, arm=lgb_h65_cohortknn, `workspace/runs/h69_cohortknn/`
Next: пробовать cohortknn только поверх hurdle/stack, не как соло-фичи на H65.
