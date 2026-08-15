# H47 — Канальная воронка в окна

Статус: ❌ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: к H26_COLS добавлены оконные суммы search/cat to_ord/to_cart (7/30/90) и lifetime has_*; две LGB log1p-головы 3-seed как H31.
Метрики: primary 1.696525 vs H45 1.696101; holdout 1.741538 vs 1.74135
Вердикт: отклонить
Почему:
- persist=24263, fixed=737, regress=790 vs H45 на primary; holdout persist=24304, fixed=696, regress=749
- mid 1.8853 ≈ H45 1.8846; воронка коллинеарна `to_ord`/`to_cart`, линейный Spearman уже был ~0.05
- densify не использовался
Repro: h47_funnel, arm=lgb_funnel, `workspace/runs/h47_funnel/`
Next: не наращивать funnel-окна; ось BTYD (H48) живая
