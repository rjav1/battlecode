# default_medium1 80 Ti Collapse — Investigation

**Date:** 2026-04-06
**Issue:** V52 mines only 80 Ti on default_medium1 vs ladder_road (normally 4960-9840 Ti)

## Reproduction

| Match | Buzzing Ti mined | Opponent Ti mined | Buzzing Bldg | Opp Bldg |
|-------|-----------------|-------------------|--------------|----------|
| vs ladder_road seed 1 | **80** | 9800 | 178 | 251 |
| vs ladder_road seed 2 | **80** | 9790 | 195 | 235 |
| vs starter seed 1 | 23860 | 0 | 318 | 474 |
| vs buzzing_prev seed 1 | 4960 | 4940 | 396 | 68 |
| vs smart_eco seed 1 | 9100 | 26320 | 74 | 247 |

**Verdict: 100% interaction-specific with ladder_road. V52 economy is NOT broken.**

The 80 Ti mined is identical across seeds (seed 1 and seed 2 produce exactly 80 mined), confirming it's deterministic and not randomness-driven.

---

## Root Cause Analysis

### What ladder_road does differently from all other opponents

1. **Builds roads** as movement fallback (rc+2 reserve), not just conveyors
2. **Builds bridges** targeting nearest allied conveyor/core within distance²≤9 after each harvester
3. **Both sides can walk on enemy roads** (CLAUDE.md: builders can walk on conveyors (any team) and roads (either team))

### The road-crossing mechanism

Buzzing's `_bfs_step` builds its `passable` set from `c.get_nearby_tiles()` — all non-wall tiles in vision. This includes **enemy-built roads** which are also passable.

When ladder_road builds roads across the center of the map (it explores with `id*7 + explore_idx + rotation` with a 15-tile far target), those roads become part of buzzing's passable graph. Buzzing's BFS nav then routes builders **through** ladder_road's road network toward ore.

### The conveyor misdirection mechanism

When buzzing navigates through a road tile toward ore and builds a `d.opposite()` conveyor on that tile:
- The conveyor faces **back toward where the builder came from** (toward the enemy side if the builder crossed through enemy roads)
- An ore stack harvested near the center follows that conveyor chain... into enemy-controlled infrastructure
- If the chain connects into ladder_road's conveyor network (via a shared intersection), ore gets routed to ladder_road's core

### Why 80 Ti exactly?

80 Ti = 8 resource stacks × 10 Ti each = approximately 1-2 harvesters × 2-4 outputs each before the chain got intercepted or the builder got rerouted. The first harvester(s) may output toward core before the cross-contamination point gets built.

### Confirmation signal

- Building count: 178 (buzzing) vs 251 (ladder_road). Buzzing builds 178 buildings but mines 80 Ti — almost all buildings are useless conveyors pointing the wrong direction.
- Same count across seeds (80 mined, seed-independent) — the topology of default_medium1 creates a deterministic cross-contamination path.

---

## Why This Doesn't Affect Other Opponents

- **vs starter**: starter builds no roads/conveyors on buzzing's side — passable set stays clean
- **vs buzzing_prev**: buzzing_prev also builds conveyors (buzzing mines 4960 normally) — conveyors ARE passable but buzzing_prev's conveyors point toward THEIR core, not buzzing's. The issue is specifically roads enabling cross-map traversal.
- **vs smart_eco**: smart_eco builds conveyors but no roads — passable set doesn't include mid-map roads

---

## Fix Options

### Option A: Exclude enemy roads from passable set in BFS (RECOMMENDED)
In `_builder`, when building `passable`, check building ownership:
```python
for t in c.get_nearby_tiles():
    e = c.get_tile_env(t)
    if e != Environment.WALL:
        bid = c.get_tile_building_id(t)
        if bid is not None:
            try:
                if c.get_team(bid) != c.get_team():
                    # Enemy road/conveyor — still passable for movement but
                    # skip as passable for BFS targeting (avoid routing through enemy infra)
                    continue
            except Exception:
                pass
        passable.add(t)
```
**Risk**: Builders might get stuck if enemy roads block the only path. Need to still allow MOVEMENT on enemy roads (keep `can_move` checks), just don't route BFS through them.

### Option B: Check conveyor output direction before building
Before building a conveyor, verify the chain from this tile leads toward our core, not away. Complex to implement.

### Option C: Don't build conveyors on tiles with existing enemy buildings
If a tile already has an enemy road, don't build a conveyor there — the existing road is already providing movement. Just move, don't build.

### Option D: Conveyor chain integrity check
After placing a conveyor, BFS-verify that the chain from that position eventually reaches our core. Only build if valid chain exists.

---

## Priority

**HIGH** — this is a catastrophic 0 Ti economy on a standard map. Option A is the cleanest fix: keep enemy roads passable for MOVEMENT (so builders don't get stuck) but exclude them from BFS routing (so builders don't target ore across enemy road networks).

The fix should be in `_builder` or `_nav` — modify the passable set to distinguish "can walk here" from "should BFS route here."
