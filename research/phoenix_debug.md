# Phoenix Debug: Why 0 Ti on Cold/Hooks/etc

## Date: 2026-04-08

---

## Bug Found: Conveyor Direction Was Backwards

In `_nav_conveyors`, conveyors were built with `face = d.opposite()`. Since the builder walks TOWARD core during chain mode, `d` points toward core and `d.opposite()` points AWAY from core. Resources flowed away from core — backwards.

**Fix applied:** `face = d` (conveyors face toward core). Resources now flow correctly: harvester → chain → core.

**Impact:** Fixed resource flow direction, but didn't fix the 0 Ti problem on cold/hooks/default_small1/default_large1/wasteland_oasis. The issue is deeper.

---

## Root Cause: Builder Can't Retrace Outbound Path Through Mazes

### The problem on cold (maze map):

1. Builder walks OUTBOUND via roads, using BFS to navigate around walls
2. BFS finds a winding path through the maze: e.g., east → south → east → north → east
3. Builder builds harvester at ore
4. Builder enters chain mode, walks BACK toward core building conveyors
5. Return BFS starts from harvester position, trying to navigate to core
6. Return BFS finds a DIFFERENT path (or gets stuck at walls)
7. Builder builds conveyors on dead-end paths, never reaching core
8. Result: 306 buildings (mostly dead-end conveyors), 0 Ti delivered

### Why this doesn't affect buzzing:
Buzzing builds conveyors DURING the outbound walk. The conveyor chain IS the path. Every conveyor faces `d.opposite()` (toward core). The chain is built as the builder walks, so it naturally follows the BFS path. No retrace needed.

### Why this doesn't affect face/arena/default_medium1:
These maps have few or no walls. The return path is a straight line — no maze navigation needed. BFS trivially finds the core.

---

## Missing Features Causing 0 Ti

### 1. No bridge fallback in `_nav_conveyors`
Buzzing's `_nav` has a bridge fallback (lines 447-464) for crossing walls. Phoenix's `_nav_conveyors` only tries conveyors and roads. On wall-heavy maps, the builder gets permanently stuck.

### 2. No path memory
The builder doesn't remember its outbound path. It can't retrace roads it built. Each BFS call starts fresh from the current position.

### 3. Builder walks away before chain connects
The debug shows builders building harvesters at round 15-20 (core_dist 64-80), then slowly walking back. Builder 1 reaches core_dist=5 by round 31. But by then, other builders are also building harvesters and chains, all competing for Ti.

---

## Phoenix vs Buzzing on Face (Detailed)

| Metric | Phoenix | Buzzing |
|--------|---------|---------|
| Ti mined | 4,990 | 9,910 |
| Buildings | 101 | 107 |
| Total Ti | 9,568 | 13,886 |

Phoenix mines HALF what buzzing mines on face, with similar building count. The 2x travel time (outbound roads + inbound conveyors) means phoenix builds harvesters later. Each harvester produces less total Ti over the game because it was built later.

**Face is a tight map (20x20).** Even here, buzzing's 1-pass approach is faster. The road savings (1 Ti vs 3 Ti per tile, ~10 tiles = 20 Ti saved) don't compensate for the delayed harvesters (each round of delay = ~2.5 Ti lost per harvester).

---

## Fundamental Design Flaw

The phoenix architecture has an irreducible problem: **the return trip is wasted time.**

| Architecture | Outbound | Return | Total | Conveyors |
|-------------|----------|--------|-------|-----------|
| Buzzing | Build conveyors while walking | No return needed | N rounds | N |
| Phoenix | Build roads while walking | Build conveyors while walking back | 2N rounds | N |

Both architectures build the SAME number of conveyors. Phoenix just takes TWICE as long because it makes two trips. The 2 Ti saved per tile (road vs conveyor on outbound) is dwarfed by the N rounds of delayed harvester production.

**The math:** 
- Saving: ~10 tiles × 2 Ti/tile = 20 Ti saved on roads vs conveyors
- Cost: ~10 rounds of delayed harvester = 10 × 2.5 Ti/round = 25 Ti lost
- Net: -5 Ti per harvester. **Roads are net negative even ignoring maze issues.**

---

## Conclusion

Phoenix is architecturally inferior to buzzing for a fundamental reason: any 2-pass approach (outbound + return) takes 2x the rounds of a 1-pass approach (buzzing). The conveyor-during-walk design is not just simpler — it's faster.

The only way roads+bridges beats conveyors is if bridges can SKIP most of the chain (reaching ore in 1-2 hops instead of 5-10 conveyors). But bridge r^2=9 (3 tiles) means you still need chains for anything beyond 3 tiles from core.

**Phoenix is a dead end. V61 buzzing remains the correct architecture.**
