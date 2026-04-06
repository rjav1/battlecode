# Constrained Maps Failure Analysis: cold, corridors, shish_kebab

## Executive Summary

Our bot's core economic mechanism — the `d.opposite()` conveyor trail — breaks down on constrained maps because **every tile the builder walks on gets a conveyor, creating long winding chains that don't actually connect harvesters to the core**. The builder lays conveyors as navigation infrastructure (to walk on), not as intentional resource pipelines. On open maps this accidentally works because paths are short and roughly straight. On constrained maps, the chains zigzag through corridors and never form a connected path back to core.

**The ONE fix: Stop building conveyors during navigation. Only build conveyors as a deliberate chain FROM a harvester BACK TO the core.**

---

## Map-by-Map Root Cause Analysis

### 1. cold (37x37, 115 Ti ore) — Mining 5K vs opponent's 23K

**Root cause: Conveyor chains are disconnected spaghetti.**

cold has 7.2% walls but the 8-dir path between cores is 12 while the 4-dir path is 28. This means diagonal shortcuts exist but cardinal paths wind. Our builder navigates using BFS and lays `d.opposite()` conveyors on EVERY tile it walks through.

Trace through a specific example on cold:
- Builder spawns at core (12,14), targets ore at (20,24) — 10 tiles of Ti ore in the southern region
- BFS finds a path that zigzags around wall clusters: goes SOUTH, then SOUTHEAST, then EAST, then SOUTH again, then SOUTHWEST...
- Each step builds a conveyor facing `d.opposite()`:
  - Step SOUTH → conveyor facing NORTH
  - Step SOUTHEAST → conveyor facing NORTHWEST  
  - Step EAST → conveyor facing WEST
  - Step SOUTH → conveyor facing NORTH
  - Step SOUTHWEST → conveyor facing NORTHEAST

**The problem**: These conveyors point in random directions. A conveyor facing NORTHWEST feeds into whatever is to its northwest — NOT necessarily the next conveyor in the chain. The chain only works if the path is perfectly straight or if adjacent conveyors happen to align. On a winding path, conveyor A outputs NORTHWEST but conveyor B (which came from a different step direction) is to the NORTH, not NORTHWEST. **Resources fall off the chain.**

On cold specifically:
- 115 Ti ore tiles exist, many in dense clusters in the south
- Builders reach ore and build harvesters (good)
- Harvesters output resources but the conveyor chain back to core is broken at every turn
- Resources pile up in conveyors mid-chain or get sent into walls/nowhere
- Result: 5K Ti from the few harvesters whose chains happen to be straight enough

**Why smart_eco gets 4x more**: smart_eco has the SAME `d.opposite()` bug but spawns 8 builders (vs our 3-5 capped by `econ_cap = vis_harv * 2 + 3`). More builders = more harvesters = more chances that SOME chains work. Also smart_eco has no military overhead (no barriers, gunners, attackers eating resources and rounds).

### 2. corridors (31x31, narrow passages) — Exactly 9,930 Ti every game

**Root cause: Deterministic builder behavior + broken chains = fixed output.**

corridors has a regular grid of wall columns creating corridors. Path between cores is 46 steps (vs Euclidean ~20). The suspiciously exact 9,930 Ti breaks down as:

- **Passive income**: 10 Ti every 4 rounds × 2000 rounds = 5,000 Ti passive
- **Harvester income needed**: 9,930 - 5,000 = 4,930 Ti from harvesters
- **Per harvester**: 1 stack of 10 Ti every 4 rounds = 2.5 Ti/round. Over ~1960 productive rounds ≈ 4,900 Ti
- **This is almost exactly 1 harvester's full output reaching core**

So our bot builds multiple harvesters on corridors, but only ONE has a conveyor chain that actually connects back to core. The rest have broken chains due to corridor zigzagging.

Why exactly 9,930 and not 9,900 or 10,000:
- 1 harvester producing from ~round 40 to round 2000: (2000-40)/4 = 490 stacks × 10 Ti = 4,900 Ti
- Passive: (2000/4) × 10 = 5,000 Ti  
- Slight variation from exact harvester build timing: 4,900 + 5,000 = 9,900, close to 9,930
- The extra 30 Ti likely from a second harvester whose partial chain delivers a few stacks before breaking

**The corridor zigzag problem in detail**: corridors force builders to go EAST, then NORTH (around column), then EAST, then SOUTH (around next column). Each direction change creates a conveyor pointing the wrong way. A chain of E→N→E→S conveyors creates: W-facing, S-facing, W-facing, N-facing. The S-facing conveyor outputs SOUTH, but the next conveyor in the path is to the EAST. **Complete disconnect.**

### 3. shish_kebab (20x20, 5 regions) — 0-6 losses

**Root cause: Walls between regions + bridge threshold too high + scarce resources.**

shish_kebab has 5 diagonal diamond-shaped regions separated by walls. With 8-dir movement, all regions connect via diagonal gaps (path=19). Only 10 Ti and 4 Ax — extremely scarce.

Problems compound here:
1. **Bridge threshold is too high**: `bridge_threshold = bc + 10` on tight maps (bridge costs 20 Ti base, so threshold = 30+ Ti). On a map with only 10 Ti ore tiles and 500 starting Ti, we can't afford to be picky about bridges. But the real issue is bridges aren't even the right solution — diagonal movement through wall corners should work without bridges.

2. **`d.opposite()` chains across diagonal gaps are useless**: When a builder squeezes through a diagonal wall gap (moving SOUTHEAST), it places a NORTHWEST-facing conveyor. But the wall gap is exactly 1 tile wide — there's nothing to the NORTHWEST except wall. The conveyor output goes nowhere.

3. **Scarce resources amplified**: With only 10 Ti tiles, every harvester matters. If even 2-3 harvester chains are broken, that's 20-30% of total Ti production lost. Meanwhile the opponent (likely smart_eco or similar) also struggles but gets more harvesters connected by using more builders.

4. **Builder cap strangles economy**: `econ_cap = vis_harv * 2 + 3` means with 0 visible harvesters, cap = 3 builders. On a 5-region map, 3 builders can't cover all regions. By the time they find ore and build harvesters, the game is half over.

---

## The Fundamental Flaw: Conveyors as Navigation vs. Conveyors as Pipelines

Our bot conflates two completely different purposes:

| Purpose | What we do | What we should do |
|---------|-----------|-------------------|
| **Navigation** | Build conveyor on every tile we walk on | Build ROADS (cost 1 Ti, +0.5% scale) |
| **Resource pipeline** | Hope the `d.opposite()` trail connects | Build a deliberate chain from harvester to core AFTER placing the harvester |

The `d.opposite()` trick works ONLY when the builder walks in a straight line from core to ore. On any map with walls, corridors, or turns, it creates disconnected conveyor spaghetti.

### Why smart_eco mines more despite the same bug

smart_eco (`bots/smart_eco/main.py`) uses the identical `d.opposite()` navigation pattern. But it outperforms because:

1. **No military overhead**: No barriers (cost 3 Ti each, +1% scale), no gunners (10 Ti, +10% scale), no attacker bots wasting rounds
2. **More builders (8 vs 5-7)**: More builders = more harvesters = more lottery tickets for chains that happen to work
3. **No `econ_cap` throttle**: smart_eco doesn't limit builders based on visible harvesters. Our bot's `econ_cap = vis_harv * 2 + 3` means we need to see harvesters near core before spawning more builders — but on constrained maps, harvesters are far from core and often not visible
4. **No rounds wasted on sentinel infrastructure**: Our builders spend 5+ rounds each on the gunner state machine (destroy conveyor, build splitter, build branch, build gunner). On constrained maps this is pure waste

### But smart_eco still has the same fundamental problem

smart_eco would ALSO fail to get maximum output on constrained maps because its conveyor chains also break on turns. The gap between smart_eco and a truly optimized bot on corridors would be similar — maybe 12K vs the theoretical 20K+.

---

## The ONE Highest-Leverage Fix

### Use roads for navigation, build conveyor chains only as deliberate harvester→core pipelines

**Specific code change in `_nav()` (line 203-235 of `bots/buzzing/main.py`):**

Replace the current approach where `_nav()` builds a conveyor on every step with:

```python
def _nav(self, c, pos, target, passable):
    """Navigate toward target using ROADS, not conveyors."""
    dirs = self._rank(pos, target)
    bfs_dir = self._bfs_step(pos, target, passable)
    if bfs_dir is not None and bfs_dir != dirs[0]:
        dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]

    w, h = c.get_map_width(), c.get_map_height()
    for d in dirs:
        nxt = pos.add(d)
        if nxt.x < 0 or nxt.x >= w or nxt.y < 0 or nxt.y >= h:
            continue
        # Build ROAD for navigation (1 Ti, +0.5% scale vs 3 Ti, +1% scale)
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            rc = c.get_road_cost()[0]
            if ti >= rc + 5:
                if c.can_build_road(nxt):
                    c.build_road(nxt)
                    return
        if c.get_move_cooldown() == 0 and c.can_move(d):
            c.move(d)
            return
    # Bridge fallback stays the same
    ...
```

**Then add a new method `_build_conveyor_chain()` called AFTER building a harvester:**

```python
def _build_conveyor_chain(self, c, harvester_pos):
    """After placing a harvester, walk back toward core building conveyors."""
    # BFS from harvester_pos to core_pos through passable tiles
    # For each step in the path, build a conveyor facing toward core (d toward core)
    # This creates a CONNECTED chain because we compute the full path first
    self.chain_target = self.core_pos
    self.chain_mode = True  # Flag: builder is in chain-building mode
```

### Why this fixes all 3 maps:

1. **cold**: Roads let builders navigate cheaply through winding paths. After placing a harvester on the rich Ti deposits, the builder walks back toward core, building conveyors that actually face toward core at each step. Chain is connected by construction.

2. **corridors**: Roads through the corridor grid (1 Ti each, 0.5% scale — much cheaper than 3 Ti conveyors at 1% scale). After harvester placement, deliberate conveyor chain follows the corridor path back. Even if the chain zigzags E→N→E→S, each conveyor faces the NEXT conveyor in the chain, not `d.opposite()` of the walk direction.

3. **shish_kebab**: Roads through diagonal wall gaps. Conveyors only placed on the return path from harvester to core. On a 20x20 map with 5 regions, this means short chains with correct facing.

### Additional benefits:
- **3x cheaper navigation**: Roads cost 1 Ti vs conveyors at 3 Ti. On corridors (46-step path), that's 46 Ti vs 138 Ti just to reach the first ore
- **50% less scale inflation**: Roads add +0.5% vs conveyors at +1%. 46 roads = +23% scale vs 46 conveyors = +46% scale
- **No wasted conveyors**: Currently we build conveyors on exploration paths that lead nowhere. Roads for exploration, conveyors only for productive chains
- **Fixes the `econ_cap` bottleneck indirectly**: Cheaper navigation = more Ti available = more builders spawned = more harvesters built

### Implementation complexity: LOW

The core change is ~20 lines: swap `build_conveyor` for `build_road` in `_nav()`, add a `_build_chain_to_core()` method that runs after `build_harvester()`, setting a builder state flag to walk back toward core laying conveyors with correct facing at each step.

---

## Secondary Fixes (lower leverage but still helpful)

1. **Remove `econ_cap` on constrained maps**: On tight/balanced maps, the visible-harvester cap prevents builder spawning. Remove it or set minimum cap = 5.

2. **Delay military on tight maps**: Barriers at round 80 and gunners at round 200 are too early on 20x20 maps where economy is everything. Push to round 400+.

3. **Bridge placement for shish_kebab**: Lower bridge threshold to `bc + 5` on tight maps, or better yet, just use diagonal movement (roads on diagonal tiles).

4. **Exploration diversity**: On 5-region maps, assign builders to different exploration directions by ID to cover all regions instead of clustering.
