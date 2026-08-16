# Cemetery — мёртвые линии (не повторять без нового механизма)

Компактный список. Детали эпох — [`01_foundation.md`](01_foundation.md) … [`04_btyd_ipi.md`](04_btyd_ipi.md). Scorecard — [`../INDEX.md`](../INDEX.md).

## Запрещённые / провальные оси

| Ось | Ids | Почему |
|-----|-----|--------|
| Hurdle / clf×reg | H03 | хуже прямого log1p |
| Post-hoc scale / bucket c | H09, H14, H60 | бьёт нули; RMSLE↑ |
| log1p(y+ε) / transform≠eval | H61 | +0.03… |
| Quantile / mean-matching | H16 | mean↑ RMSLE↑↑ |
| Poisson / Tweedie identity | H18, H38 | ~2.4–2.5 |
| Single-head total y | H33, H37 | две головы обязательны |
| Zero-weight / zero-snap | H12, H40 | holdout или шум |
| Isotonic / fit-калибровка | H44 | сезон не переносится |
| Другой бустер без фич | H08 MLP, H32 Cat, H46 XGB | ≤ шум vs LGB |
| MoE / residual mid-маска | H36, H39 | регресс |
| Extra cutoff / time weights | H22, H43, H56 | не закрыли RMSLE |
| Calendar как промоут | H49, H58 | holdout fail |
| Funnel / channel-BTYD / channel-recency | H47, H51, H55 | хуже H48-стека |
| Dual-channel независимый hurdle | H76 | хуже единого P(y>0) |
| Logit temperature T<1 | H81 | mean_pred↑ RMSLE↑ both |
| Channel balance ratios на H78 | H83 | шум / коллинеарность |
| Multi-depth leaves в hurdle | H86 | primary↑, holdout шум |
| Naive scale / blend | H02, H10 | вырождение или шум |

## Микро-тюны (шум, не линия)

H20 ord_lag · H21 abs loss · H23/H30 leaf · H24 mono · H27 ens+decay · H28 depth7 · H29 zero-hist guard · H34 weekend · H35 last-K · H42 burstiness · H54 blend на BTYD

## ⚠️ не cemetery, но не champion

H01 global scale · H12 zero-w · H41 RFM TE · H49/H58 calendar — primary без holdout-промоута.
