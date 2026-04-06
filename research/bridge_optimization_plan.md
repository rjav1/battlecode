# Bridge Optimization Plan — Close-Harvester Shortcut

## Summary

Bridges replace entire conveyor chains for harvesters near core. Bridge sends
resources directly from output to any tile within distance² ≤ 9 of the bridge's
own position, bypassing direction constraints. A single bridge adjacent to a
harvester can deliver directly to core with no intermediate conveyors, provided
the core tile is within distance² ≤ 9 of the bridge tile.

---

## Bridge Mechanics (from CLAUDE.md)

- `c.build_bridge(pos, target)` — builds at `pos`, outputs to `target`
- Target distance² from BRIDGE position (not builder) must be ≤ 9
- Bridge footprint: 1 tile, accepts from any side, outputs to fixed target
- Cost: 20 Ti + 10% scale (base — grows with every entity built)
- HP: 20 (same as standard conveyor)

Distance² ≤ 9 means the target tile is within a 3-tile Chebyshev radius
(Chebyshev ≠ distance², so more precisely: sqrt(distance²) ≤ 3.0, i.e.
any tile where dx²+dy² ≤ 9 — e.g. (3,0), (2,2), (1,2) all qualify but
(3,1) = 10 does not).

---

## Geometry: When a Bridge Reaches Core

For a bridge at position B adjacent to harvester H, the bridge must reach
any tile of the core (3×3 footprint centered at core_pos). The builder
must be AT or adjacent to H to place the bridge, so the bridge goes on a
tile adjacent to H (adjacent = distance² ≤ 2).

Let core_pos = the core center. Core tiles span positions within Chebyshev
distance 1 of core_pos (9 tiles total).

For the bridge at B to reach a core tile T: `B.distance_squared(T) ≤ 9`

Practical geometry:
- Harvester adjacent to core (distance² ≤ 8 from core_pos): bridge at H
  is almost certainly within distance² ≤ 9 of a core edge tile → direct
  bridge works.
- Harvester 2 tiles from core (distance² ≤ 18): bridge placed between H
  and core may still reach a core edge tile.
- Harvester 3 tiles from core (distance² ≤ 32): harder; depends on exact
  geometry. A conveyor chain of 1–2 tiles is probably easier.

**Rule of thumb:** harvester distance² ≤ 18 from core_pos → worth attempting
a bridge; if `can_build_bridge` passes, use it.

---

## Break-Even Analysis: Bridge vs Conveyor Chain

### Costs (at scale 1.0 = base scale)

| Structure | Ti cost | Scale increase |
|-----------|---------|----------------|
| Conveyor | 3 Ti | +1% |
| Bridge | 20 Ti | +10% |

A chain of N conveyors costs 3N Ti and +N% scale.
A single bridge costs 20 Ti and +10% scale.

**Ti break-even:** Bridge wins when N ≥ 7 conveyors (20 < 3×7=21).
**Scale break-even:** Bridge wins when N ≥ 10 conveyors (+10% < +N×1%).

However, scale compounds — every unit built afterwards pays the cumulative
cost. At early game with few entities, the marginal scale impact per entity
is small, so Ti is the dominant cost:

- 1 conveyor: 3 Ti. Bridge is 6.7× more expensive → bridge loses badly.
- 3 conveyors: 9 Ti. Bridge is 2.2× more expensive → bridge still loses on Ti.
- 6 conveyors: 18 Ti. Bridge is 1.1× more expensive → nearly break-even on Ti.
- 7 conveyors: 21 Ti. Bridge is cheaper on Ti (20 < 21), scale also favored.

**Practical conclusion:** Bridge is worth it ONLY when the chain to core would
require ≥ 7 conveyors (ore is 7+ tiles from core along the actual path,
accounting for walls). For close harvesters (1–3 conveyors needed), bridge is
strictly worse. For mid-range (4–6 conveyors), it's marginal — scale savings
may tip it in favor of bridge late game when scale is already high.

**Why Blue Dragon uses 33 bridges:** They likely use bridges for ALL harvesters
regardless of distance, accepting Ti inefficiency in exchange for simplicity,
reliability (no mis-facing bugs), and coverage of harvesters that are moderately
far (4–6 tiles from core).

---

## Current Code: Bridge Fallback in `_nav`

Location: `bots/buzzing/main.py` lines 448–466

```python
# Bridge fallback (before road — bridges cross walls, roads don't)
if c.get_action_cooldown() == 0:
    ti = c.get_global_resources()[0]
    bc = c.get_bridge_cost()[0]
    map_mode = getattr(self, 'map_mode', 'balanced')
    bridge_threshold = bc + 10 if map_mode == "tight" else bc + 20
    if ti >= bridge_threshold:
        for d in dirs[:3]:
            for step in range(2, 4):
                dx, dy = d.delta()
                bt = Position(pos.x + dx * step, pos.y + dy * step)
                if bt.distance_squared(pos) > 9:
                    continue
                for bd in DIRS:
                    bp = pos.add(bd)
                    if c.can_build_bridge(bp, bt):
                        c.build_bridge(bp, bt)
                        return
```

**Problems with current approach:**
1. Bridge is only tried as a FALLBACK when the builder cannot move or build a
   conveyor. This means bridges never fire during normal ore targeting — only
   when the builder is stuck.
2. The target `bt` is a tile in FRONT of the builder (toward the ore target),
   not toward core. This is wrong for the close-harvester use case — we want
   the bridge to point TOWARD core.
3. Bridges used for wall-crossing during navigation won't help with resource
   delivery (the bridge target is a random forward tile, not the core).

**The harvester build location:** Lines 328–354. After `c.build_harvester(ore)`,
the bot sets `self.target = None` and returns. No bridge is placed.

---

## Proposed Optimization: Post-Harvester Bridge to Core

### Condition for bridge preference

After building a harvester, check:
1. `self.core_pos` is known
2. Harvester ore tile distance² from core_pos ≤ a threshold T
3. `can_build_bridge(ore_adj, core_tile)` succeeds for some adjacent tile

Threshold T: To ensure the bridge tile can reach a core tile within distance²
≤ 9, we need:
- ore tile distance² from core ≤ 18 (ore at most ~4.2 tiles from core center)
- More conservatively: ≤ 12 (about 3.5 tiles) to have high confidence

**Recommended threshold: 20** (gives comfortable margin for diagonal placements).

### Code insertion point

In `_builder` (line 327–354), immediately AFTER `c.build_harvester(ore)`:

```python
c.build_harvester(ore)
self.harvesters_built += 1
self.target = None
self._claimed_pos = None
self._marker_placed = False

# NEW: Try to build a bridge from adjacent to harvester toward core
if (self.core_pos
        and ore.distance_squared(self.core_pos) <= 20
        and c.get_action_cooldown() == 0):
    ti = c.get_global_resources()[0]
    bc = c.get_bridge_cost()[0]
    if ti >= bc + 5:
        # Try each core tile as bridge target
        cx, cy = self.core_pos.x, self.core_pos.y
        core_tiles = [Position(cx + dx, cy + dy)
                      for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        placed = False
        for ct in sorted(core_tiles,
                         key=lambda t: ore.distance_squared(t)):
            for bd in DIRS:
                bp = ore.add(bd)  # bridge adjacent to harvester
                if bp == ore:
                    continue
                if c.can_build_bridge(bp, ct):
                    c.build_bridge(bp, ct)
                    placed = True
                    break
            if placed:
                break
        if placed:
            # Chain-fix not needed — bridge handles delivery
            self.fix_path = []
            return

# existing chain-fix logic...
```

### Alternative insertion: dedicated `_build_harvester_bridge` helper

Called from `_builder` right after the `build_harvester` call, keeps the main
flow clean.

---

## Risk Assessment

### Low risk
- `can_build_bridge` is a reliable guard — if the geometry doesn't work, it
  simply won't fire. No danger of mis-placed bridges.
- Only triggers when Ti threshold is met (bc + 5), so economy is protected.

### Medium risk
- **Wasted Ti on bridges that don't help.** If the ore is within 2 tiles of core,
  a single conveyor (3 Ti) would suffice. A bridge (20 Ti) here wastes 17 Ti
  early game. Mitigate: only attempt bridge when ore distance² > 8 (not immediately
  adjacent to core) AND ≤ 20.
- **Scale inflation.** Each bridge costs +10% vs +1% per conveyor. If we build 5
  bridges instead of 5 single conveyors, scale jumps +50% vs +5%. This makes
  later units (harvesters, gunners) significantly more expensive. Mitigate: only
  use bridge when it replaces ≥ 3 conveyors (distance² > 8 from core).

### High risk (conditional)
- **Over-eager bridging on open maps.** If 80% of harvesters are within 3 tiles
  of core (unusual), aggressively bridging every one inflates scale badly. On
  maps where ore is clustered near core, a single conveyor chain is optimal.
  Mitigate: use the ore-distance threshold strictly.

---

## Expected Elo Impact

**Upside (why Blue Dragon does this):**
- Eliminates conveyor mis-facing bugs for close harvesters
- Resources start flowing immediately (no multi-tile chain to lay)
- Frees builder sooner to seek next ore (skips chain-building phase)
- One bridge is far harder for enemy attackers to sever than a 4-conveyor chain

**Realistic Elo gain:** +20 to +50 Elo if we currently lose games due to early
resource flow delays or broken conveyor chains near core.

**Downside risk:** -10 to -30 Elo on maps with ore clustered near core (wastes
Ti on bridges that 1-2 conveyors would handle for 1/7th the cost).

**Net recommendation:** Implement with distance guard (ore distance² 9–20 from
core). Skip bridge if ore is very close (distance² ≤ 8) where 1 conveyor suffices.
This should be a strict improvement on open maps with moderate ore distance.

---

## Implementation Priority

1. Add `_build_harvester_bridge(c, ore)` helper
2. Call it in `_builder` right after `build_harvester`
3. Gate on: `ore.distance_squared(core_pos) in range (9, 21)`
4. Test on maps: galaxy (open, ore far), butterfly (ore-rich near core), cold
   (diamond walls, ore offset), arena (tight, close ore)
5. Run `cambc test-run buzzing starter` on 3+ maps before deploying

---

## Open Questions

1. Does `can_build_bridge` check that the bridge tile itself is buildable (not
   a wall, not occupied)? Yes — standard build guard.
2. Can a bridge output directly to a core tile? Core tiles are NOT walls and
   accept resources. Should work.
3. Does the builder need to be adjacent to the bridge tile to build it? Yes —
   action radius = 2 (distance² ≤ 2 from builder). Builder on the ore tile can
   build bridges on all 8 adjacent tiles including the ore tile itself.
4. Can bridge be placed ON the harvester tile? No — harvester occupies that tile.
   Bridge goes on an adjacent tile. Builder standing on ore tile can build bridge
   on any adjacent empty tile within distance² ≤ 2, which covers all 8 neighbors.
