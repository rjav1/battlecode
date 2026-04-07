# V55 vs New Test Bots

**Date:** 2026-04-06
**Bot:** buzzing (V55 = explore reach fix)
**Seed:** 1

## Results

| # | Match | Map | Winner | Buzzing Ti mined | Opponent Ti mined | Buzzing Bldg | Opp Bldg |
|---|-------|-----|--------|-----------------|-------------------|--------------|----------|
| 1 | vs ladder_sentinel | default_medium1 | ladder_sentinel | 9100 | 26320 | 74 | 274 |
| 2 | vs ladder_sentinel | cold | **buzzing** | 19670 | 19610 | 375 | 334 |
| 3 | vs ladder_road | cold | ladder_road | 15750 | 20020 | 373 | 325 |
| 4 | vs ladder_road | galaxy | **buzzing** | 13790 | 4970 | 425 | 299 |

**Overall: 2W-2L (50%)**

---

## V52 → V55 Comparison

All tested maps show **identical results to V52**:
- ladder_sentinel default_medium1: 9100 vs 26320 (same)
- ladder_sentinel cold: 19670 vs 19610 (same)
- ladder_road cold: 15750 vs 20020 (same)

V55's "explore reach fix" doesn't change behavior on these maps. The fix (explore rotation reaching further) helps maps where exploration was the bottleneck, not these.

## Critical: default_medium1 vs ladder_road still broken

Additional check run: `buzzing vs ladder_road default_medium1 --seed 1`

**Result: 80 Ti mined (STILL BROKEN)**

The enemy-road BFS contamination bug from V52 is NOT fixed in V55. This remains a critical open issue.

---

## Match Analysis

### vs ladder_sentinel default_medium1 — LOSS (9100 vs 26320)
Buzzing built only 74 buildings vs sentinel's 274. Sentinel is building harvesters at 3x the rate. The ladder_sentinel bot is on the same spawn side (team A default_medium1 advantage), explaining the large gap. Buzzing's economy on default_medium1 as team B is weak in general.

### vs ladder_sentinel cold — WIN (19670 vs 19610, +60 Ti)
Near-draw. Buzzing's narrow win is a spawn-side advantage on cold — same 60 Ti margin as V52. Not a skill win.

### vs ladder_road cold — LOSS (15750 vs 20020)
Buzzing mined 4270 Ti less. Both built many buildings (373 vs 325) on cold's maze-like terrain. ladder_road's road+bridge network delivers ore more efficiently in mazes. Buzzing's chain-fix logic helps but can't match road-based delivery here.

### vs ladder_road galaxy — WIN (13790 vs 4970)
Strong win: +8820 Ti mined gap. ladder_road only mines 4970 on galaxy — this map likely has spawn-side or ore layout disadvantage for team B. Buzzing built 425 buildings (high conveyor count) but still dominated.

---

## Key Issues Remaining

1. **default_medium1 vs ladder_road: 80 Ti (BUG UNFIXED)** — enemy road BFS contamination
2. **default_medium1 as team B**: buzzing mines only 9100 Ti vs ladder_sentinel's 26320 — the spawn-side disadvantage on this map is severe regardless of opponent
3. **cold vs ladder_road**: -4270 Ti — road+bridge delivery beats buzzing's conveyor approach on maze maps

## Priority Fix

The enemy-road BFS bug (80 Ti on default_medium1 vs ladder_road) is the highest-priority fix. Proposed solution: exclude tiles with enemy buildings from the BFS passable set while still allowing movement on them.
