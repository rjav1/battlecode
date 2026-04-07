# V57 Turtle/Barrier_Wall Regression Analysis

**Date:** 2026-04-06

---

## Test Results

### buzzing vs turtle

| Map | buzzing mined | turtle mined | Buildings buzzing/turtle | Winner |
|-----|--------------|-------------|--------------------------|--------|
| default_medium1 | 19220 | 12860 | 237 / 343 | **buzzing WIN** |
| galaxy | 14810 | 4960 | 246 / 532 | **buzzing WIN** |
| face | 4980 | 9850 | 78 / 207 | turtle LOSS |
| cold | 19670 | 0 | 385 / 373 | **buzzing WIN** |

**V57 vs turtle: 3W-1L** (face is the loss)

### buzzing vs barrier_wall

| Map | buzzing mined | barrier_wall mined | Buildings buzzing/barrier_wall | Winner |
|-----|--------------|--------------------|---------------------------------|--------|
| cold | 15700 | 21040 | 523 / 108 | barrier_wall LOSS |
| dna | 14400 | 27660 | 398 / 194 | barrier_wall LOSS |
| face | 13490 | 17100 | 133 / 70 | barrier_wall LOSS |
| settlement | 35590 | 30870 | 614 / 203 | **buzzing WIN** |
| gaussian | 28930 | 29730 | 197 / 110 | barrier_wall LOSS |

**V57 vs barrier_wall: 1W-4L**

---

## Is This a V57 Regression?

**No.** buzzing_prev was 0/4 vs turtle and 0/4 vs barrier_wall on these same maps. V57 is 3/4 vs turtle — strictly better. The "100%→0%" report likely compared against an older bot version, not buzzing_prev.

| Opponent | buzzing_prev | buzzing V57 |
|----------|-------------|-------------|
| turtle | 0W-4L | 3W-1L |
| barrier_wall | 0W-4L | 1W-4L |

---

## Root Cause: Exploration Conveyor Sprawl

The building count explosion (200–600 buildings) on maps where buzzing loses reveals the underlying problem.

**buzzing_prev during exploration:** `self._nav(c, pos, far, passable, ti_reserve=999999)` — never builds conveyors while exploring, only roads as fallback.

**buzzing V57 during exploration:** `self._nav(c, pos, far, passable, ti_reserve=explore_reserve)` where `explore_reserve` can be as low as 5 on non-maze open maps. With ti_reserve=5, the builder builds a conveyor on EVERY step during exploration, creating long orphaned chains pointing away from core toward map edges.

These exploratory conveyor chains:
1. Cost 3 Ti each + scale increase each time
2. Don't connect to any harvester
3. Don't deliver resources (they point away from core via d.opposite())
4. Inflate building count by 100–400 extra conveyors per game

On maps where buzzing loses vs barrier_wall: 523 buildings on cold (vs 108), 398 on dna (vs 194), 614 on settlement (vs 203 — buzzing wins here despite waste because settlement has abundant ore).

**Secondary contributor:** The nav bridge fallback in `_nav` (lines 436–453) still exists — when stuck, it builds bridges to empty tiles 2-3 steps ahead (20 Ti each, +10% scale). This fires on winding maps.

---

## Fix Recommendation

**Change explore to never build conveyors** — restore buzzing_prev behavior:

In `_explore`, replace:
```python
self._nav(c, pos, far, passable, ti_reserve=explore_reserve)
```
With:
```python
self._nav(c, pos, far, passable, ti_reserve=999999)
```

This eliminates orphaned exploration conveyors. Builders will still move (using existing conveyors/roads) and build roads as fallback when stuck — roads are cheap (1 Ti) and don't hurt chain delivery.

Expected impact: reduce building count by 50–80% on open maps, freeing ~300–500 Ti per game for additional harvesters.

---

## Summary

The turtle/barrier_wall issue is not a V57 regression — it predates V57 and even buzzing_prev. The building count explosion on losing maps is caused by explore_reserve=5 causing conveyor sprawl during exploration. Fix: restore `ti_reserve=999999` in `_explore`.
