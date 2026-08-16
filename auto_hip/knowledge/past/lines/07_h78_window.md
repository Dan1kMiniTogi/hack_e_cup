# Линия: окно H78–H87 (свёртка)

Полные отчёты в корне: H80, H82, H84–H91. Сюда — H78/H79 и ❌ эпохи.

## Folded

- **H78 ✅** стек 0.30 H65 + 0.70 hurdle 3-seed: 1.689400 / 1.738825. База H87.
- **H79 ⚠️** веса 0.15/0.85: primary лучше, holdout хуже H78. Стоп сетки весов.
- **H81 ❌** logit temperature T=0.9 на p: mean_pred↑, RMSLE↑ оба сплита (1.692937 / 1.740194). Не T<1; H91 показал, что T=1.05 работает в другую сторону.
- **H83 ❌** CHANNEL_BALANCE на стек H78: primary хуже, holdout шум.

## Напоминание по keepers (не дублировать файлы)

- H80 ⚠️ intent в μ. H87 ✅ intent только clf. H91 ✅ T=1.05.
- H82/H84/H88/H90 ⚠️ mixed/4-bag CB — лучший holdout (H90 1.738551), primary не проходит без T.
- H85 ⚠️ log-blend. H86 ❌ multi-depth. H89 ❌ rord-in-μ.
