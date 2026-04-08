# Dynamic Explore Reserve Based on Visible Building Count

## Date: 2026-04-08
## Status: THOUGHT EXPERIMENT — not implementing

---

## The Idea

When a builder sees many allied buildings nearby (high density = scale inflation happening), raise `explore_reserve` to suppress new exploration conveyors. This is self-regulating: more buildings → higher reserve → fewer new conveyors → building count plateaus.

## Current System (lines 520-528)

```python
if self._wall_density > 0.20:
    explore_reserve = 60
elif core_dist_sq > 50:
    explore_reserve = 30
else:
    explore_reserve = 5
```

Reserve gates conveyor building: `ti >= conveyor_cost + explore_reserve`. At reserve=5, needs 8 Ti. At reserve=60, needs 63 Ti.

## Proposed Change

```python
# Count visible allied buildings
vis_buildings = len(c.get_nearby_buildings())
# Dynamic reserve: scales with building density
building_reserve = vis_buildings * 2  # 10 buildings = +20, 30 buildings = +60

if self._wall_density > 0.20:
    explore_reserve = 60
elif core_dist_sq > 50:
    explore_reserve = max(30, building_reserve)
else:
    explore_reserve = max(5, building_reserve)
```

## Analysis: Why This Is Different From Previous Attempts

### Previous scale-cap attempts:
- `c.get_scale_percent() > 200` → hard cap on builders. FAILED because it blocked ALL spawning, even when more builders were needed.
- `explore_reserve = 60` for mazes → static, doesn't adapt to game state.

### This approach:
- **Per-builder, per-round decision** — each builder independently adjusts based on what it sees nearby
- **Graceful degradation** — doesn't stop building, just makes conveyors more expensive during exploration. When the builder finds ore (target, not exploring), `_nav` uses `ti_reserve=5` regardless.
- **Self-regulating** — more buildings → higher reserve → fewer new conveyors → building count stabilizes
- **No global state needed** — uses `c.get_nearby_buildings()` which is already available

### Key distinction from ti_reserve=999:
Previous attempts raised explore_reserve so high that builders couldn't build ANY conveyors during exploration, getting stuck. Dynamic reserve scales gradually — at 10 nearby buildings, reserve is 25 (still buildable at 28 Ti). At 30 nearby buildings, reserve is 65 (needs 68 Ti — only buildable when Ti is abundant).

## Potential Problems

### 1. Builders far from core see few buildings
A builder exploring in an empty sector sees 0 nearby buildings → reserve stays at 5 → builds freely. This is actually CORRECT — in empty areas, building conveyors is cheap (low scale from few buildings).

### 2. Builders near core see MANY buildings
A builder near core (where chains converge) sees 20+ buildings → reserve = 45+ → can't build exploration conveyors. The builder gets stuck near core unable to explore. BUT: near core, the builder should be finding nearby ore (not exploring), so `_nav` with `ti_reserve=5` handles that.

Wait — there's a subtlety. When no ore is visible, the builder enters `_explore`, which uses `explore_reserve`. If the builder is near core with 20+ visible buildings, it can't explore outward because it can't afford conveyors. It's trapped near core.

**This might be GOOD:** builders near core with many buildings SHOULD stop exploring and wait for ore to appear nearby (via other builders' exploration or new spawns). Over-exploring from a saturated area wastes conveyors.

**Or it might be BAD:** if all builders are near core and all see 20+ buildings, NOBODY explores. The bot stalls.

### 3. `get_nearby_buildings()` includes enemy buildings
The count includes enemy conveyors/harvesters visible in the builder's vision. Near map center, the builder sees enemy buildings too, inflating the count. This makes the reserve higher than intended near the map border.

**Fix:** Filter to allied buildings only:
```python
vis_buildings = sum(1 for eid in c.get_nearby_buildings()
                    if c.get_team(eid) == c.get_team())
```
But this adds a loop over nearby buildings every round, which costs CPU (2ms limit).

### 4. `get_nearby_buildings()` is cheap but how many buildings?
Builder vision r^2=20 covers ~63 tiles. With 400 buildings on a 30x30=900 tile map, that's ~28 buildings per vision cone. At 2 per building, reserve = 56 — similar to maze-level suppression. This might be too aggressive.

**Alternative scaling:** `building_reserve = vis_buildings // 2` — 28 buildings = +14 reserve. More gradual.

## Why This Might Actually Work (Unlike 29 Previous Attempts)

Every previous attempt was a GLOBAL gate:
- Scale cap: affects ALL builders equally
- Builder cap: stops ALL spawning
- Conveyor cap: limits total conveyors
- Roads for exploration: changes ALL navigation

This approach is LOCAL and ADAPTIVE:
- Each builder adjusts independently based on its own surroundings
- Builders in empty sectors explore freely (few nearby buildings)
- Builders in saturated areas slow down (many nearby buildings)
- The gate is explore_reserve, not a hard block — builder can still build conveyors when Ti is abundant
- No change to `_nav` when targeting ore (ti_reserve=5 stays)

## Cost-Benefit

**Benefit:** Reduces exploration conveyors in saturated areas. If 3 builders near core each see 20 buildings and stop exploring, that's ~30 fewer conveyors = -30% scale = cheaper harvesters.

**Cost:** Builder time spent NOT exploring. If the builder can't explore, it sits idle (no ore visible, can't build conveyors to walk). Idle builder = wasted scale (30 Ti + 20% for nothing).

**Net:** Depends on whether the saved conveyors are worth the idle time. At 400+ buildings (current state), the conveyors are very expensive (3 Ti * 3x-4x scale = 9-12 Ti each). Saving 30 conveyors saves 270-360 Ti. An idle builder for 30 rounds costs 0 Ti but wastes the 30 Ti + 20% scale already invested.

## Verdict

**This is the most promising untested approach.** Unlike all previous attempts, it's:
- Local (per-builder, not global)
- Adaptive (scales with game state)
- Gradual (not a hard block)
- Self-regulating (more buildings → less exploration → building count plateaus)

**The risk:** builders getting stuck near core when the area is saturated. Mitigation: use `building_reserve = vis_buildings // 3` (gentler) and only apply during `_explore`, not during `_nav` to ore.

**If implementing:** ~5 lines changed in `_explore`. No new functions, no new state variables, no architectural changes.

```python
# In _explore, before computing explore_reserve:
vis_buildings = len(c.get_nearby_buildings())
building_factor = vis_buildings // 3  # 30 buildings = +10 reserve

# Existing logic with building_factor added:
if self._wall_density is not None and self._wall_density > 0.20:
    explore_reserve = max(60, building_factor)
elif core_dist_sq > 50:
    explore_reserve = max(30, building_factor)
else:
    explore_reserve = max(5, building_factor)
```

This is the gentlest possible version. At 30 nearby buildings, it adds +10 to the reserve. Only matters when Ti < 13 (reserve 5 → 15). At Ti > 15, no effect. Very safe.

**But "very safe" also means "very small effect."** The building count problem (400+ buildings) needs a bigger lever. A bolder version:

```python
building_factor = vis_buildings  # 30 buildings = +30 reserve
explore_reserve = max(explore_reserve, building_factor)
```

At 30 nearby buildings, reserve = 30 (need 33 Ti for exploration conveyor). At Ti < 33, builder doesn't explore. At Ti > 33, builder explores normally. This is more impactful but risks stalling builders in saturated areas.
