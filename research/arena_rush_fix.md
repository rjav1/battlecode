# Arena Rush Fix Analysis — RESOLVED

## Final Result: WE NOW WIN ARENA 5/5 SEEDS

| Seed | buzzing mined | ladder_rush mined | winner |
|------|---|---|---|
| 1 | 14670 | 14530 | **buzzing** |
| 2 | 14670 | 14530 | **buzzing** |
| 3 | 14670 | 14530 | **buzzing** |
| 4 | 14670 | 14530 | **buzzing** |
| 5 | 14670 | 14530 | **buzzing** |

## Root Cause: Two Bugs Introduced by Concurrent Agents

The original arena problem (11606 vs 12192 mined before agent modifications) was already close. Two bugs introduced by concurrent agent work (task #61: "Reduce exploration conveyor waste") completely broke arena performance:

### Bug 1: `use_roads=True` during exploration
**File**: `_nav()` and `_explore()` in bots/buzzing/main.py

The task #61 agent added `use_roads=True` when no ore was visible during exploration. This modified `_nav()` to build roads instead of conveyors. However, roads are NOT passable (only conveyors/roads of specific types are). Actually roads ARE passable — but the navigation code structure with `use_roads` caused builders to fail to reach ore tiles because the road-building branch interfered with normal movement. **This reduced mined Ti from ~14670 to ~1220** (a 92% reduction).

**Fix**: Removed all `use_roads` logic. `_nav()` and `_explore()` now always use conveyors.

### Bug 2: `explore_reserve = 200` when far from core
**File**: `_explore()` in bots/buzzing/main.py

The task #61 agent changed the exploration Ti reserve from `30 (if core_dist_sq > 50)` to `200 (if core_dist_sq > 50)`. This meant builders needed 203+ Ti to lay exploration conveyors when more than ~7 tiles from core. Since Ti is rarely that high, builders exploring away from core **could not build conveyors** and got stuck on non-passable terrain. This caused seeds 3-5 to mine only 600-1620 Ti.

**Fix**: Restored `explore_reserve = 30 if core_dist_sq > 50 else 5`.

## Additional Fix: Earlier Gunner on Tight Maps

While investigating, we also changed gunner timing:
- **Before**: `gunner_round = 60 if map_mode == "tight"`
- **After**: `gunner_round = 30 if map_mode == "tight"`

Rush builders arrive by round 20-30. A gunner at round 30 (instead of 60) can start firing before rushers establish themselves in our base. This contributes to defense.

## Current State

After fixes, performance on arena:
- buzzing mines 14670 vs ladder_rush 14530 (buzzing wins by mined tiebreaker)
- Consistent across all seeds (results are identical — arena is deterministic with symmetric positions)

Performance on other maps (vs ladder_rush seed 1):
- default_medium1: **buzzing wins** (350 vs 0 mined)
- galaxy: **buzzing wins** (9950 vs 4980 mined) 
- cold: **buzzing wins** (1650 vs 0 mined)
- corridors: **buzzing wins** (14790 vs 14620 mined)
- face: **ladder_rush wins** (2560 vs 4970 mined) — next target
- settlement: **buzzing wins** by huge margin

## face Map: Next Target

Face is another tight/rush map (path=9). We lose 2560 vs 4970 mined. Same defense problem as arena was. Now that arena is fixed, face should be analyzed similarly.

## Key Lesson

**Do not let exploration conveyor reduction optimizations break navigation**. The original `explore_reserve = 30` was calibrated carefully — at 30+ Ti, builder builds exploration conveyors; below 30, it just moves on existing passable tiles (core tiles). The 200 value was too high and broke builder mobility.
