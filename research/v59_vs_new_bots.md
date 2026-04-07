# V59 vs New Test Bots

**Date:** 2026-04-07  
**Bot tested:** buzzing V59 (chain-join removed, core-bridge dist 9-25 guard)

---

## vs ladder_road (6 matches)

ladder_road builds roads extensively — triggers enemy-road BFS contamination bug in buzzing.

| # | Map | Seed | Result | Buzzing Ti | ladder_road Ti | Notes |
|---|-----|------|--------|-----------|---------------|-------|
| 1 | default_medium1 | 1 | LOSS | 1870 | 12780 | BFS bug: 210 vs 282 buildings |
| 2 | default_medium1 | 2 | LOSS | — | — | Same pattern |
| 3 | default_large1 | 1 | LOSS | — | — | |
| 4 | galaxy | 1 | WIN | — | — | |
| 5 | wasteland | 1 | LOSS | — | — | |
| 6 | pixel_forest | 1 | LOSS | — | — | |

**vs ladder_road: 1W-5L (17%)**

Root cause confirmed: enemy-road BFS contamination still present in V59. The chain-join fix (V59) did NOT address this bug. Default_medium1 seed 1: 1870 Ti mined vs 12780 — same 80 Ti collapse pattern seen in V54/V55. Enemy roads are included in buzzing's passable set, routing builders through enemy territory and causing misdirected conveyors.

This requires the BFS passable-set fix (exclude tiles with enemy buildings) — not yet implemented.

---

## vs ladder_sentinel (6 matches)

ladder_sentinel builds sentinels defensively — tests our ability to win on pure economy vs a defended opponent.

| # | Map | Seed | Result | Buzzing Ti | ladder_sentinel Ti | Notes |
|---|-----|------|--------|-----------|-------------------|-------|
| 7 | face | 1 | LOSS | 16590 | 21480 | Economy gap |
| 8 | face | 2 | LOSS | — | — | |
| 9 | default_medium1 | 1 | WIN | — | — | |
| 10 | default_large1 | 1 | LOSS | — | — | |
| 11 | galaxy | 1 | LOSS | — | — | |
| 12 | cold | 1 | LOSS | — | — | |

**vs ladder_sentinel: 1W-5L (17%)**

We're consistently behind on economy (16590 vs 21480 Ti on face). ladder_sentinel appears to be a strong eco bot with defensive capability. Our V59 improvement didn't help here — this is likely a fundamental economy gap on these specific maps, not a chain/bridge issue.

---

## Summary

| Opponent | W | L | Win% | Root Cause |
|----------|---|---|------|-----------|
| ladder_road | 1 | 5 | 17% | Enemy-road BFS contamination (unfixed bug) |
| ladder_sentinel | 1 | 5 | 17% | Economy gap on large/medium maps |

**Neither opponent benefits from V59's chain-join fix** — both failures are due to different root causes:
1. ladder_road: BFS passable set includes enemy roads → V60 must fix this
2. ladder_sentinel: pure economy gap → may need builder ramp or ore targeting improvements

---

## Note on ladder_mergeconflict / ladder_fast_rush / ladder_hybrid_defense

Eco-debugger has not yet created these bots. Will test once available.
