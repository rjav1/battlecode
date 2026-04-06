# Phase 6 Design: Splitter-Based Sentinel Ammo + Defensive Improvements

## Problem Statement

Sentinels never fire because they have no ammo. Phase 5 proved that without splitters, no approach works: feed conveyors have no source, chain intercepts break the economy, and adjacent conveyors push toward core not toward turrets. The solution requires **splitters** to branch resources from existing conveyor chains.

---

## 1. Splitter Mechanics Review

From the game rules:

- **Cost:** 6 Ti, +1% scale (same scale as conveyor)
- **HP:** 20
- **Input:** Accepts resources from behind ONLY (the tile at `facing.opposite()`)
- **Output:** Alternates between 3 directions: `facing`, `facing.rotate_left()`, `facing.rotate_right()`
- **Distribution:** Least-recently-used direction gets the next stack

This means a splitter facing NORTH:
- Accepts input from SOUTH (behind)
- Outputs to NORTH (facing), NORTHWEST (rotate_left), NORTHEAST (rotate_right)
- 1/3 of stacks go to each output direction on average

---

## 2. Core Design: The Splitter-Feed Pattern

### 2.1 Target Layout

The goal is to build this pattern somewhere along an existing conveyor chain:

```
Legend:
  H = Harvester
  > = Conveyor facing EAST (toward core)
  S = Splitter facing EAST
  v = Feed conveyor facing SOUTH
  T = Sentinel (facing any direction toward enemy)
  C = Core (3x3)

BEFORE (existing chain):
  H -> [>] -> [>] -> [>] -> [>] -> [C]

AFTER (splitter inserted):
  H -> [>] -> [S] -> [>] -> [>] -> [C]
                |
               [v]
                |
               [T]
```

The splitter replaces one conveyor in the chain. It faces the same direction as the replaced conveyor so that resources continue flowing toward core. One of its two side outputs feeds a short conveyor spur to a sentinel.

### 2.2 Concrete Example (chain flowing EAST)

```
     col:  0    1    2    3    4    5    6
row 5:    [H]  [>]  [S→] [>]  [>]  [CCC]
row 6:              [v↓]                    ← feed conveyor facing SOUTH
row 7:              [T]                     ← sentinel facing EAST (toward enemy)
```

- Splitter at (2,5) faces EAST
- Input comes from (1,5) -- the conveyor behind it (WEST side)
- Outputs go to: (3,5) EAST (main chain continues), (2,4) NE, (2,6) SE
- Feed conveyor at (2,6) faces SOUTH, receives from splitter's SE output
- Sentinel at (2,7) faces EAST toward enemy
- The feed conveyor outputs SOUTH into the sentinel's tile
- Sentinel accepts ammo from non-facing sides, so it accepts from NORTH (the feed conveyor's output side)

**Wait -- correction on conveyor output.** A conveyor facing SOUTH outputs to the tile at its SOUTH side. The sentinel at (2,7) receives from (2,6)'s SOUTH output. The sentinel faces EAST, so NORTH is a non-facing side. This works.

### 2.3 General Pattern for Each Chain Direction

The chain direction is the direction conveyors face (toward core). For each chain direction, here are the two possible spur directions:

| Chain Dir | Splitter Faces | Left Spur Dir | Right Spur Dir |
|-----------|---------------|---------------|----------------|
| NORTH     | NORTH         | NORTHWEST     | NORTHEAST      |
| SOUTH     | SOUTH         | SOUTHEAST     | SOUTHWEST      |
| EAST      | EAST          | NORTHEAST     | SOUTHEAST      |
| WEST      | WEST          | NORTHWEST     | SOUTHWEST      |
| NE        | NE            | NORTH         | EAST           |
| NW        | NW            | WEST          | NORTH          |
| SE        | SE            | EAST          | SOUTH          |
| SW        | SW            | SOUTH         | WEST           |

For each spur direction, the feed conveyor faces that same direction, and the sentinel sits one tile beyond the feed conveyor in that direction.

---

## 3. Placement Algorithm

### 3.1 When to Trigger

**Trigger conditions (checked by builder with `my_id % 4 == 1`):**
- Round >= 100 (earlier than Phase 5's round 200)
- At least 1 harvester connected to core (economy established)
- Fewer than 2 sentinels visible near core
- Ti >= sentinel_cost + splitter_cost + conveyor_cost + 30 (budget reserve)
- Builder is within distance_sq <= 25 of core

### 3.2 Phase 1: Find a Conveyor to Replace

The builder scans nearby buildings to find a conveyor that is part of a chain (has input from one side and outputs toward core).

```python
def _find_chain_conveyor(self, c, pos):
    """Find a conveyor near core that can be replaced with a splitter."""
    candidates = []
    for eid in c.get_nearby_buildings():
        try:
            if (c.get_entity_type(eid) != EntityType.CONVEYOR
                    or c.get_team(eid) != c.get_team()):
                continue
            cpos = c.get_position(eid)
            cdir = c.get_direction(eid)
            # Must be within action range to destroy + rebuild
            if pos.distance_squared(cpos) > 2:
                continue
            # Prefer conveyors 2-4 tiles from core (not too close, not too far)
            if self.core_pos:
                dist = cpos.distance_squared(self.core_pos)
                if dist < 2 or dist > 25:
                    continue
            # Check that at least one spur direction has 2 empty tiles
            # (one for feed conveyor, one for sentinel)
            left_spur = cdir.rotate_left()
            right_spur = cdir.rotate_right()
            for spur_dir in [left_spur, right_spur]:
                feed_pos = cpos.add(spur_dir)
                sent_pos = feed_pos.add(spur_dir)
                if (c.is_tile_empty(feed_pos) and c.is_tile_empty(sent_pos)
                        and c.get_tile_env(feed_pos) != Environment.WALL
                        and c.get_tile_env(sent_pos) != Environment.WALL):
                    candidates.append((cpos, cdir, spur_dir, feed_pos, sent_pos))
        except Exception:
            continue
    # Prefer candidates closer to core (defense priority)
    if candidates and self.core_pos:
        candidates.sort(key=lambda x: x[0].distance_squared(self.core_pos))
    return candidates[0] if candidates else None
```

### 3.3 Phase 2: Destroy-and-Replace Sequence

This is a multi-step process that happens across multiple rounds. We use a state machine:

**State 0 -- FIND:** Scan for a candidate conveyor. Store the plan.
**State 1 -- DESTROY:** Walk to the conveyor, destroy it with `c.destroy(cpos)`.
**State 2 -- BUILD SPLITTER:** Build splitter at same position, same direction.
**State 3 -- BUILD FEED CONVEYOR:** Build conveyor at feed_pos facing spur_dir.
**State 4 -- BUILD SENTINEL:** Build sentinel at sent_pos facing toward enemy.
**State 5 -- DONE:** Resume normal builder behavior.

```python
# State machine instance variables (in __init__):
self.sentry_state = 0      # 0=idle, 1=destroy, 2=splitter, 3=feed, 4=sentinel, 5=done
self.sentry_plan = None    # (conv_pos, conv_dir, spur_dir, feed_pos, sent_pos)
```

### 3.4 Detailed State Machine Pseudocode

```python
def _build_sentry_system(self, c, pos):
    """Multi-round state machine to build splitter + feed + sentinel."""
    ti = c.get_global_resources()[0]

    # STATE 0: Find candidate
    if self.sentry_state == 0:
        plan = self._find_chain_conveyor(c, pos)
        if plan is None:
            return False  # No candidate found, skip
        self.sentry_plan = plan
        self.sentry_state = 1
        # Fall through to try destroy immediately

    conv_pos, conv_dir, spur_dir, feed_pos, sent_pos = self.sentry_plan

    # STATE 1: Navigate to conveyor and destroy it
    if self.sentry_state == 1:
        if pos.distance_squared(conv_pos) > 2:
            # Walk toward the conveyor
            self._nav(c, pos, conv_pos, ...)
            return True
        if c.can_destroy(conv_pos):
            c.destroy(conv_pos)
            self.sentry_state = 2
            # destroy() has no cooldown, fall through immediately
        else:
            # Can't destroy -- tile may have changed
            self.sentry_state = 0
            self.sentry_plan = None
            return False

    # STATE 2: Build splitter at same position, same direction
    if self.sentry_state == 2:
        if c.get_action_cooldown() != 0:
            return True  # Wait for cooldown
        cost = c.get_splitter_cost()[0]
        if ti < cost + 30:
            return True  # Wait for resources
        if c.can_build_splitter(conv_pos, conv_dir):
            c.build_splitter(conv_pos, conv_dir)
            self.sentry_state = 3
            return True
        else:
            # Position blocked -- abort
            self.sentry_state = 0
            self.sentry_plan = None
            return False

    # STATE 3: Build feed conveyor
    if self.sentry_state == 3:
        if c.get_action_cooldown() != 0:
            return True
        cost = c.get_conveyor_cost()[0]
        if ti < cost + 30:
            return True
        if c.can_build_conveyor(feed_pos, spur_dir):
            c.build_conveyor(feed_pos, spur_dir)
            self.sentry_state = 4
            return True
        else:
            self.sentry_state = 0
            self.sentry_plan = None
            return False

    # STATE 4: Build sentinel
    if self.sentry_state == 4:
        if c.get_action_cooldown() != 0:
            return True
        cost = c.get_sentinel_cost()[0]
        if ti < cost + 30:
            return True
        enemy_dir = self._get_enemy_direction(c)
        if not enemy_dir:
            enemy_dir = conv_dir  # Fallback
        if c.can_build_sentinel(sent_pos, enemy_dir):
            c.build_sentinel(sent_pos, enemy_dir)
            self.sentry_state = 5
            return True
        else:
            self.sentry_state = 0
            self.sentry_plan = None
            return False

    # STATE 5: Done
    return False
```

### 3.5 Critical Detail: Sentinel Ammo Input Direction

A turret accepts ammo from conveyors that output onto its tile from **non-facing** directions. So:

- Sentinel faces EAST (toward enemy)
- Feed conveyor outputs SOUTH into sentinel's tile from the NORTH side
- NORTH is not EAST, so the sentinel accepts the ammo

**Validation rule:** `spur_dir != enemy_dir`. If the spur direction equals the sentinel's facing direction, the sentinel will reject the ammo. We must check this in the candidate selection:

```python
# In _find_chain_conveyor, add this check:
enemy_dir = self._get_enemy_direction(c)
if enemy_dir and spur_dir == enemy_dir:
    continue  # Sentinel would reject ammo from this direction
```

### 3.6 What About Diagonal Chains?

Many chains will use diagonal conveyors (NE, NW, SE, SW). The same pattern works.

Example: chain flowing NORTHEAST toward core:

```
     col:  0    1    2    3
row 4:                   [CCC]
row 3:              [/NE]
row 2:         [S/NE]           ← splitter facing NE
row 3:         [v↓E]            ← feed conveyor facing EAST (right spur)
row 4:         [T]              ← sentinel
```

Wait -- let me recalculate. Splitter facing NE:
- Input from SW (behind)
- Outputs to NE (facing), NORTH (rotate_left of NE), EAST (rotate_right of NE)

So the right spur is EAST: feed_pos = splitter_pos.add(EAST), and the feed conveyor faces EAST. Sentinel at feed_pos.add(EAST), facing toward enemy.

Actually this needs only 1 feed conveyor if the sentinel is directly adjacent to the splitter's side output. But the splitter only outputs to the 3 forward tiles. The sentinel can sit directly on the output tile of a spur direction IF:
- We skip the feed conveyor
- The sentinel's non-facing side includes the direction FROM which the splitter pushes

**Simplification: 1-tile spur (no feed conveyor needed)**

If we place the sentinel directly on the splitter's side-output tile:

```
Splitter at (2,5) faces EAST, outputs to:
  (3,5) EAST    -- main chain continues
  (2,4) NE      -- left spur output
  (2,6) SE      -- right spur output

Place sentinel at (2,6). The splitter outputs SE into (2,6).
The sentinel at (2,6) faces EAST (toward enemy).
The splitter's SE output enters from the NW direction.
NW != EAST, so the sentinel accepts it.
```

**This eliminates the need for a feed conveyor entirely!** The splitter's side output goes directly into the sentinel.

BUT WAIT: The splitter outputs in direction SE, which means it pushes the resource to tile (2,6). The resource arrives at (2,6). For a turret to accept the resource, a conveyor/splitter must output onto the turret's tile. The splitter at (2,5) outputs SE to tile (2,6). The sentinel is at (2,6). The resource arrives from direction NW (relative to sentinel). If sentinel faces EAST, then NW is a non-facing direction, so it accepts.

**However**, re-reading the rules: "Ammo fed via conveyors from non-facing directions." The question is whether a splitter counts as a conveyor for ammo feeding purposes. The rules say "Turrets only accept resources when completely empty" and ammo is "fed via conveyors." Splitters are a type of transport building separate from conveyors. This is ambiguous.

**Safe approach: Keep the feed conveyor.** Use 1 feed conveyor between splitter and sentinel. This guarantees the ammo delivery mechanism is a conveyor (not relying on splitter-to-turret transfer which may not work).

### 3.7 Revised Layout (with 1 feed conveyor)

```
Case: Chain flowing EAST, spur going SOUTH (right spur)

     col:  2    3    4    5    6
row 5:    [>]  [S→] [>]  [>]  [CCC]    ← splitter replaces conveyor at (3,5)
row 6:         [v↓]                      ← feed conveyor at (3,6) facing SOUTH
row 7:         [T→]                      ← sentinel at (3,7) facing EAST
```

- Splitter at (3,5) outputs SE to (3,6) ← wait, SE would be (4,6), not (3,6)

**Let me re-derive the spur directions carefully.**

Splitter facing EAST:
- `facing` = EAST, output tile = pos.add(EAST) = (4,5)
- `facing.rotate_left()` = NORTHEAST, output tile = pos.add(NE) = (4,4)
- `facing.rotate_right()` = SOUTHEAST, output tile = pos.add(SE) = (4,6)

So the 3 output tiles are:
- (4,5) -- main chain continues EAST
- (4,4) -- NE spur
- (4,6) -- SE spur

The feed conveyor must sit on one of these spur tiles. Let's use (4,6) for the SE spur.

```
     col:  2    3    4    5    6
row 5:    [>]  [S→] [>→]               ← splitter at (3,5), conveyor at (4,5) continues chain
row 6:              [v↓]                ← feed conveyor at (4,6) facing SOUTH
row 7:              [T→]                ← sentinel at (4,7) facing EAST (toward enemy)
```

- Splitter at (3,5) faces EAST
- Splitter outputs SE to (4,6) where feed conveyor sits
- Feed conveyor at (4,6) faces SOUTH
- Feed conveyor accepts input from non-output sides. Its output is SOUTH. It accepts from NORTH, EAST, WEST. The splitter pushes from the NW direction into (4,6). NW... hmm.

**Critical: How does a splitter's output connect to a conveyor's input?**

A conveyor accepts resources from its 3 non-output sides. If a conveyor faces SOUTH, it accepts from NORTH, EAST, WEST (and diagonals? No -- conveyors accept from tiles on the 3 non-output sides).

Actually, re-reading: "Accepts from 3 non-output sides, outputs in facing direction." The non-output sides are the 3 sides that are NOT the facing direction. But what counts as a "side"?

Looking at the splitter: "Accepts input from behind ONLY (opposite of facing direction)." So input is from one specific direction. For conveyors: "Accepts from 3 non-output sides." This means from any direction EXCEPT the facing direction.

Wait -- there are 8 possible directions (N, NE, E, SE, S, SW, W, NW). "3 non-output sides" likely means the 3 cardinal-adjacent directions excluding the output. But that's confusing with 8 directions.

Let me re-read: conveyors output in facing direction. They accept from 3 non-output sides. With 4 sides (N, E, S, W), "3 non-output sides" makes sense for cardinal directions. But what about diagonal neighbors?

**Key insight from game docs:** The transport system works on a 4-side model (not 8). A tile has 4 sides: NORTH, EAST, SOUTH, WEST. A conveyor facing EAST outputs from its EAST side. It accepts on its NORTH, SOUTH, and WEST sides. Diagonal adjacency may not count for resource transfer.

**This changes the entire design.** If resource transfer only works along cardinal directions (N/E/S/W), then:

1. The chain must use cardinal-direction conveyors (not diagonal)
2. The splitter must face a cardinal direction
3. The feed conveyor must be cardinally adjacent to the splitter's output

Let me re-examine. Splitter facing EAST:
- Output directions: EAST, NE (rotate_left), SE (rotate_right)
- If NE and SE outputs go to diagonal tiles, and diagonal resource transfer doesn't work, then the splitter's side outputs are useless

**Actually, re-reading the splitter spec more carefully:** "Alternates output between 3 directions: facing, facing.rotate_left(), facing.rotate_right()." This means the splitter outputs to 3 tiles: the one in the facing direction, and the two 45-degree rotated tiles. These are the actual output tiles.

Whether resource transfer works diagonally is the key question. Since the game has 8 directions for facing and movement, and the splitter explicitly outputs in diagonal directions, **diagonal resource transfer must work**.

For conveyors: "Accepts from 3 non-output sides." With 8 directions, there are 7 non-output sides. "3 non-output sides" probably means: WEST (behind), and the two 90-degree perpendicular sides. For a conveyor facing EAST, input comes from WEST, NORTH, SOUTH (but not NW, NE, SW, SE).

Actually, let me reconsider. A tile has 4 edges (sides): North, East, South, West. A conveyor facing EAST outputs from the EAST side. It accepts from the remaining 3 sides: NORTH, SOUTH, WEST. This is the most natural interpretation.

For a splitter facing EAST:
- Input from the WEST side (behind)
- Outputs to: EAST (facing), NE (rotate_left), SE (rotate_right)

The NE and SE outputs go to diagonal tiles. The question is whether a conveyor/turret at a diagonal tile considers the resource as arriving from a specific side.

**Given the ambiguity, the safest approach uses only cardinal directions for the spur.** Use a splitter facing a cardinal direction, and use one of its side outputs that goes to a cardinal-direction tile through the intermediary.

**Actually, the simplest correct design:** Place the splitter facing a cardinal direction. Its rotate_left and rotate_right outputs are 45 degrees off. To feed a sentinel, we use ONE of these diagonal outputs, place a feed conveyor there, and that feed conveyor faces a cardinal direction toward the sentinel.

Let me try a completely clean example:

```
Splitter faces SOUTH (chain going southward toward core):
- Input: from NORTH (behind)
- Outputs: SOUTH (facing), SW (rotate_right), SE (rotate_left)

Place feed conveyor at SE diagonal tile, facing EAST.
Place sentinel at the tile EAST of the feed conveyor.

     col:  5    6    7
row 2:    [v↓]              ← incoming chain, conveyor facing SOUTH
row 3:    [S↓]              ← splitter at (5,3) facing SOUTH
row 4:    [v↓] [>→] [T]    ← chain continues SOUTH at (5,4)
                             ← feed at (6,4) facing EAST... wait
```

This doesn't work because the splitter's SE output goes to (6,4), which is diagonal from (5,3).

**Let me try the approach of using 2 feed conveyors to make a right-angle turn:**

```
Splitter faces EAST at (5,5):
- Outputs: (6,5) EAST, (6,4) NE, (6,6) SE
- Place feed conveyor at (6,6) facing SOUTH ← receives from NW (the splitter)
  Does a conveyor facing SOUTH accept from NW? 
  A conveyor facing SOUTH accepts from NORTH, EAST, WEST sides.
  NW is not one of {NORTH, EAST, WEST} if we use strict 4-side model.
```

This is getting circular. Let me take the approach that has the highest chance of working based on what we know:

**The known-working approach: cardinal-only chain with cardinal spur.**

Our current bot builds conveyors facing `d.opposite()` where d is the direction of movement. Builders often move diagonally, producing diagonal conveyors. But for the splitter system, we should find a chain segment where conveyors face a cardinal direction.

However, we can't control where cardinal conveyors appear in the chain. So instead:

### 3.8 Revised Approach: Dedicated Harvester-Fed Sentinel

Instead of modifying an existing chain, build a NEW mini-chain: harvester -> conveyor -> splitter -> feed -> sentinel, plus splitter -> conveyor -> core.

**This avoids the chain-modification problem entirely.**

But Phase 5 already noted: "A dedicated harvester with conveyors pointed at the sentinel" as an alternative. The problem is cost and complexity.

### 3.9 FINAL APPROACH: Replace-and-Spur (Cardinal Only)

Given the constraints, here is the simplest pattern that should work:

**Precondition:** Find a conveyor facing a cardinal direction (N, S, E, W) in the chain near core.

**Pattern (chain facing EAST):**

```
     col:  3    4    5    6    7
row 5:    [>→] [S→] [>→] [>→] [CCC]
row 6:         [v↓]
row 7:         [T→]
```

Step by step:
1. Conveyor at (4,5) faces EAST -- this is the one we replace
2. Destroy conveyor at (4,5)
3. Build splitter at (4,5) facing EAST
4. Splitter outputs: (5,5) EAST, (5,4) NE, (5,6) SE
5. Main chain continues through (5,5) which already has a conveyor
6. Build feed conveyor at (4,6) facing SOUTH -- **wait**, (4,6) is SOUTH of (4,5), but the splitter facing EAST outputs to (5,6) SE, not (4,6) SOUTH

**The splitter doesn't output SOUTH.** A splitter facing EAST outputs to EAST, NE, SE. None of those are straight SOUTH.

**This is the fundamental geometry problem.** The splitter's 3 outputs are all in a forward cone. To get resources to a tile that's perpendicular (SOUTH of the splitter), we need the splitter to face differently.

**Solution: Use the diagonal outputs and place a cardinal feed conveyor.**

Splitter at (4,5) faces EAST:
- SE output goes to (5,6)
- Place feed conveyor at (5,6) facing SOUTH
- Conveyor facing SOUTH outputs to (5,7)
- Place sentinel at (5,7) facing EAST

```
     col:  3    4    5    6    7
row 5:    [>→] [S→] [>→] [>→] [CCC]
row 6:              [v↓]              ← feed conveyor at (5,6) facing SOUTH
row 7:              [T→]              ← sentinel at (5,7) facing EAST
```

The question is: does the feed conveyor at (5,6) accept input from the splitter at (4,5) via the SE diagonal?

A conveyor facing SOUTH accepts from its NORTH, EAST, and WEST sides. The splitter is at (4,5), which is to the NW of (5,6). NW is NOT one of {NORTH, EAST, WEST}.

**If the game uses strict 4-side input, this fails.** The conveyor at (5,6) would not accept from the NW.

**Alternative: Place the feed conveyor directly on the splitter's cardinal output.**

The splitter facing EAST outputs EAST to (5,5). But that's the main chain tile. We can't use that.

**KEY REALIZATION: We should use a splitter facing a direction such that one side output hits a cardinally-adjacent tile.**

Consider a splitter facing NORTHEAST:
- Outputs: NE (facing), N (rotate_left), E (rotate_right)
- The N and E outputs are **cardinal directions**!
- If the chain flows NE, the main output continues NE
- The E output goes to a cardinally-adjacent tile
- A conveyor at that E tile facing EAST or SOUTH could accept from WEST (the splitter's side)

Wait... the splitter pushes from position (x,y) to (x+1,y) via EAST output. A conveyor at (x+1,y) facing SOUTH accepts from NORTH, EAST, WEST. The splitter is WEST of the conveyor. So the conveyor accepts from WEST. **This works!**

But our chains rarely flow NE consistently. Let me think differently.

**BETTER REALIZATION: Use a splitter facing a cardinal direction and note that it also outputs to two diagonal tiles. Then place the feed conveyor to be cardinally adjacent to one of those diagonal tiles.**

Splitter at (4,5) faces EAST → outputs to (5,5) E, (5,4) NE, (5,6) SE.

To feed sentinel, we need a conveyor at a tile that:
1. Is cardinally adjacent to a splitter output tile (so it accepts from a cardinal side), OR
2. Is directly on a splitter output tile and the splitter's push counts

If option 2 works (diagonal push into conveyor), then:
- Feed conveyor at (5,6) facing SOUTH, splitter pushes SE into it
- The push comes from NW. Conveyor accepts from N, E, W. NW is not accepted.

If option 2 doesn't work, we need option 1:
- Splitter outputs SE to (5,6). Place a conveyor at (5,6) facing any direction.
- Then place ANOTHER conveyor at (5,7) facing SOUTH, which accepts from (5,6) via NORTH.
- Then sentinel at (5,8).

This adds an extra conveyor but guarantees cardinal-to-cardinal transfer.

**But we still have the problem of getting resources FROM the splitter TO (5,6).**

### 3.10 THE DEFINITIVE SOLUTION

After analyzing the geometry, the cleanest pattern that guarantees cardinal resource flow:

**Use a splitter facing a cardinal direction. Place the feed conveyor on the main-chain forward tile (which gets 1/3 of resources). Branch the main chain around the splitter.**

No, that breaks the chain worse.

**Actually, the simplest solution:** Trust that diagonal resource transfer works (the game explicitly supports 8-direction splitter outputs), and place the sentinel directly on a splitter's diagonal output tile, with no feed conveyor.

**Testing this is critical.** But the design should support both approaches.

### 3.11 TWO-TIER DESIGN

**Tier A (simple, may work):** Place sentinel directly on splitter's diagonal output. No feed conveyor.

```
     col:  3    4    5    6
row 5:    [>→] [S→] [>→] [CCC]
row 6:              [T↗]         ← sentinel at (5,6), facing NE (toward enemy)
```

Splitter at (4,5) outputs SE to (5,6) where sentinel sits. Sentinel faces NE. SE (the direction resources arrive from) is not NE, so sentinel accepts. Resources come 1/3 of the time.

**Tier B (safe, uses feed conveyor):** If Tier A doesn't work (sentinel doesn't accept directly from splitter), add a feed conveyor between.

```
     col:  3    4    5    6
row 5:    [>→] [S→] [>→] [CCC]
row 6:         [v↓]              ← feed conveyor at (4,6) facing SOUTH
row 7:         [T→]              ← sentinel at (4,7) facing toward enemy
```

For Tier B, the feed conveyor at (4,6) must receive from the splitter. Splitter at (4,5) outputs SE to (5,6), not to (4,6). **So (4,6) is not a splitter output tile.** This doesn't work either.

**OK. Let me anchor on what the splitter actually outputs and design around that.**

Splitter at position P facing direction D outputs to exactly 3 tiles:
1. P.add(D) -- forward
2. P.add(D.rotate_left()) -- left
3. P.add(D.rotate_right()) -- right

For the spur, we use output #2 or #3. The feed conveyor OR sentinel must sit on that exact tile.

**Tier A:** Sentinel on output tile #2 or #3. Sentinel facing != arrival direction.

**Tier B:** Feed conveyor on output tile #2 or #3, facing away from splitter. Sentinel one tile further in that direction.

For Tier B, "facing away from splitter" means the feed conveyor faces TOWARD the sentinel. The conveyor's output goes to the sentinel's tile. The sentinel accepts from non-facing sides.

For Tier B to work, the feed conveyor must accept the splitter's push. Since the splitter pushes INTO the feed conveyor's tile, and the resource "arrives" there, the conveyor at that tile should pick it up.

**Actually, I think the resource distribution works by tile-to-tile transfer at end of round.** The splitter pushes to its 3 output tiles. If a conveyor/turret is on the output tile, it receives the resource. The direction of arrival shouldn't matter -- what matters is that the receiving entity is on the correct tile and is willing to accept.

For conveyors: "Accepts from 3 non-output sides" means the conveyor accepts resources that are being pushed FROM those 3 sides. So if a splitter at (4,5) pushes SE to (5,6), the resource comes FROM the NW side of (5,6). A conveyor at (5,6) facing SOUTH accepts from N, E, W. NW is NOT one of these.

**This confirms that diagonal-to-cardinal transfer does NOT work for conveyors.** The conveyor has 4 sides (N, E, S, W), and resources pushed diagonally don't enter through any of these 4 sides.

BUT for turrets: "Ammo fed via conveyors from non-facing directions." If the turret uses the same 4-side model, diagonal pushes also wouldn't work for turrets.

**HOWEVER:** The splitter itself "alternates output between 3 directions" which includes diagonals. If diagonal outputs couldn't reach anything, splitters would be nearly useless (only cardinal-facing splitters could use 1 of their 3 outputs). This seems wrong.

**Resolution:** The game likely uses 8-direction adjacency for resource transfer. "Accepts from 3 non-output sides" for a conveyor facing EAST means: it accepts from the 3 tiles on the WEST semicircle: NW, W, SW. This is the "behind" hemisphere. Similarly, turrets accept from 7 non-facing directions.

**Using 8-direction model:**

Conveyor facing SOUTH:
- Output: SOUTH
- Accepts from: N, NE, E, W, NW (all non-SOUTH directions? But docs say "3 non-output sides")

Hmm, "3 non-output sides" only works with a 4-side model. Let me re-read:

> **Conveyor:** Accepts from 3 non-output sides, outputs in facing direction

With 4 sides (N,E,S,W) and 8 possible facing directions, a conveyor facing NE:
- Output: NE (not one of the 4 sides)
- This doesn't fit the "4 sides" model

**The 4 sides likely refer to the 3 non-facing and non-opposite-facing sides in the 8-direction model? No...**

**Simplest interpretation:** "3 non-output sides" = every adjacent tile EXCEPT the one in the facing direction can provide input. But with 8 neighbors, that's 7, not 3.

**Most likely interpretation:** Conveyors accept from tiles on the 3 sides that are NOT the output side. With a 4-side model (each side covers 2-3 of the 8 neighbors):
- EAST side: tiles at E, NE, SE → output
- WEST side: tiles at W, NW, SW → input
- NORTH side: tile at N → input  
- SOUTH side: tile at S → input

So a conveyor facing EAST accepts from N, S, W, NW, SW (5 tiles), not just 3. "3 sides" refers to the 3 non-output sides of a square, each of which may cover multiple tiles.

Under this model, a conveyor at (5,6) facing SOUTH:
- Output side (SOUTH): S, SE, SW tiles
- Accepts from NORTH side (N, NE, NW), EAST side (E), WEST side (W)
- So it DOES accept from NW, which is where the splitter at (4,5) sits

**This means the design works!**

### 3.12 FINAL DEFINITIVE PATTERN

```
Chain flowing EAST:

     col:  3    4    5    6    7
row 5:    [>→] [S→] [>→] [>→] [CCC]
row 6:              [v↓]              ← feed conveyor at (5,6) facing SOUTH
row 7:              [T→]              ← sentinel at (5,7) facing EAST

Splitter at (4,5) faces EAST.
- Output SE to (5,6): feed conveyor picks up (NORTH side includes NW)
- Output EAST to (5,5): main chain continues
- Output NE to (5,4): wasted (or place another sentinel later)

Feed conveyor at (5,6) faces SOUTH.
- Accepts from NORTH side (includes NW where splitter is)
- Outputs SOUTH to (5,7)

Sentinel at (5,7) faces EAST (toward enemy).
- Accepts ammo from non-EAST directions (NORTH side is fine)
- Gets 1/3 of chain's resources as ammo
```

**If the 4-side model is too strict** (conveyor only accepts from exactly N, S, W for facing-EAST), we need the feed conveyor's NORTH side to align:

```
Alternative -- feed conveyor directly SOUTH of splitter:

     col:  3    4    5    6    7
row 5:    [>→] [S→] [>→] [>→] [CCC]
row 6:         [v↓]                   ← feed conveyor at (4,6) facing SOUTH
row 7:         [T→]                   ← sentinel at (4,7) facing EAST
```

But splitter at (4,5) facing EAST doesn't output SOUTH. Its outputs are EAST, NE, SE. The tile (4,6) is SOUTH of (4,5), which is NOT one of the outputs.

**We cannot reach directly SOUTH.** The splitter's closest output to SOUTH is SE = (5,6).

So the pattern in 3.12 is correct, assuming the NORTH side of the feed conveyor covers the NW neighbor (the splitter tile).

**For the implementation, we'll use this pattern and test it.** If it doesn't work, we fall back to Tier A (sentinel directly on splitter output, no feed conveyor).

---

## 4. Implementation-Ready Algorithm

### 4.1 New Instance Variables

```python
def __init__(self):
    # ... existing vars ...
    self.sentry_state = 0       # 0=idle, 1=nav_to_conv, 2=destroy, 3=build_splitter,
                                # 4=build_feed, 5=nav_to_feed, 6=build_sentinel, 7=done
    self.sentry_plan = None     # (conv_pos, conv_dir, spur_dir, feed_pos, sent_pos, sent_face)
    self.sentry_built = 0       # Number of sentry systems built by this builder
```

### 4.2 Candidate Selection

```python
CARDINAL = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]

def _find_sentry_candidate(self, c, pos):
    """Find a chain conveyor to replace with a splitter for sentinel ammo."""
    if not self.core_pos:
        return None
    enemy_dir = self._get_enemy_direction(c)
    candidates = []

    for eid in c.get_nearby_buildings():
        try:
            if (c.get_entity_type(eid) != EntityType.CONVEYOR
                    or c.get_team(eid) != c.get_team()):
                continue
            cpos = c.get_position(eid)
            cdir = c.get_direction(eid)

            # Must be reachable (within action radius to destroy)
            if pos.distance_squared(cpos) > 2:
                continue

            # Must be near core (distance_sq 4-20)
            core_dist = cpos.distance_squared(self.core_pos)
            if core_dist < 4 or core_dist > 20:
                continue

            # Try both spur directions (rotate_left, rotate_right of chain dir)
            for spur_side in ['left', 'right']:
                if spur_side == 'left':
                    spur_dir = cdir.rotate_left()
                else:
                    spur_dir = cdir.rotate_right()

                # Feed conveyor position = splitter output tile
                feed_pos = cpos.add(spur_dir)
                # Sentinel position = one step further in a cardinal direction from feed
                # The feed conveyor should face toward the sentinel
                # Pick a cardinal direction perpendicular to chain that goes away from core
                feed_face = None
                sent_pos = None
                # Try: feed faces the spur direction (approximately)
                # We need feed_face such that feed_pos.add(feed_face) is empty
                for try_dir in [spur_dir, spur_dir.rotate_left(), spur_dir.rotate_right()]:
                    sp = feed_pos.add(try_dir)
                    if (c.is_in_vision(sp) and c.is_tile_empty(sp)
                            and c.get_tile_env(sp) != Environment.WALL):
                        feed_face = try_dir
                        sent_pos = sp
                        break

                if feed_face is None or sent_pos is None:
                    continue

                # Feed tile must be empty
                if not (c.is_in_vision(feed_pos) and c.is_tile_empty(feed_pos)
                        and c.get_tile_env(feed_pos) != Environment.WALL):
                    continue

                # Sentinel facing direction
                sent_face = enemy_dir if enemy_dir else cdir

                # Sentinel must not face the direction from which ammo arrives
                # Ammo arrives from feed_face.opposite() direction
                if sent_face == feed_face.opposite():
                    # Try rotating sentinel face
                    sent_face = sent_face.rotate_left()

                candidates.append((cpos, cdir, spur_dir, feed_pos, feed_face,
                                   sent_pos, sent_face, core_dist))
        except Exception:
            continue

    if not candidates:
        return None

    # Prefer closest to core
    candidates.sort(key=lambda x: x[7])
    best = candidates[0]
    return best[:7]  # Drop core_dist
```

### 4.3 State Machine

```python
def _build_sentry_system(self, c, pos, passable):
    """Multi-round state machine: splitter + feed conveyor + sentinel."""
    if self.sentry_built >= 2:
        return False  # Max 2 sentry systems per builder

    ti = c.get_global_resources()[0]

    # STATE 0: Find candidate
    if self.sentry_state == 0:
        total_cost = (c.get_splitter_cost()[0] + c.get_conveyor_cost()[0]
                      + c.get_sentinel_cost()[0])
        if ti < total_cost + 40:
            return False  # Not enough resources
        result = self._find_sentry_candidate(c, pos)
        if result is None:
            return False
        conv_pos, conv_dir, spur_dir, feed_pos, feed_face, sent_pos, sent_face = result
        self.sentry_plan = (conv_pos, conv_dir, spur_dir, feed_pos,
                            feed_face, sent_pos, sent_face)
        self.sentry_state = 1

    conv_pos, conv_dir, spur_dir, feed_pos, feed_face, sent_pos, sent_face = self.sentry_plan

    # STATE 1: Navigate to conveyor (within action radius)
    if self.sentry_state == 1:
        if pos.distance_squared(conv_pos) > 2:
            self._nav(c, pos, conv_pos, passable)
            return True
        self.sentry_state = 2

    # STATE 2: Destroy the conveyor
    if self.sentry_state == 2:
        if c.can_destroy(conv_pos):
            c.destroy(conv_pos)
            self.sentry_state = 3
            # destroy has no cooldown cost, fall through
        else:
            # Conveyor gone or not ours anymore
            self.sentry_state = 0
            self.sentry_plan = None
            return False

    # STATE 3: Build splitter at same pos, same direction
    if self.sentry_state == 3:
        if c.get_action_cooldown() != 0:
            return True
        if ti < c.get_splitter_cost()[0] + 20:
            return True  # Wait for resources
        if c.can_build_splitter(conv_pos, conv_dir):
            c.build_splitter(conv_pos, conv_dir)
            self.sentry_state = 4
            return True
        else:
            self.sentry_state = 0
            self.sentry_plan = None
            return False

    # STATE 4: Build feed conveyor
    if self.sentry_state == 4:
        if c.get_action_cooldown() != 0:
            return True
        if ti < c.get_conveyor_cost()[0] + 20:
            return True
        # May need to navigate closer to feed_pos
        if pos.distance_squared(feed_pos) > 2:
            self._nav(c, pos, feed_pos, passable)
            return True
        if c.can_build_conveyor(feed_pos, feed_face):
            c.build_conveyor(feed_pos, feed_face)
            self.sentry_state = 5
            return True
        else:
            # Can't build feed -- try without it (Tier A: sentinel directly on splitter output)
            self.sentry_state = 6  # Skip to sentinel
            self.sentry_plan = (conv_pos, conv_dir, spur_dir, feed_pos,
                                feed_face, feed_pos, sent_face)  # Put sentinel at feed_pos
            return True

    # STATE 5: Navigate toward sentinel position
    if self.sentry_state == 5:
        if pos.distance_squared(sent_pos) > 2:
            self._nav(c, pos, sent_pos, passable)
            return True
        self.sentry_state = 6

    # STATE 6: Build sentinel
    if self.sentry_state == 6:
        if c.get_action_cooldown() != 0:
            return True
        if ti < c.get_sentinel_cost()[0] + 20:
            return True
        if pos.distance_squared(sent_pos) > 2:
            self._nav(c, pos, sent_pos, passable)
            return True
        if c.can_build_sentinel(sent_pos, sent_face):
            c.build_sentinel(sent_pos, sent_face)
            self.sentry_state = 7
            self.sentry_built += 1
            return True
        else:
            self.sentry_state = 0
            self.sentry_plan = None
            return False

    # STATE 7: Done
    self.sentry_state = 0
    self.sentry_plan = None
    return False
```

### 4.4 Integration Point

In the `_builder` method, replace the existing `_try_place_sentinel` call:

```python
# BEFORE (in _builder, around line 100-103):
# P0: Opportunistic sentinel near core
if (c.get_action_cooldown() == 0 and c.get_current_round() > 200
        and self.core_pos and pos.distance_squared(self.core_pos) <= 20):
    if self._try_place_sentinel(c, pos):
        return

# AFTER:
# P0: Splitter-fed sentinel system (replaces old sentinel placement)
if (c.get_current_round() >= 100
        and self.core_pos and pos.distance_squared(self.core_pos) <= 25
        and (self.my_id or 0) % 4 == 1):
    if self.sentry_state > 0 or c.get_current_round() % 20 == 0:
        # Active state machine OR periodic check every 20 rounds
        if self._build_sentry_system(c, pos, passable):
            return
```

Remove `_try_place_sentinel` entirely. It is replaced by `_build_sentry_system`.

### 4.5 Fallback: Tier A (No Feed Conveyor)

If the feed conveyor can't be placed (state 4 failure), the state machine already falls back to placing the sentinel directly on the splitter's output tile. This is Tier A.

In Tier A, the sentinel sits at `feed_pos` (the splitter's diagonal output tile). The splitter pushes resources directly to the sentinel. This works if turrets accept from all 7 non-facing neighbors.

---

## 5. Secondary Improvements

### 5.1 Earlier Sentinel Timing (Round 100)

The top teams (especially Kessoku Band) have sentinels by round 100-148. Our current code waits until round 200.

**Change:** In the integration point above, the round check is already `>= 100`. Additionally, the builder cap should allow more builders earlier to support both economy and defense:

```python
# In _core method, change cap logic:
cap = 2 if rnd <= 30 else (3 if rnd <= 80 else (5 if rnd <= 200 else (7 if rnd <= 500 else 9)))
```

This gives us 3 builders by round 80 (up from 2 at round 40), allowing the `id % 4 == 1` builder to exist earlier.

### 5.2 Barrier Walls Around Core

Barriers cost only 3 Ti (+1% scale) and have 30 HP -- excellent HP/cost ratio. Place 4-8 barriers on empty tiles around the core on the enemy-facing side to slow rushes.

**Trigger:** Round >= 60, builder near core (distance_sq <= 8), Ti > 100.

```python
def _build_core_barriers(self, c, pos):
    """Place barriers on empty tiles adjacent to core, facing enemy side."""
    if not self.core_pos or c.get_current_round() < 60:
        return False
    if pos.distance_squared(self.core_pos) > 8:
        return False
    ti = c.get_global_resources()[0]
    if ti < c.get_barrier_cost()[0] + 80:
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
                    and c.get_position(eid).distance_squared(self.core_pos) <= 12):
                barrier_count += 1
        except Exception:
            pass
    if barrier_count >= 6:
        return False  # Enough barriers

    # Place barriers on enemy-facing side of core
    # Core is 3x3, so check tiles 2 steps from core center toward enemy
    for dist in [2, 3]:
        for spread in [Direction.CENTRE, enemy_dir.rotate_left(), enemy_dir.rotate_right()]:
            if spread == Direction.CENTRE:
                d = enemy_dir
            else:
                d = spread
            dx, dy = d.delta()
            bp = Position(self.core_pos.x + dx * dist, self.core_pos.y + dy * dist)
            if (pos.distance_squared(bp) <= 2
                    and c.get_action_cooldown() == 0
                    and c.can_build_barrier(bp)):
                c.build_barrier(bp)
                return True
    return False
```

**Integration point:** Insert between sentinel system and harvester building:

```python
# P0.5: Core barriers (cheap defense)
if (c.get_current_round() >= 60 and self.core_pos
        and pos.distance_squared(self.core_pos) <= 8
        and (self.my_id or 0) % 4 == 0):
    if self._build_core_barriers(c, pos):
        return
```

### 5.3 More Aggressive Attackers on Narrow Maps

Detect narrow maps (width or height <= 25) and send more attackers.

```python
# In _builder method, replace attacker activation:

# BEFORE:
if (c.get_current_round() > 400 and (self.my_id or 0) % 4 == 2
        and self.harvesters_built >= 2):

# AFTER:
is_narrow = c.get_map_width() <= 25 or c.get_map_height() <= 25
attack_round = 300 if is_narrow else 400
attack_slots = ((self.my_id or 0) % 4 == 2) or (is_narrow and (self.my_id or 0) % 4 == 3)
if (c.get_current_round() > attack_round and attack_slots
        and self.harvesters_built >= 1):
```

On narrow maps:
- Attack starts at round 300 (vs 400)
- 2 attackers (id%4 == 2 or 3) instead of 1
- Only need 1 harvester built (vs 2)

---

## 6. Build Order Summary

### Rounds 1-30: Economy Foundation
- 2 builders spawn and seek Ti ore
- Build harvesters + conveyor chains toward core
- No defense spending

### Rounds 30-60: Second Builder Wave
- 3rd builder spawns at round 30 cap change
- Continue harvester + chain building
- Builder id%4==0 starts checking for barrier placement at round 60

### Rounds 60-100: Early Defense
- id%4==0 builder places 4-6 barriers on enemy-facing side of core (18 Ti total)
- Other builders continue economy

### Rounds 100+: Sentinel System
- id%4==1 builder begins sentry state machine
- Finds chain conveyor near core, destroys it
- Builds splitter -> feed conveyor -> sentinel
- Sentinel starts firing with 1/3 of chain's resource flow as ammo
- Up to 2 sentry systems per builder

### Rounds 300-400: Attacker Deployment
- Narrow maps: 2 attackers at round 300
- Wide maps: 1 attacker at round 400
- Attackers walk toward enemy core, damage buildings en route

---

## 7. Cost Analysis

### Sentry System Cost
| Component | Base Cost | Scaling Impact |
|-----------|-----------|---------------|
| Destroy conveyor | 0 Ti | -1% scale |
| Build splitter | 6 Ti | +1% scale |
| Build feed conveyor | 3 Ti | +1% scale |
| Build sentinel | 30 Ti | +20% scale |
| **Total** | **39 Ti** | **+21% scale (net +20%)** |

This is 9 Ti more than the old approach (just sentinel = 30 Ti) but the sentinel actually fires now.

### Economy Impact
- 1/3 of resources from one chain diverted to sentinel ammo
- Sentinel uses 10 ammo per shot, 3-round cooldown
- At 1 stack (10 resources) every ~12 rounds (3x splitter delay), sentinel fires every ~12 rounds
- 18 damage per shot = ~1.5 damage/round sustained

### Barrier Cost
| Barriers | Total Ti | Scale Impact |
|----------|----------|-------------|
| 4 | 12 Ti | +4% |
| 6 | 18 Ti | +6% |

Very cheap for 120-180 HP of defense.

---

## 8. Risk Assessment

### Risk 1: Diagonal resource transfer doesn't work
**Mitigation:** Tier A fallback places sentinel directly on splitter output (no feed conveyor). If even this fails, we try placing the feed conveyor cardinally (requires the chain to have a suitable geometry).

**Testing plan:** Run a test on default_small1 with debug prints in sentinel's `_sentinel` method logging `c.get_ammo_amount()` every round. If ammo > 0 at any point, the system works.

### Risk 2: Chain breaks when conveyor is destroyed
**Mitigation:** The splitter is built in the SAME ROUND the conveyor is destroyed (destroy has no action cooldown, but building does cost cooldown). There's a 1-round gap where no building exists at the chain position. Resources in transit during this round may be lost (1 stack at most).

**Mitigation improvement:** Build the splitter immediately after destroying (same action if cooldown == 0). The `destroy()` method has no cooldown cost, so if action cooldown is already 0, we can destroy AND build in the same turn... but `build_splitter` does cost 1 action cooldown. So destroy + build happens if cooldown was 0 before destroy.

### Risk 3: Sentinel faces wrong direction
**Mitigation:** Sentinel direction validation ensures it doesn't face the direction from which ammo arrives. The candidate selection checks `sent_face != feed_face.opposite()`.

### Risk 4: Not enough chain conveyors near core
**Mitigation:** If no candidate is found, the builder resumes normal behavior. As more conveyors are built during economy expansion, candidates will appear over time. The check runs every 20 rounds.

---

## 9. Test Plan

1. **default_small1 (20x20):** Verify sentry system builds, sentinel gets ammo, sentinel fires at starter bot units
2. **default_medium1 (30x30):** Check economy impact -- are we still winning by similar margins?
3. **corridors:** Test barrier placement near core on narrow map
4. **hourglass:** Test 2-attacker behavior on narrow map
5. **wasteland:** Regression test (currently loses -- should not get worse)
6. **Self-play:** Verify both sides can build sentry systems without crashing
7. **CPU test on cubes (50x50):** Verify state machine doesn't cause timeouts

### Debug Output
Add to sentinel `_sentinel` method:
```python
import sys
print(f"Sentinel {c.get_id()} ammo={c.get_ammo_amount()} round={c.get_current_round()}", file=sys.stderr)
```

---

## 10. Files to Modify

- `bots/buzzing/main.py` -- All changes in single file:
  1. Add `sentry_state`, `sentry_plan`, `sentry_built` to `__init__`
  2. Add `_find_sentry_candidate` method
  3. Add `_build_sentry_system` state machine method
  4. Add `_build_core_barriers` method
  5. Modify `_builder` to integrate new priority system
  6. Modify `_core` to adjust builder cap schedule
  7. Modify attacker activation for narrow map detection
  8. Remove `_try_place_sentinel` method
  9. Add debug logging to `_sentinel`
