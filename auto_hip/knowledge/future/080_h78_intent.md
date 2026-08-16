# 080 — H78 + intent dynamics только в hurdle 3-seed

**Тип:** explore
**Линия:** H78 / Intent on stacked hurdle3
**Исследование:** [`../investigate/008_h73_next.md`](../investigate/008_h73_next.md) — primary-сигнал H77 перенести на holdout-safe чемпиона

**Идея:**
Baseline H78 (0.30 H65 + 0.70 hurdle3seed, 1.689400 / 1.738825). H77 intent дал primary 1.689251 при худшем holdout на соло-hurdle. Arm `stack_h65_hurdle3_intent`: тот же стек весов 0.30/0.70, H65-голова без изменений, а в hurdle 3-seed добавляем INTENT_DYNAMICS_FEATURES. Формула c=0 без изменений. Ожидаемый эффект — mid/primary выигрыш H77 при holdout-страховке H78.

**Почему:**
Intent на голом hurdle не держал holdout; стек H65 historically стабилизирует holdout (H73/H78). Риск — коллинеарность и holdout регресс; если holdout > H78 → ❌.

**Acceptance:** лучше H78 на primary и holdout.

**Избегать:** dual-channel, сетка весов, knn solo.
