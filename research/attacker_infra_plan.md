# Attacker Infrastructure Targeting — Implementation Plan

## Current Attacker Flow (Line-by-Line Analysis)

### Assignment (lines 282–288 in main.py)
```
After round 500, 4+ harvesters built, and id%6==5 → is_attacker = True
```
Once assigned, every round calls `_attack(c, pos, passable)` and returns early.

### `_attack` method (lines 759–789)

**Phase 1 — Opportunistic attack on current tile (lines 760–769):**
```python
if c.get_action_cooldown() == 0:
    bid = c.get_tile_building_id(pos)
    if bid is not None and c.get_team(bid) != c.get_team():
        if c.can_fire(pos):
            c.fire(pos)
            return
```
If the attacker is already standing on an enemy building, fire immediately.

**Phase 2 — Move to adjacent enemy building (lines 770–784):**
```python
for d in DIRS:
    ap = pos.add(d)
    abid = c.get_tile_building_id(ap)
    if abid is not None and c.get_team(abid) != c.get_team():
        if c.get_move_cooldown() == 0 and c.can_move(d):
            c.move(d)
            return
```
If any neighbor tile has an enemy building, move onto it.
**Problem:** `can_move` only succeeds when the target is passable. A builder bot can stand on conveyors (any team), but NOT on most buildings (harvesters, turrets, etc). So this mostly works for conveyors but fails for other buildings.

**Phase 3 — Navigate to enemy core (lines 785–789):**
```python
enemy_pos = self._get_enemy_core_pos(c)
if enemy_pos:
    self._nav(c, pos, enemy_pos, passable)
else:
    self._explore(c, pos, passable)
```
Falls through to navigate toward the enemy core using `_nav`, which builds conveyors along the path. This is the **main problem**: the bot heads for core (500 HP) instead of soft infrastructure targets.

### `_get_enemy_core_pos` (lines 963–983)
Uses map symmetry (reflection/rotation scoring) to infer enemy core position. Returns a `Position`. Cached in `self._enemy_core`.

### `_nav` (lines 411–478)
General pathfinding: BFS step + greedy ranking, builds conveyors on empty tiles, tries bridges as fallback. **Issue for attacker:** it lays conveyors, wasting Ti and helping route resources back to our side — or even accidentally feeding the enemy.

---

## What API Calls Detect Enemy Buildings

```python
# Get all buildings within vision radius
c.get_nearby_buildings()  # list[int] — entity IDs of ALL nearby buildings

# Filter to enemy:
for eid in c.get_nearby_buildings():
    if c.get_team(eid) != c.get_team():
        etype = c.get_entity_type(eid)  # EntityType.CONVEYOR, HARVESTER, etc.
        epos  = c.get_position(eid)
        ehp   = c.get_hp(eid)
```

No range filter needed since we use default vision radius (r^2=20 for builder bots).

---

## Attack Mechanics — What Works vs. What Doesn't

| Action | Works On | Notes |
|--------|----------|-------|
| `c.fire(pos)` | Enemy building on same tile | 2 damage, costs 2 Ti, uses action cooldown |
| `c.destroy(pos)` | ALLIED buildings only | Cannot use on enemy buildings |
| `c.move(d)` | Conveyors (any team), Roads, Allied core | Can walk ON enemy conveyors — key infiltration path |

**Key insight:** `c.destroy()` is NOT available for enemy buildings. The only way to damage enemies is `c.fire(pos)` while standing on the tile, which costs **2 Ti per fire**. At 2 damage/fire, kill counts are:
- Conveyor (20 HP): 10 fires, 20 Ti
- Armoured Conveyor (50 HP): 25 fires, 50 Ti
- Harvester (30 HP): 15 fires, 30 Ti
- Barrier (30 HP): 15 fires, 30 Ti
- Gunner (40 HP): 20 fires, 40 Ti
- Core (500 HP): 250 fires, 500 Ti — **not viable**

---

## Priority Target Ranking

Order targets by cost-efficiency (impact per Ti spent on attacking):

1. **Conveyor** (20 HP, +1% cost scale reversal) — cheapest to kill, forms the conveyor chains; destroying breaks resource delivery
2. **Harvester** (30 HP, +5% cost scale reversal) — kills resource income permanently; highest scale reversal per HP
3. **Splitter** (20 HP, +1% cost scale reversal) — same as conveyor, also breaks routing
4. **Armoured Conveyor** (50 HP, +1% scale) — expensive to kill, low priority
5. **Foundry** (50 HP, +100% scale reversal) — VERY high value if reachable; destroys refining capacity
6. **Gunner/Sentinel/Breach** (40/30/60 HP, +10/20/10% scale) — removes offensive pressure
7. **Core** (500 HP) — essentially unkillable at 2 damage/fire

**Sorting heuristic for live target selection:**
```python
# Lower score = higher priority
priority_score = hp / scale_reversal_percent
# CONVEYOR: 20/1 = 20
# HARVESTER: 30/5 = 6   ← best
# SPLITTER:  20/1 = 20
# FOUNDRY:   50/100 = 0.5 ← best if reachable
# GUNNER:    40/10 = 4
```

In practice: harvesters and foundries are the highest value kills. Conveyors are the most reachable (walkable!).

---

## Infiltration via Enemy Conveyor Network

**This is the key mechanic:** Builder bots can walk on enemy conveyors. Enemy conveyor chains run from ore tiles all the way to the enemy core. An attacker that reaches the start of an enemy chain can:
1. Walk along the enemy conveyor network
2. Fire on each conveyor tile it stops on
3. Systematically dismantle the entire chain

### Approach
- Detect enemy conveyors in vision: `c.get_nearby_buildings()` filtered to `EntityType.CONVEYOR` and enemy team
- Find the closest walkable enemy conveyor
- Navigate to it (building roads, NOT conveyors, for efficient travel — saves Ti)
- Once on an enemy conveyor, fire, then use `passable` check to keep walking along the chain
- Follow the chain toward ore tiles (highest density of harvesters at the terminus)

### Detecting chain direction
Enemy conveyors face toward the core. So walking **against** the conveyor direction (i.e., toward the ore source) leads to harvesters. The direction of a conveyor is `c.get_direction(eid)`. To walk toward harvesters: move in `c.get_direction(eid).opposite()` direction.

---

## Changes Required to `_attack`

### Current flow problems:
1. Navigates toward enemy **core** — wrong target entirely
2. Calls `_nav` which builds conveyors — wasteful, wrong infrastructure type for attacker
3. Only attacks if immediately adjacent; doesn't actively seek enemy buildings proactively
4. No target prioritization at all

### New flow design:

```
_attack(c, pos, passable):

  # STEP 1: If standing on enemy building, fire immediately
  bid = c.get_tile_building_id(pos)
  if bid is not None and enemy_team:
      c.fire(pos) if can_fire
      # Don't return yet — also try to move to next target after firing

  # STEP 2: Scan nearby buildings, find best target
  target_pos = _find_best_infra_target(c, pos)

  # STEP 3: If adjacent to target (or ON it), fire/move onto it
  if target_pos:
      if pos == target_pos → fire
      elif adjacent and can_move → move onto it

  # STEP 4: Navigate toward best target (or enemy core as fallback)
  if target_pos:
      _nav_attacker(c, pos, target_pos, passable)
  else:
      # No targets in vision — navigate toward known enemy area
      enemy_pos = _get_enemy_core_pos(c)
      _nav_attacker(c, pos, enemy_pos or fallback, passable)
```

### New helper: `_find_best_infra_target(c, pos)`
```python
def _find_best_infra_target(self, c, pos):
    PRIORITY = {
        EntityType.FOUNDRY: 0,
        EntityType.HARVESTER: 1,
        EntityType.GUNNER: 2,
        EntityType.SENTINEL: 3,
        EntityType.BREACH: 4,
        EntityType.SPLITTER: 5,
        EntityType.CONVEYOR: 6,
        EntityType.ARMOURED_CONVEYOR: 7,
        EntityType.BARRIER: 8,
    }
    best = None
    best_score = float('inf')
    for eid in c.get_nearby_buildings():
        if c.get_team(eid) == c.get_team():
            continue
        etype = c.get_entity_type(eid)
        if etype == EntityType.CORE:
            continue  # skip core
        epos = c.get_position(eid)
        pri = PRIORITY.get(etype, 9)
        dist = pos.distance_squared(epos)
        score = pri * 1000 + dist  # prioritize type, break ties by distance
        if score < best_score:
            best_score = score
            best = epos
    return best
```

### New helper: `_nav_attacker(c, pos, target, passable)`
Unlike `_nav`, this should:
- NOT build conveyors (they feed into our supply chain or nowhere useful)
- Build roads instead for walkability (1 Ti vs 3 Ti for conveyors)
- Or walk on existing enemy conveyors without building anything
- Use the same BFS/rank logic for direction

```python
def _nav_attacker(self, c, pos, target, passable, ti_reserve=20):
    """Navigate toward target without building conveyors."""
    dirs = self._rank(pos, target)
    bfs_dir = self._bfs_step(pos, target, passable)
    if bfs_dir is not None and bfs_dir != dirs[0]:
        dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]

    w, h = c.get_map_width(), c.get_map_height()
    for d in dirs:
        nxt = pos.add(d)
        if nxt.x < 0 or nxt.x >= w or nxt.y < 0 or nxt.y >= h:
            continue
        # Move if passable
        if c.get_move_cooldown() == 0 and c.can_move(d):
            c.move(d)
            return
        # Build road as walkable path (cheaper than conveyor)
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            rc = c.get_road_cost()[0]
            if ti >= rc + ti_reserve and c.can_build_road(nxt):
                c.build_road(nxt)
                return
```

**Note:** `passable` must include enemy conveyors. The passable check in the main bot filters by what builder bots can walk on — enemy conveyors ARE passable so BFS should naturally find them.

---

## Ti Economy of Attacking

| Action | Ti Cost |
|--------|---------|
| `c.fire(pos)` | 2 Ti per attack |
| Build road for path | 1 Ti per tile |
| Build conveyor (avoid!) | 3+ Ti per tile |

**Vs. passive income:** 10 Ti every 4 rounds = 2.5 Ti/round passive. At peak (many harvesters), we may earn 50–100+ Ti/round. Attacker spending 2 Ti/fire is negligible.

**Ti reserve concern:** The attacker should avoid consuming Ti that the economy needs. Set `ti_reserve=20` minimum before attacking (ensure core/harvesters have buffer). Only fire when `c.get_global_resources()[0] >= 20`.

**Ti conservation:**
- Do NOT build conveyors while attacking (wastes 3 Ti and may misdirect resources)
- Build roads only when necessary for movement
- Fire every turn when standing on enemy building (action cooldown allows it)

---

## Survival: Builder Has 30 HP, Turrets Kill It

Enemy turrets are the main threat:
- **Gunner:** 10 damage, fires every round along a ray
- **Sentinel:** 18 damage, hits Chebyshev-1 of forward line, 3-round reload
- **Breach:** 40 direct + 20 splash, 1 round reload — most dangerous

### Survival strategies:

1. **Target conveyors first, not turrets** — conveyors don't shoot back; stay away from turret firing lines initially

2. **Don't stand still:** After firing, move to the next enemy conveyor rather than staying on the same tile. This can dodge turret fire that's aimed at last position.

3. **Approach from sides:** Turrets face one direction and have a firing ray/cone. Approach from the non-facing side. Check `c.get_direction(eid)` for facing turrets.

4. **Heal when safe:** If `c.get_hp() < 20` and near friendly buildings, `c.heal(pos)` costs 1 Ti, heals 4 HP to self + adjacents.

5. **Self-destruct as last resort:** If HP is very low near enemy infrastructure and we can't escape, no benefit — just die or try to get one more fire in.

6. **Avoid breach splash zones:** Never stand adjacent to breach target tiles. Breach hits 8 surrounding tiles for 20 splash — can one-shot a 30 HP builder.

7. **Prioritize reachable soft targets:** Walk on enemy conveyor chains, staying away from sentinel/breach placements.

### Rough survival math:
- 30 HP builder vs. gunner (10 damage): dies in 3 hits
- 30 HP builder vs. sentinel (18 damage): dies in 2 hits
- If approaching along enemy conveyor chain AWAY from turret facing direction: survives many more rounds

---

## Expected Impact vs. Different Opponent Types

| Opponent Type | Expected Impact |
|---------------|----------------|
| Passive/econ bots | HIGH — many conveyors/harvesters to kill, no defenses |
| Turret rush bots | LOW — will die quickly to gunners/sentinels |
| Mixed economy+defense | MEDIUM — can kill early conveyors before turrets are placed |
| Mirror (our own bot) | MEDIUM-HIGH — can break their conveyor chains |

**Best case:** Attacker reaches enemy ore tiles, fires on harvesters (15 shots = 30 Ti to kill one). One harvester kill = permanent loss of 1 stack every 4 rounds for enemy, plus reversal of +5% cost scale. Over 1500 remaining rounds, that's 375 fewer stacks delivered.

**Break-even:** Killing one harvester costs 30 Ti + transit time. The enemy loses 375 resource stacks. This is an excellent trade even accounting for the attacker dying en route.

**Secondary benefit:** Disrupting conveyor chains stops resource delivery even without destroying the harvester — resources pile up at broken junctions.

---

## Implementation Changes Summary

### Files to modify: `bots/buzzing/main.py`

1. **Lines 759–789 (`_attack` method):** Completely rewrite to:
   - Call `_find_best_infra_target` each turn
   - Navigate to best target using `_nav_attacker`
   - Fire on current tile if enemy building present
   - Fall back to enemy area (not core) if no targets visible

2. **Add `_find_best_infra_target` method:** Scans nearby buildings, prioritizes by type (foundry > harvester > conveyor), breaks ties by distance.

3. **Add `_nav_attacker` method:** Like `_nav` but builds roads instead of conveyors, avoids wasting Ti on infrastructure that benefits nobody.

4. **Update `_attack` Ti check:** Only fire if `c.get_global_resources()[0] >= 20` (leave buffer for economy).

5. **Passable check for enemy conveyors:** Verify that the existing `passable` set already includes enemy conveyors (it should — builder bots can walk on them).

### Lines affected:
- `_attack`: lines 759–789 (31 lines, full rewrite)
- New methods: ~50 lines of new code
- No changes needed to assignment logic (lines 282–288) or other builder methods

---

## Open Questions for Implementation

1. ~~Does the existing `passable` dict include enemy conveyors?~~ **ANSWERED:** `passable` is built from all non-WALL Environment tiles (lines 202–212), so it includes every non-wall tile regardless of what building is on it. Enemy conveyors are included. However, `_bfs_step` uses `nxt in passable` which only checks tile environment — not whether the tile is walkable for a builder bot (which additionally requires the tile to have a conveyor, road, or allied core). **Fix needed:** `_nav_attacker` should not use `_bfs_step` directly; it should use a modified passable set that includes enemy conveyors.

2. Should the attacker stop building infrastructure entirely, or can it still place roads strategically? **Recommendation:** Only build roads when absolutely necessary to cross a gap. Never build conveyors (wastes Ti, may misdirect resources).

3. Should multiple attackers coordinate targets via markers? **Later optimization.** Start with independent targeting — each attacker finds its own nearest high-value target. Marker coordination can be added later.

4. After destroying a target, the attacker should immediately re-run `_find_best_infra_target` to pick the next target. No caching needed — scan every round.

5. **Critical detail:** `c.can_move(d)` only succeeds if the target tile is actually passable for a builder (conveyor, road, allied core). The attacker can walk the enemy conveyor chain naturally — `can_move` will succeed on enemy conveyor tiles. However, BFS via `_bfs_step` uses the terrain-based `passable` set which may include non-walkable tiles. The `_nav_attacker` should check `c.is_tile_passable(nxt)` or filter to only include road/conveyor tiles.
