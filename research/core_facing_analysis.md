# Core-Facing Conveyor Analysis

**Date:** 2026-04-08  
**Question:** Replace `face = d.opposite()` with `face = pos.direction_to(self.core_pos)` in `_nav()` line 429. Would this work? What breaks?

---

## Current Behavior: `face = d.opposite()`

When a builder at `pos` moves in direction `d` to `nxt`:
- It builds a conveyor on `nxt` facing `d.opposite()`
- If moving EAST, the conveyor faces WEST — i.e., output goes WEST (back toward where the builder came from)
- This is correct: the builder walks away from core, so `d.opposite()` points back toward core

**When this is correct:** Builder is walking in a straight line away from core. Every conveyor faces back the way the builder came = toward core. Resources chain correctly.

**When this breaks:** Builder zigzags around walls. The BFS step might route NORTH to avoid a wall, then EAST, then SOUTH. Each conveyor faces opposite its local step direction. The chain becomes: NORTH conveyor faces SOUTH, EAST conveyor faces WEST, SOUTH conveyor faces NORTH. Resources from a harvester at the end flow into the first conveyor they reach, but then the chain is disconnected — each segment points toward where it was placed from, not toward core. **This already breaks on any non-straight path** — which is why V61 sometimes loses resource flow on wall-heavy maps.

---

## Proposed: `face = pos.direction_to(self.core_pos)`

Every conveyor placed on `nxt` faces toward core from `pos` (the builder's current position).

### Does it fix resource flow?

**Yes, mostly.** Every conveyor independently points toward core. On any path shape (straight, zigzag, L-shaped), every conveyor faces the correct general direction. Resources placed at `nxt` by a harvester flow in the core direction immediately.

**The critical question:** Do adjacent conveyors connect?

Conveyor mechanics: a conveyor accepts resources from its **3 non-output sides** and outputs in its **facing direction**. For two adjacent conveyors A → B to chain:
- B must face toward core
- A must be on one of B's 3 non-output sides (i.e., A must NOT be in B's facing direction)

With `pos.direction_to(core)`:
- Both A and B face roughly the same direction (toward core)
- A is typically behind B (farther from core)
- B faces toward core, so its output side faces toward core, and its input sides are the other 3 — including the side where A sits

This works as long as both conveyors point in the **same direction**. If A and B are on a straight radial path from core, they both face toward core along the same axis — chain works perfectly.

**Edge case: diagonal paths.** If A is at (5,5) facing NORTHWEST (toward core at 0,0) and B is at (6,5) (east of A) also facing NORTHWEST: B's output is NORTHWEST, its 3 input sides are S, E, NE. A is to the EAST of B — that's one of B's input sides. Chain works.

**Edge case: sharp bends.** Builder walks EAST 3 steps then NORTH 3 steps. All 6 conveyors face toward core. The EAST segment faces NORTHWEST, the NORTH segment faces NORTHWEST. They all share the same facing. At the corner tile, the eastward conveyor and the northward conveyor are adjacent — they will both try to output NORTHWEST. The corner tile receives from east and sends northwest — that's fine.

### Does it break walkability?

**No.** Builders can walk on conveyors facing any direction. The facing direction only affects resource routing, not traversal. A builder can step onto a conveyor facing SOUTHEAST even while walking NORTH.

### Does it break the harvester connection?

The harvester outputs 1 stack every 4 rounds. It outputs to **any adjacent tile** that can accept (has a conveyor with an open input side facing away from the harvester). 

With `d.opposite()`: the last conveyor placed before the harvester faces back toward where the builder walked from — which is the builder's previous position, roughly toward core. The harvester is placed adjacent. For the harvester to feed the chain, the last conveyor must have the harvester on one of its input sides.

With `pos.direction_to(core)`: same logic applies. The last conveyor placed (at `nxt`) faces toward core. The harvester is built adjacent. Whether the harvester lands on an input side of that conveyor depends on the exact geometry.

**Specific risk:** Builder walks to ore tile, builds conveyor on the step just before ore, then builds harvester on ore. The last conveyor faces toward core. The harvester is adjacent — but the harvester is NOT between the conveyor and core; it's on the ore tile which may be in any direction. If the ore tile happens to be on the output side of the last conveyor (i.e., between the conveyor and core), the harvester can't feed into it.

This is the **main breakage risk**: if the ore tile is approximately between the builder and the core, the last conveyor faces toward core = toward the ore tile. The ore tile is on the output side of the conveyor. Harvester on output side = conveyor won't accept from the harvester.

---

## Comparison Table

| Scenario | `d.opposite()` | `pos.direction_to(core)` |
|---|---|---|
| Straight path toward ore | Works perfectly | Works perfectly |
| Zigzag around walls | **Broken** — each segment disconnected | Works — all face core |
| Ore tile between builder start and core | Works (harvester feeds first conveyor) | **Broken** — last conveyor faces harvester, won't accept from it |
| Ore tile past core (far side) | Broken (rare) | Works |
| Large open map | Works | Works |
| Tight corridor map | Often broken | Works (main improvement) |

---

## Net Assessment

**`pos.direction_to(core)` is a genuine improvement for wall-heavy maps.** The current `d.opposite()` already fails silently on any non-straight BFS path — which is every non-trivial map. Core-facing fixes that.

**The harvester connection edge case is real but rare.** It only triggers when ore is roughly between the spawn point and the core — an unusual geometry. Most ore is at map edges far from core, making the last conveyor face away from ore toward core (correct).

**Estimated impact:**
- Tight/corridor maps: +10-20% resource delivery improvement (fewer dead-end conveyor segments)  
- Open maps: ~0% change (paths already mostly straight)
- Failure case: ~5-10% of ore tiles where geometry puts ore "inward" — these lose delivery entirely

**Recommendation:** Test with a prototype bot. The improvement on zigzag paths likely outweighs the inward-ore edge case. A hybrid might be ideal: `pos.direction_to(core)` when `pos.distance_squared(core) > ore.distance_squared(core)` (ore is farther than builder from core), `d.opposite()` otherwise.

---

## Implementation Note

The change is exactly 1 line in `_nav()` at line 429:
```python
# Current:
face = d.opposite()

# Proposed:
face = pos.direction_to(self.core_pos)
```

Requires `self.core_pos` to be set before `_nav()` is called — it already is (set in `__init__` via core detection). Zero other changes needed.

**Risk level:** Low for prototype. The fallback road mode and bridge fallback are unaffected. Worst case on the edge case: harvester exists but chain is broken, builder builds a bridge on next visit to reconnect.
