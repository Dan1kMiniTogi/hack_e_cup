# H41 — OOF RFM target encoding

Статус: ⚠️ | Primary: local_val_cutoff_2026-01-14 | Holdout: holdout_cutoff_2025-12-15 | N: 250000
Идея: фича mean y по ячейкам hist×recency (OOF по cutoff) + LGB две головы.
Метрики: primary 1.696112 vs H31 1.696113 (чуть лучше); holdout 1.74162 vs 1.74146 (хуже)
Вердикт: не промоутить; holdout не подтвердил
Почему:
- persist=24516, fixed=484, regress=476 vs H31 — шум
- ячейки не дали скачка; сезон holdout ломает TE
Repro: h41_rfm, arm=rfm_te
Next: не TE с fit-mean_true
