# Линия: окно H78–H87 (свёртка ❌ / шум)

Полные отчёты в корне: H78, H79, H80, H82, H84, H85, H86, H87 (+ H65, H75). Сюда — то, что не нужно держать открытым.

## Folded

- **H81 ❌** logit temperature T=0.9 на p: mean_pred↑, RMSLE↑ оба сплита (1.692937 / 1.740194). Не T<1, не путать с post-hoc c.
- **H83 ❌** CHANNEL_BALANCE (dominance/entropy/ord ratio) на стек H78: primary хуже, holdout шум. Коллинеарно с channel lags.

## Напоминание по keepers (не дублировать файлы)

- H78 ✅ стек + hurdle 3-seed. H79 ⚠️ стоп весов 0.15/0.85. H80 ⚠️ intent в μ. H87 ✅ intent только clf.
- H82/H84 ⚠️ mixed/4-bag CB — лучший holdout, primary не проходит. H85 ⚠️ log-blend. H86 ❌ multi-depth leaves.
