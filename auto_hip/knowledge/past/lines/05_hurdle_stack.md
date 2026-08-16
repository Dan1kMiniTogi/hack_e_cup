# Линия: hurdle-logmix и стек H65 (H70–H77)

Champion-path: H65 → **H70** hurdle-logmix c=0 (−0.00131) → **H73** stack 0.30 H65 + 0.70 hurdle (−0.00012) → H78 3-seed. H75 свёрнут сюда.

## Keep

- **H70 ✅:** P(y>0) + channel log1p на покупателях, сборка `expm1(p·log1p(μ))`, c=0. Primary 1.690181 / holdout 1.739575. Закрывает banned `hurdle_zero_positive` (H03 = p×μ).
- **H73 ✅:** 0.30 H65 3-seed + 0.70 hurdle. 1.690065 / 1.739049. Dual в стеке вреден — H65-голова полезна.
- **H75 ⚠️:** соло hurdle 3-seed. Лучший primary эпохи **1.689143**, holdout 1.739171 vs H73 +0.00012. Стал hurdle-головой H78.

## Dead / ⚠️ folded

- **H71 ❌** dual-capacity 47/95 соло.
- **H72 ❌** 0.70 dual + 0.30 hurdle (веса в сторону dual).
- **H74 ⚠️** cohortknn на hurdle: primary 1.689840, holdout хуже H70/H73. Не solo-promote knn.
- **H76 ❌** dual-channel независимый hurdle (два P(y_ch>0)). Хуже единого P(y>0).
- **H77 ⚠️** intent в clf+μ соло-hurdle: primary 1.689251, holdout хуже. Дальше H80/H87 (intent только clf).
