# Линия: HGB features (H06–H19)

Champion-path: H05 → **H07** gaps → **H11** ratios → **H13** deeper → **H15** L2 → **H17** order recency → **H19** more iter (~1.6967). Шаги ≤0.001.

## Keep

- **Gaps** полезны на *канальном* стеке (H07), не на едином GMV (H06).
- **Ratios** (intensity/conversion) — микро-сдвиг mid без ломки нулей (H11).
- **Ёмкость:** depth 8 + больше итераций + слабая L2 стабилизируют (H13/H15/H19).
- **Order recency** (`recency_order_days` по последнему `to_ord>0`) отделяет поиск без покупки (H17) — ось вошла в дальнейший стек.
- **H12 ⚠️:** `sample_weight` на y=0 даёт primary ↓, holdout ↑ — не промоутить без сезонного guard.

## Dead here

- **H06** — gaps на single-head H04: хуже H05.
- **H08** — MLP CPU: хуже HGB, сломан mean на holdout.
- **H09 / H14** — post-hoc `c` / bucket-множители: up-scale бьёт нули сильнее, чем помогает хвосту.
- **H10** — blend с naive: выродился в α=1 (champion).
- **H16** — quantile 0.6: mean ближе к true, RMSLE сильно хуже.
- **H18** — Poisson identity: катастрофа (~2.5).
