# H45 — Смесь LightGBM и sklearn HGB

Статус: ✅ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: 0.5 × (LGB 3-seed две головы) + 0.5 × (HGB 3-seed две головы), одни фичи H26.
Метрики: primary 1.696101 vs H31 1.696113; holdout 1.74135 vs 1.74146
Вердикт: принять, новый champion
Почему:
- persist=24642, fixed=358, regress=364 vs H31; holdout persist=24651, fixed=349, regress=310
- ошибки leaf-wise и level-wise частично ортогональны; скачок микро, но оба сплита лучше
Repro: h45_blend, arm=blend_lgb_hgb, `workspace/runs/h45_blend/`
Next: стоп по запросу; офлайн плато ~1.696, public 1.65 скорее другой split/модель вне этой таблицы
