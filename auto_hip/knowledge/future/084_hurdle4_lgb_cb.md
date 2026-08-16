# 084 — Hurdle bag 3×LGB + 1×CatBoost на стеке H78

**Тип:** explore
**Линия:** H82 / 4-member heterogeneous hurdle
**Исследование:** [`../investigate/010_h82_holdout.md`](../investigate/010_h82_holdout.md) — удержать holdout H82, вернуть primary к H78

**Идея:**
Baseline H78 (hurdle = 3 LGB seeds 42/43/44). H82 заменил один LGB на CatBoost и улучшил holdout (1.738559), но primary вырос до 1.689586. Arm `stack_h65_hurdle4_mixed`: hurdle-bag = LGB(42)+LGB(43)+LGB(44)+CatBoost(45) — четыре члена, равное усреднение p и μ, сборка c=0; H65 3-seed и веса 0.30/0.70 без изменений. Ожидаемый эффект — CB даёт holdout-стабильность H82, а третий LGB-сид возвращает primary ближе к H78.

**Почему:**
H82 потерял один LGB-голос; 4-member сохраняет полный LGB-бэггинг H78 и добавляет разнообразие CB. Риск — дольше train и лёгкий primary шум; фиксированные сиды без сетки весов.

**Acceptance:** лучше H78 на primary и holdout (цель: holdout ≤ 1.738559 и primary ≤ 1.689400).

**Избегать:** замена всех LGB на CB, dual-channel, T<1.
