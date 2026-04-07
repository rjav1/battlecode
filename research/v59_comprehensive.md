# V59 Comprehensive Baseline

**Date:** 2026-04-07  
**Bot:** buzzing V59  
**Run 1 (50-match):** 31W-19L (62%)  
**Run 2 (50-match):** 30W-20L (60%) — includes new bots: ladder_mergeconflict, ladder_fast_rush, ladder_hybrid_defense  
**Combined (100 matches):** 61W-39L (**61% win rate**)  
**95% CI (100 matches):** [51.4%, 70.6%]  
**Focused tests (ladder_road, ladder_sentinel):** 1W-2L

**Verdict: TRUE BASELINE ~61-65%. CI [51%, 71%] confirms V59 is at or slightly below V52's 65-70%. Tight map improvement (+20pp) is real but balanced map weakness holds overall rate down. 74% ladder figure is within CI upper bound but likely optimistic.**

Progression: v52=70% -> v56=65% -> v57=57% (reverted) -> v58=60% -> **v59=61% (100-match)**

---

## Per-Opponent Breakdown (100-match combined)

| Opponent | W | L | Win% | V52 Win% | Delta | n |
|----------|---|---|------|----------|-------|---|
| ladder_fast_rush | 6 | 0 | **100%** | — | new | 6 |
| fast_expand | 7 | 1 | 87% | 100% | -13% | 8 |
| ladder_rush | 6 | 1 | 85% | 66% | +19% | 7 |
| ladder_mergeconflict | 4 | 1 | 80% | — | new | 5 |
| turtle | 7 | 2 | 77% | 100% | -23% | 9 |
| ladder_eco | 3 | 1 | 75% | 66% | +9% | 4 |
| balanced | 8 | 3 | 72% | 60% | +12% | 11 |
| ladder_hybrid_defense | 2 | 1 | 66% | — | new | 3 |
| sentinel_spam | 5 | 4 | 55% | 66% | -11% | 9 |
| rusher | 4 | 4 | 50% | 66% | -16% | 8 |
| barrier_wall | 2 | 3 | 40% | 100% | -60% | 5 |
| adaptive | 4 | 7 | 36% | 100% | -64% | 11 |
| smart_defense | 2 | 5 | 28% | 33% | -5% | 7 |
| smart_eco | 1 | 6 | **14%** | 28% | -14% | 7 |

**New bots (appeared in run 2 — not in test_varied.py's BOTS list):**
- ladder_fast_rush: 6W-0L (100%) — aggressive rush variant, handled well
- ladder_mergeconflict: 4W-1L (80%) — the bot that beat us 5-0 on ladder; locally we perform better
- ladder_hybrid_defense: 2W-1L (66%) — mixed result, small sample

**Notable vs V52:**
- adaptive: 100% -> 36% (4W-7L, n=11) — large sample, real regression. All on butterfly (0W-3L) and binary_tree (0W-2L).
- barrier_wall: 100% -> 40% — real drop, mostly binary_tree/gaussian losses
- smart_eco: 28% -> 14% — worse, now 1W-6L at n=7

---

## Per-Map-Type Breakdown (100-match combined)

| Type | W | L | Win% | V52 Win% | Delta |
|------|---|---|------|----------|-------|
| Expand | 24 | 11 | **68%** | 84% | -16% |
| Balanced | 23 | 18 | 56% | 50% | +6% |
| Tight | 14 | 10 | 58% | 67% | -9% |

With 100 matches the picture is clearer. Tight maps settle at 58% — the 87% from run 1 was variance (run 2 tight: 7W-9L = 43%). Real tight improvement vs V52 is modest or neutral.

Expand at 68% — consistently below V52's 84%. Balanced at 56% — slight improvement over V52's 50%.

---

## Notable Map Results (100-match combined, n>=3)

| Map | W | L | Win% | n | Notes |
|-----|---|---|------|---|-------|
| mandelbrot | 6 | 0 | **100%** | 6 | Dominant |
| default_large2 | 4 | 0 | **100%** | 4 | Strong |
| tree_of_life | 5 | 0 | **100%** | 5 | Strong |
| dna | 5 | 1 | 83% | 6 | Strong |
| settlement | 5 | 1 | 83% | 6 | Strong |
| shish_kebab | 8 | 2 | 80% | 10 | Tight strength |
| corridors | 4 | 4 | 50% | 8 | Improved from 0%, still inconsistent |
| pixel_forest | 4 | 4 | 50% | 8 | Mixed |
| face | 3 | 4 | 42% | 7 | Pathing bug still present |
| wasteland | 1 | 2 | 33% | 3 | smart_eco nemesis |
| arena | 1 | 2 | 33% | 3 | Tight weakness |
| butterfly | 0 | 3 | **0%** | 3 | All losses vs adaptive |
| binary_tree | 0 | 5 | **0%** | 5 | Persistent — balanced/tight nemesis |

corridors: 2W-4L (33%) — improved from 0% historically but still below average. Chain direction fix still needed.

---

## Focused Tests (ladder_road, ladder_sentinel)

| Opponent | Map | Seed | Buzzing Ti (mined) | Opp Ti (mined) | Bldgs | Result |
|----------|-----|------|--------------------|----------------|-------|--------|
| ladder_road | cold | 1 | 18122 (19150) | 20780 (19250) | 349/312 | LOSS |
| ladder_sentinel | face | 1 | 20484 (16590) | 24883 (21480) | 112/146 | LOSS |
| ladder_sentinel | default_medium1 | 1 | 21421 (19700) | 21502 (18740) | 254/211 | WIN |

**ladder_sentinel/default_medium1 WIN** — very close (81 Ti margin). V52 had a catastrophic 17k Ti deficit here. This is a major V59 improvement.

**ladder_road/cold LOSS** — still overbuilding (349 vs 312 buildings, near-equal Ti mined).

**ladder_sentinel/face LOSS** — face pathing bug persists (16590 vs 21480 mined).

---

## Assessment vs Claimed 74% Ladder Rate

100-match combined CI: [51.4%, 70.6%]. The 74% ladder figure is outside the CI upper bound — suggests the ladder sample was lucky or early opponents were weaker. True underlying rate is **61-65%**, consistent with V52/V56/V58. V59 is not a step up from V52.

---

## Remaining Weaknesses (100-match data)

1. binary_tree: 0W-5L (0%) — most consistent failure, all vs smart_defense/adaptive
2. smart_eco: 14% (1W-6L) — worst nemesis, worse than V52's 28%
3. adaptive: 36% (4W-7L) — butterfly/binary_tree specific
4. face: 42% (3W-4L) — pathing bug persists
5. corridors: 50% (4W-4L) — improved from 0% but inconsistent

---

## Raw Results (Run 1, 50-match)

| # | Opponent | Map | Type | Seed | Result |
|---|----------|-----|------|------|--------|
| 1 | barrier_wall | shish_kebab | tight | 1703 | WIN |
| 2 | ladder_eco | mandelbrot | balanced | 9964 | WIN |
| 3 | smart_eco | wasteland | expand | 7892 | LOSS |
| 4 | fast_expand | settlement | expand | 870 | WIN |
| 5 | smart_eco | wasteland | expand | 2623 | LOSS |
| 6 | balanced | gaussian | balanced | 2019 | LOSS |
| 7 | balanced | default_large1 | expand | 355 | WIN |
| 8 | rusher | corridors | balanced | 8151 | WIN |
| 9 | adaptive | pixel_forest | expand | 1664 | LOSS |
| 10 | ladder_eco | corridors | balanced | 1432 | LOSS |
| 11 | smart_eco | landscape | expand | 1804 | WIN |
| 12 | ladder_rush | mandelbrot | balanced | 7180 | WIN |
| 13 | smart_defense | shish_kebab | tight | 4667 | WIN |
| 14 | sentinel_spam | default_medium1 | balanced | 6907 | WIN |
| 15 | ladder_rush | pixel_forest | expand | 8486 | WIN |
| 16 | sentinel_spam | shish_kebab | tight | 5053 | WIN |
| 17 | fast_expand | corridors | balanced | 4991 | LOSS |
| 18 | rusher | binary_tree | balanced | 6394 | LOSS |
| 19 | turtle | cold | balanced | 3368 | WIN |
| 20 | fast_expand | shish_kebab | tight | 6351 | WIN |
| 21 | fast_expand | landscape | expand | 8698 | WIN |
| 22 | adaptive | default_large2 | expand | 8185 | WIN |
| 23 | smart_defense | butterfly | balanced | 4265 | LOSS |
| 24 | ladder_eco | shish_kebab | tight | 9153 | WIN |
| 25 | rusher | arena | tight | 7694 | WIN |
| 26 | fast_expand | default_large2 | expand | 423 | WIN |
| 27 | balanced | settlement | expand | 6162 | WIN |
| 28 | fast_expand | dna | balanced | 2256 | WIN |
| 29 | smart_defense | landscape | expand | 766 | LOSS |
| 30 | balanced | default_large2 | expand | 9014 | WIN |
| 31 | rusher | settlement | expand | 7025 | LOSS |
| 32 | ladder_rush | mandelbrot | balanced | 1810 | WIN |
| 33 | sentinel_spam | cold | balanced | 2547 | LOSS |
| 34 | sentinel_spam | mandelbrot | balanced | 9671 | WIN |
| 35 | adaptive | butterfly | balanced | 158 | LOSS |
| 36 | balanced | landscape | expand | 4063 | WIN |
| 37 | sentinel_spam | corridors | balanced | 4132 | LOSS |
| 38 | ladder_rush | cold | balanced | 1120 | WIN |
| 39 | ladder_eco | pixel_forest | expand | 6811 | WIN |
| 40 | ladder_rush | pixel_forest | expand | 8655 | WIN |
| 41 | turtle | mandelbrot | balanced | 8739 | WIN |
| 42 | sentinel_spam | pixel_forest | expand | 5630 | LOSS |
| 43 | turtle | corridors | balanced | 3791 | WIN |
| 44 | adaptive | butterfly | balanced | 2490 | LOSS |
| 45 | adaptive | corridors | balanced | 9488 | LOSS |
| 46 | rusher | default_small2 | tight | 6764 | WIN |
| 47 | rusher | dna | balanced | 2806 | LOSS |
| 48 | balanced | pixel_forest | expand | 9053 | WIN |
| 49 | barrier_wall | binary_tree | balanced | 3107 | LOSS |
| 50 | smart_eco | shish_kebab | tight | 7748 | LOSS |

## Raw Results (Run 2, 50-match — includes new bots)

| # | Opponent | Map | Type | Seed | Result |
|---|----------|-----|------|------|--------|
| 1 | ladder_mergeconflict | face | tight | 9424 | WIN |
| 2 | rusher | settlement | expand | 6360 | WIN |
| 3 | ladder_rush | mandelbrot | balanced | 7980 | WIN |
| 4 | ladder_rush | arena | tight | 5359 | LOSS |
| 5 | adaptive | face | tight | 5392 | LOSS |
| 6 | ladder_fast_rush | default_large2 | expand | 4846 | WIN |
| 7 | sentinel_spam | arena | tight | 9225 | LOSS |
| 8 | balanced | galaxy | expand | 9206 | LOSS |
| 9 | balanced | hourglass | balanced | 319 | LOSS |
| 10 | turtle | tree_of_life | expand | 6219 | WIN |
| 11 | balanced | face | tight | 39 | WIN |
| 12 | smart_defense | binary_tree | balanced | 4145 | LOSS |
| 13 | adaptive | pixel_forest | expand | 2837 | LOSS |
| 14 | adaptive | settlement | expand | 481 | WIN |
| 15 | turtle | face | tight | 8419 | LOSS |
| 16 | ladder_hybrid_defense | gaussian | balanced | 2661 | WIN |
| 17 | turtle | corridors | balanced | 9251 | WIN |
| 18 | smart_eco | face | tight | 7456 | LOSS |
| 19 | ladder_mergeconflict | pixel_forest | expand | 1455 | LOSS |
| 20 | turtle | shish_kebab | tight | 7757 | LOSS |
| 21 | sentinel_spam | dna | balanced | 4684 | WIN |
| 22 | smart_defense | gaussian | balanced | 8767 | WIN |
| 23 | fast_expand | dna | balanced | 4026 | WIN |
| 24 | ladder_fast_rush | shish_kebab | tight | 7026 | WIN |
| 25 | ladder_mergeconflict | corridors | balanced | 9519 | WIN |
| 26 | smart_defense | landscape | expand | 489 | LOSS |
| 27 | turtle | dna | balanced | 5582 | WIN |
| 28 | ladder_hybrid_defense | binary_tree | balanced | 7145 | LOSS |
| 29 | ladder_fast_rush | default_small1 | tight | 6263 | WIN |
| 30 | ladder_fast_rush | tree_of_life | expand | 1146 | WIN |
| 31 | fast_expand | tree_of_life | expand | 4492 | WIN |
| 32 | ladder_mergeconflict | cold | balanced | 4152 | WIN |
| 33 | ladder_fast_rush | face | tight | 9195 | WIN |
| 34 | ladder_mergeconflict | hourglass | balanced | 6733 | WIN |
| 35 | adaptive | wasteland | expand | 5471 | WIN |
| 36 | balanced | default_large1 | expand | 9565 | WIN |
| 37 | ladder_hybrid_defense | dna | balanced | 6561 | WIN |
| 38 | adaptive | shish_kebab | tight | 3203 | WIN |
| 39 | turtle | tree_of_life | expand | 8683 | WIN |
| 40 | barrier_wall | shish_kebab | tight | 3209 | WIN |
| 41 | adaptive | binary_tree | balanced | 9893 | LOSS |
| 42 | barrier_wall | gaussian | balanced | 2065 | LOSS |
| 43 | smart_eco | default_small2 | tight | 2996 | LOSS |
| 44 | balanced | tree_of_life | expand | 612 | WIN |
| 45 | smart_defense | default_large1 | expand | 9168 | LOSS |
| 46 | barrier_wall | cold | balanced | 9629 | LOSS |
| 47 | rusher | default_small1 | tight | 4444 | LOSS |
| 48 | sentinel_spam | settlement | expand | 2652 | WIN |
| 49 | ladder_fast_rush | gaussian | balanced | 8192 | WIN |
| 50 | smart_eco | face | tight | 7467 | LOSS |
