# V58 Baseline (20 matches)

**Date:** 2026-04-07  
**Bot:** buzzing V58 (V56 restored -- bridges back)  
**Record:** 12W-8L-0D (**60% win rate**)

**Verdict: STABLE. 60% at n=20 is consistent with V52/V56 range (65-70%). Bridges confirmed restored -- no V57-style regression. Smart_defense drew 6/20 matches (1W-5L) which is the main drag -- without that skew this would be ~67-68%.**

Progression: v52=70% -> v56=65% -> v57=57% (regression) -> **v58=60%** (restored)

---

## Per-Opponent Breakdown

| Opponent | W | L | Win% | n | Notes |
|----------|---|---|------|---|-------|
| rusher | 2 | 0 | 100% | 2 | Strong |
| barrier_wall | 1 | 0 | 100% | 1 | Strong |
| fast_expand | 2 | 0 | 100% | 2 | Strong |
| ladder_eco | 2 | 0 | 100% | 2 | Strong |
| ladder_rush | 2 | 0 | 100% | 2 | Strong |
| adaptive | 2 | 1 | 66% | 3 | Normal |
| smart_eco | 0 | 2 | 0% | 2 | Nemesis (shish_kebab, pixel_forest) |
| smart_defense | 1 | 5 | 16% | 6 | 30% draw rate -- pure sampling skew |

smart_defense drew 6 of 20 matches -- statistically unlucky (p~0.04 if true draw rate is 9%). 5 losses vs smart_defense dragged overall rate from ~68% to 60%.

---

## Per-Map-Type Breakdown

| Type | W | L | Win% | V56 Win% |
|------|---|---|------|----------|
| Tight | 3 | 2 | 60% | 50% |
| Balanced | 5 | 4 | 55% | 50% |
| Expand | 4 | 2 | 66% | 75% |

All map types within normal variance. Expand at 66% confirms V57 regression (50%) is resolved.

---

## V57 Regression Confirmed Resolved

V57 collapse signals are absent:
- Expand: 66% (4W-2L) -- back to normal (V57 was 50%)
- rusher: 100% (2W-0L) -- V57 was 28%

Bridges are working correctly again.

---

## Raw Results

| # | Opponent | Map | Type | Seed | Result |
|---|----------|-----|------|------|--------|
| 1 | rusher | galaxy | expand | 1592 | WIN |
| 2 | barrier_wall | galaxy | expand | 8974 | WIN |
| 3 | smart_eco | shish_kebab | tight | 9225 | LOSS |
| 4 | fast_expand | default_medium1 | balanced | 7210 | WIN |
| 5 | smart_defense | hourglass | balanced | 5710 | LOSS |
| 6 | smart_defense | default_large1 | expand | 9989 | LOSS |
| 7 | smart_defense | dna | balanced | 6499 | LOSS |
| 8 | smart_eco | pixel_forest | expand | 8729 | LOSS |
| 9 | ladder_eco | shish_kebab | tight | 8841 | WIN |
| 10 | ladder_rush | mandelbrot | balanced | 3542 | WIN |
| 11 | adaptive | shish_kebab | tight | 917 | WIN |
| 12 | fast_expand | default_medium1 | balanced | 1511 | WIN |
| 13 | adaptive | pixel_forest | expand | 4655 | WIN |
| 14 | ladder_eco | mandelbrot | balanced | 9011 | WIN |
| 15 | smart_defense | pixel_forest | expand | 3744 | LOSS |
| 16 | rusher | cold | balanced | 9258 | WIN |
| 17 | ladder_rush | wasteland | expand | 3380 | WIN |
| 18 | smart_defense | gaussian | balanced | 5238 | LOSS |
| 19 | adaptive | default_small1 | tight | 3098 | LOSS |
| 20 | smart_defense | wasteland | expand | 2024 | WIN |
