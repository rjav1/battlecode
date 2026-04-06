# v28 Full Benchmark Results
Date: 2026-04-04
Bot: buzzing (v28)
Opponent: smart_eco
Seed: 1

All matches run to turn 2000 (tiebreak by Resources).

## Results Table

| Map | Winner | Our Ti Mined | Their Ti Mined | Gap |
|---|---|---|---|---|
| default_medium1 | **buzzing** | 18,770 | 4,900 | +13,870 |
| cold | smart_eco | 9,750 | 13,730 | -3,980 |
| settlement | **buzzing** | 38,390 | 19,320 | +19,070 |
| corridors | **buzzing** | 14,790 | 14,660 | +130 |
| face | smart_eco | 14,560 | 17,710 | -3,150 |
| arena | smart_eco | 4,940 | 24,330 | -19,390 |
| hourglass | smart_eco | 24,500 | 24,600 | -100 |
| galaxy | **buzzing** | 14,650 | 9,930 | +4,720 |
| shish_kebab | **buzzing** | 14,490 | 9,840 | +4,650 |
| butterfly | smart_eco | 29,020 | 34,810 | -5,790 |

## Overall Record

**5W - 5L (50%)**

## Average Ti Gap

| Metric | Value |
|---|---|
| Wins average gap | +8,488 Ti |
| Losses average gap | -6,482 Ti |
| Overall average gap | +1,003 Ti |

Calculation:
- Wins: (+13,870 + 19,070 + 130 + 4,720 + 4,650) / 5 = +8,488
- Losses: (-3,980 + -3,150 + -19,390 + -100 + -5,790) / 5 = -6,482
- Overall: (+13,870 + -3,980 + 19,070 + 130 + -3,150 + -19,390 + -100 + 4,720 + 4,650 + -5,790) / 10 = +1,003 (sum = 10,030)

## v25 vs v28 Comparison

| Map | v25 Winner | v25 Gap | v28 Winner | v28 Gap | Change |
|---|---|---|---|---|---|
| default_medium1 | buzzing | +13,870 | **buzzing** | +13,870 | 0 (stable) |
| cold | buzzing | +2,890 | smart_eco | -3,980 | **-6,870 (REGRESSED — flipped!)** |
| settlement | buzzing | +14,930 | **buzzing** | +19,070 | **+4,140 (improved)** |
| corridors | buzzing | +130 | **buzzing** | +130 | 0 (stable) |
| face | smart_eco | -3,150 | smart_eco | -3,150 | 0 (stable) |
| arena | smart_eco | -24,130 | smart_eco | -19,390 | **+4,740 (improved — still losing)** |
| hourglass | buzzing | +90 | smart_eco | -100 | **-190 (REGRESSED — flipped!)** |
| galaxy | buzzing | +4,720 | **buzzing** | +4,720 | 0 (stable) |
| shish_kebab | buzzing | +4,700 | **buzzing** | +4,650 | -50 (stable) |
| butterfly | smart_eco | -9,940 | smart_eco | -5,790 | **+4,150 (improved — still losing)** |

## Map Analysis

### Regressions (maps that got worse)
1. **cold**: +2,890 → -3,980, a -6,870 swing — **flipped from win to loss**. This is the most significant regression. cold was specifically fixed in v25; v28 has broken it again.
2. **hourglass**: +90 → -100, a -190 swing — **flipped from win to loss**. Was already a razor-thin win in v25; now a razor-thin loss.

### Improvements (maps that got better)
1. **settlement**: +14,930 → +19,070, a +4,140 improvement — already dominant, now more so.
2. **arena**: -24,130 → -19,390, a +4,740 improvement — still losing badly but gap narrowed.
3. **butterfly**: -9,940 → -5,790, a +4,150 improvement — still losing but gap narrowed.

### Stable Maps (no meaningful change)
- **default_medium1**: exactly the same (+13,870)
- **corridors**: exactly the same (+130)
- **face**: exactly the same (-3,150)
- **galaxy**: exactly the same (+4,720)
- **shish_kebab**: nearly the same (+4,700 → +4,650)

## Overall Verdict

**Regression: v25 was 7W-3L (70%), v28 is 5W-5L (50%)**

v28 lost 2 wins compared to v25:
- **cold** flipped to a loss (-6,870 swing) — the biggest regression
- **hourglass** flipped to a loss (-190 swing) — narrow but decisive

The improvements to arena (+4,740), butterfly (+4,150), and settlement (+4,140) did not compensate for the two wins lost.

## Key Findings

### Critical Regression: cold
- v25 had specifically fixed cold (was -3,950 in v24, fixed to +2,890 in v25)
- v28 has broken cold again: now -3,980, nearly identical to the v24 value
- v28 cold performance is almost exactly as bad as v24 cold — the v25 fix was lost or overridden
- **Top priority: identify what v25 changed for cold that v28 removed**

### Near-Miss Regression: hourglass
- hourglass was +90 in v25 (essentially a coin flip), now -100
- The tiny gap means this is likely noise or a marginal change, but the result flipped
- Mined amounts are nearly identical (24,500 vs 24,600) — this is a toss-up map

### Partial Progress: arena and butterfly
- Both large open-map losses improved by ~+4,000-4,700 Ti gap
- Arena improved from -24,130 to -19,390 (still a severe loss but trending right)
- Butterfly improved from -9,940 to -5,790 (still a loss but more competitive)
- The open-map expansion work is having effect but not yet enough to flip these to wins

### Unchanged Stable Core
- default_medium1, corridors, face, galaxy, shish_kebab all identical or nearly identical
- These maps are not affected by v28 changes

## Recommendations for v29

1. **Diagnose cold regression** (critical): Compare v25 and v28 code to find what changed. The cold result is nearly identical to v24, suggesting a v25 fix was lost. This is the highest-priority item.
2. **Investigate hourglass**: Although the gap is tiny (-100), it crossed the threshold. Check if any v28 change affects building placement on hourglass-type maps.
3. **Continue arena/butterfly work**: The gap is narrowing (+4,000-4,700 improvement per version). Another iteration of the open-map expansion strategy should bring these closer.
4. **Do not break settlement**: Settlement improved significantly (+4,140) in v28 — whatever caused that, preserve it.
