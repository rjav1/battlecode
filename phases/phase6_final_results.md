# Phase 6 Final Results - Features Added to Proven Economy Base

## Approach

Started from the proven eco_opponent base (196 lines, 36K+ Ti mined). Added features ONE AT A TIME, testing after each to verify Ti mined stays above 30K.

## Changes Made (in order)

### 1. Symmetry Detection (no impact on economy)
Added `_get_enemy_direction()` and `_get_enemy_core_pos()` methods. Detects rotational, horizontal, and vertical symmetry by sampling visible tiles. Caches result. Used by sentinel and attacker.

### 2. Bridge Fallback in _nav (threshold: Ti >= bridge_cost + 200)
Added after road fallback. Only triggers when Ti is abundant (200+ above bridge cost) to avoid draining economy. Bridges 2-3 tiles ahead across walls.

### 3. Sentinel with Splitter Ammo (proven splitter_test pattern)
State machine: find conveyor near core -> destroy it -> build splitter (same dir) -> build branch conveyor (perpendicular) -> build sentinel at end.
- Triggers: id%5==1, round > 1000, 3+ harvesters, within dist^2=36 of core, 200+ Ti
- Cap: 2 sentinels max
- Late timing (round 1000) is critical -- earlier timings (200-600) dropped Ti mined by 30-50%

### 4. Basic Attacker
- Triggers: id%4==2, round > 500, 4+ harvesters
- Walks toward enemy core using `_nav` (laying conveyors along the way)
- Attacks enemy buildings on current tile with `c.fire(pos)`

## Test Results (all seed 1)

### vs starter (8-0 sweep)

| Map | Winner | Ti Mined | Ti Remaining | Buildings |
|-----|--------|---------|-------------|----------|
| default_medium1 | **buzzing** | 37,200 | 38,268 | 254 |
| settlement | **buzzing** | 34,190 | 30,470 | 488 |
| cold | **buzzing** | 25,460 | 23,456 | 354 |
| corridors | **buzzing** | 9,930 | 14,879 | 25 |
| landscape | **buzzing** | 16,530 | 18,141 | 257 |
| battlebot | **buzzing** | 19,170 | 22,135 | 186 |
| arena | **buzzing** | 19,720 | 23,403 | 141 |
| face | **buzzing** | 14,330 | 18,251 | 112 |

### Mirror match
| Map | P1 Ti Mined | P2 Ti Mined |
|-----|------------|------------|
| default_medium1 | 18,680 | 21,130 |

## Key Lessons Learned

1. **The d.opposite() pattern cannot be changed.** Roads for exploration, forward chains, and other approaches all produced 0 Ti mined. The breadcrumb trail of conveyors from core outward is the ONLY working approach.

2. **Late sentinel timing is critical.** Sentinel building before round 1000 diverts builder economy and drops Ti mined 30-50%. The splitter pattern itself is proven (from splitter_test), but the TIMING of when to build it matters enormously.

3. **Bridge threshold must be high.** Bridges at low Ti threshold (cost+30) caused economy to crash. At cost+200, they only fire when flush.

4. **Individual builder harvester counts are low.** With 7 builders, each builds ~1-4 harvesters. Thresholds like "7+ harvesters" per builder are never reached.

## File
`C:\Users\rahil\downloads\battlecode\bots\buzzing\main.py` (~340 lines)
