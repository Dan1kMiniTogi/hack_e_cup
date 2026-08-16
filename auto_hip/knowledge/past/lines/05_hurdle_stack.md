# Линия: Hurdle-logmix и стек H65 (H70–H73)

Champion-path: H65 → **H70** hurdle-logmix c=0 (−0.00131) → **H73** stack 0.30 H65 + 0.70 hurdle (−0.00012). Дальше H78 3-seed hurdle.

## Keep

- **H70 ✅:** P(y>0) + channel log1p на покупателях, сборка expm1(p·log1p(μ)), c=0. Primary 1.690181 / holdout 1.739575.
- **H73 ✅:** 0.30 H65 3-seed + 0.70 hurdle. 1.690065 / 1.739049. Dual в стеке вреден.

## Dead here

- **H71 ❌** dual-capacity 47/95 соло.
- **H72 ❌** 0.70 dual + 0.30 hurdle (веса в сторону dual).
