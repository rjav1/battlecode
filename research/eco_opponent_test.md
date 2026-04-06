# Eco Opponent Comparative Test — April 6, 2026

## Summary

**The current buzzing bot is COMPLETELY BROKEN. It mines 0 Ti on every map.**

Task #9 (another agent) modified `bots/buzzing/main.py` to build roads instead of conveyors during exploration. The new chain-building code (lines 127-174) tries to build conveyors at the builder's current position, but that position already has a road from the outbound trip. You can't build a conveyor on a tile that already has a building. Result: zero conveyor chains, zero resource delivery, zero Ti mined.

## CRITICAL: Regression from Task #9

The original buzzing bot built conveyors with `face = d.opposite()` during `_nav()`. This created breadcrumb chains that, while wasteful, DID deliver resources (16690 Ti on landscape seed 1, 18890 Ti on cold seed 1).

The modified buzzing bot (current version) builds only roads during `_nav()` and attempts to build a conveyor chain after placing a harvester. But the chain code at line 154 calls `c.can_build_conveyor(pos, d_to_core)` — this fails because `pos` already has a road (the builder is standing on it). **The result is that NO conveyors are ever built, NO resources flow, and the bot runs on passive income only.**

## Eco Opponent Design

The eco_opponent bot uses the proven `d.opposite()` conveyor approach:
- Core spawns 3 builders immediately
- Builders explore using conveyors facing `d.opposite()` (creates chain back toward start)
- Adjacent to Ti ore: build harvester
- No military, no attacks, pure economy

## Test Results: buzzing (current/broken) vs eco_opponent

| Map | buzzing Ti (mined) | eco_opponent Ti (mined) | Winner |
|-----|-------------------|------------------------|--------|
| default_medium1 | 4,084 (0) | 46,239 (44,900) | eco_opponent |
| landscape | 1,719 (0) | 12,694 (9,770) | eco_opponent |
| cold | 3,428 (0) | 26,180 (24,170) | eco_opponent |
| corridors | 4,638 (0) | 14,879 (9,930) | eco_opponent |

**Buzzing mines 0 on all maps. eco_opponent mines 9,930-44,900 per map.**

## Eco Opponent vs Starter (baseline verification)

| Map | eco_opponent Ti (mined) | starter Ti (mined) |
|-----|------------------------|--------------------|
| default_medium1 | 34,935 (31,920) | 2,976 (0) |
| cold | 17,829 (19,660) | 428 (0) |

eco_opponent works correctly and vastly outperforms starter.

## Root Cause Analysis

The bug in the current buzzing bot is in the interaction between two code sections:

### 1. `_nav()` method (lines 301-346) — builds ROADS only
```python
# Line 311-314: Modified by task #9
if c.can_build_road(nxt):
    c.build_road(nxt)
    return
```
Every tile the builder walks onto gets a road. Roads cost 1 Ti (+0.5% scale) — cheap but NOT conveyors, so resources can't flow through them.

### 2. Chain-building code (lines 127-174) — tries to build conveyors on existing roads
```python
# Line 154: Tries to build conveyor at builder's current position
if c.can_build_conveyor(pos, d_to_core):
    c.build_conveyor(pos, d_to_core)
```
This ALWAYS fails because `pos` already has a road from the outbound trip. `can_build_conveyor` requires an empty tile.

### Why it fails silently
When `can_build_conveyor` returns False, the code falls through to movement (line 159), which moves the builder toward core. The builder walks the whole way back to core without building any conveyors, then resumes exploring, laying more roads. The harvester sits isolated, never connected.

## Fix Required

**Option A (Quick fix): Destroy road before building conveyor in chain code**
```python
# In chain code, destroy the road first
bid = c.get_tile_building_id(pos)
if bid is not None:
    c.destroy(pos)  # remove road
# Then build conveyor
c.build_conveyor(pos, d_to_core)
```

**Option B (Revert to working approach): Build conveyors during outbound nav**
Change `_nav()` back to building conveyors with `face = d.opposite()` instead of roads. This is the approach that mined 16690+ Ti.

**Option C (Best of both): Build conveyors facing toward core during outbound nav**
```python
# In _nav(), build conveyor facing toward core instead of d.opposite()
face = nxt.direction_to(self.core_pos)
if face == Direction.CENTRE:
    face = d.opposite()
```
BUT: this doesn't create connected chains (as tested — direction-toward-core from each tile creates a fan, not a chain). The `d.opposite()` approach works because it creates step-by-step connectivity.

**Recommended: Option B (revert to d.opposite() conveyors in _nav())** — it's proven to work and deliver resources. Then later optimize to reduce wasted conveyors.

## Immediate Action Needed

1. Revert `_nav()` to build conveyors with `face = d.opposite()` instead of roads
2. Remove or fix the broken chain-building code (lines 127-174)
3. Re-test to confirm Ti mining is restored
4. THEN work on efficiency improvements (reduce wasted conveyors)
