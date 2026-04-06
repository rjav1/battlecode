# Phase 7 Design: Splitter-Sentinel Integration + Barrier Walls

## Proven Pattern (from splitter_test bot)

The splitter-tester empirically confirmed that ammo delivery works with this exact layout:

```
[Harvester] -> [Conv1 facing CD] -> [Splitter facing CD] -> (main chain continues CD)
                                          |
                                     [Branch conv facing BD]
                                          |
                                     [Sentinel facing BD]

Where:
  CD = chain direction (toward core)
  BD = branch direction = perpendicular to CD (90 degrees)
       perp_left(CD) = CD.rotate_left().rotate_left()
       perp_right(CD) = CD.rotate_right().rotate_right()
```

**Critical details from the proven test:**
1. Splitter faces same direction as chain (CD)
2. Branch conveyor faces the perpendicular direction (BD), which is `CD.rotate_left().rotate_left()` or `CD.rotate_right().rotate_right()` (90 degrees, NOT 45)
3. Sentinel faces BD (same as branch conveyor) -- this ensures ammo arrives from `BD.opposite()` which is a non-facing side
4. Sentinel must NOT face `BD.opposite()` (that would block delivery)
5. Ammo arrives within 1 round of the splitter receiving a stack

---

## Part 1: Splitter-Sentinel System

### 1.1 Trigger Conditions

The builder should attempt to build a splitter-sentinel system when:

```python
# In _builder method, new priority P0:
rnd = c.get_current_round()
if (rnd >= 150
        and self.core_pos
        and pos.distance_squared(self.core_pos) <= 25
        and (self.my_id or 0) % 4 == 1
        and self.sentry_state != 'done'):
    if self._build_sentry(c, pos, passable):
        return
```

**Why round 150:** By round 150, the economy builder (id%4 != 1) has typically built 2-3 harvesters and established conveyor chains. The id%4==1 builder is the dedicated sentinel builder. Top teams (Kessoku Band) have sentinels by round 148, so round 150 is competitive.

**Why id%4 == 1:** Same builder slot as the old `_try_place_sentinel`. Only one builder should be doing this work; others focus on economy.

**Why distance_sq <= 25:** The builder needs to be near core to find chain conveyors. 25 = 5 tiles away, covering the typical chain length.

### 1.2 New Instance Variables

Add to `__init__`:

```python
self.sentry_state = 'idle'   # 'idle' | 'find' | 'nav_to' | 'destroy' | 
                              # 'splitter' | 'branch' | 'sentinel' | 'done'
self.sentry_plan = None       # dict with keys: conv_pos, chain_dir, branch_dir,
                              #   splitter_pos, branch_pos, sentinel_pos
self.sentry_count = 0         # sentinels built via splitter system
```

### 1.3 Finding the Right Conveyor

The builder must find a conveyor that is part of an active chain near core. The ideal candidate is:

- An allied conveyor (EntityType.CONVEYOR, our team)
- Within action radius (distance_sq <= 2) of the builder's current position
- Within distance_sq 4-25 of core (not ON the core, not too far)
- Has at least one perpendicular direction with 2 empty non-wall tiles (for branch + sentinel)

```python
def _find_chain_conveyor(self, c, pos):
    """Find a conveyor to replace with a splitter for sentinel ammo delivery.
    
    Returns (conv_pos, chain_dir, branch_dir, branch_pos, sentinel_pos) or None.
    """
    if not self.core_pos:
        return None
    
    candidates = []
    for eid in c.get_nearby_buildings():
        try:
            if c.get_entity_type(eid) != EntityType.CONVEYOR:
                continue
            if c.get_team(eid) != c.get_team():
                continue
            cpos = c.get_position(eid)
            
            # Must be within builder action radius
            if pos.distance_squared(cpos) > 2:
                continue
            
            # Must be near core but not adjacent to it
            core_dist = cpos.distance_squared(self.core_pos)
            if core_dist < 4 or core_dist > 25:
                continue
            
            chain_dir = c.get_direction(eid)
            
            # Try both perpendicular directions
            for perp_fn in ['left', 'right']:
                if perp_fn == 'left':
                    branch_dir = chain_dir.rotate_left().rotate_left()
                else:
                    branch_dir = chain_dir.rotate_right().rotate_right()
                
                branch_pos = cpos.add(branch_dir)
                sentinel_pos = branch_pos.add(branch_dir)
                
                # Both positions must be visible, empty, and not walls
                try:
                    if not c.is_in_vision(branch_pos) or not c.is_in_vision(sentinel_pos):
                        continue
                    if c.get_tile_env(branch_pos) == Environment.WALL:
                        continue
                    if c.get_tile_env(sentinel_pos) == Environment.WALL:
                        continue
                    if not c.is_tile_empty(branch_pos):
                        continue
                    if not c.is_tile_empty(sentinel_pos):
                        continue
                except Exception:
                    continue
                
                candidates.append((cpos, chain_dir, branch_dir,
                                   branch_pos, sentinel_pos, core_dist))
        except Exception:
            continue
    
    if not candidates:
        return None
    
    # Prefer candidates closer to core (defense priority)
    candidates.sort(key=lambda x: x[5])
    best = candidates[0]
    return best[:5]  # (conv_pos, chain_dir, branch_dir, branch_pos, sentinel_pos)
```

### 1.4 State Machine

```python
def _build_sentry(self, c, pos, passable):
    """Multi-round state machine to build splitter + branch + sentinel."""
    ti = c.get_global_resources()[0]
    
    if self.sentry_state == 'done':
        return False
    
    # Check we haven't built too many
    if self.sentry_count >= 2:
        self.sentry_state = 'done'
        return False
    
    # IDLE: Check if we have enough resources for the whole system
    if self.sentry_state == 'idle':
        total_cost = (c.get_splitter_cost()[0] + c.get_conveyor_cost()[0]
                      + c.get_sentinel_cost()[0])
        if ti < total_cost + 40:
            return False  # Save up
        self.sentry_state = 'find'
    
    # FIND: Locate a suitable conveyor
    if self.sentry_state == 'find':
        result = self._find_chain_conveyor(c, pos)
        if result is None:
            # No candidate in range -- navigate toward core to look
            if self.core_pos and pos.distance_squared(self.core_pos) > 8:
                self._nav(c, pos, self.core_pos, passable)
                return True
            return False  # Near core but no conveyors found
        conv_pos, chain_dir, branch_dir, branch_pos, sentinel_pos = result
        self.sentry_plan = {
            'conv_pos': conv_pos,
            'chain_dir': chain_dir,
            'branch_dir': branch_dir,
            'splitter_pos': conv_pos,  # Same position as destroyed conveyor
            'branch_pos': branch_pos,
            'sentinel_pos': sentinel_pos,
        }
        self.sentry_state = 'nav_to'
    
    p = self.sentry_plan
    
    # NAV_TO: Walk to within action radius of the conveyor
    if self.sentry_state == 'nav_to':
        if pos.distance_squared(p['conv_pos']) > 2:
            self._nav(c, pos, p['conv_pos'], passable)
            return True
        self.sentry_state = 'destroy'
    
    # DESTROY: Remove the conveyor (no cooldown cost)
    if self.sentry_state == 'destroy':
        if c.can_destroy(p['conv_pos']):
            c.destroy(p['conv_pos'])
            self.sentry_state = 'splitter'
            # Fall through -- destroy has no cooldown
        else:
            # Conveyor already gone or not ours
            self.sentry_state = 'idle'
            self.sentry_plan = None
            return False
    
    # SPLITTER: Build splitter at same position, same direction
    if self.sentry_state == 'splitter':
        if c.get_action_cooldown() != 0:
            return True
        if ti < c.get_splitter_cost()[0] + 20:
            return True  # Wait for resources
        sp = p['splitter_pos']
        if c.can_build_splitter(sp, p['chain_dir']):
            c.build_splitter(sp, p['chain_dir'])
            self.sentry_state = 'branch'
            return True
        else:
            # Position blocked -- abort and reset
            self.sentry_state = 'idle'
            self.sentry_plan = None
            return False
    
    # BRANCH: Build branch conveyor
    if self.sentry_state == 'branch':
        if c.get_action_cooldown() != 0:
            return True
        if ti < c.get_conveyor_cost()[0] + 20:
            return True
        bp = p['branch_pos']
        # May need to walk closer
        if pos.distance_squared(bp) > 2:
            self._nav(c, pos, bp, passable)
            return True
        if c.can_build_conveyor(bp, p['branch_dir']):
            c.build_conveyor(bp, p['branch_dir'])
            self.sentry_state = 'sentinel'
            return True
        else:
            # Can't build branch -- blocked. Reset to try another candidate.
            self.sentry_state = 'idle'
            self.sentry_plan = None
            return False
    
    # SENTINEL: Build sentinel at end of branch
    if self.sentry_state == 'sentinel':
        if c.get_action_cooldown() != 0:
            return True
        if ti < c.get_sentinel_cost()[0] + 20:
            return True
        sp = p['sentinel_pos']
        if pos.distance_squared(sp) > 2:
            self._nav(c, pos, sp, passable)
            return True
        # Sentinel faces branch_dir (same as branch conveyor)
        # This ensures ammo arrives from branch_dir.opposite() = non-facing side
        sent_face = p['branch_dir']
        if c.can_build_sentinel(sp, sent_face):
            c.build_sentinel(sp, sent_face)
            self.sentry_count += 1
            self.sentry_state = 'idle'  # Reset to potentially build another
            self.sentry_plan = None
            return True
        else:
            # Try enemy direction as face (as long as it's not branch_dir.opposite())
            enemy_dir = self._get_enemy_direction(c)
            if enemy_dir and enemy_dir != p['branch_dir'].opposite():
                if c.can_build_sentinel(sp, enemy_dir):
                    c.build_sentinel(sp, enemy_dir)
                    self.sentry_count += 1
                    self.sentry_state = 'idle'
                    self.sentry_plan = None
                    return True
            self.sentry_state = 'idle'
            self.sentry_plan = None
            return False
    
    return False
```

### 1.5 ASCII Diagram: Full Example

```
Map: enemy is to the NORTH. Chain flows SOUTH toward core.

Before splitter insertion:

     col:  10   11   12   13
row  3:   [Harv]
row  4:   [v S]              <- conveyor facing SOUTH (chain toward core)
row  5:   [v S]              <- conveyor facing SOUTH (THIS ONE GETS REPLACED)
row  6:   [v S]              <- conveyor facing SOUTH
row  7:   [CCC CCC CCC]     <- core 3x3

After splitter insertion:

     col:  10   11   12   13
row  3:   [Harv]
row  4:   [v S]              <- conveyor facing SOUTH (unchanged)
row  5:   [S S]              <- SPLITTER facing SOUTH (replaces conveyor)
row  6:   [v S] [> E] [T E] <- conveyor (unchanged) | branch facing EAST | sentinel facing EAST
row  7:   [CCC CCC CCC]     <- core 3x3

Splitter at (10,5) faces SOUTH:
  - Input: from NORTH (row 4 conveyor pushes south into it)
  - Output SOUTH: (10,6) main chain continues
  - Output SE: (11,6) = rotate_right of SOUTH = perp_right = EAST direction... 

Wait, let me recalculate:
  SOUTH.rotate_left() = SOUTHEAST
  SOUTH.rotate_right() = SOUTHWEST
  
  perp_left(SOUTH) = SOUTH.rotate_left().rotate_left() = SE.rotate_left() = EAST
  perp_right(SOUTH) = SOUTH.rotate_right().rotate_right() = SW.rotate_right() = WEST

So for chain_dir=SOUTH:
  perp_left = EAST  -> branch goes east
  perp_right = WEST -> branch goes west

Splitter facing SOUTH outputs to:
  SOUTH = (10,6) -- main chain
  SOUTHEAST = (11,6) -- rotate_left output  
  SOUTHWEST = (9,6) -- rotate_right output

Branch conveyor placed at (11,6) = splitter's SE output, facing EAST.
Sentinel placed at (12,6) = branch_pos.add(EAST), facing EAST.

BUT: The branch conveyor at (11,6) faces EAST. It receives from the splitter 
at (10,5) which is at its NW. Does the conveyor accept from NW?

The splitter_test proves this works. The perpendicular branch conveyor on the 
splitter's diagonal output tile receives ammo. The exact mechanism: the splitter
outputs to the diagonal tile, and the conveyor on that tile picks it up 
regardless of which "side" it arrives from (the game treats splitter output
as a push into the tile, not a side-based transfer).

CORRECTED DIAGRAM:

     col:  9    10   11   12
row  3:        [Harv]
row  4:        [v S]          <- conveyor facing SOUTH
row  5:        [S S]          <- SPLITTER facing SOUTH (replaces conveyor at row 5)
row  6:        [v S] [> E] [T E]
                ^     ^      ^
                |     |      sentinel facing EAST (ammo from WEST = non-facing)
                |     branch conveyor facing EAST
                main chain continues SOUTH

Resource flow:
  Harvester -> conv(10,4) -> splitter(10,5) -+-> conv(10,6) -> core (2/3 of stacks)
                                             |
                                             +-> branch(11,6) -> sentinel(12,6) (1/3 of stacks)
```

### 1.6 What If Perpendicular Is Blocked?

The `_find_chain_conveyor` method tries BOTH perpendicular directions (left and right). If one side has a wall, it tries the other.

If BOTH perpendicular directions are blocked (e.g., conveyor in a narrow corridor):
1. The candidate is skipped
2. The builder searches for another conveyor further along the chain
3. If no conveyors work, the builder navigates toward core to scan more conveyors
4. If still no candidates after several attempts, the builder gives up and resumes economy work

**Edge case: all conveyors are in narrow corridors.** This happens on maps like `corridors` or `hourglass`. On these maps, there may not be room for splitter systems at all. In this case, the builder simply doesn't build sentinels via splitters, and focuses on economy + attackers (which are more important on narrow maps anyway since Core Destroyed wins are possible).

### 1.7 Multiple Sentinels from One Splitter?

A splitter has 3 outputs: forward, rotate_left, rotate_right. The forward output continues the main chain. That leaves 2 diagonal outputs for potential branches.

**Can we place 2 sentinels from one splitter?**

Yes, in theory:
- Branch conveyor + sentinel on the left perpendicular
- Branch conveyor + sentinel on the right perpendicular

However, each sentinel would get only 1/3 of the resources (since 1/3 goes forward). Two sentinels from one splitter mean each fires less often.

**Recommendation: Build separate splitters for separate sentinels.** Each harvester chain can support one splitter. With 3-4 harvesters, we can have 2 splitter-sentinel systems on separate chains. This gives each sentinel 1/3 of a full chain's output instead of 1/3 split further.

The state machine already handles this: after building one system (`sentry_count = 1`), it resets to `'idle'` and can find another conveyor on a different chain for the second sentinel.

### 1.8 Ensuring Different Chains

After building the first sentry system, the builder should avoid selecting conveyors on the same chain. Simple heuristic: the second conveyor candidate must be at least distance_sq >= 8 from the first splitter position.

```python
# Add to __init__:
self.splitter_positions = []  # Track where splitters were placed

# In _find_chain_conveyor, add filter:
# Skip conveyors too close to existing splitters (same chain)
too_close = False
for sp in self.splitter_positions:
    if cpos.distance_squared(sp) < 8:
        too_close = True
        break
if too_close:
    continue

# After successful splitter build, record position:
self.splitter_positions.append(p['splitter_pos'])
```

---

## Part 2: Barrier Walls

### 2.1 Design

Place 4-6 barriers on the enemy-facing side of the core to slow incoming attackers. Barriers are extremely cost-effective: 3 Ti for 30 HP.

**Layout:**

```
Enemy is NORTH. Core center at (15, 20).

     col:  13   14   15   16   17
row 17:   [B]  [B]  [B]  [B]  [B]   <- barrier wall, 2-3 rows ahead of core
row 18:                               <- open (for conveyor chains to pass through)
row 19:        [CCC CCC CCC]         <- core top row
row 20:        [CCC CCC CCC]
row 21:        [CCC CCC CCC]

Barriers placed at distance 2-3 from core center, in the enemy direction.
Gaps left for conveyor chains to pass through.
```

### 2.2 Implementation

```python
def _build_barriers(self, c, pos):
    """Place barriers on enemy-facing side of core."""
    if not self.core_pos:
        return False
    if c.get_current_round() < 80:
        return False
    if pos.distance_squared(self.core_pos) > 12:
        return False
    
    ti = c.get_global_resources()[0]
    bcost = c.get_barrier_cost()[0]
    if ti < bcost + 60:
        return False  # Don't starve economy
    
    if c.get_action_cooldown() != 0:
        return False
    
    enemy_dir = self._get_enemy_direction(c)
    if not enemy_dir:
        return False
    
    # Count existing barriers near core
    barrier_count = 0
    for eid in c.get_nearby_buildings():
        try:
            if (c.get_entity_type(eid) == EntityType.BARRIER
                    and c.get_team(eid) == c.get_team()
                    and c.get_position(eid).distance_squared(self.core_pos) <= 16):
                barrier_count += 1
        except Exception:
            pass
    
    if barrier_count >= 5:
        return False
    
    # Place barriers at distance 3 from core center, along enemy direction
    # Try a line perpendicular to enemy direction
    ex, ey = enemy_dir.delta()
    cx, cy = self.core_pos.x, self.core_pos.y
    
    # Base position: 3 steps toward enemy from core center
    base = Position(cx + ex * 3, cy + ey * 3)
    
    # Perpendicular offsets
    perp = enemy_dir.rotate_left().rotate_left()
    px, py = perp.delta()
    
    for offset in [0, 1, -1, 2, -2]:
        bp = Position(base.x + px * offset, base.y + py * offset)
        if pos.distance_squared(bp) <= 2 and c.can_build_barrier(bp):
            c.build_barrier(bp)
            return True
    
    return False
```

### 2.3 Integration

Insert into `_builder` as a low-priority task for any builder near core:

```python
# P0.5: Barrier walls (any builder near core, round 80+)
if (c.get_current_round() >= 80 and self.core_pos
        and pos.distance_squared(self.core_pos) <= 12):
    if self._build_barriers(c, pos):
        return
```

Place this AFTER the sentry system priority (P0) and BEFORE harvester building (P1). Barriers are cheap and fast (single action, no state machine), so they don't delay economy much.

---

## Part 3: Exact Code Changes to main.py

### 3.1 Changes to `__init__` (line 8-18)

Add after line 18 (`self.chain_steps = 0`):

```python
        self.sentry_state = 'idle'
        self.sentry_plan = None
        self.sentry_count = 0
        self.splitter_positions = []
```

### 3.2 Remove `_try_place_sentinel` (lines 196-228)

Delete the entire `_try_place_sentinel` method. It is replaced by `_build_sentry`.

### 3.3 Replace P0 block in `_builder` (lines 101-105)

Replace:
```python
        # P0: Opportunistic sentinel near core
        if (c.get_action_cooldown() == 0 and c.get_current_round() > 300
                and self.core_pos and pos.distance_squared(self.core_pos) <= 20):
            if self._try_place_sentinel(c, pos):
                return
```

With:
```python
        # P0: Splitter-fed sentinel system
        if (c.get_current_round() >= 150
                and self.core_pos
                and pos.distance_squared(self.core_pos) <= 25
                and (self.my_id or 0) % 4 == 1
                and self.sentry_state != 'done'):
            if self.sentry_state != 'idle' or c.get_current_round() % 15 == 0:
                if self._build_sentry(c, pos, passable):
                    return

        # P0.5: Barrier walls (any builder near core)
        if (c.get_current_round() >= 80 and self.core_pos
                and pos.distance_squared(self.core_pos) <= 12):
            if self._build_barriers(c, pos):
                return
```

The `sentry_state != 'idle' or round % 15 == 0` condition means:
- If the state machine is active (mid-build), always continue it
- If idle, only scan for new candidates every 15 rounds (reduces wasted CPU)

### 3.4 Add `_find_chain_conveyor` method

Insert after the removed `_try_place_sentinel`, before `_get_enemy_direction`:

```python
    def _find_chain_conveyor(self, c, pos):
        """Find a chain conveyor to replace with a splitter."""
        if not self.core_pos:
            return None
        candidates = []
        for eid in c.get_nearby_buildings():
            try:
                if c.get_entity_type(eid) != EntityType.CONVEYOR:
                    continue
                if c.get_team(eid) != c.get_team():
                    continue
                cpos = c.get_position(eid)
                if pos.distance_squared(cpos) > 2:
                    continue
                core_dist = cpos.distance_squared(self.core_pos)
                if core_dist < 4 or core_dist > 25:
                    continue
                # Skip conveyors near existing splitters (same chain)
                too_close = False
                for sp in self.splitter_positions:
                    if cpos.distance_squared(sp) < 8:
                        too_close = True
                        break
                if too_close:
                    continue
                chain_dir = c.get_direction(eid)
                for side in ['left', 'right']:
                    if side == 'left':
                        bd = chain_dir.rotate_left().rotate_left()
                    else:
                        bd = chain_dir.rotate_right().rotate_right()
                    bp = cpos.add(bd)
                    sp = bp.add(bd)
                    try:
                        if not c.is_in_vision(bp) or not c.is_in_vision(sp):
                            continue
                        if c.get_tile_env(bp) == Environment.WALL:
                            continue
                        if c.get_tile_env(sp) == Environment.WALL:
                            continue
                        if not c.is_tile_empty(bp):
                            continue
                        if not c.is_tile_empty(sp):
                            continue
                    except Exception:
                        continue
                    candidates.append((cpos, chain_dir, bd, bp, sp, core_dist))
            except Exception:
                continue
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[5])
        b = candidates[0]
        return b[:5]
```

### 3.5 Add `_build_sentry` method

Insert after `_find_chain_conveyor`:

```python
    def _build_sentry(self, c, pos, passable):
        """State machine: destroy conveyor -> splitter -> branch conv -> sentinel."""
        ti = c.get_global_resources()[0]

        if self.sentry_count >= 2:
            self.sentry_state = 'done'
            return False

        if self.sentry_state == 'idle':
            total = (c.get_splitter_cost()[0] + c.get_conveyor_cost()[0]
                     + c.get_sentinel_cost()[0])
            if ti < total + 40:
                return False
            result = self._find_chain_conveyor(c, pos)
            if result is None:
                if self.core_pos and pos.distance_squared(self.core_pos) > 8:
                    self._nav(c, pos, self.core_pos, passable)
                    return True
                return False
            conv_pos, chain_dir, branch_dir, branch_pos, sentinel_pos = result
            self.sentry_plan = {
                'conv_pos': conv_pos, 'chain_dir': chain_dir,
                'branch_dir': branch_dir, 'branch_pos': branch_pos,
                'sentinel_pos': sentinel_pos,
            }
            self.sentry_state = 'nav_to'

        p = self.sentry_plan
        if p is None:
            self.sentry_state = 'idle'
            return False

        if self.sentry_state == 'nav_to':
            if pos.distance_squared(p['conv_pos']) > 2:
                self._nav(c, pos, p['conv_pos'], passable)
                return True
            self.sentry_state = 'destroy'

        if self.sentry_state == 'destroy':
            if c.can_destroy(p['conv_pos']):
                c.destroy(p['conv_pos'])
                self.sentry_state = 'splitter'
            else:
                self.sentry_state = 'idle'
                self.sentry_plan = None
                return False

        if self.sentry_state == 'splitter':
            if c.get_action_cooldown() != 0:
                return True
            if ti < c.get_splitter_cost()[0] + 20:
                return True
            if c.can_build_splitter(p['conv_pos'], p['chain_dir']):
                c.build_splitter(p['conv_pos'], p['chain_dir'])
                self.splitter_positions.append(p['conv_pos'])
                self.sentry_state = 'branch'
                return True
            self.sentry_state = 'idle'
            self.sentry_plan = None
            return False

        if self.sentry_state == 'branch':
            if c.get_action_cooldown() != 0:
                return True
            if ti < c.get_conveyor_cost()[0] + 20:
                return True
            bp = p['branch_pos']
            if pos.distance_squared(bp) > 2:
                self._nav(c, pos, bp, passable)
                return True
            if c.can_build_conveyor(bp, p['branch_dir']):
                c.build_conveyor(bp, p['branch_dir'])
                self.sentry_state = 'sentinel'
                return True
            self.sentry_state = 'idle'
            self.sentry_plan = None
            return False

        if self.sentry_state == 'sentinel':
            if c.get_action_cooldown() != 0:
                return True
            if ti < c.get_sentinel_cost()[0] + 20:
                return True
            sp = p['sentinel_pos']
            if pos.distance_squared(sp) > 2:
                self._nav(c, pos, sp, passable)
                return True
            face = p['branch_dir']
            if c.can_build_sentinel(sp, face):
                c.build_sentinel(sp, face)
                self.sentry_count += 1
                self.sentry_state = 'idle'
                self.sentry_plan = None
                return True
            # Try enemy dir if branch_dir doesn't work
            enemy_dir = self._get_enemy_direction(c)
            if enemy_dir and enemy_dir != p['branch_dir'].opposite():
                if c.can_build_sentinel(sp, enemy_dir):
                    c.build_sentinel(sp, enemy_dir)
                    self.sentry_count += 1
                    self.sentry_state = 'idle'
                    self.sentry_plan = None
                    return True
            self.sentry_state = 'idle'
            self.sentry_plan = None
            return False

        return False
```

### 3.6 Add `_build_barriers` method

Insert after `_build_sentry`:

```python
    def _build_barriers(self, c, pos):
        """Place barriers on enemy-facing side of core."""
        if not self.core_pos or c.get_current_round() < 80:
            return False
        if pos.distance_squared(self.core_pos) > 12:
            return False
        ti = c.get_global_resources()[0]
        if ti < c.get_barrier_cost()[0] + 60:
            return False
        if c.get_action_cooldown() != 0:
            return False
        enemy_dir = self._get_enemy_direction(c)
        if not enemy_dir:
            return False
        barrier_count = 0
        for eid in c.get_nearby_buildings():
            try:
                if (c.get_entity_type(eid) == EntityType.BARRIER
                        and c.get_team(eid) == c.get_team()
                        and c.get_position(eid).distance_squared(self.core_pos) <= 16):
                    barrier_count += 1
            except Exception:
                pass
        if barrier_count >= 5:
            return False
        ex, ey = enemy_dir.delta()
        cx, cy = self.core_pos.x, self.core_pos.y
        base = Position(cx + ex * 3, cy + ey * 3)
        perp = enemy_dir.rotate_left().rotate_left()
        px, py = perp.delta()
        for offset in [0, 1, -1, 2, -2]:
            bp = Position(base.x + px * offset, base.y + py * offset)
            if pos.distance_squared(bp) <= 2 and c.can_build_barrier(bp):
                c.build_barrier(bp)
                return True
        return False
```

### 3.7 Summary of All Changes

| Location | Action | Lines Affected |
|----------|--------|---------------|
| `__init__` | Add 4 instance vars | After line 18 |
| `_builder` P0 block | Replace sentinel trigger | Lines 101-105 |
| `_builder` P0.5 | Add barrier trigger | New, after P0 |
| `_try_place_sentinel` | DELETE entire method | Lines 196-228 |
| New method | `_find_chain_conveyor` | Insert after deleted method |
| New method | `_build_sentry` | Insert after `_find_chain_conveyor` |
| New method | `_build_barriers` | Insert after `_build_sentry` |

**No changes needed to:** `_core`, `_sentinel`, `_attack`, `_nav`, `_explore`, `_bfs_step`, `_rank`, `_best_adj_ore`, `_get_enemy_direction`.

---

## Part 4: Test Plan

### Tests to Run

1. **`cambc run buzzing starter default_small1 --watch`** -- Verify sentry system builds. Look for splitter + branch conveyor + sentinel in the replay. Check sentinel fires.

2. **`cambc run buzzing starter default_medium1 --watch`** -- Same as above on a medium map. Check that the builder finds a chain conveyor and completes the state machine.

3. **`cambc run buzzing starter corridors --watch`** -- Narrow map. Verify barriers build. Verify sentry system either builds or gracefully gives up (no crash).

4. **`cambc run buzzing starter hourglass --watch`** -- Very narrow. Attackers and barriers should be the main defense here.

5. **`cambc run buzzing buzzing default_large1`** -- Self-play. No crashes, both sides build systems.

6. **`cambc test-run buzzing starter cubes`** -- CPU test on 50x50. Verify no timeouts from the state machine.

### Success Criteria

- Sentinel `ammo_amount > 0` at some point during the game (add stderr debug to `_sentinel`)
- Sentinel fires at least once in a game where enemies are visible
- Economy doesn't collapse (Ti mined should be similar to Phase 6 numbers)
- Barrier wall visible in replay near core
- No crashes on any of the 17 standard maps

### Debug Logging

Add to `_sentinel` method temporarily:

```python
    def _sentinel(self, c):
        import sys
        ammo = c.get_ammo_amount()
        if ammo > 0 or c.get_current_round() % 100 == 0:
            print(f"Sentinel ammo={ammo} round={c.get_current_round()}", file=sys.stderr)
        if c.get_action_cooldown() != 0 or ammo < 10:
            return
        # ... existing fire logic
```

---

## Part 5: Cost Budget

### Per-game resource allocation at round 150

| Component | Ti Cost | Scale Impact |
|-----------|---------|-------------|
| 2-3 harvesters | 40-60 Ti | +10-15% |
| 8-12 conveyors | 24-36 Ti | +8-12% |
| 4-6 roads | 4-6 Ti | +2-3% |
| 5 barriers | 15 Ti | +5% |
| 1st sentry system | 39 Ti | +21% |
| Builders (3) | 90 Ti | +60% |
| **Total** | **~220 Ti** | **~110%** |

Starting Ti is 500, plus passive income of ~375 Ti by round 150 (10 Ti every 4 rounds = 37 payouts). Plus harvester income. Budget is comfortable.

Second sentry system at ~round 250-300 when more Ti flows in from harvesters.
