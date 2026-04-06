# Chain Census via Markers: Feasibility Analysis

## Problem Statement

Our bot builds 30-43 harvesters but collects 2-3x LESS Ti than opponents with 8-22 harvesters. The root cause (documented in `chain_connectivity_truth.md`) is that `d.opposite()` conveyor chains follow the builder's wandering path, and diagonal movement creates gaps that silently disconnect chains. Resources enter disconnected conveyors and never reach the core.

**Question:** Can we use markers to detect and repair broken chains?

---

## Feasibility Assessment: NOT RECOMMENDED

**Verdict: A chain census system via markers is the wrong tool for this problem.** The analysis below explains why, and proposes the actual fix.

### Why markers can't solve chain breaks

1. **Markers occupy tiles (they ARE buildings).** Placing diagnostic markers on or near conveyors blocks future building on those tiles. Every marker placed for census purposes is a tile permanently consumed (until destroyed).

2. **1 marker per unit per round.** A builder scanning a 20-conveyor chain can only mark 1 tile per round. A full census of one chain takes 20+ rounds — by which time the chain state may have changed.

3. **No unit can read another unit's conveyor state remotely.** Builder A can see if a conveyor near it has `get_stored_resource() == None`, but this only means the conveyor is currently empty — NOT that the chain is broken. Harvesters output 1 stack every 4 rounds, so conveyors are legitimately empty 75% of the time.

4. **False positive rate is catastrophic.** A conveyor that just passed its resource downstream is empty. A conveyor waiting for the next harvester cycle is empty. A conveyor on a chain where the harvester was just built (first output is immediate, but subsequent ones are every 4 rounds) is empty. Distinguishing "empty because broken" from "empty because normal flow" requires tracking resource stack IDs over multiple rounds — far too CPU-expensive.

5. **Repair is harder than detection.** Even if a builder identifies a gap, fixing it requires:
   - Walking to the gap location (may be far away)
   - Determining correct conveyor facing to bridge the gap
   - Having enough Ti to build
   - Not disrupting adjacent conveyors in the process
   
   The builder would need to reconstruct the intended chain direction from local context only, which is extremely error-prone.

6. **The real problem is upstream of census.** The chains are broken because `_nav()` builds them wrong (diagonal gaps). Detecting broken chains after the fact and dispatching repair crews is a Rube Goldberg solution. **Fix the chain construction instead.**

---

## What Markers COULD Do (Limited Value)

If we still wanted marker-based chain diagnostics, here's the best encoding:

### Proposed Encoding (32-bit marker value)

```
Bits 31-28: Type tag (4 bits, 16 types)
  0x0 = ore claim (existing, value=1)
  0x1 = chain health beacon
  0x2 = enemy sighting
  0x3-0xF = reserved

Bits 27-16: Round number (12 bits, mod 4096)
Bits 15-0:  Payload (16 bits, type-dependent)

Chain health beacon payload:
  Bits 15-8: Chain ID (harvester entity ID mod 256)
  Bits 7-4:  Conveyor count in chain (0-15)
  Bits 3-0:  Last observed gap count (0-15)
```

### Detection Algorithm (if implemented)

```python
def _scan_chain(self, c, pos):
    """Scan nearby conveyors for chain health. O(n) where n = nearby buildings."""
    my_team = c.get_team()
    empty_conveyors = 0
    total_conveyors = 0
    for eid in c.get_nearby_buildings():
        try:
            if (c.get_entity_type(eid) == EntityType.CONVEYOR 
                    and c.get_team(eid) == my_team):
                total_conveyors += 1
                if c.get_stored_resource(eid) is None:
                    empty_conveyors += 1
        except Exception:
            pass
    # Heuristic: if >80% of conveyors empty after round 50, chain likely broken
    if total_conveyors > 3 and empty_conveyors / total_conveyors > 0.8:
        return True  # probably broken
    return False
```

**CPU cost:** ~50-100 microseconds per scan (iterating nearby buildings). Acceptable within 2ms budget but wasteful given the high false positive rate.

### Repair Algorithm (if implemented)

```python
def _find_gap(self, c, pos):
    """Find a conveyor whose output tile has no conveyor."""
    my_team = c.get_team()
    for eid in c.get_nearby_buildings():
        try:
            if (c.get_entity_type(eid) != EntityType.CONVEYOR 
                    or c.get_team(eid) != my_team):
                continue
            conv_pos = c.get_position(eid)
            conv_dir = c.get_direction(eid)
            output_tile = conv_pos.add(conv_dir)
            if not c.is_in_vision(output_tile):
                continue
            output_bid = c.get_tile_building_id(output_tile)
            if output_bid is None:
                # Gap found: this conveyor outputs into empty space
                return (conv_pos, conv_dir, output_tile)
        except Exception:
            pass
    return None
```

**Problem:** This finds gaps but can't determine where the chain SHOULD go. The output tile might be empty because:
- It's the end of a chain (harvester side) — no gap
- It's a diagonal gap — need to trace back to find the intended path
- It's a deliberate dead-end (exploration conveyor not on a chain)

Without knowing the intended chain topology, repair is guesswork.

---

## The Actual Fix: Prevent Broken Chains

### Root Cause (from chain_connectivity_truth.md)

1. **Diagonal steps produce no conveyor** — `can_build_conveyor(pos, SOUTHWEST)` returns False because conveyors only face cardinal directions. Builder walks diagonally, no conveyor placed, gap created.

2. **Wandering paths create unnecessarily long chains** — BFS navigation + d.opposite() means the conveyor chain follows every twist of the builder's path, not a direct route to core.

### Fix 1: Cardinal-only navigation for chain building (HIGH IMPACT)

In `_nav()`, when the builder has a harvester target (not exploring), decompose diagonal steps into two cardinal steps:

```python
# In _nav(), when building toward ore:
if d in (NE, SE, SW, NW):
    dx, dy = d.delta()
    horiz = EAST if dx > 0 else WEST
    vert = SOUTH if dy > 0 else NORTH
    # Try horizontal first, then vertical on next round
    for card_d in [horiz, vert]:
        nxt = pos.add(card_d)
        if c.can_build_conveyor(nxt, card_d.opposite()):
            c.build_conveyor(nxt, card_d.opposite())
            return
        if c.can_move(card_d):
            c.move(card_d)
            return
```

**Trade-off:** 2 steps instead of 1 diagonal, but every step gets a conveyor. Chain is guaranteed connected for cardinal turns (proven in chain_connectivity_truth.md).

### Fix 2: Direct-path conveyor chains (HIGHEST IMPACT, more complex)

Instead of building conveyors as the builder walks, build a dedicated chain AFTER harvester placement:
1. Builder walks to ore using roads (cheap, 0.5% scale vs 1% for conveyors)
2. After placing harvester, builder retraces to core building conveyors on a computed straight-line cardinal path
3. Chain follows the shortest cardinal path, not the builder's wandering route

This is essentially what `_fix_chain()` already attempts, but done proactively and with a computed optimal path rather than retracing the wandering walk.

### Fix 3: Bridge-based chains (MEDIUM IMPACT, expensive)

For nearby harvesters (dist_sq <= 9 from core), skip conveyors entirely and use a bridge. One bridge replaces an entire chain. Cost: 20 Ti + 10% scale, but saves multiple conveyors worth of scale.

---

## Integration Points (for the actual fixes, not census)

### Fix 1 integration:
- Modify `_nav()` (line 411-445): Add diagonal decomposition when builder has a harvester target
- No new state, no markers, no inter-unit communication needed
- ~15 lines of code

### Fix 2 integration:
- After `c.build_harvester(ore)` (line 332): compute cardinal path from harvester to core
- New method `_build_direct_chain(c, start, end)`: BFS cardinal-only pathfinding + conveyor placement
- Requires multi-round stateful build (similar to sentinel splice)
- ~50-80 lines of code

### Fix 3 integration:
- In `_best_adj_ore()` or harvester build section: check if ore is within bridge range of core
- If yes, build bridge instead of conveyor chain
- ~10 lines of code

---

## Testing Strategy

1. **Visual verification:** Run `cambc run buzzing_fix buzzing --watch` on galaxy/arena, inspect conveyor chains in visualizer for gaps
2. **Resource comparison:** Compare `get_global_resources()` at round 500/1000/2000 between old and new
3. **Key maps:** galaxy (diagonal-heavy, open), cold (wall clusters), corridors (cardinal-forced), butterfly (fragmented)
4. **A/B on ladder:** Submit and compare Elo trajectory over 20+ matches

---

## Expected Elo Impact

| Approach | Expected Impact | Confidence |
|----------|----------------|------------|
| Chain census via markers | +0 to +10 Elo | Low — high false positive rate, repair is unreliable |
| Fix 1: Cardinal decomposition | +30 to +60 Elo | Medium — eliminates diagonal gaps, proven mechanism |
| Fix 2: Direct-path chains | +50 to +100 Elo | Medium-High — shortest chains, lowest scale inflation |
| Fix 3: Bridge for nearby ore | +10 to +20 Elo | Medium — only helps close ore, but very cheap to implement |

**Recommendation:** Implement Fix 1 first (quick, safe), then Fix 2 (higher impact but more complex). Skip chain census entirely — it treats symptoms rather than the disease.

---

## Summary

The chain census approach via markers is **technically possible but practically useless** for this problem:
- High false positive rate (empty ≠ broken)
- Markers consume tiles
- Repair without topology knowledge is guesswork  
- CPU budget better spent on other things

The correct fix is **preventing broken chains** by ensuring `_nav()` only builds cardinal-direction conveyor steps, eliminating the diagonal gap problem at its source. This requires no markers, no inter-unit communication, and no detection/repair loop.
