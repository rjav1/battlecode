# v29: Fix cold regression — marker placement distance guard

## Problem

v28 added a marker-based ore claiming system that caused cold to regress from
+2,890 Ti (win) to -3,980 Ti (loss) vs smart_eco.

## Root Cause Diagnosis

The regression was **not** caused by ore_density or wall_density
misclassifying cold as a maze map (cold has wall_density=0.2029 which triggers
is_maze=True in both v25 and v28, yet v25 won cold).

The actual cause: `can_build_harvester(ore_pos)` returns False when a marker
is present on the ore tile. The v28 marker system placed markers directly on
target ore tiles, so when a builder arrived adjacent and tried to build a
harvester, the call failed because the marker was still there.

The v28 "fix" for this (destroy marker before building) was correct in that
destroy() doesn't cost action cooldown — but it didn't fix the root issue: the
marker placement itself caused builders to fail harvester builds on the same
turn as arrival, wasting at minimum one turn.

**Confirmed by bisection**: v25, v26, v27 all win cold identically (15161 Ti,
455 buildings). v28 loses (8710 Ti, 410 buildings). Removing only
`c.place_marker()` from v28 restores v27 performance.

## Fix

**Marker placement guard**: Only place a claim marker when the builder is NOT
yet adjacent to the target ore (distance_squared > 2). The marker signals intent
while the builder is navigating, and naturally disappears or isn't placed once
the builder is adjacent and ready to build a harvester.

Additional improvements over v28:
- **Ore scan**: Include ore tiles with markers in ore_tiles (don't exclude them).
  v28 excluded other builders' claimed tiles entirely, causing builders to see
  fewer ore targets and over-explore on maps like cold.
- **Ore scoring**: Add +10000 penalty for tiles with another builder's allied
  marker (prefer unclaimed ore without hard-blocking fallback options).
- **Target abandonment fix**: Don't abandon target when a marker (vs a real
  building) is on the ore tile.
- **State cleanup**: Reset `_claimed_pos` and `_marker_placed` when harvester
  is built or target changes.

## Results

| Map | v27 buzzing Ti | v29 buzzing Ti | smart_eco Ti | Winner |
|-----|----|----|----|----|
| cold | 15161 (17230 mined) | 15161 (17230 mined) | 16648 | buzzing |
| butterfly | 33348 (29020 mined) | 33348 (29020 mined) | 39245 | smart_eco |
| galaxy | 17175 (14650 mined) | 17175 (14650 mined) | 12428 | buzzing |
| arena | 15443 (12030 mined) | 15443 (12030 mined) | 25335 | smart_eco |

Cold fixed, no regressions on butterfly/galaxy/arena.
