# buzzing_v2 Diagnostic: Does Simpler Beat V61?

**Date:** 2026-04-08  
**Test:** buzzing_v2 (minimal, ~165 lines, 3 builders, no features) vs buzzing V61 (662 lines)

## Result: V61 wins 7/10. Features ARE net positive.

### 10-map head-to-head (buzzing_v2=A, buzzing=B)

| Map | V2 Ti mined | V61 Ti mined | Winner |
|-----|-------------|--------------|--------|
| default_small1 | 4,980 | 19,540 | **V61** |
| default_small2 | 11,780 | 39,690 | **V61** |
| arena | 24,170 | 9,910 | **V2** |
| thread_of_connection | 29,770 | 28,460 | **V2** (close) |
| socket | 0 | 30,500 | **V61** |
| pls_buy_cucats_merch | 0 | 0 | **V61** (unit count) |
| cold | 0 | 25,730 | **V61** |
| galaxy | 4,990 | 22,390 | **V61** |
| butterfly | 34,840 | 34,390 | **V2** (close) |
| corridors | 9,930 | 14,600 | **V61** |

**V61 wins: 7. V2 wins: 3.**

### Verdict: Features ARE net positive. V61 is clearly better on complex topology maps.

V2 fails to reach ore on maps with walls and complex layouts (socket: 0 mined, cold: 0 mined, galaxy: only 4990). V61's exploration infrastructure (roads, BFS navigation, sector exploration) is essential on these maps.

---

## Critical Finding: V61 Has a Severe Bug on Arena (SE Starting Position)

Arena is a 25x25 tight map with only 10 Ti ore tiles total (~5 per side). Results are **seed-independent** (deterministic):

| Starting side | V2 mined | V61 mined | Ratio |
|---------------|----------|-----------|-------|
| Side A (NW) | 16,090 | 18,490 | V61 +15% |
| Side B (SE) | **24,170** | **9,910** | **V2 +144%** |

**From the SE corner, V61 mines only 9,910 Ti while V2 mines 24,170 (2.4x more).**

V61 also over-builds on arena: **217 buildings** vs V2's **72 buildings**. The excess infrastructure spend on a map with only 5 accessible ore tiles is the likely cause — builders spend Ti building roads/conveyors to nowhere instead of harvesting.

### Impact on MergeConflict Match

In our 3-2 win, we were side B (SE) on both loss maps (arena and default_small1):
- Arena: we lost as V61 from SE (9,910 mined). **V2 would have won** (24,170 mined from SE beats MC's 7,460)
- default_small1: V61 wins from both sides, V2 loses

If we fix V61's arena behavior, we'd likely go **4-1** against MergeConflict instead of 3-2.

---

## Why V2 Beats V61 on Arena

V2's design:
- 3 builders maximum (no over-staffing for 5 ore tiles)
- Direct conveyor chains only (no roads, no exploratory infrastructure)
- Immediately targets visible ore, no complex scoring

V61's failure mode on arena:
- Spawns up to 8 builders on a map with only ~5 Ti ore per side
- Builders build roads/conveyors as they explore, spending Ti
- Extra builders have no ore to harvest but keep costing maintenance

**The ore-sparse tight map failure is real and measurable.**

---

## Actionable Fixes

### Fix 1: Ore-count-based builder cap (confirmed needed)
Current V61: tight mode = 8 builders  
Proposed: if visible Ti ore near core < 8, cap at 4-5 builders

From arena analysis: we confirmed this with the replay-analyst finding that arena has only 10 Ti ore tiles total (5 per side). Our 8-builder cap is 1.6x more builders than ore tiles.

### Fix 2: Investigate road/conveyor spending on ore-scarce maps
V61 builds 217 buildings on arena while mining only 9,910 Ti. Most of these are road/conveyor tiles with no harvester at the end. Need to gate road-building on "I have a harvester destination" check.

### Maps where V2 is competitive (potential V61 regressions to watch)
- **arena**: V2 wins from SE. V61 has a clear bug here.
- **thread_of_connection**: Close race (29,770 vs 28,460). V61 barely wins.
- **butterfly**: Close (34,840 vs 34,390). V61 barely wins.

These three maps are where V61's extra features provide marginal or negative ROI.
