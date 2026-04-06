# Bridge Relay Architecture Design

## Problem Statement

Bridge `distance_squared` is capped at 9 (max ~3 tiles in any direction). Harvesters placed more than 3 tiles from the nearest conveyor chain or core cannot be directly bridged. Current buzzing bot falls back to `d.opposite()` conveyor chains for these cases, which:
- Cost +1% scale per conveyor tile
- Leave winding paths on wall-heavy maps
- Are slow to build (one tile per round per builder)

Top bots like Polska Gurom use ~33 bridges per game, suggesting they use **relay points** to chain bridges across arbitrary distances.

## Current Bridge Usage in Buzzing (v42)

1. **Post-harvester bridge shortcut** (lines 290-344): After placing a harvester, tries to bridge to the nearest allied conveyor/splitter/bridge that is closer to core, or directly to a core tile. Only works if target is within dist^2 <= 9.

2. **Navigation bridge fallback** (lines 530-548): When a builder is stuck during nav, tries bridging 2-3 tiles ahead in the top-3 ranked directions. Conservative Ti threshold (bc+20 on non-tight maps).

**Key limitation:** Both only attempt a single bridge hop. If the harvester is 6+ tiles from core/chain, no bridge is built and it falls back to conveyor chains.

## Current Bridge Usage in ladder_bridge

The ladder_bridge bot (lines 162-236) has a simpler approach:
- After building a harvester, finds the nearest allied conveyor/core tile (`_find_bridge_sink`)
- Tries to build a bridge on an adjacent tile pointing to that sink
- If the sink is too far (>dist^2=9), it walks toward core laying conveyors as fallback
- No relay concept -- single hop only

## Bridge Relay Concept

### Core Idea
Chain multiple bridges through intermediate **relay conveyors** to transport resources over arbitrary distances:

```
Harvester -> [Bridge A] -> Relay Conveyor 1 -> [Bridge B] -> Relay Conveyor 2 -> [Bridge C] -> Core/Chain
```

Each bridge covers up to 3 tiles. A relay conveyor receives from the bridge's output and holds the resource stack for the next bridge to pick up from.

### Key Mechanic: How Bridges Move Resources

From the game rules:
- A bridge **outputs** to its target position (within dist^2 <= 9)
- A bridge **accepts** resources from any tile within its footprint (1x1) that isn't the output side
- Resources move in stacks of 10 at end of round

For a relay to work:
1. Bridge A is placed adjacent to harvester, targets Relay Conveyor 1's position
2. Bridge A outputs a stack to Relay Conveyor 1
3. Bridge B is placed adjacent to Relay Conveyor 1, targets Relay Conveyor 2 (or core)
4. Bridge B picks up from Relay Conveyor 1 and outputs to its target

**Critical question:** Can a bridge accept from a conveyor on the same tile or adjacent? The bridge accepts from its non-output sides. The relay conveyor just needs to be at a position that the next bridge can read from. Actually -- the bridge is a building on a tile. The relay conveyor is on a DIFFERENT tile. The next bridge must be placed such that:
- The bridge is adjacent to (or on?) the relay conveyor -- no, bridge is built on an empty tile
- The bridge's **input** comes from adjacent tiles (non-output direction)

**Revised understanding:** Bridges don't "pick up" from conveyors. Bridges accept resource stacks delivered TO them via conveyors (from non-output sides). Then they output to their target tile.

So the actual relay chain is:
```
Harvester -> Conveyor(facing bridge A) -> [Bridge A] -> target tile has Conveyor(facing bridge B) -> [Bridge B] -> target tile -> ... -> Core
```

Wait -- bridge output goes to a TILE. If that tile has a conveyor, the conveyor receives the resource and then outputs in its facing direction. If that tile has another bridge, the bridge receives it.

### Corrected Relay Pattern

```
Harvester(H) outputs to adjacent tile
  -> Conveyor C1 (facing toward Bridge B1 position)
  -> Bridge B1 (placed adjacent to C1, target = position of C2 ~3 tiles away)
  -> C2 receives from B1 output (C2 is at B1's target position)
  -> C2 faces toward Bridge B2
  -> Bridge B2 (adjacent to C2, target = C3 position ~3 tiles away)
  -> ... repeat ...
  -> Final bridge targets a core tile or existing chain conveyor
```

Each relay segment:
- 1 Conveyor (3 Ti, +1% scale) -- receives from previous bridge, feeds next bridge
- 1 Bridge (20 Ti, +10% scale) -- jumps ~3 tiles

### Simplified Pattern (Bridge-to-Bridge)

Can we skip the relay conveyor? If Bridge A outputs to the tile where Bridge B sits, does Bridge B receive the stack?

Bridge accepts from its non-output sides. If Bridge A targets Bridge B's tile, the stack arrives at Bridge B's tile. Bridge B is a building on that tile. The stack would be "delivered" to Bridge B if it arrives from a non-output direction of Bridge B.

**This might work!** If we place bridges in a line:
```
H -> B1(target=B2.pos) -> B2(target=B3.pos) -> B3(target=core)
```

But the bridge needs to accept the incoming stack. A bridge's input sides are all sides except its output direction. Since bridges have a target (not a facing direction per se), the bridge's "output side" is the direction toward its target.

If B1 targets B2's position, B2 receives from the direction of B1. As long as B1 is not in B2's output direction (toward B3), this works.

**Verdict:** Bridge-to-bridge relay MIGHT work if the bridges are not collinear in the same direction (otherwise B2's output direction = toward B3, and input from B1 direction is the opposite = valid). Actually for a straight line: B1 is behind B2 (non-output side), so B2 WOULD accept from B1. This should work!

However, this needs empirical verification. If it works:
- No relay conveyors needed
- Each hop = 1 bridge (20 Ti, +10% scale)
- 3 tiles per hop

If it doesn't work (bridge doesn't accept from another bridge's output):
- Need relay conveyor between each bridge
- Each hop = 1 bridge + 1 conveyor (23 Ti, +11% scale)

## Algorithm

### Phase 1: After placing a harvester, compute relay path

```python
def _compute_relay_path(self, harvester_pos, core_pos, c):
    """Compute a series of waypoints from harvester toward core, ~3 tiles apart."""
    path = []
    current = harvester_pos
    target = core_pos  # or nearest chain tile

    while current.distance_squared(target) > 9:
        # Compute direction from current to target
        d = current.direction_to(target)
        dx, dy = d.delta()

        # Try 3-tile step in that direction
        candidate = Position(current.x + dx * 3, current.y + dy * 3)

        # Clamp to map bounds
        candidate = Position(
            max(0, min(c.get_map_width() - 1, candidate.x)),
            max(0, min(c.get_map_height() - 1, candidate.y))
        )

        # If wall, try adjacent positions (2-tile step, perpendicular offsets)
        if c.get_tile_env(candidate) == Environment.WALL or not c.is_tile_empty(candidate):
            found = False
            for step in (3, 2):
                for alt_d in [d, d.rotate_left(), d.rotate_right()]:
                    adx, ady = alt_d.delta()
                    alt = Position(current.x + adx * step, current.y + ady * step)
                    if (c.is_in_vision(alt)
                            and c.get_tile_env(alt) != Environment.WALL
                            and c.is_tile_empty(alt)
                            and alt.distance_squared(current) <= 9):
                        candidate = alt
                        found = True
                        break
                if found:
                    break
            if not found:
                break  # Can't extend relay, fall back to conveyors

        path.append(candidate)
        current = candidate

    return path
```

### Phase 2: Build relay infrastructure

The builder walks along the relay path, building at each waypoint:

```python
def _build_relay_segment(self, c, pos, relay_path, relay_idx):
    """Build the next relay point and bridge."""
    if relay_idx >= len(relay_path):
        return  # Done

    waypoint = relay_path[relay_idx]

    # If we can build a bridge from current area to this waypoint
    for bd in DIRS:
        bp = pos.add(bd)
        if c.can_build_bridge(bp, waypoint):
            c.build_bridge(bp, waypoint)
            self._relay_idx += 1
            return True

    # Otherwise, need to walk closer to current position or waypoint
    return False
```

### Phase 3: Builder walks relay path

After computing the relay path, the builder needs to:
1. Build bridge from harvester area to waypoint[0]
2. Walk/road to waypoint[0]
3. Build conveyor at waypoint[0] (if needed for relay) facing toward waypoint[1]
4. Build bridge from waypoint[0] area to waypoint[1]
5. Repeat until final waypoint bridges to core/chain

**Builder movement challenge:** The builder needs walkable tiles to reach each waypoint. Options:
- Build roads to each waypoint (cheap, 1 Ti each)
- Use the bridges themselves if passable (they're not -- builders can only walk on conveyors, roads, and allied core)
- Build the relay conveyor first, then bridge -- relay conveyor is walkable

### State Machine for Relay Builder

```
RELAY_PLAN    -> compute path, store in self._relay_path
RELAY_BRIDGE  -> at current position, build bridge to next waypoint
RELAY_WALK    -> walk toward next waypoint (building roads as needed)
RELAY_CONV    -> at waypoint, build relay conveyor facing next segment
RELAY_DONE    -> all segments built, resume normal behavior
```

## Cost Analysis

### Bridge Relay (per 3-tile hop)
| Component | Ti Cost | Ax Cost | Scale Impact |
|-----------|---------|---------|-------------|
| Bridge | 20 | 0 | +10% |
| Relay Conveyor (if needed) | 3 | 0 | +1% |
| Road to waypoint (~2) | 2 | 0 | +1% |
| **Total per hop** | **23-25** | **0** | **+11-12%** |

### Pure Conveyor Chain (per 3 tiles)
| Component | Ti Cost | Ax Cost | Scale Impact |
|-----------|---------|---------|-------------|
| 3 Conveyors | 9 | 0 | +3% |
| **Total per 3 tiles** | **9** | **0** | **+3%** |

### Comparison for Various Distances

| Distance | Bridge Relay Ti | Bridge Relay Scale | Conveyor Ti | Conveyor Scale |
|----------|----------------|-------------------|-------------|----------------|
| 3 tiles | 23 | +11% | 9 | +3% |
| 6 tiles | 46 | +22% | 18 | +6% |
| 9 tiles | 69 | +33% | 27 | +9% |
| 12 tiles | 92 | +44% | 36 | +12% |
| 15 tiles | 115 | +55% | 45 | +15% |

### Bridge Relay Advantages (despite higher cost)
1. **Wall penetration:** Bridges cross walls. Conveyor chains cannot cross walls and must path around them, often adding 2-5x the straight-line distance
2. **Speed:** Bridge is one build action per hop. Conveyor chain requires builder to walk each tile and build sequentially
3. **Reliability:** Straight-line relay path is deterministic. BFS conveyor paths can create winding chains that waste resources
4. **Enemy disruption resistance:** Fewer buildings to destroy along the path (bridges are spread out)
5. **Throughput:** Bridge is instant (1 stack per round). Long conveyor chains have multi-round latency before first delivery

### Bridge Relay Disadvantages
1. **Expensive per hop:** 23 Ti + 11% scale vs 9 Ti + 3% scale for same distance
2. **Scale explosion:** 5 harvesters at 6 tiles each = +110% scale from relay alone
3. **Bridge +10% scale is brutal:** Each bridge adds as much scale as a gunner or launcher
4. **Builder time:** Must walk to each waypoint and build, similar time to conveyor chain
5. **Visibility requirement:** Can only build on tiles in vision -- may not see full path

## When Bridge Relay is Better vs d.opposite() Chains

### Use Bridge Relay When:
- **Harvester is behind walls** that force a long conveyor detour (>2x straight-line distance)
- **Map is wall-heavy** (>30% wall density) where BFS paths are extremely winding
- **Early game** when you need the FIRST resource delivery ASAP (bridge is instant, no pipeline latency)
- **Distance > 8 tiles** where conveyor chain latency matters (8+ rounds for first delivery)

### Use d.opposite() Conveyor Chains When:
- **Clear path** between harvester and core (no walls blocking)
- **Short distance** (<= 5 tiles) where conveyor chain is cheap and fast enough
- **Scale is already high** (>150%) and can't afford +10% per bridge
- **Multiple harvesters** on same axis that can share a conveyor trunk line

### Hybrid Approach (Recommended)
Best strategy combines both:
1. **First 2-3 harvesters:** Pure conveyor chains to keep scale low
2. **Harvesters behind walls:** Bridge relay to cross wall barriers, then join existing conveyor chain
3. **Distant harvesters (>6 tiles):** Bridge relay to nearest existing chain tile, not all the way to core
4. **Chain-join optimization:** Always prefer bridging to an existing chain over building a full relay to core

## Risk Assessment

### High Risk
- **Scale explosion:** Each bridge is +10%. A 4-hop relay adds +40% scale, making ALL future buildings significantly more expensive. This can cripple mid-game military spending.
- **Empirical uncertainty:** Bridge-to-bridge relay (without intermediate conveyors) needs testing. If it doesn't work, cost doubles.

### Medium Risk
- **Builder routing:** Builder must navigate to each waypoint. On wall-heavy maps, this itself requires roads/bridges, adding cost.
- **Vision gaps:** Builder may not see the full relay path when planning. Need incremental planning (compute next segment when arriving at current waypoint).
- **Enemy targeting:** Relay bridges are high-value targets. Destroying one bridge breaks the entire chain.

### Low Risk
- **Complexity:** State machine is straightforward. Main risk is edge cases (walls at waypoints, map edge, occupied tiles).
- **Resource contention:** Bridge relay building competes with harvester/gunner/barrier spending. Need good Ti thresholds.

## Implementation Recommendations

1. **Start with chain-join relay only:** Don't build full relay paths to core. Build 1-2 bridge hops to connect to existing conveyor infrastructure.

2. **Limit relay length:** Max 2-3 hops (2-3 bridges = +20-30% scale). Beyond that, the conveyor chain is more scale-efficient.

3. **Only relay when blocked:** Use relay exclusively when BFS path to chain is >2x straight-line distance (wall detour detected).

4. **Test bridge-to-bridge first:** Run a local test to verify bridges can chain without intermediate conveyors. This halves the cost.

5. **Incremental planning:** Compute one hop at a time (builder's vision is limited). Don't plan the full path upfront.

6. **Priority over conveyor exploration:** When relay is chosen, the builder should NOT lay conveyors along its walking path -- those are wasted scale.
