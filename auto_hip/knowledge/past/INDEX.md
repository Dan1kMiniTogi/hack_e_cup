# INDEX — scorecard гипотез

**Champion: H70** `hurdle_logmix_c0` · primary **1.690181** · holdout **1.739575**. Предыдущий H65 reg 1.691493 / 1.739622.

Синтез: [`SYNTHESIS.md`](SYNTHESIS.md). Линии: [`lines/`](lines/). Активные отчёты (~15): `h58_*.md`…`h72_*.md` в корне. Аудит H45: [`../analytics/results/004_h45_debug.md`](../analytics/results/004_h45_debug.md).

Почти весь выигрыш — H04 (−0.487) и две головы H05 (−0.009). H48 BTYD −0.0025 vs H45; H52 IPI −0.0010 vs H48; H59 IPI+chlag −0.0007 vs H52; H65 reg −0.00044 vs H59; **H70 hurdle-logmix c=0 −0.00131 vs H65**.

| id | status | type | primary metrics | vs champion | note |
|----|--------|------|-----------------|-------------|------|
| H00 | control | naive | rmsle 2.195 | — | last-30d GMV, full 250k |
| H01 | ⚠️ | refine | rmsle 2.037 | vs H00 better both | c=0.4, не champion |
| H02 | ❌ | refine | rmsle 2.187 | хуже H05 | naive high-scale |
| H03 | ❌ | pivot | rmsle 2.070 | хуже H04 | hurdle |
| H04 | ✅ | pivot | rmsle 1.708 | vs H00 holdout 1.746 vs 2.214 | HGB log1p |
| H05 | ✅ | explore | rmsle 1.699 | vs H04 both better | channel_sum |
| H06 | ❌ | explore | rmsle 1.707 | хуже H05 | HGB+gaps |
| H07 | ✅ | refine | rmsle 1.6987 | vs H05 both better | channel+gaps |
| H08 | ❌ | explore | rmsle 1.714 | хуже H05 | MLP CPU |
| H09 | ❌ | refine | rmsle 1.705 | хуже H07 | c=1.05 |
| H10 | ❌ | pivot | rmsle 1.699 | = H07 | alpha=1 |
| H11 | ✅ | explore | rmsle 1.6981 | vs H07 both better | ratios |
| H12 | ⚠️ | pivot | rmsle 1.690 | holdout 1.782 worse | zero-weight |
| H13 | ✅ | explore | rmsle 1.6976 | vs H11 both better | deeper |
| H14 | ❌ | refine | rmsle 1.709 | хуже H11 | bucket c |
| H15 | ✅ | refine | rmsle 1.6975 | vs H13 both better | L2 |
| H16 | ❌ | pivot | rmsle 1.899 | хуже H13 | quantile 0.6 |
| H17 | ✅ | explore | rmsle 1.6970 | vs H15 both better | order recency |
| H18 | ❌ | pivot | rmsle 2.527 | хуже H15 | poisson |
| H19 | ✅ | refine | rmsle 1.6967 | vs H17 both better | more iter |
| H20 | ❌ | explore | rmsle 1.6974 | хуже H17 primary | ord_lag |
| H21 | ❌ | pivot | rmsle 1.806 | хуже H19 | abs loss |
| H22 | ❌ | explore | rmsle 1.6974 | holdout better, primary worse | extra cutoff |
| H23 | ❌ | refine | rmsle 1.6969 | holdout better | leaf 20 |
| H24 | ❌ | explore | rmsle 1.6969 | holdout better | monotonic GMV |
| H25 | ✅ | explore | rmsle 1.6966 | vs H19 both | decay GMV |
| H26 | ✅ | pivot | rmsle 1.6965 | vs H19 both | 3-seed HGB |
| H27 | ❌ | explore | rmsle 1.6966 | хуже H26 | ens+decay |
| H28 | ❌ | pivot | rmsle 1.6965 | хуже H26 | depth 7 |
| H29 | ❌ | refine | rmsle 1.69963 | хуже H31 | zero hist guard |
| H30 | ❌ | refine | rmsle 1.69650 | хуже H31 | leaf 50 |
| H31 | ✅ | pivot | rmsle 1.69611 | vs H26 both better | LightGBM 3-seed |
| H32 | ❌ | pivot | rmsle 1.69627 | хуже H31 | CatBoost |
| H33 | ❌ | pivot | rmsle 1.70543 | хуже H31 | single-head total y |
| H34 | ❌ | explore | rmsle 1.69703 | хуже H26 primary | weekend share |
| H35 | ❌ | explore | rmsle 1.69660 | хуже H31 | last-K events |
| H36 | ❌ | explore | rmsle 1.69877 | хуже H31 | mid residual |
| H37 | ❌ | pivot | rmsle 1.70473 | хуже H31 | LGB total y |
| H38 | ❌ | pivot | rmsle 2.488 | хуже H31 | Tweedie |
| H39 | ❌ | explore | rmsle 1.69877 | хуже H31 | MoE hist_gmv |
| H40 | ❌ | pivot | rmsle 1.69649 | хуже H31 | zero-snap τ |
| H41 | ⚠️ | explore | rmsle 1.696112 | primary ≈ H31, holdout worse | RFM TE |
| H42 | ❌ | explore | rmsle 1.69653 | хуже H31, holdout better | burstiness |
| H43 | ❌ | explore | rmsle 1.69681 | хуже H31 | time weights |
| H44 | ❌ | refine | rmsle 1.70670 | хуже H31 | isotonic log |
| H45 | ✅ | explore | rmsle 1.696101 | vs H31 both better | LGB+HGB mix |
| H46 | ❌ | pivot | rmsle 1.69745 | хуже H31 | XGBoost |
| H47 | ❌ | explore | rmsle 1.696525 | хуже H45 | funnel windows |
| H48 | ✅ | pivot | rmsle 1.693588 | vs H45 both better | BTYD-фичи |
| H49 | ⚠️ | explore | rmsle 1.693343 | holdout 1.740312 worse | calendar 30d |
| H50 | ✅ | explore | rmsle 1.693554 | vs H48 both, < H52 | nested GMV lags |
| H51 | ❌ | explore | rmsle 1.694336 | хуже H48 | channel BTYD |
| H52 | ✅ | explore | rmsle 1.692618 | vs H48 both better | order IPI |
| H53 | ✅ | explore | rmsle 1.693417 | vs H48 both, < H52 | channel lags |
| H54 | ❌ | pivot | rmsle 1.693688 | хуже H48 primary | LGB+HGB на BTYD |
| H55 | ❌ | explore | rmsle 1.693671 | хуже H48 primary | channel recency |
| H56 | ❌ | pivot | rmsle 1.694647 | хуже H48 | якорь 2025-11-08 |
| H57 | ✅ | refine | rmsle 1.693444 | vs H48 both, < H52 | ord days 30/90 |
| H58 | ⚠️ | explore | rmsle 1.692532 | holdout 1.740267 worse | IPI+calendar |
| H59 | ✅ | explore | rmsle 1.691937 | vs H52 both better | IPI+chlag |
| H60 | ❌ | refine | rmsle 1.702081 | хуже H52 | bucket c на IPI |
| H61 | ❌ | refine | rmsle 1.729107 | хуже H52 | log1p(y+1) |
| H62 | ❌ | explore | rmsle 1.692303 | хуже H59 both | H59 + nested lags |
| H63 | ⚠️ | refine | rmsle 1.692294 | holdout better, primary worse | H59 + rord |
| H64 | ❌ | explore | rmsle 1.692401 | хуже H59 both | H59 + cart conv |
| H65 | ✅ | refine | rmsle 1.691493 | vs H59 both better | H59 reg (prev champ) |
| H66 | ❌ | explore | rmsle 1.692314 | хуже H59 both | H59 + joint lags/rord |
| H67 | ✅ | pivot | rmsle 1.691867 | vs H59 both better | H59+HGB blend |
| H68 | ❌ | explore | rmsle 1.691886 | хуже H65 both | v3+funnel2 на H65 |
| H69 | ❌ | explore | rmsle 1.691916 | хуже H65 both | RFM cohortknn на H65 |
| H70 | ✅ | pivot | rmsle 1.690181 | vs H65 both better | **champion** hurdle-logmix c=0 |
| H71 | ❌ | refine | rmsle 1.691743 | хуже H70/H65 | dual-capacity 47/95 |
| H72 | ❌ | explore | rmsle 1.690623 | хуже H70; primary лучше H65 | 0.70 dual+0.30 hurdle |

Легенда status: ✅ принята · ⚠️ кандидат / нужен holdout · ❌ отклонена. Полный отчёт Hx → корень `past/` (окно ~15) или свёртка в [`lines/`](lines/).
