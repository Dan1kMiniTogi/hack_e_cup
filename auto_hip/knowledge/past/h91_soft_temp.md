# H91 — Мягкая температура логитов T=1.05 на p hurdle
Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Архитектура H87 (intent только в clf), на усреднённом p применяется σ(logit(p)/1.05) до сборки expm1(p·log1p(μ)); стек 0.30/0.70, c=0.
Метрики:
- Primary: **1.688156** vs H87 1.689383 (−0.001227)
- Holdout: **1.738581** vs H87 1.738805 (−0.000224)
Вердикт: принять как **нового чемпиона (H91)**
Почему:
- persist=24510, fixed=490, regress=142 на primary; holdout persist=24546, fixed=454, regress=120
- FA в хвосте Q90: 13858→13663 (primary), 11245→11066 (holdout); missed buyers ≈ без изменений (~5500)
- mean_pred↓ (45.50→44.84 / 45.71→45.09); corr с H87 ≈0.99997 — тот же ранг, мягче уверенность clf. T<1 (H81) был противоположным знаком и ❌
Repro: h91_soft_temp, arm=stack_h87_soft_temp, `workspace/runs/h91_soft_temp/`
Next: сабмит H91; 4-bag CB и mixed-3 на этой калибровке; не сетка T и не T<1
