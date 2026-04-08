# Conveyor Destruction Design Research

## Date: 2026-04-08
## Question: Can we destroy unused conveyors to reduce scale inflation?

---

## Mechanics Confirmed (from CLAUDE.md + _types.py)

- `c.destroy(pos)` -- removes allied building, **NO action cooldown cost**, repeatable
- `c.can_destroy(pos)` -- building must be within **action radius r^2=2** (adjacent tile)
- Destroying reverses the entity's scaling contribution (-1% per conveyor destroyed)
- Builder must be standing on or adjacent to the conveyor to destroy it
- Conveyors are walkable -- builders can walk on them and destroy them
- `c.get_stored_resource(id)` -- returns None if conveyor is empty, ResourceType if carrying

---

## The Opportunity

From the minimal bot experiment, buzzing builds 100-547 buildings on medium/large maps. Many are exploration conveyors that never carry resources. If we could destroy 50 of those, we'd reduce scale by 50% -- everything costs half as much.

Example: On cold, buzzing built 547 buildings. If 300 are exploration conveyors, destroying them drops scale from ~400% to ~100%. A harvester that costs 80 Ti would cost 20 Ti again.

---

## Detection Approaches

### Approach 1: `get_stored_resource` check (UNRELIABLE)

Check if a conveyor has resources flowing through it:
```python
for eid in c.get_nearby_buildings():
    if c.get_entity_type(eid) == EntityType.CONVEYOR and c.get_team(eid) == c.get_team():
        if c.get_stored_resource(eid) is None:
            # Empty -- possibly unused
```

**Problem:** Harvesters output 1 stack every 4 rounds. A conveyor in a working chain is empty 3 out of 4 rounds. Checking `get_stored_resource` at a random moment has a 75% chance of seeing "empty" even for an active chain. You'd need to observe the conveyor for 8+ rounds to confirm it's truly unused.

**Verdict:** Requires per-conveyor tracking over multiple rounds. Builders have no persistent memory of specific conveyor IDs (each builder only knows about conveyors in its current vision). TOO COMPLEX for reliable detection.

### Approach 2: Distance from nearest harvester (UNRELIABLE)

Destroy conveyors > 20 tiles from any visible harvester.

**Problem:** A builder can only see within r^2=20 (~4.5 tiles). It can't detect harvesters 20 tiles away. It would need to track harvester positions globally -- but there's no shared state between builders (only markers, which are already used for ore claiming).

**Also:** A conveyor chain from a distant harvester to core passes through areas far from any harvester. The middle of the chain is the most important part to keep, but this heuristic would destroy it.

**Verdict:** Fundamentally broken. The important part of a chain (the middle) is far from both the harvester AND the core.

### Approach 3: Direction coherence check (MODERATE)

Exploration conveyors form wandering chains (left, right, diagonal). Delivery chains are more linear (consistently pointing toward core). Check if a conveyor's facing direction points roughly toward the core:

```python
conv_dir = c.get_direction(eid)
conv_pos = c.get_position(eid)
core_dir = conv_pos.direction_to(self.core_pos)
# If conveyor faces AWAY from core, it's likely exploration waste
```

**Problem:** BFS navigation creates zigzag paths around walls. These are legitimate delivery chains where individual conveyors might face sideways or even briefly away from core while routing around obstacles.

**Verdict:** Too many false positives on wall-heavy maps. Would destroy working chains.

### Approach 4: Builder self-cleanup on return trip (MOST VIABLE)

After a builder builds a harvester and the bridge-hop (lines 274-326), it heads back toward core or explores for more ore. On the return path, it walks OVER the conveyors it laid on the way out. At this point:

- If the harvester-to-core chain is working (bridge or short chain), the outbound exploration conveyors are redundant
- The builder is already standing on them (no detour needed)
- Destroy them as it walks back

Implementation:
```python
# In _builder, after building harvester + bridge, set cleanup mode
if self._returning_from_harvest:
    # Destroy conveyor under current tile if it's far from core
    bid = c.get_tile_building_id(pos)
    if bid is not None:
        try:
            if (c.get_entity_type(bid) == EntityType.CONVEYOR
                    and c.get_team(bid) == c.get_team()
                    and pos.distance_squared(self.core_pos) > 25):
                c.destroy(pos)
        except Exception:
            pass
```

**Problems:**
1. Builder walks ON conveyors. Destroying the conveyor under it removes the walkable surface. Can it still stand there? No -- conveyors are walkable, empty tiles might not be. If the tile is empty (not ore, not wall), the builder CANNOT stand on it. **Destroying the conveyor under the builder would strand it** unless the tile has ore or another walkable surface beneath.

Wait -- let me re-read the rules. "Can only walk on: Conveyors, Roads, Allied core." If a builder destroys the conveyor it's standing on, the tile becomes empty. The builder is already there but can't MOVE to another empty tile. It's not clear if the builder is ejected or stranded.

**This is a critical unknown.** If destroying the conveyor under the builder is allowed but strands it on a non-walkable tile, the builder becomes permanently stuck.

2. Even if we only destroy ADJACENT conveyors (not the one under the builder), we need to know which are exploration waste vs delivery chain. Adjacent conveyors could be part of any chain.

3. The bridge-hop (lines 274-326) already provides an alternative delivery path. But if it fails (which happens often -- 3-tile limit), the conveyor chain IS the delivery path, and destroying it kills resource flow.

### Approach 5: Destroy during exploration (SIMPLEST)

Don't destroy conveyors on delivery chains. Instead, prevent exploration conveyors from being built in the first place -- which is what `_explore` already does with high `ti_reserve` (line 529, explore_reserve=5-60).

Wait -- checking the explore function:

```python
explore_reserve = 5  # default
if self._wall_density > 0.20:
    explore_reserve = 60
elif core_dist_sq > 50:
    explore_reserve = 30
```

Then `_nav` is called with this reserve:
```python
self._nav(c, pos, far, passable, ti_reserve=explore_reserve)
```

In `_nav`, conveyor mode checks `ti >= cc + ti_reserve`. With explore_reserve=60, it needs 63+ Ti to build a conveyor during exploration. This already suppresses exploration conveyors when Ti is low.

**But:** On maps where Ti flows well, the bot accumulates 5,000+ Ti and explore_reserve=60 doesn't stop anything (5,000 > 63).

**Fix for Approach 5:** During exploration, use roads not conveyors. Change line 397:
```python
self._nav(c, pos, far, passable, ti_reserve=explore_reserve, use_roads=True)
```

**This has been tried before and failed** (V62 bridge removal, mentioned in commit history: "V62 bridge removal FAILED (50%)"). But it may have failed for other reasons (bridge removal, not roads-for-explore).

---

## Viability Assessment

| Approach | Viable? | Risk | Complexity |
|----------|---------|------|------------|
| 1. get_stored_resource | No | N/A | High (multi-round tracking) |
| 2. Distance from harvester | No | N/A | Builder vision too small |
| 3. Direction coherence | No | High false positives | Medium |
| 4. Self-cleanup on return | **Maybe** | Stranding risk | Medium |
| 5. Roads for exploration | **Maybe** | Failed before | Low (1 line) |

---

## The Fundamental Problem

**Detection is hard because builders have no global knowledge.** Each builder only sees within r^2=20 (~4.5 tiles). It can't know:
- Whether a conveyor 10 tiles away is part of another builder's active delivery chain
- Whether a harvester exists somewhere upstream that depends on this conveyor
- Whether another builder is currently using this conveyor as a walkway

The only entity with broad vision is the core (r^2=36), but the core can't destroy buildings (only builders can).

**Markers can't help either** -- we'd need to encode "this conveyor is in use" on every tile, which conflicts with the ore-claiming marker system and costs 1 marker/round/builder.

---

## Recommendation

**Conveyor destruction is NOT viable as a primary scale-reduction strategy.** The detection problem is unsolved, and the risk of destroying working chains is high.

### What IS viable (in priority order):

1. **Scale-based builder cap** (from ore_scarcity_cap research): Stop spawning when `c.get_scale_percent() > 200%`. Prevents the problem instead of cleaning it up. Zero risk of chain breakage.

2. **Roads for late-game exploration**: After round 300 or when scale > 150%, switch `_explore` to use roads. Builders that already found ore have laid their conveyor chains. New builders exploring for more ore use roads. This limits NEW exploration conveyors without touching existing chains.

   Implementation: In `_explore` (line 529), add scale check:
   ```python
   use_roads_explore = c.get_scale_percent() > 150.0
   self._nav(c, pos, far, passable, ti_reserve=explore_reserve,
             use_roads=use_roads_explore)
   ```

3. **Targeted destruction only for KNOWN dead-ends**: If a builder builds a bridge-hop from harvester to chain (lines 274-326, `built = True`), the outbound conveyor chain that the builder walked on is now redundant. The builder knows it just created an alternative path. On its next few moves, destroy adjacent conveyors that face AWAY from core AND are farther from core than the bridge position. This is the only case where we have enough context to safely destroy.

   Risk: Bridge might fail to deliver (broken chain). Destroying the backup conveyors removes the fallback.

### Bottom line:
Prevention (scale cap, roads for exploration) beats cleanup (destruction). Destruction is a scalpel surgery on a system without X-ray vision -- the builder can't see enough to know what's safe to cut.
