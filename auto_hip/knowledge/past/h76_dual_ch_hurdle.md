# H76 — Dual-channel независимый hurdle
Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: Отдельные P(y_search>0)/μ_s и P(y_cat>0)/μ_c с суммой двух logmix-сборок.
Метрики:
- Primary: **1.690824** vs H73 1.690065 (+0.000759)
- Holdout: **1.739599** vs H73 1.739049 (+0.000550)
Вердикт: отклонить
Почему:
- Раздельные классификаторы хуже единого P(y>0) на обоих сплитах.
- Канальная асимметрия уже учтена двумя регрессорами; двойной hurdle добавляет шум.
Repro: h76_dual_ch_hurdle, arm=dual_channel_hurdle, `workspace/runs/h76_dual_ch_hurdle/`
Next: не refine dual-channel без нового guard; линия cemetery-adjacent.
