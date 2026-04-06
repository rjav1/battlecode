# Splitter-Sentinel Integration: How to Splice Into d.opposite() Chains
## Cambridge Battlecode 2026
### Compiled: April 6, 2026

---

## THE PROBLEM

Our bot uses `d.opposite()` conveyors: when a builder moves in direction `d`, it builds a conveyor on the next tile facing `d.opposite()` (back toward where it came from, which is roughly toward core). This creates chains that flow from ore deposits back toward core.

To add splitter-fed sentinels, a second builder (the "sentinel builder", `id%5==1`) must:
1. Find an existing conveyor in an active chain
2. Destroy it
3. Build a splitter facing the same direction
4. Build a branch conveyor + sentinel perpendicular to the chain

The challenge: how does the sentinel builder **find and identify** good conveyors to splice into, given that many conveyors are "exploration waste" not connected to anything useful?

---

## CURRENT CODE ANALYSIS

### The Existing Sentinel Builder (lines 213-336 in main.py)

The current `_build_sentinel_infra` method does:

1. **Step 0 (Find):** Scans `get_nearby_buildings()` for allied conveyors within distance 4-50 of core. Picks the closest one. Checks if perpendicular tiles (90 degrees left or right) are empty for branch + sentinel.

2. **Steps 1-4 (Build):** Walks to conveyor, destroys it, builds splitter in same direction, builds branch conveyor, builds sentinel.

3. **Triggers:** Only when `id%5==1`, round > 1000, 3+ harvesters built, near core (d^2 <= 36), 200+ Ti.

### Problems with Current Approach

**Problem 1: No chain validation.** The code picks the closest conveyor to core, but doesn't verify it's part of an active chain. It could be a dead-end exploration conveyor with no resource flow.

**Problem 2: Trigger is too late (round 1000).** By round 1000, the economy should already be established. Sentinels should start appearing by round 200-300.

**Problem 3: Cap too low (2 sentinels).** Diamond-tier bots have 3-5 sentinels.

**Problem 4: Perpendicular-only branching.** The code checks exactly 90 degrees left/right for branch positions. If those tiles are walls, it fails silently.

---

## HOW TO IDENTIFY ACTIVE CHAIN CONVEYORS

### The Core Insight: d.opposite() Chains Have a Signature

When a builder walks from core toward ore and builds `d.opposite()` conveyors, the chain has these properties:

1. **Each conveyor points roughly toward core** (since d.opposite() points back the way the builder came from, which started at core).

2. **Consecutive conveyors in the chain form a connected path:** conveyor A's output direction points to conveyor B, conveyor B's output direction points to conveyor C, etc., all the way to core.

3. **An active chain has a HARVESTER at one end** (the far end from core) and the **CORE at the other end** (or at least conveyors leading to core).

### Method 1: Trace-to-Core Validation (RECOMMENDED)

The most reliable way to verify a conveyor is in an active chain:

```python
def is_chain_conveyor(c, conv_id):
    """Check if a conveyor is part of a chain that leads toward core."""
    try:
        conv_pos = c.get_position(conv_id)
        conv_dir = c.get_direction(conv_id)
        
        # Follow the chain forward (in the conveyor's output direction)
        # For up to 15 steps, check if we reach a tile near core
        current = conv_pos
        for step in range(15):
            next_tile = current.add(conv_dir)
            
            # Check what's on the next tile
            bid = c.get_tile_building_id(next_tile)
            if bid is None:
                return False  # Chain broken -- dead end
            
            btype = c.get_entity_type(bid)
            if btype == EntityType.CORE:
                return True  # Chain reaches core!
            
            if btype in (EntityType.CONVEYOR, EntityType.SPLITTER):
                # Continue following
                conv_dir = c.get_direction(bid)
                current = next_tile
            else:
                return False  # Hit a non-transport building
        
        return False  # Chain too long, didn't reach core in 15 steps
    except Exception:
        return False
```

**Pros:** Highly reliable. Only selects conveyors that actually lead to core.
**Cons:** Expensive (up to 15 API calls per conveyor checked). But we only run this once per sentinel build, so it's fine.

### Method 2: Harvester-Adjacency Check (SIMPLER)

Check if the conveyor has a harvester within a few tiles upstream:

```python
def has_upstream_harvester(c, conv_id):
    """Check if a conveyor has a harvester feeding it from behind."""
    try:
        conv_pos = c.get_position(conv_id)
        conv_dir = c.get_direction(conv_id)
        
        # Look upstream (opposite of output direction) for 5 tiles
        back_dir = conv_dir.opposite()
        current = conv_pos
        for step in range(5):
            prev_tile = current.add(back_dir)
            bid = c.get_tile_building_id(prev_tile)
            if bid is None:
                return False
            
            btype = c.get_entity_type(bid)
            if btype == EntityType.HARVESTER:
                return True  # Found a harvester upstream!
            
            if btype in (EntityType.CONVEYOR, EntityType.SPLITTER):
                back_dir = c.get_direction(bid).opposite()
                current = prev_tile
            else:
                return False
        
        return False
    except Exception:
        return False
```

**Pros:** Confirms the chain has a resource source.
**Cons:** Doesn't verify the chain reaches core. But if there's a harvester upstream, the chain was probably built intentionally.

### Method 3: Stored-Resource Check (CHEAPEST)

Check if the conveyor is currently carrying a resource:

```python
def has_resource(c, conv_id):
    """Check if conveyor currently holds a resource."""
    try:
        return c.get_stored_resource(conv_id) is not None
    except Exception:
        return False
```

**Pros:** Single API call. If a conveyor has a resource, it's definitely in an active chain.
**Cons:** Resources only appear intermittently (harvester outputs every 4 rounds). The conveyor might be empty at the moment of checking but still active. High false-negative rate.

### Method 4: Direction-Toward-Core Heuristic (FASTEST)

Check if the conveyor's facing direction points roughly toward core:

```python
def faces_toward_core(c, conv_id, core_pos):
    """Check if conveyor faces roughly toward core."""
    try:
        conv_pos = c.get_position(conv_id)
        conv_dir = c.get_direction(conv_id)
        
        # Direction from conveyor to core
        to_core = conv_pos.direction_to(core_pos)
        
        # Check if conveyor faces toward core (same direction or within 45 degrees)
        return conv_dir == to_core or conv_dir == to_core.rotate_left() or conv_dir == to_core.rotate_right()
    except Exception:
        return False
```

**Pros:** Very fast (3 API calls). d.opposite() conveyors inherently face toward where the builder came from, which is usually toward core.
**Cons:** Exploration conveyors also face toward core (builder walked away from core, so d.opposite() points back). This doesn't distinguish chain conveyors from exploration waste.

### RECOMMENDED: Combine Methods 1 + 4

```python
def find_best_chain_conveyor(c, core_pos):
    """Find the best conveyor to splice a splitter into."""
    candidates = []
    
    for eid in c.get_nearby_buildings():
        try:
            if (c.get_entity_type(eid) != EntityType.CONVEYOR
                    or c.get_team(eid) != c.get_team()):
                continue
            
            epos = c.get_position(eid)
            d2 = epos.distance_squared(core_pos)
            
            # Must be 4-50 tiles from core (not too close, not too far)
            if d2 < 4 or d2 > 50:
                continue
            
            # Quick filter: must face roughly toward core
            if not faces_toward_core(c, eid, core_pos):
                continue
            
            # Expensive check: must trace to core
            if not is_chain_conveyor(c, eid):
                continue
            
            # Check perpendicular tiles for branch + sentinel space
            conv_dir = c.get_direction(eid)
            for branch_dir in [perp_left(conv_dir), perp_right(conv_dir)]:
                bp = epos.add(branch_dir)
                sp = bp.add(branch_dir)
                if (c.get_tile_env(bp) != Environment.WALL
                        and c.get_tile_env(sp) != Environment.WALL
                        and c.is_tile_empty(bp)
                        and c.is_tile_empty(sp)):
                    # Score: prefer conveyors further from core (more resource flow)
                    # but not too far (builder needs to walk there)
                    candidates.append((eid, epos, conv_dir, branch_dir, bp, sp, d2))
                    break
        except Exception:
            continue
    
    if not candidates:
        return None
    
    # Pick the candidate with moderate distance from core (sweet spot: 10-30 d^2)
    candidates.sort(key=lambda x: abs(x[6] - 20))
    return candidates[0]
```

---

## DISTINGUISHING CHAIN CONVEYORS FROM EXPLORATION WASTE

### The d.opposite() Problem

When a builder explores, it builds conveyors everywhere it walks. These "exploration conveyors" have `d.opposite()` facing, which means they point back toward core -- exactly like chain conveyors. How to tell them apart?

**Key differences:**

| Property | Chain Conveyor | Exploration Conveyor |
|----------|---------------|---------------------|
| Connects to harvester upstream | YES | NO |
| Traces to core downstream | YES | Probably not (dead ends) |
| Has downstream conveyor accepting its output | YES | Often NO (chain breaks) |
| Currently holds a resource | Sometimes | Never |
| Adjacent to other conveyors in sequence | YES (chain) | Maybe (scattered) |

### The Simplest Discriminator: Downstream Neighbor

The cheapest and most reliable single check:

```python
def has_downstream_neighbor(c, conv_id):
    """Check if the conveyor's output tile has another transport building."""
    try:
        conv_pos = c.get_position(conv_id)
        conv_dir = c.get_direction(conv_id)
        output_tile = conv_pos.add(conv_dir)
        
        bid = c.get_tile_building_id(output_tile)
        if bid is None:
            return False
        
        btype = c.get_entity_type(bid)
        return btype in (EntityType.CONVEYOR, EntityType.SPLITTER, EntityType.CORE,
                         EntityType.BRIDGE)
    except Exception:
        return False
```

**Why this works:** An exploration conveyor's output tile is usually either empty (the builder moved on without building there) or has another conveyor facing a different direction (also d.opposite() from a different walk path). A chain conveyor's output tile has the NEXT conveyor in the chain, which accepts from the correct side.

Actually, since d.opposite() chains are built step-by-step as the builder walks, the output tile almost always has a conveyor (the previous step). The real question is whether the chain is COMPLETE all the way to core.

**Conclusion:** `is_chain_conveyor` (trace-to-core) is the gold standard. Use `faces_toward_core` as a cheap pre-filter.

---

## HANDLING WINDING PATHS

### Problem: d.opposite() Chains Aren't Straight

When a builder navigates around walls, it changes direction. The chain might go:
```
Harvester -> SOUTH -> SOUTH -> SOUTHEAST -> EAST -> EAST -> SOUTH -> Core
```

Each conveyor faces the opposite of the builder's step direction. This creates a winding chain where adjacent conveyors face different directions.

### Impact on Splitter Placement

When we replace a conveyor with a splitter:
- The splitter must face the SAME direction as the conveyor it replaces
- The splitter accepts from BEHIND only (opposite of facing)
- The upstream conveyor must output INTO the splitter's back

**If the chain turns at the splice point:**
```
Before:
[Conv facing SOUTH] -> [Conv facing SOUTHEAST] -> [Conv facing EAST]
                        ↑ this one we want to replace

After replacing middle conveyor with splitter:
[Conv facing SOUTH] -> [Splitter facing SOUTHEAST] -> [Conv facing EAST]
```

The splitter faces SOUTHEAST, so it accepts from NORTHWEST (behind). The upstream conveyor faces SOUTH, outputting to the tile south of it. Does this tile match the splitter's position? Yes, if the upstream conveyor is directly north of the splitter. But the upstream conveyor faces SOUTH, not SOUTHEAST -- so its output goes to the tile directly south, which IS the splitter's position. The splitter accepts from NORTHWEST (behind). The upstream conveyor is to the NORTH (or NORTHWEST) of the splitter.

**Key question:** Does a SOUTH-facing conveyor output to a tile that is the back (NORTHWEST) of a SOUTHEAST-facing splitter?

The splitter at position P faces SOUTHEAST. Its "back" is NORTHWEST. So it accepts input from position P.add(NORTHWEST). The upstream conveyor at position P.add(NORTHWEST) faces SOUTH and outputs to P.add(NORTHWEST).add(SOUTH). This would be position (P.x-1+0, P.y-1+1) = (P.x-1, P.y). That's NOT position P -- it's one tile west.

**This means chain turns can BREAK the splitter splice!**

### Solution: Only Splice Into Straight Segments

The safest approach is to only replace conveyors that are part of a STRAIGHT segment -- where the upstream conveyor faces the same direction:

```python
def is_straight_segment(c, conv_id):
    """Check if this conveyor and its upstream neighbor face the same direction."""
    try:
        conv_pos = c.get_position(conv_id)
        conv_dir = c.get_direction(conv_id)
        
        # Look at the tile behind (where input comes from)
        back_tile = conv_pos.add(conv_dir.opposite())
        back_id = c.get_tile_building_id(back_tile)
        if back_id is None:
            return False
        
        back_type = c.get_entity_type(back_id)
        if back_type not in (EntityType.CONVEYOR, EntityType.HARVESTER):
            return False
        
        if back_type == EntityType.HARVESTER:
            return True  # Harvester directly feeding -- always OK
        
        back_dir = c.get_direction(back_id)
        return back_dir == conv_dir  # Same direction = straight segment
    except Exception:
        return False
```

**Why this works:** If the upstream conveyor faces the same direction as our target, then:
- Upstream outputs to our target's position (straight line)
- Splitter replaces our target, faces same direction
- Splitter's back faces opposite direction
- Upstream conveyor outputs into splitter's back -- CORRECT

**When the chain turns:** The upstream conveyor faces a different direction, and its output might not align with the splitter's input side. Skip these and find a straight segment instead.

---

## CHOOSING THE BEST CONVEYOR TO SPLICE

### Ranking Criteria

1. **Must be part of an active chain** (traces to core)
2. **Must be in a straight segment** (upstream faces same direction)
3. **Must have empty perpendicular tiles** (for branch + sentinel)
4. **Prefer moderate distance from core** (d^2 = 10-30): close enough for the sentinel builder to reach, far enough that the sentinel has good defensive coverage
5. **Prefer chains with more harvesters** (more resource flow = faster ammo delivery)

### Optimal Distance from Core

- **Too close (d^2 < 4):** Sentinel would be on core tiles. No room.
- **Too close (d^2 4-9):** Sentinel fires in limited directions. Barriers would be more useful here.
- **Sweet spot (d^2 10-30):** Sentinel at ~3-5 tiles from core. Good vision coverage. Resource chains pass through this zone.
- **Too far (d^2 > 50):** Sentinel builder has to walk far. Chain may be winding.

---

## THE SIMPLEST INTEGRATION

### Revised Algorithm

```python
def find_and_splice(c, core_pos):
    """Find the best chain conveyor and return splice parameters."""
    for eid in c.get_nearby_buildings():
        try:
            if (c.get_entity_type(eid) != EntityType.CONVEYOR
                    or c.get_team(eid) != c.get_team()):
                continue
            
            epos = c.get_position(eid)
            edir = c.get_direction(eid)
            d2 = epos.distance_squared(core_pos)
            
            # Distance filter
            if d2 < 8 or d2 > 40:
                continue
            
            # Must face roughly toward core
            to_core = epos.direction_to(core_pos)
            if edir != to_core and edir != to_core.rotate_left() and edir != to_core.rotate_right():
                continue
            
            # Must be straight segment (upstream faces same direction)
            back_tile = epos.add(edir.opposite())
            back_id = c.get_tile_building_id(back_tile)
            if back_id is None:
                continue
            back_type = c.get_entity_type(back_id)
            if back_type == EntityType.CONVEYOR:
                if c.get_direction(back_id) != edir:
                    continue  # Chain turns here, skip
            elif back_type != EntityType.HARVESTER:
                continue  # Not a valid upstream
            
            # Must have downstream conveyor
            fwd_tile = epos.add(edir)
            fwd_id = c.get_tile_building_id(fwd_tile)
            if fwd_id is None:
                continue
            fwd_type = c.get_entity_type(fwd_id)
            if fwd_type not in (EntityType.CONVEYOR, EntityType.SPLITTER, EntityType.CORE):
                continue
            
            # Check perpendicular space for branch + sentinel
            for branch_dir in [edir.rotate_left().rotate_left(),
                               edir.rotate_right().rotate_right()]:
                bp = epos.add(branch_dir)
                sp = bp.add(branch_dir)
                try:
                    if (c.get_tile_env(bp) != Environment.WALL
                            and c.get_tile_env(sp) != Environment.WALL
                            and c.is_tile_empty(bp)
                            and c.is_tile_empty(sp)):
                        return (epos, edir, bp, sp, branch_dir)
                except:
                    pass
        except Exception:
            continue
    
    return None
```

### Key Changes from Current Code

1. **Added straight-segment check:** Only splices into conveyors where the upstream neighbor faces the same direction. Prevents broken chains.

2. **Added downstream check:** Verifies the conveyor's output tile has another transport building. Prevents splicing into dead-end exploration conveyors.

3. **Added direction-to-core filter:** Quick pre-filter that eliminates conveyors not facing toward core.

4. **Combined 3 checks in order of cost:** direction (cheap) -> straight segment (medium) -> downstream (medium). No need for the expensive trace-to-core in most cases, since having both upstream AND downstream neighbors in the right direction is a very strong signal.

---

## TIMING RECOMMENDATIONS

### When to Start Building Sentinels

Current trigger: round 1000, 3+ harvesters, near core, 200+ Ti.

**Recommended change:**
- **Round 200** (not 1000) -- Diamond bots have sentinels by round 150-200
- **2+ harvesters** (not 3) -- economy needs to be running but not massive
- **100+ Ti reserve** (not 200) -- splitter + conveyor + sentinel = ~39 Ti at base scale
- **Near core OR near active chain** -- sentinel builder should look for chains within vision, not just near core

### How Many Sentinels

| Elo Target | Sentinels | Why |
|------------|-----------|-----|
| 1500-1800 | 1-2 | Just having armed sentinels is a huge advantage |
| 1800-2000 | 2-3 | Axionite Inc uses 2-3 |
| 2000+ | 3-5 | Need zone control on multiple approach angles |

### Builder Role Assignment

Current: `id%5==1` is sentinel builder.

**Recommended:** Keep `id%5==1` as the primary sentinel builder. After building 2 sentinels, reassign to normal harvester duty. The sentinel cap (2-3) prevents over-investment.

---

## SENTINEL FACING DIRECTION

### Current Code (lines 316-327)

```python
face = self.sent_branch_dir
if c.can_build_sentinel(self.sent_sentinel_pos, face):
    c.build_sentinel(self.sent_sentinel_pos, face)
```

The sentinel faces the branch direction (perpendicular to the chain, away from it). This means:
- The sentinel fires sideways relative to the chain
- Ammo enters from `branch_dir.opposite()` (from the branch conveyor)
- Since sentinel accepts from non-facing directions, and it faces `branch_dir`, it does NOT face `branch_dir.opposite()` -- so ammo delivery WORKS

### Better: Face Toward Enemy

```python
enemy_dir = self._get_enemy_direction(c)
face = enemy_dir if enemy_dir else self.sent_branch_dir

# Verify ammo delivery won't be blocked
# Ammo enters from branch_dir.opposite()
# Sentinel must NOT face branch_dir.opposite()
if face == self.sent_branch_dir.opposite():
    face = self.sent_branch_dir  # Fallback to perpendicular

if c.can_build_sentinel(self.sent_sentinel_pos, face):
    c.build_sentinel(self.sent_sentinel_pos, face)
```

This makes the sentinel face toward the enemy (better coverage) while ensuring ammo delivery still works (sentinel doesn't face toward the ammo source).

---

## SUMMARY: CHANGES NEEDED FOR INTEGRATION

### Code Changes (Minimal)

1. **In `_build_sentinel_infra` step 0:** Replace the simple "closest conveyor" search with the `find_and_splice` function that validates:
   - Direction toward core
   - Straight segment (upstream faces same direction)
   - Downstream neighbor exists
   - Perpendicular space available

2. **Adjust triggers:**
   - Round threshold: 1000 -> 200
   - Harvester threshold: 3 -> 2
   - Ti threshold: 200 -> 100
   - Sentinel cap: 2 -> 3

3. **Sentinel facing:** Face toward enemy direction instead of branch direction (with ammo-delivery safety check).

4. **Remove near-core constraint:** The sentinel builder should look for chain conveyors anywhere in vision, not just within d^2 <= 36 of core. Chains often extend 5-10 tiles from core.

### What NOT to Change

- The multi-step state machine (steps 1-5) works correctly
- The walk-to logic works correctly
- The destroy-then-build-splitter sequence works correctly
- The branch conveyor + sentinel build sequence works correctly

The only thing broken is the FINDING logic (step 0). Fix that, and the rest works.

---

*Analysis based on code review of bots/buzzing/main.py (462 lines) and bots/splitter_test/main.py, combined with game mechanics research from phase6_research.md. April 6, 2026.*
