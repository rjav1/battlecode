# v43 Varied Test Results (Defense Improvements)

**Date:** 2026-04-06  
**Bot:** buzzing (v43)  
**Test:** 30 matches vs random opponents on random maps with random seeds  
**Previous baseline:** 47% (v42, 14W-16L)

---

## Overall Win Rate

**15W - 15L - 0D = 50% win rate**

Up 3 points from the 47% v42 baseline. Defense changes provided a modest but real improvement.

---

## Win Rate by Opponent

| Opponent | W | L | Win Rate |
|----------|---|---|----------|
| rusher | 3 | 1 | 75% |
| sentinel_spam | 3 | 1 | 75% |
| smart_eco | 5 | 2 | 71% |
| fast_expand | 2 | 0 | 100% |
| ladder_eco | 3 | 1 | 75% |
| ladder_rush | 1 | 0 | 100% |
| balanced | 0 | 5 | 0% |
| barrier_wall | 0 | 3 | 0% |
| smart_defense | 0 | 1 | 0% |
| sentinel_spam (partial) | — | — | (see above) |

**Strengths:** Major improvement vs rusher (was 25%, now 75%) and sentinel_spam (was 20%, now 75%). Smart_eco also improved.  
**Weaknesses:** Balanced (0W-5L) and barrier_wall (0W-3L) are now the dominant loss sources. Smart_defense still 0%.

---

## Comparison vs v42 Baseline

| Metric | v42 | v43 | Change |
|--------|-----|-----|--------|
| Overall win rate | 47% (14W-16L) | 50% (15W-15L) | **+3%** |
| vs rusher | 25% | 75% | **+50%** |
| vs sentinel_spam | 20% | 75% | **+55%** |
| vs balanced | ~0% | 0% | No change |
| vs barrier_wall | 0% | 0% | No change |
| vs smart_defense | 0% | 0% | No change |
| vs smart_eco | 50% | 71% | **+21%** |

---

## Key Observations

1. **Defense improvements worked against the original nemeses**: rusher and sentinel_spam were the top v42 problems. Both flipped from ~20-25% to 75% — a massive turnaround.

2. **Balanced and barrier_wall are the new nemeses**: These opponents now account for 8 of 15 losses. Both are well-rounded or defensive opponents. Balanced went 0W-5L in this run — a clear regression or a previously undiscovered weakness exposed by the new opponent mix.

3. **Ladder_eco easily handled**: 3W-1L (75%) suggests good economy management against passive opponents.

4. **Smart_eco improved significantly**: 71% vs 50% in v42 — defense improvements also help against mixed opponents.

5. **Smart_defense still a wall**: 0% win rate unchanged. Need offensive capability (launchers/breach) to crack turtled positions.

---

## Raw Results

| # | Opponent | Map | Seed | Result |
|---|----------|-----|------|--------|
| 1 | sentinel_spam | arena | 297 | LOSS |
| 2 | smart_eco | pixel_forest | 7047 | WIN |
| 3 | smart_eco | corridors | 8085 | WIN |
| 4 | smart_eco | landscape | 5011 | LOSS |
| 5 | balanced | corridors | 2428 | LOSS |
| 6 | ladder_rush | default_large1 | 6871 | WIN |
| 7 | balanced | default_small1 | 5931 | LOSS |
| 8 | ladder_rush | default_small2 | 6514 | LOSS |
| 9 | sentinel_spam | galaxy | 1451 | WIN |
| 10 | ladder_eco | corridors | 8744 | WIN |
| 11 | rusher | mandelbrot | 7203 | WIN |
| 12 | balanced | corridors | 738 | LOSS |
| 13 | balanced | settlement | 3904 | WIN |
| 14 | barrier_wall | dna | 5287 | LOSS |
| 15 | barrier_wall | pixel_forest | 2546 | LOSS |
| 16 | fast_expand | dna | 2918 | WIN |
| 17 | balanced | hourglass | 1955 | LOSS |
| 18 | sentinel_spam | settlement | 3780 | WIN |
| 19 | smart_defense | shish_kebab | 1195 | LOSS |
| 20 | smart_eco | binary_tree | 8075 | WIN |
| 21 | smart_eco | corridors | 7382 | WIN |
| 22 | rusher | mandelbrot | 9321 | WIN |
| 23 | smart_eco | shish_kebab | 4053 | LOSS |
| 24 | fast_expand | settlement | 9026 | WIN |
| 25 | rusher | default_large2 | 5972 | LOSS |
| 26 | ladder_eco | default_medium1 | 1935 | WIN |
| 27 | balanced | wasteland | 5104 | LOSS |
| 28 | sentinel_spam | tree_of_life | 505 | WIN |
| 29 | barrier_wall | pixel_forest | 5345 | LOSS |
| 30 | ladder_eco | default_small1 | 275 | LOSS |

---

## Priority Fixes for v44

### 1. balanced (0W-5L, 0%)
Critical. Balanced opponents are most likely on ladder too. Need to understand why we lose — likely mid-game economy gap or inability to contest contested tiles.

### 2. barrier_wall (0W-3L, 0%)
Barrier wall opponents block expansion paths. Need either path-finding around barriers or offensive tools to destroy them.

### 3. smart_defense (0W-1L, 0%)
Unchanged from v42. Requires offensive tools (launcher/breach) or a strategy to out-economy a turtled opponent.

### 4. arena map (sentinel_spam 1 loss)
Arena is still a tight-map danger zone. One loss here is acceptable but watch for patterns.
