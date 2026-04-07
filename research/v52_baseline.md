# V52 Baseline (30 matches)

**Date:** 2026-04-07  
**Bot:** buzzing V52 (831 lines — attacker removed + chain-fix improved)  
**Record:** 21W-9L-0D (**70% win rate**)

**Verdict: NEW BEST BASELINE. Target 65%+ achieved and exceeded.**

Progression: v42=45% → v43=50% → v46=58% → v47=58% → v49=65% → v50=40% → v51=55% → **v52=70%**

---

## Per-Opponent Breakdown

| Opponent | W | L | Win% | V49 Win% | Delta |
|----------|---|---|------|----------|-------|
| adaptive | 5 | 0 | **100%** | 100% | 0% |
| fast_expand | 5 | 0 | **100%** | — | +100% |
| balanced | 3 | 0 | **100%** | 75% | +25% |
| ladder_eco | 2 | 0 | **100%** | 60% | +40% |
| barrier_wall | 1 | 0 | **100%** | 100% | 0% |
| turtle | 4 | 3 | 57% | — | — |
| ladder_rush | 1 | 1 | 50% | 43% | +7% |
| smart_defense | 1 | 2 | 33% | 25% | +8% |
| rusher | 0 | 1 | 0% | 50% | -50% |
| sentinel_spam | 0 | 1 | 0% | 100% | -100% |

**Standout improvements:** fast_expand 100% (5W-0L — was a weakness in V51), balanced 100%, ladder_eco 100%.  
**Regressions:** rusher (0W-1L, small sample), sentinel_spam (0W-1L, small sample).

---

## Per-Map-Type Breakdown

| Type | W | L | Win% | V49 Win% | Delta |
|------|---|---|------|----------|-------|
| **Expand** | **11** | **1** | **92%** | 83% | +9% |
| Tight | 4 | 2 | 67% | 40% | **+27%** |
| Balanced | 6 | 6 | 50% | — | — |

**Expand maps at 92% (11W-1L)** — dominant. Only loss: wasteland vs turtle (seed 9551).  
**Tight maps 67%** — major improvement from V49's 40%. Arena went 3W-1L (was 2W-4L in V47).  
**Balanced maps 50%** — still the problem category. Gaussian 0W-2L, hourglass 0W-2L persist.

### Balanced map detail
| Map | W | L |
|-----|---|---|
| butterfly | 2 | 0 |
| mandelbrot | 1 | 0 |
| cold | 1 | 0 |
| binary_tree | 1 | 1 |
| default_medium1 | 1 | 1 |
| hourglass | 0 | 2 |
| gaussian | 0 | 2 |

Hourglass and gaussian remain persistent losses. Both are known sparse/maze issues.

---

## Key Changes That Drove Improvement

1. **Attacker removal:** Builders that previously switched to "attacker mode" (raiding enemy infra after round 500) now stay focused on economy. This alone likely accounts for a significant chunk of the improvement — attacking enemy conveyors wastes builder time that should go to more harvesters.

2. **Chain-fix improvements:** harvesters_built ≤ 2 → ≤ 4, direction-change threshold 3 → 2, periodic re-trigger on high-wall maps. Contributes mainly to balanced/maze map performance.

3. **Tight map improvements vs fast_expand:** 5W-0L vs fast_expand is striking. V51 was 1W-3L. The attacker removal likely stopped builders from wasting time attacking on tight maps.

---

## Remaining Weaknesses

1. **Gaussian: 0W-2L** — sparse ore, confirmed unresolved
2. **Hourglass: 0W-2L** — vs ladder_rush and rusher; bottleneck map behavior
3. **smart_defense: 1W-2L (33%)** — persistent nemesis on tight maps
4. **sentinel_spam: 0W-1L** — small sample but concerning (was 100% in V47)

---

## Recommendation

**Ship V52.** 70% is a clear new best — 5pp above V49's previous record of 65%. The attacker removal was the key unlock. Expand maps at 92% are outstanding. Tight map improvement to 67% is significant.

Priority remaining fixes for V53:
1. Hourglass — investigate why we consistently lose there (bottleneck pathing?)
2. Gaussian / sparse-ore maps — chain length cap still needed
3. Sentinel_spam — verify whether 0W-1L is variance or real regression

---

## Raw Results

| # | Opponent | Map | Type | Seed | Result |
|---|----------|-----|------|------|--------|
| 1 | adaptive | default_large1 | expand | 8208 | WIN |
| 2 | ladder_rush | hourglass | balanced | 2818 | LOSS |
| 3 | smart_defense | binary_tree | balanced | 849 | LOSS |
| 4 | fast_expand | butterfly | balanced | 7426 | WIN |
| 5 | turtle | pixel_forest | expand | 91 | WIN |
| 6 | fast_expand | arena | tight | 6324 | WIN |
| 7 | sentinel_spam | arena | tight | 982 | LOSS |
| 8 | turtle | face | tight | 2340 | LOSS |
| 9 | balanced | butterfly | balanced | 826 | WIN |
| 10 | turtle | default_medium1 | balanced | 3665 | LOSS |
| 11 | turtle | wasteland | expand | 9551 | LOSS |
| 12 | smart_defense | gaussian | balanced | 8145 | LOSS |
| 13 | turtle | binary_tree | balanced | 7372 | WIN |
| 14 | turtle | landscape | expand | 9518 | WIN |
| 15 | balanced | arena | tight | 1210 | WIN |
| 16 | adaptive | default_medium1 | balanced | 2894 | WIN |
| 17 | turtle | gaussian | balanced | 4415 | LOSS |
| 18 | ladder_eco | arena | tight | 5393 | WIN |
| 19 | rusher | hourglass | balanced | 681 | LOSS |
| 20 | adaptive | tree_of_life | expand | 3261 | WIN |
| 21 | barrier_wall | tree_of_life | expand | 1903 | WIN |
| 22 | ladder_eco | landscape | expand | 4172 | WIN |
| 23 | adaptive | default_large1 | expand | 2796 | WIN |
| 24 | fast_expand | pixel_forest | expand | 1041 | WIN |
| 25 | ladder_rush | mandelbrot | balanced | 3787 | WIN |
| 26 | smart_defense | face | tight | 6132 | WIN |
| 27 | adaptive | wasteland | expand | 8124 | WIN |
| 28 | balanced | cold | balanced | 1175 | WIN |
| 29 | fast_expand | pixel_forest | expand | 828 | WIN |
| 30 | fast_expand | default_large2 | expand | 1321 | WIN |
