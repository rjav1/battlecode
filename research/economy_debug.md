# Economy Debug Report — April 4, 2026

## Context
Lost ladder match 1-4 against 1493 Elo team. All 5 games went to 2000 rounds, all decided by Resource Victory. Lost on: landscape, battlebot, cold, corridors. Won on: pls_buy_cucats_merch.

## Raw Test Results: buzzing vs starter

| Map | Seed | Winner | Our Ti (mined) | Their Ti (mined) | Our Buildings | Their Buildings |
|-----|------|--------|----------------|------------------|---------------|-----------------|
| landscape | 1 | buzzing | 17168 (16690) | 2082 (0) | 162 | 556 |
| landscape | 42 | buzzing | 19503 (19270) | 2493 (0) | 176 | 624 |
| battlebot | 1 | buzzing | 13494 (9850) | 4271 (0) | 110 | 255 |
| battlebot | 42 | buzzing | 17591 (14160) | 4169 (0) | 109 | 268 |
| cold | 1 | buzzing | 21008 (18890) | 380 (0) | 115 | 697 |
| cold | 42 | buzzing | 4591 (7840) | 2001 (0) | 391 | 646 |
| corridors | 1 | buzzing | 14863 (9940) | 2876 (0) | 19 | 466 |
| corridors | 42 | buzzing | 18833 (14420) | 1939 (0) | 59 | 562 |
| pls_buy_cucats_merch | 1 | **starter** | 43 (0) | 188 (0) | 270 | 901 |
| pls_buy_cucats_merch | 42 | **starter** | 4531 (0) | 1837 (0) | 34 | 693 |

**Key observation:** We beat starter on all maps except pls_buy_cucats_merch. The starter mines 0 Ti on every map — it only builds roads, not conveyors, so resources never flow to core. Our losses are NOT against the starter bot; they're against a real 1500-Elo opponent who presumably has a better economy.

## Self-Play Results: buzzing vs buzzing

| Map | P1 Ti (mined) | P2 Ti (mined) | P1 Buildings | P2 Buildings |
|-----|---------------|---------------|--------------|--------------|
| landscape | 22566 (19160) | 9814 (9780) | 105 | 155 |
| battlebot | 18106 (13760) | 19855 (15600) | 55 | 69 |
| cold | 11922 (17050) | 20332 (19730) | 437 | 180 |
| corridors | 19034 (14380) | 19202 (14410) | 23 | 30 |
| pls_buy_cucats_merch | 4298 (0) | 4849 (0) | 34 | 36 |

## Identified Root Causes

### ROOT CAUSE #1: pls_buy_cucats_merch — 0 Ti mined (CRITICAL)

**Both sides mine 0 Ti** on this map. The map has 60 Ti ore tiles but Nearest Ti = `*` (unreachable with 4-dir BFS). It requires diagonal movement through wall gaps to reach ore.

Our bot builds conveyors and roads in 8 directions but the BFS in `_bfs_step()` only considers tiles in the `passable` set (non-wall tiles in vision). The problem is the bot can't pathfind through diagonal wall gaps because the tile on the other side of the gap may not be visible or passable from BFS perspective.

**Impact:** Guaranteed loss on this map (and likely butterfly, pixel_forest, sierpinski_evil, wasteland_oasis — all 6 diagonal-gap maps).

**Fix:** Need to verify whether the engine allows diagonal movement through wall corners. If it does, our pathfinding works. If it doesn't, we need to handle these maps with a different strategy (pure passive income, max builder spawns for tiebreaker on unit count).

### ROOT CAUSE #2: Massive building waste — conveyors built along winding paths (HIGH)

Evidence from cold seed 42: Mined 7840 Ti but only have 4591 — spent 3249 Ti on 391 buildings. On cold seed 1: mined 18890, have 21008, only 115 buildings. The difference is **276 extra buildings** on the bad seed.

The code at `main.py:259-261`:
```python
face = d.opposite()
if c.can_build_conveyor(nxt, face):
    c.build_conveyor(nxt, face)
```

Every builder builds a conveyor on EVERY tile it walks onto, facing backward. If the builder wanders (BFS finds a winding path, stuck detection kicks in and redirects), it lays conveyors along the entire winding path. These conveyors:
1. Cost 3 Ti each (at base, more with scale)
2. Each adds +1% to cost scale — 100 wasted conveyors = +100% cost scaling
3. Most don't connect to any harvester chain, so they deliver nothing

**Impact:** On bad seeds, we waste thousands of Ti on useless conveyors and inflate cost scaling to 200-400%, making harvesters and builders prohibitively expensive.

### ROOT CAUSE #3: No chain validation — conveyors don't form connected paths to core (HIGH)

A conveyor built at position X facing `d.opposite()` points back toward where the builder came from. But the builder came from a conveyor that faces... the direction the builder was walking BEFORE that step. So we get chains like:

```
Core <- Conv(WEST) <- Conv(SOUTHWEST) <- Conv(SOUTH) <- Harvester
```

This chain is BROKEN. A conveyor accepts from 3 non-output sides and outputs in its facing direction. If Conv(SOUTHWEST) outputs SOUTHWEST but Conv(WEST) is not southwest of it, the resource flow doesn't connect.

Actually, re-reading the rules: conveyors accept from 3 non-output sides. So Conv(WEST) at position (5,5) accepts from NORTH, SOUTH, EAST (all non-WEST sides). If Conv(SOUTHWEST) is at (6,6) and outputs SOUTHWEST toward (5,7), it does NOT feed (5,5). The chain breaks whenever the builder changes direction.

**Impact:** Many harvesters may be "connected" by a chain of conveyors but the chain has direction mismatches so resources never actually flow to core.

### ROOT CAUSE #4: Harvester placement favors proximity to core, not ore density (MEDIUM)

`_best_adj_ore()` at line 305-311 picks the ore tile closest to core. This means builders near core build harvesters on nearby ore first, even if distant ore clusters are much richer. On maps like cold (115 Ti tiles, massive southern deposits), our builders may harvest only the few tiles near core while ignoring the rich deposits further away.

**Impact:** Suboptimal harvester placement. We mine fewer tiles than possible.

### ROOT CAUSE #5: Self-play shows huge P1/P2 variance (MEDIUM)

On landscape: P1 mined 19160, P2 mined 9780 (2x difference with same code). On cold: P1 mined 17050, P2 mined 19730. The only difference is starting position. This means our economy is very sensitive to map topology relative to core position — some directions from core have ore, others don't, and our exploration is not adaptive enough.

### ROOT CAUSE #6: Builder cap too low early game (MEDIUM)

Line 33: `cap = 2 if rnd <= 40 else (4 if rnd <= 200 else ...)`

Only 2 builders for the first 40 rounds. This means only 2 units exploring/harvesting. If one gets stuck, we have 50% exploration capacity. Competitive bots likely spawn 3-4 builders immediately.

### ROOT CAUSE #7: Attacker builder wastes economy (LOW)

Line 106-108: After round 400, builders with `my_id % 4 == 2` become attackers. This removes 25% of builders from the economy. On maps where attack can't reach the enemy (high walls, long paths), this is pure waste.

### ROOT CAUSE #8: Sentinel spending drains Ti (LOW)

Sentinels cost 30 Ti base (+20% scale) and need 10-stack ammo delivery. On pure economy maps, sentinels are a net negative — they cost resources and don't generate any. Building 2 sentinels costs ~60+ Ti that could have been 3 harvesters.

## Priority Ranking of Fixes

### P0: Fix conveyor chain efficiency
- **Don't build a conveyor on every step.** Only build conveyors when they form a valid chain toward core.
- Track the direction from current position to core. Only build conveyors whose output direction points toward core (or at least doesn't point away).
- Consider building conveyors ONLY on the return trip from harvester to core, not during outbound exploration.

### P1: Reduce wasted building spending  
- Add a budget for exploration conveyors. After N conveyors without a harvester, switch to roads (cheaper, lower scale impact).
- Or: explore on existing conveyors/roads first before building new ones.

### P2: Fix pls_buy_cucats_merch (and 5 other diagonal-gap maps)
- Test empirically whether diagonal movement through wall corners works.
- If not, implement a passive-only strategy for these maps (maximize passive income, spawn builders for unit count tiebreaker).

### P3: Increase early builder count
- Spawn 3 builders in first 20 rounds instead of capping at 2 for 40 rounds.
- The 30 Ti cost is recovered quickly if the builder finds ore.

### P4: Smarter harvester targeting
- Don't just pick nearest ore to core. Consider ore density — a cluster of 5 ore tiles is worth walking further for.
- Prioritize building harvesters on ore tiles that are already adjacent to existing conveyor chains.

### P5: Defer sentinels and attackers on economy maps
- Don't build sentinels until round 400+ or until we have 4+ harvesters producing.
- Don't assign attacker role until we have 6+ harvesters.

## Specific Code Changes Needed

### Change 1: Conveyor direction validation (P0)
In `_nav()`, before building a conveyor, check if it actually contributes to a chain toward core:
```python
# Only build conveyor if its output direction has a component toward core
face = d.opposite()  # current code
core_dir = pos.direction_to(self.core_pos)
# Check if face is roughly toward core (within 90 degrees)
if not self._dir_toward(face, core_dir):
    # Build road instead (cheaper, no chain pollution)
    if c.can_build_road(nxt):
        c.build_road(nxt)
```

### Change 2: Exploration uses roads, not conveyors (P1)
During exploration (no target), build roads instead of conveyors. Only build conveyors on the path between a discovered ore tile and core.

### Change 3: Early builder cap (P3)
```python
cap = 3 if rnd <= 30 else (5 if rnd <= 200 else (7 if rnd <= 500 else 9))
```

### Change 4: Defer military spending (P5)
```python
# Sentinel: only after 4+ harvesters globally
if self.harvesters_built < 4:
    return False
# Attacker: only after round 600 and 3+ harvesters per builder
if c.get_current_round() <= 600 or self.harvesters_built < 3:
    return  # stay as economy builder
```

## Comparison: What 1500 Elo Opponents Likely Do Better

1. **Directed conveyor chains**: Build conveyors in a planned path from ore to core, not as breadcrumbs behind the builder.
2. **More harvesters faster**: 3-4 harvesters by round 100, we might have 1-2.
3. **Less wasted spending**: Fewer dead-end conveyors, lower cost scaling.
4. **Ore scouting**: Dedicated scout builders that use roads (cheap) to find ore, then dedicated chain-builders that lay conveyor paths.
5. **Axionite economy**: Refining axionite and delivering to core for the #1 tiebreaker. We mine 0 axionite.

## Next Steps

1. Implement P0 fix (conveyor direction validation) and re-test
2. Run against starter on all 5 maps to verify improvement
3. Run self-play to check consistency improvement
4. If pls_buy_cucats_merch is unsolvable (engine blocks diagonal gaps), implement passive strategy
5. Consider axionite harvesting for tiebreaker advantage
