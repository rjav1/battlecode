# Conveyor Waste Analysis: 200-450 Conveyors vs Opponents' 9-32

Date: 2026-04-06

## Summary

Our bot builds 200-450 conveyors per game (600-1350 Ti) while The Defect uses 9-32 (27-96 Ti). This 10-15x overbuilding of conveyors is the primary driver of cost scale inflation and Ti waste. Conveyors serve two purposes in our bot — resource transport AND builder movement — but opponents separate these concerns by using roads for movement.

---

## Root Cause #1: _nav Builds Conveyors for Movement, Not Just Transport (CRITICAL)

### Code Analysis (`main.py:498-532`)

```python
def _nav(self, c, pos, target, passable, ti_reserve=5):
    """Navigate toward target, building conveyors with d.opposite() facing."""
    dirs = self._rank(pos, target)
    bfs_dir = self._bfs_step(pos, target, passable)
    ...
    for d in dirs:
        nxt = pos.add(d)
        ...
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            cc = c.get_conveyor_cost()[0]
            if ti >= cc + ti_reserve:
                face = d.opposite()
                ...
                if c.can_build_conveyor(nxt, face):
                    c.build_conveyor(nxt, face)    # <-- EVERY step builds a conveyor
                    return
        if c.get_move_cooldown() == 0 and c.can_move(d):
            ...
            c.move(d)
            return
```

The design: the builder tries to build a conveyor FIRST on every step, and only moves if it can't build. This means every tile the builder walks over gets a conveyor. On a 15-tile path from core to ore, that's 15 conveyors (45 Ti, +15% scale).

The Defect's approach: roads for movement (1 Ti, +0.5% scale each), conveyors only for the ~3-8 tiles of actual resource transport chain between harvester and core/bridge.

### Impact
- A 15-tile conveyor path: 45 Ti + 15% scale
- A 15-tile road path: 15 Ti + 7.5% scale
- Savings per path: 30 Ti + 7.5% scale
- With 10 harvesters at avg 10-tile paths: 300 Ti + 75% scale saved

### Specific Code Change (`main.py:498-532`)

Split _nav into two modes: "transport" (conveyor) and "explore" (road-first):

```python
def _nav(self, c, pos, target, passable, ti_reserve=5, use_roads=False):
    """Navigate toward target. use_roads=True builds roads instead of conveyors."""
    dirs = self._rank(pos, target)
    bfs_dir = self._bfs_step(pos, target, passable)
    if bfs_dir is not None and bfs_dir != dirs[0]:
        dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]

    w, h = c.get_map_width(), c.get_map_height()
    for d in dirs:
        nxt = pos.add(d)
        if nxt.x < 0 or nxt.x >= w or nxt.y < 0 or nxt.y >= h:
            continue
        # Try move first (no building needed)
        if c.get_move_cooldown() == 0 and c.can_move(d):
            if self.target is not None and len(self.fix_path) < 30:
                self.fix_path.append(pos)
            c.move(d)
            return
        # Build walkable tile
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            if use_roads:
                rc = c.get_road_cost()[0]
                if ti >= rc + ti_reserve and c.can_build_road(nxt):
                    c.build_road(nxt)
                    return
            else:
                cc = c.get_conveyor_cost()[0]
                if ti >= cc + ti_reserve:
                    face = d.opposite()
                    # Destroy allied road so we can place conveyor
                    bid = c.get_tile_building_id(nxt)
                    if bid is not None:
                        try:
                            if (c.get_entity_type(bid) == EntityType.ROAD
                                    and c.get_team(bid) == c.get_team()):
                                if c.can_destroy(nxt):
                                    c.destroy(nxt)
                        except Exception:
                            pass
                    if c.can_build_conveyor(nxt, face):
                        c.build_conveyor(nxt, face)
                        return
    # ... bridge and road fallback remain as-is
```

Then change `_explore` to use roads:
```python
# main.py:616, change:
self._nav(c, pos, far, passable, ti_reserve=explore_reserve)
# to:
self._nav(c, pos, far, passable, ti_reserve=explore_reserve, use_roads=True)
```

---

## Root Cause #2: _explore Lays Conveyors While Searching for Ore (HIGH)

### Code Analysis (`main.py:567-616`)

`_explore` calls `_nav` with the same conveyor-building behavior. When a builder has no ore target, it picks a far point and navigates toward it, building conveyors the entire way. These conveyors:
- Lead away from ore (builder is exploring, not mining)
- May never carry any resources
- Each adds +1% to the global cost scale
- Cost 3 Ti each with no return

### Data
On wasteland (game 2 of 0-5 loss), buzzing built 248 conveyors and collected 0 Ti. All 248 conveyors were pure waste — ~744 Ti spent on conveyors that never transported anything.

### Specific Code Change

Already covered in RC#1 above — use `use_roads=True` in `_explore`. Additionally:

**`main.py:610-616` (explore_reserve):**
```python
# CURRENT:
if self._check_needs_low_reserve():
    explore_reserve = 5
else:
    explore_reserve = 30 if core_dist_sq > 50 else 5

# PROPOSED (with road-based explore):
explore_reserve = 5  # roads are cheap (1 Ti), always allow building them
```

---

## Root Cause #3: No Bridge-First Delivery = Long Conveyor Chains (HIGH)

### Code Analysis (`main.py:292-344`)

The current bridge logic is a deferred afterthought:
1. Builder builds harvester (line 415)
2. Sets `_bridge_target = ore` for NEXT round (line 420)
3. Next round, tries bridge from ore to nearest chain or core (lines 292-344)
4. Bridge only attempted if `ore.distance_squared(core) > 9` (line 298)

Problems:
- The conveyor chain from core to ore already exists by the time bridge is attempted
- Bridge adds to the chain instead of replacing it
- If the bridge attempt fails, the long conveyor chain persists

The Defect's approach: build harvester, then immediately bridge it to nearest infrastructure. No long conveyor chains needed. Resources hop via bridge directly to the existing network.

### Specific Code Change

**`main.py:415-437` (after harvester build):**
Instead of deferred bridge, attempt bridge immediately in the same turn (destroy is free, bridge build is an action but harvester build already consumed the action... so this must be deferred to next round as it currently is).

The real fix: when navigating TO ore, use roads instead of conveyors. Then after building harvester + bridge, there's no conveyor chain at all — just roads (walkable but don't transport) + bridge (transports directly).

```python
# After building harvester at line 415-416:
c.build_harvester(ore)
self.harvesters_built += 1
self.target = None
self._bridge_target = ore  # keep bridge attempt next round
self.fix_path = []  # no chain-fix needed if we used roads to get here
return
```

Combined with RC#1 (roads for movement), this means:
- Builder walks to ore via roads (cheap, low scale)
- Builds harvester on ore
- Next round, builds bridge from ore to nearest infra/core
- Total infrastructure per harvester: ~10 roads (10 Ti, 5% scale) + 1 bridge (20 Ti, 10% scale) = 30 Ti, 15% scale
- Current: ~15 conveyors (45 Ti, 15% scale) + optional bridge (20 Ti, 10% scale) = 45-65 Ti, 15-25% scale

---

## Root Cause #4: Chain-Fix Creates Duplicate Conveyors (MEDIUM)

### Code Analysis (`main.py:421-436, 1166-1218`)

After building a harvester, if the path was winding (3+ direction changes), the builder enters chain-fix mode. It walks back along `fix_path`, destroying and rebuilding conveyors with corrected facing. This:
- Costs additional Ti (destroy + rebuild)
- Takes 10-20 rounds of builder time (not mining)
- The old conveyors are already counted in cost scale

### Specific Code Change

With road-based navigation + bridge delivery, chain-fix becomes unnecessary. The resource path is: harvester → bridge → existing infrastructure. No long conveyor chain to fix.

**`main.py:421-436`:** Remove chain-fix trigger entirely:
```python
# Remove these lines:
if (self.core_pos and len(self.fix_path) >= 4
        and self.harvesters_built <= 2):
    changes = 0
    for i in range(1, len(self.fix_path) - 1):
        ...
    if changes >= 3:
        self.fixing_chain = True
        ...

# Replace with:
self.fix_path = []
```

---

## Root Cause #5: Cost Scale Compounding (SYSTEMIC)

### Data

| Game | buzzing buildings | buzzing scale (est) | The Defect buildings | The Defect scale (est) |
|------|-------------------|--------------------|-----------------------|----------------------|
| landscape | 293 conv + misc | ~350% | 71 conv + 178 road | ~210% |
| wasteland | 248 conv + misc | ~320% | 264 conv + misc | ~330% |
| hooks | 336 conv + misc | ~400% | 62 conv + 315 road | ~225% |
| starry_night | 440 conv + misc | ~500% | 225 conv + 336 road | ~330% |
| chemistry_class | 454 conv + misc | ~510% | 169 conv + 341 road | ~280% |

Note: Each conveyor adds +1% scale, each road adds +0.5% scale. So The Defect's 315 roads = +157.5% while our 336 conveyors = +336%.

At 500% scale, a harvester that normally costs 20 Ti costs 100 Ti. A builder at 500% costs 150 Ti instead of 30 Ti. This makes late-game expansion nearly impossible for us.

### The Vicious Cycle

1. Builder explores → builds conveyor (waste)
2. More conveyors → higher cost scale
3. Higher scale → harvesters cost more
4. Expensive harvesters → fewer harvesters built
5. Fewer harvesters → less Ti income
6. Less Ti → builders explore more (can't afford harvesters)
7. Go to step 1

The Defect breaks this cycle by using roads for movement. Roads add half the scale of conveyors, and cost 1/3 the Ti.

---

## Recommended Implementation Order

### Step 1: Add `use_roads` parameter to `_nav` (line 498)
- When `use_roads=True`, build roads instead of conveyors
- Move-first logic: try `can_move` before building anything

### Step 2: Change `_explore` to use roads (line 616)
- `self._nav(c, pos, far, passable, ti_reserve=5, use_roads=True)`
- Immediate impact: exploration conveyors eliminated

### Step 3: Navigation to ore uses roads (line 493)
- When `self.target` is set (ore tile), navigate via roads
- Only build conveyors for the actual transport chain (harvester → core)
- This requires separating "walk to ore" from "build transport chain"

### Step 4: Remove chain-fix (lines 404-407, 421-436, 1166-1218)
- With road-based nav + bridge delivery, chain-fix is unnecessary

### Step 5: Aggressive bridge placement (lines 292-344)
- After every harvester, bridge to nearest allied infrastructure
- Remove the `distance_squared > 9` restriction

---

## Projected Impact

| Change | Conveyors saved | Ti saved | Scale saved |
|--------|----------------|----------|-------------|
| Road-based explore | 50-150 per game | 150-450 Ti | 50-150% |
| Road-based ore nav | 50-100 per game | 150-300 Ti | 50-100% |
| Bridge-first delivery | 30-80 per game | 90-240 Ti | 30-80% |
| Remove chain-fix | 5-15 per game | 15-45 Ti | 5-15% |
| **Combined** | **135-345 per game** | **405-1035 Ti** | **135-345%** |

Target: 30-60 conveyors per game (only for resource transport), matching The Defect's range.
Ti freed for harvesters: 400-1000 Ti = 20-50 additional harvesters at base cost.
