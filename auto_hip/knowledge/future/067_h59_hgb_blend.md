# 067 — Бленд H59 (LightGBM) + H48 (HGB) в log-пространстве
 
**Тип:** pivot
**Линия:** H59 / Model Diversity & Ensembling
**Исследование:** [`../investigate/006_h59_next.md`](../investigate/006_h59_next.md) — H45 показал, что комбинация алгоритмов (HGB + LGB) дает синергию за счет разницы в построении гистограммных сплитов.

**Идея:**
Обучаем 3-seed LightGBM H59 (IPI + chlag + BTYD) и 3-seed HistGradientBoosting H48/H59. Ансамблируем их усреднением в исходном пространстве (80% LGB + 20% HGB) или лог-пространстве `exp(0.8*log1p(p_lgb) + 0.2*log1p(p_hgb)) - 1`.

**Почему:**
LightGBM склонен к более агрессивным сплитам на непрерывных фичах IPI/BTYD, в то время как HGB из scikit-learn действует консервативнее, сглаживая экстремальные всплески на хвосте распределения.

**Acceptance:** лучше H59 RMSLE на primary и holdout; non_negative_preds.
