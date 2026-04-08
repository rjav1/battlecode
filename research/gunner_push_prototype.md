# Gunner Push Prototype — Research Results

**Date:** 2026-04-08  
**Bot:** bots/buzzing_v5/main.py (copy of V61 + rush code)  
**Goal:** Kill enemy core on binary_tree via offensive rush

---

## Key Mechanics Discovered

### Builder Attack is NOT viable for core kills

From CLAUDE.md: "Attack: 2 damage to building on own tile, costs 2 Ti + action cooldown"

The builder's `c.fire(target)` attack is a "self-tile attack" — it damages the building ON THE BUILDER'S OWN TILE. The builder must be STANDING on the enemy building to attack it.

**Critical constraint:** Builders can only walk on Conveyors (any team), Roads (either team), Allied core. Enemy core tiles are NOT walkable. Therefore:
- Builder cannot stand on enemy core tiles
- Builder cannot fire at enemy core

This eliminates the builder-attack approach entirely.

### Gunner vision r²=13 means very close placement required

Gunner fires at "first targetable tile on forward ray within r²=13 (~3.6 tiles)". Enemy core must be within 3.6 tiles of the gunner to be targeted. On binary_tree (cores ~20 tiles apart), the gunner must be placed adjacent to the enemy core.

### Ammo delivery is the bottleneck

Gunner needs 2 Ti stacks per shot. Ammo delivered via conveyors from non-facing directions. To place a gunner near the enemy core, you need:
1. A builder to reach within 3.6 tiles of enemy core (via roads or conveyors)
2. A conveyor chain from your Ti economy to the gunner

The problem: roads don't carry resources. If the builder advances via roads, the gunner gets no ammo. If it advances via conveyors, the conveyors face BACKWARD (toward our core), carrying resources TO our core, not TO the gunner.

---

## Implementation Attempts

### Attempt 1: Builder attack (wrong mechanic)
Tried `c.fire(pos.add(d))` on adjacent core tiles — returned `can_fire=False` for all adjacent tiles. Discovery: builder fires at OWN tile only.

### Attempt 2: Builder attack on own tile
Fixed to `c.fire(pos)` when standing on enemy building. Builder navigated to enemy core center via roads. But:
- The predicted enemy core position was WRONG (symmetry detection failed for binary_tree)
- Builder attacked its own roads instead of enemy core tiles
- Fixed symmetry: used `farthest mirror = 180° rotation` which was correct for binary_tree

### Attempt 3: Gunner placement near enemy core
Builder walks via `_nav` (with BFS wall routing) toward enemy core. When within r²=13, places gunner facing enemy core. 

**Findings:**
- Gunner placed at round 93-400 (varies by seed) at dsq=4-10 from enemy core
- Gunner faces correct direction 
- But gunner gets ZERO ammo — no conveyor chain connects to it
- Roads don't carry resources; the approach path is roads

### Attempt 4: Conveyor approach for ammo chain
Switched from roads to conveyors for approach. Builder lays conveyors from our core area to gunner position. 

**Findings:**
- Conveyors cost 3 Ti each, +1% scale each
- 20+ conveyors to reach enemy core = 60+ Ti + 20% scale increase
- Economy tanks: Ti mined drops from 16k to 5k vs V61
- Still doesn't work: conveyors face BACKWARD (toward our core), not toward gunner
  - Conveyor at position X facing direction D outputs to X+D
  - Builder moving EAST places conveyor facing WEST (opposite of movement)
  - This creates a chain that carries resources from ore tiles TOWARD our core, not toward the gunner

---

## Root Cause Analysis

### Why top bots (Blue Dragon, 2834 Elo) kill cores by round 297

We cannot determine their exact strategy from observation. Possibilities:
1. They build gunners MUCH earlier with a more efficient path
2. They use a different conveyor routing that feeds gunner ammo
3. They use a completely different mechanism (mass builders? sentinels?)
4. They have specialized per-map code for binary_tree specifically

### Why our approach fails

The ammo delivery problem requires a FORWARD-facing conveyor chain (delivering from core area TO gunner), which is opposite to how harvester chains work (delivering from ore TO core).

To build a forward chain:
- Build conveyors facing TOWARD the gunner (not away from core)
- This requires the builder to lay them in the OPPOSITE order — place from gunner end back to core end
- Or: use a bridge to jump resources from the main chain to the gunner directly

### Binary_tree map-specific issues

- Our core starts at (10,16) (not (2,2) as assumed)
- Enemy core 180° rotation: (30,13)
- BFS path through binary_tree walls is 36+ steps with many narrow corridors
- Builder gets stuck at wall junctions without BFS routing
- Adjacent tiles near enemy core all occupied by our roads when builder arrives

---

## Current State (buzzing_v5)

The rush code is included but economy-disabled (`rush_map = False`). With rush disabled, V5 performs approximately equal to V61 (14400 vs 14760 Ti mined on default_small1 vs starter).

With rush enabled, economy drops 40-60% on binary_tree due to:
1. Multiple builders designated as rushers (id%5==3 matches 2+ builders)
2. Road/conveyor building consumes Ti needed for harvesters
3. Gunner gets no ammo — fails silently

---

## Viable Path Forward

### Option A: Forward conveyor chain to gunner (complex)
After placing gunner near enemy core, builder needs to:
1. Walk BACK from gunner toward our main conveyor chain
2. Build conveyors FACING toward the gunner (opposite direction)
3. Bridge the gap between existing chain and new forward chain
Estimated: 40+ lines of new code, significant testing required.

### Option B: Early gunner on tight maps only (simpler)
On actual tight maps (arena, default_small1, area≤625):
- Cores are only 10-15 tiles apart
- Gunner placed 3-4 tiles from our core can target enemy core within r²=13
- Our existing conveyor chain is right there for ammo delivery
This is the correct target for a gunner rush — NOT binary_tree.

### Option C: Multiple builder swarm (experimental)
Send 3+ builders to enemy core area via roads. Each builder tries to stand on an enemy CONVEYOR tile (walkable) adjacent to the enemy core. Can they fire at the core? No — `fire()` attacks building on OWN tile, and conveyors adjacent to core are not the core itself.

### Conclusion: Not ready for deployment

The gunner push prototype is NOT ready for competition. The core challenge (ammo delivery to enemy-adjacent gunner) is unsolved. Recommend shelving until Sprint 4 deadline and focusing on economy improvements for current Elo range (1461, rank 144).

---

## Test Results Summary

| Test | Result | Notes |
|------|--------|-------|
| V5 (rush off) vs starter, binary_tree | 15k Ti (win) | Competitive |
| V5 (rush off) vs V61, default_small1 | 14.4k vs 14.8k | ~Equal |
| V5 (rush on) vs V61, binary_tree | 5k vs 16k | Rush kills economy |
| V5 (road rush) vs starter, binary_tree | 13-22k Ti (win) | Depends on seed |
| Core destroyed by round 297? | NO | Never achieved |
