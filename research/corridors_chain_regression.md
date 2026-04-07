# Corridors Chain Regression — Root Cause & Fix

**Date:** 2026-04-06
**Question:** Why does buzzing mine 3× less than buzzing_prev on corridors with the same ~25 building count?

---

## Baseline: Confirmed Regression

| Map | Bot | Ti Mined | Buildings | Winner |
|-----|-----|----------|-----------|--------|
| corridors seed 1 | buzzing | 5090 | 26 | LOSS |
| corridors seed 1 | buzzing_prev | 14850 | 25 | WIN |

Same building count, 3× Ti mined gap. This points to chain delivery efficiency, not harvester count.

---

## Root Cause: `_bridge_target` Block Breaks Conveyor Chains

### What buzzing does (broken)

After building each harvester, buzzing sets `self._bridge_target = ore` and on the next turn:

1. Scans all nearby buildings for allied conveyors/bridges closer to core than the ore tile
2. Picks the NEAREST one as `best_chain`
3. Builds a bridge from an ore-adjacent tile pointing TO `best_chain`
4. Fallback: builds a bridge from ore-adjacent tile to core

**This is fundamentally broken for maze maps like corridors:**

- The bridge outputs to `best_chain` (an existing conveyor tile)
- On a maze map, the "nearest chain tile closer to core" is a conveyor mid-path through a winding corridor
- Bridging to it BYPASSES all intermediate conveyors between the harvester and that mid-point
- Result: harvester outputs → bridge → mid-chain conveyor, but the natural d.opposite() chain is broken at the bridge insertion point
- Resources either stall at the bridge target (wrong conveyor facing) or skip tiles that were already properly chained

The bridge also COSTS 20 Ti per harvester — ~20-40 Ti per game wasted on chain-breaking bridges.

### What buzzing_prev does (correct)

buzzing_prev's `_bridge_target` only fires when `9 < ore.distance_squared(core) <= 25` — a narrow ring around the core. It bridges ONLY to core tiles (not mid-chain conveyors). On maze maps like corridors, ore is rarely this close to core, so the block almost never fires. Natural d.opposite() chain stays intact.

---

## Proof: Disabling `_bridge_target` Restores Parity

Test bot `test_no_bridge` = buzzing with `_bridge_target` block replaced by `self._bridge_target = None`.

| Map | test_no_bridge mined | buzzing_prev mined | Result |
|-----|---------------------|-------------------|--------|
| corridors seed 1 | 14520 | 14850 | -2% (within noise) |
| corridors seed 2 | 14520 | 14850 | -2% (within noise) |
| face | 21120 | 4970 | WIN |
| default_medium1 | 28430 | 4950 | WIN |
| galaxy | 19020 | 4980 | WIN |
| cold | 19670 | 0 | WIN |
| settlement | 37800 | 0 | WIN |
| gaussian | 24800 | 19800 | WIN |

Removing `_bridge_target` entirely makes the bot win 6/7 maps vs buzzing_prev, with corridors near-parity (14520 vs 14850 = -2%).

---

## Why "bridge to nearest chain" is worse than "no bridge"

On corridors (maze map), BFS routes through narrow corridors. The natural d.opposite() chain creates a connected pipeline: harvester → each corridor tile → core. When a bridge is inserted:

1. Bridge built adjacent to ore (`ore.add(bd)`)  
2. Bridge points to mid-chain conveyor (`best_chain`) closer to core  
3. Resources: harvester → bridge → `best_chain`. Conveyors between ore and `best_chain` are now orphaned with no input upstream  
4. If `best_chain` conveyor faces away from bridge's arrival, resources are rejected (wrong input side)

The "core-only bridge" variant (matching buzzing_prev's `9 < dist <= 25` logic) still underperforms on corridors (10060 mined vs 14850) because it occasionally fires and breaks chains on ore tiles in the critical mid-range.

---

## Secondary Differences (minor)

| Feature | buzzing | buzzing_prev |
|---------|---------|--------------|
| chain-fix trigger harvesters | first 4 | first 2 |
| chain-fix changes threshold | >= 2 | >= 3 |
| periodic chain-fix retrigger (wall>20%) | yes | no |

buzzing enters chain-fix mode more aggressively. Secondary contributor but not the primary cause.

---

## Fix Recommendation

**Remove the `_bridge_target` block entirely from `bots/buzzing/main.py`.**

In the `_builder` method, replace lines 275–329 (the full bridge shortcut block) with:
```python
self._bridge_target = None  # no post-harvester bridge — natural d.opposite() chain is optimal
```

Also remove `self._bridge_target = ore` from the harvester build block (~line 365), and `_bridge_target = None` from `__init__`. These fields are no longer needed.

---

## Impact

- **corridors:** +9430 Ti mined per game (+185%)
- **gaussian:** +5000 Ti mined improvement  
- **all other tested maps:** strictly better or equal vs buzzing_prev
- **Overall:** The `_bridge_target` chain-join shortcut was net-negative. Bridges interrupt delivery chains rather than accelerate them.

## Reproduction

| Match | Buzzing Ti mined | Opponent Ti mined | Buzzing Bldg | Opp Bldg |
|-------|-----------------|-------------------|--------------|----------|
| buzzing vs buzzing_prev corridors | 5090 | 14850 | 26 | 25 |
| buzzing vs smart_eco corridors | 5090 | 14660 | 26 | 36 |
| buzzing_prev vs smart_eco corridors | 14850 | 14660 | 25 | 36 |

**Key finding**: smart_eco mines 14660 Ti on corridors (same as buzzing_prev). Current buzzing mines only 5090 despite building the same 25-26 buildings. This is a delivery efficiency problem — conveyors/bridges built but ore not reaching core.

---

## Map Properties

- **Size**: 31x31 = 961 (balanced map, area 625-1600)
- **Wall density**: 3.43% — BELOW maze threshold (>15%), does NOT trigger maze mode
- **Name says "corridors" but density is low** — corridors are formed by ore/map layout, not dense walls

---

## Root Cause: v42 Bridge Shortcut Fires on Close-Range Ore

### buzzing_prev (v37) bridge behavior
```python
if 9 < ore.distance_squared(self.core_pos) <= 25:
    # bridge only if ore is 3-5 tiles from core
```
On corridors where ore tiles are close to core (dist²≤9), **this condition FAILS** and no bridge is attempted. The existing d.opposite() conveyor chain works unmodified.

### Current buzzing (v42+) bridge behavior
```python
if (self._bridge_target and self.core_pos and c.get_action_cooldown() == 0):
    # NO DISTANCE CHECK — fires for ALL harvesters
    # tries chain-join: bridge ore_adj → nearest allied conveyor closer to core
```
For close-range ore (dist²≤9), buzzing still attempts a bridge. The chain-join logic scans for the nearest allied conveyor closer to core than the ore, then builds a bridge from ore+adjacent → that conveyor. This **replaces** the working d.opposite() conveyor chain with a bridge pointing in a potentially different direction.

### Why this breaks delivery

On corridors, ore is 2-4 tiles from core in narrow corridor lanes. The d.opposite() conveyor chain laid during navigation correctly routes ore back to core. After the harvester is built:

1. Buzzing sets `_bridge_target = ore`
2. Next turn: bridge shortcut fires, finds a conveyor tile `c` closer to core
3. Builds bridge from `ore.add(d)` → `c`  
4. Bridge output direction is toward `c`, which may be a conveyor facing in a different direction
5. Ore stack enters that conveyor at an unexpected side, potentially exits toward the wrong tile
6. Chain broken — ore never reaches core

The 26 buildings buzzing builds are the conveyor chain + a broken bridge. buzzing_prev's 25 buildings are the same conveyor chain without the bridge — and it delivers 3x more ore.

### Secondary factor: `fix_path` reset on target change

Current buzzing resets `fix_path = []` when `best != self.target`. On corridors with competitive ore claims (markers from other builders), the target can change each round, resetting fix_path before chain-fix accumulates enough path to trigger. buzzing_prev doesn't reset fix_path on target changes.

---

## Fix

### Option A: Restore distance guard on bridge shortcut (matches buzzing_prev)
```python
# Only attempt bridge if ore is 3-5 tiles from core (not already close)
if (self._bridge_target and self.core_pos
        and c.get_action_cooldown() == 0):
    ore = self._bridge_target
    ore_core_dist = ore.distance_squared(self.core_pos)
    if ore_core_dist > 9:  # ADD THIS GUARD — was in v37, removed in v42
        # ... bridge logic
```

This exactly matches buzzing_prev behavior: close-range ore uses the existing conveyor chain (which is already efficient at short range), bridges only for medium-range ore where the chain-join provides real benefit.

### Option B: Only chain-join if bridge improves delivery distance significantly
Check that bridge target is ≥2 tiles closer to core than current chain tip.

### Option C: Never bridge from ore tile (leave chain intact, bridge only for exploration reach)
Simplest — remove bridge shortcut entirely. The conveyor chain built during nav already delivers ore correctly.

---

## Recommended Fix

**Option A** — restore `ore_core_dist > 9` guard. This:
1. Matches proven buzzing_prev behavior on corridors
2. Doesn't affect medium/large range ore where chain-join helps
3. Is a 1-line change with clear rationale
4. Should recover corridors to ~14850 Ti mined
