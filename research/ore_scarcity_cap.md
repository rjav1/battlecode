# Ore-Scarcity Builder Cap Research

## Date: 2026-04-08
## Context: Phase 1 (core_dist * 4) scored 64% — approximately neutral. Exploring ore-scarcity-based builder capping.

---

## The Problem

Our builder cap logic (lines 87-109 in main.py) is purely time-based and map-size-based:
- Tight: 3 -> 5 -> 8 over time
- Balanced: 3 -> 4 -> 6 -> 8 over time
- Expand: 3 -> 5 -> 8 -> 15 over time

Then `econ_cap = max(time_floor, vis_harv * 3 + 4)` gates it further, but `time_floor` keeps rising regardless of ore availability. On expand maps, `time_floor` reaches 15 by round 1400.

**The result:** On ore-sparse maps, we spawn 8-10 builders that wander looking for ore, each costing 30 Ti + 20% scale. They lay conveyors during exploration that carry nothing. MergeConflict uses 2 builders and beats us.

---

## Where to Implement: Core's `_core` Method

The core has vision r^2=36 (6 tiles in each direction). It can count visible ore tiles at spawn time. This is a CORE-SIDE change, not a builder change.

### Current flow (lines 83-138):
```
1. Check action cooldown
2. Count units (line 85)
3. Compute time-based cap (lines 87-92)
4. Count visible harvesters (lines 94-101)
5. Compute econ_cap (lines 102-109)
6. If units >= min(cap, econ_cap): don't spawn
7. Check Ti affordability
8. Spawn builder
```

### Proposed change: Add ore-scarcity gate between steps 5 and 6

```python
# Count visible Ti ore (core vision r^2=36)
if not hasattr(self, '_vis_ore_count'):
    ore_count = 0
    for tile in c.get_nearby_tiles():
        env = c.get_tile_env(tile)
        if env == Environment.ORE_TITANIUM:
            bid = c.get_tile_building_id(tile)
            if bid is None:  # unoccupied Ti ore
                ore_count += 1
    self._vis_ore_count = ore_count

# Ore-scarcity cap: fewer builders when little ore is visible
if self._vis_ore_count < 8:
    ore_cap = 4  # sparse ore: max 4 builders
elif self._vis_ore_count < 15:
    ore_cap = 6  # moderate ore
else:
    ore_cap = cap  # abundant ore: use normal cap
cap = min(cap, ore_cap)
```

---

## Design Analysis

### Why snapshot once (not per-round)?

The ore count only needs to be checked ONCE because:
1. Ore tiles don't change during the game (they're map features)
2. Occupied ore (with harvesters) gets filtered out, but we want the initial count of available ore to set the builder budget
3. Per-round scanning would reduce the cap over time as harvesters get placed, which is the OPPOSITE of what we want (we want a fixed budget)

**However**, snapshotting at round 1 is problematic: the core only sees ore within r^2=36, which misses distant ore clusters. A snapshot at round 1 would always show "sparse ore" on maps like wasteland_oasis where ore is far from core.

### Alternative: Snapshot at round 20-30 (after first builder has explored)

This doesn't work either -- builders are separate Player instances with no way to communicate ore counts back to the core (markers store u32 values, not ore counts, and the encoding is already used for claim markers).

### Better alternative: Dynamic ore tracking in core

Count UNOCCUPIED ore in core vision every round. As harvesters get placed, the unoccupied count drops. When unoccupied ore in vision = 0, stop spawning new builders (all nearby ore is harvested).

```python
# Every spawn decision: count unoccupied Ti ore in core vision
vis_free_ore = 0
for tile in c.get_nearby_tiles():
    env = c.get_tile_env(tile)
    if env == Environment.ORE_TITANIUM:
        bid = c.get_tile_building_id(tile)
        if bid is None:
            vis_free_ore += 1

# If no free ore visible near core, cap builders tightly
if vis_free_ore == 0 and rnd > 50:
    cap = min(cap, units + 1)  # allow at most 1 more builder
elif vis_free_ore < 4:
    cap = min(cap, 5)
```

**Problem:** This is expensive -- iterating `get_nearby_tiles()` every round in the core. Core vision has ~113 tiles (pi * 36). But core only runs once per round, so ~113 iterations is fine.

**Bigger problem:** Core vision (r^2=36, ~6 tiles) only sees nearby ore. On maps where ore is 10+ tiles from core, the core sees 0 ore and would never spawn enough builders. This would KILL performance on maps like wasteland_oasis, cold, or gaussian where ore clusters are far from the core.

---

## Risk Analysis

### Maps where ore-scarcity cap HELPS:
- **Tight maps with limited ore** (arena, default_small): Few ore tiles near core. Extra builders find nothing, just waste Ti and scale.
- **Maps with clustered ore** (hooks, face): Ore is concentrated. Once harvested, no need for more builders.

### Maps where ore-scarcity cap HURTS:
- **Spread-out maps** (wasteland_oasis, galaxy, cold): Ore is far from core. Core sees 0 ore in vision, would cap builders at 4-5, preventing exploration of distant ore that IS there but requires walking.
- **Expand maps**: The whole point is exploring outward for ore. A tight cap kills this.

### The fundamental tension:
The core doesn't know if ore exists beyond its vision. Capping based on visible ore penalizes maps where ore IS there but far away.

---

## Recommended Approach: Harvester-Based Cap (Safer)

Instead of counting ore tiles (unreliable due to limited core vision), cap based on **harvesters built** -- a proxy for "ore found and used."

The core already counts `vis_harv` (visible harvesters, lines 94-101). But this only sees harvesters in core vision (r^2=36), missing distant harvesters.

**Better proxy:** Use scale percentage as a proxy for total building activity.

```python
scale = c.get_scale_percent()  # starts at 100.0
if scale > 200.0:  # we've built enough that costs doubled
    cap = min(cap, 3)  # stop spawning, we're overbuilt
elif scale > 150.0:
    cap = min(cap, 5)
```

This is map-agnostic, doesn't need ore visibility, and directly addresses the root cause (scale inflation from too many entities). When scale > 200%, every new entity costs 2x -- spawning another 30 Ti builder (which now costs 60 Ti) that might lay 10 conveyors (which now cost 6 Ti each) is clearly negative-value.

---

## Final Recommendation

### Primary: Scale-based builder cap (SAFEST)

Add after line 108:
```python
scale = c.get_scale_percent()
if scale > 200.0:
    cap = min(cap, 3)
elif scale > 150.0:
    cap = min(cap, 5)
```

**Why this is safer than ore-scarcity cap:**
- Works on ALL maps regardless of ore distribution
- Directly targets the root cause (scale inflation)
- Doesn't need to guess about invisible ore
- MergeConflict wins with low scale (32 conveyors + 2 bots = ~92% scale). We lose with high scale (101 conveyors + 10 bots = ~301% scale)
- Simple, 4 lines, no new data structures

### Secondary: Visible-ore cap in core (MODERATE RISK)

Only if scale-based cap passes baseline. Count free Ti ore in core vision at round 30 (after first builder leaves). If < 4 free ore tiles visible, cap at 4 builders.

**Risk:** Kills expand maps where ore is far from core.

### Tertiary: Marker-based ore reporting (HIGH COMPLEXITY)

Builders report ore findings via markers. Core reads markers to decide spawning. Too complex for the 66% baseline constraint.

---

## Implementation Notes

- `c.get_scale_percent()` returns float starting at 100.0
- Each conveyor adds +1% (101.0 after 1 conveyor)
- Each builder bot adds +20% (120.0 after 1 bot)
- Scale 200.0 means everything costs 2x base
- At 10 bots + 80 conveyors: scale = 100 + 200 + 80 = 380% -- everything costs 3.8x
- At 3 bots + 30 conveyors: scale = 100 + 60 + 30 = 190% -- everything costs 1.9x
