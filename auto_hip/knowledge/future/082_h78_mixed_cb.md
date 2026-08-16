# 082 — H78 + mixed LGBM/CatBoost hurdle bag

**Тип:** explore
**Линия:** H78 / Heterogeneous tree hurdle
**Исследование:** [`../investigate/009_h78_next.md`](../investigate/009_h78_next.md) — mid hist_gmv и дисперсия hurdle без смены весов стека

**Идея:**
Baseline H78 (0.30 H65 LGB + 0.70 hurdle 3-seed LGB, 1.689400 / 1.738825). Arm `stack_h65_hurdle3_mixed`: голова H65 без изменений (3-seed LGB reg), а hurdle-bag заменяется на 2 сида LightGBM + 1 член CatBoost (clf Logloss + два log1p-регрессора на y>0). Усреднение p и μ как в H78, сборка c=0 без изменений, веса 0.30/0.70 фиксированы. Ожидаемый эффект — снижение дисперсии на mid hist_gmv за счёт разнообразия leaf-wise vs oblivious trees.

**Почему:**
CatBoost соло (H32) был близок к LGB на H26-стеке, но не стекался в hurdle. H79 показал, что крутить веса бесполезно; нужен новый механизм внутри hurdle. Риск — CatBoost переобучит holdout; один фиксированный член без сетки гиперпараметров и без смены весов ограничивает риск.

**Acceptance:** лучше H78 на primary и holdout.

**Избегать:** dual-channel, сетка весов, XGB/MLP без новых фич.
