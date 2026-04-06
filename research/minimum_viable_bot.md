# Minimum Viable Bot: The Simplest Path to 1800 Elo
## Strategist Analysis | April 4, 2026

---

## 1. EXACT Features Needed for 1800 Elo (Priority Order)

### MUST HAVE (Without these, you stay below 1600)

**P0. Aggressive builder spawning**
- Spawn builders fast: 3 by round 15, up to 6 by round 100, 8+ by round 300
- Always keep a Ti reserve of builder_cost + 20 (not +50 -- spend more aggressively)
- Core spawns every round it can afford to, up to the cap

**P1. Road-based exploration**
- Builders explore outward from core using roads (1 Ti, +0.5% scale)
- Each builder explores a different direction (assign by spawn order: builder 0 = N, builder 1 = E, builder 2 = S, builder 3 = W, etc.)
- Roads are for MOVEMENT ONLY -- they never carry resources

**P2. Harvester placement on titanium ore**
- When a builder finds adjacent Ti ore, build harvester immediately
- Target: 4 harvesters by round 80, 8 by round 200, 12+ by round 500
- Prefer ore clusters (multiple ore tiles near each other) over isolated tiles
- Do NOT build on axionite ore (waste of time at this level)

**P3. Conveyor chain from harvester to core**
- After building a harvester, the SAME builder walks back toward core, laying one conveyor per tile
- Each conveyor faces direction_to(core) from its position
- This creates a direct chain: Harvester -> Conv -> Conv -> Conv -> ... -> Core
- Chain must actually reach the core's 3x3 footprint (any of its 9 tiles)
- Conveyors accept from 3 non-output sides, output in facing direction -- so as long as each step faces toward core, resources flow

**P4. Bridge placement to cross walls**
- When a builder hits a wall while building a conveyor chain or exploring, build a bridge
- Bridge: place on the tile BEFORE the wall, target a tile BEYOND the wall (within dist^2 <= 9)
- The bridge teleports resources over the wall gap
- After the bridge target, resume laying conveyors toward core
- This is THE critical capability that unlocks complex maps like pls_buy_cucats_merch, wasteland, etc.
- Also essential for reaching distant ore clusters separated by wall terrain

**P5. Armed sentinels (defense)**
- After 4+ harvesters are running, build 2-4 sentinels near core facing the enemy direction
- USE SPLITTERS to branch ammo from a resource chain to the sentinel
- Proven pattern from splitter_test: Harvester -> Conv -> Splitter -> (branch Conv -> Sentinel)
- Splitter accepts from behind, alternates output to 3 forward directions
- One of those 3 outputs goes to a conveyor that feeds the sentinel
- Sentinel must NOT face the direction ammo arrives from (ammo enters from non-facing sides)

### NICE TO HAVE (Gets you from 1600 to 1800)

**P6. Symmetry detection for enemy direction**
- Already implemented in buzzing bot. Keep it.
- Used for: sentinel facing, attacker direction, map awareness

**P7. Scale awareness**
- Check `c.get_scale_percent()` before building
- If scale > 300%, stop building non-essential infrastructure (roads, extra conveyors)
- Prioritize harvesters (high ROI) over everything else when scale is high
- Each harvester pays back its 20 Ti cost in ~8 rounds (1 stack of 10 every 4 rounds = 2.5 Ti/round)

**P8. Basic attacker (1 builder raids enemy)**
- After round 500 and 6+ harvesters, send ONE builder toward enemy core
- Walk on roads/conveyors toward enemy (can walk on ENEMY conveyors too)
- Attack enemy buildings on current tile via `c.fire(pos)` (2 damage, 2 Ti)
- Even if it dies, it costs enemy attention/resources to defend

### DO NOT BUILD YET (See section 3)

P9-P12: Launcher drops, marker coordination, map-specific adaptation, axionite economy -- these are for 1800->2200 push, not the MVP.

---

## 2. Minimum Line Count

**Target: 350-400 lines, single file.**

Breakdown:
- Imports + constants: ~10 lines
- Player class + init: ~15 lines
- Core logic (spawning): ~25 lines
- Sentinel logic (auto-fire): ~15 lines
- Builder main dispatch: ~20 lines
- Exploration (road-based): ~30 lines
- Harvester placement: ~20 lines
- Conveyor chain building: ~50 lines (the most complex part)
- Bridge placement: ~40 lines
- Splitter + sentinel building: ~40 lines
- Navigation helpers (walk_to, BFS): ~50 lines
- Symmetry detection: ~30 lines
- Attacker logic: ~25 lines
- Utility functions: ~20 lines

**Total: ~390 lines**

This is achievable. The splitter_test bot is 360 lines and it only does one harvester + one splitter chain. A full economy bot with multiple harvesters, bridges, and sentinels will be ~390 lines if written cleanly.

Key principle: **No abstractions.** No role classes, no state machine framework, no marker protocol encoder. Just clean if/elif chains with clear comments. Abstractions are for teams with 4 developers who need to collaborate. We are one person with an AI. Flat code is fine.

---

## 3. What NOT To Build (Complexity Traps)

### DO NOT BUILD: Marker-based communication
- Markers require a protocol (bit packing, staleness, channel allocation)
- Every builder needs to read/write markers, adding ~50-80 lines of protocol code
- The benefit (preventing duplicate harvesters) can be achieved more simply by having each builder claim a direction sector from core
- At 1800 Elo, duplicate harvesters are a minor inefficiency, not a fatal flaw
- **Alternative:** Assign each builder a sector by ID (builder 0 = north sector, builder 1 = east, etc.)

### DO NOT BUILD: Foundries / Axionite economy
- Foundry costs 40 Ti + 100% scale increase
- Refining axionite requires Ti input + raw Ax input + dedicated conveyor infrastructure
- Nobody in the top 15 uses foundries
- The tiebreaker advantage (TB#1: refined Ax) only matters in extremely close games
- **Alternative:** Win TB#2 (total Ti delivered) by having a better economy

### DO NOT BUILD: Launcher drops
- Launchers cost 20 Ti + 10% scale
- Require a builder to be positioned adjacent to the launcher
- Target tile must be passable (which you cannot always verify beyond vision)
- The thrown builder has 30 HP and no escape route
- High risk, medium reward at this Elo level
- **Save for the 1800->2200 push**

### DO NOT BUILD: Breach turrets
- Cost 15 Ti + 10 refined Ax (requires foundry = +100% scale)
- Has friendly fire on splash
- Nobody in the top 15 uses them
- **Sentinels are strictly better for our needs**

### DO NOT BUILD: Armoured conveyors
- Cost 5 Ti + 5 refined Ax (requires foundry)
- Only advantage is 50 HP vs 20 HP
- Not worth the foundry investment
- **Regular conveyors are fine**

### DO NOT BUILD: Complex state machines
- The splitter_test bot uses numbered steps (step 0-4). This works for a single builder doing a single task.
- For multiple builders with different roles, a step-counter does not scale well.
- BUT: do not over-engineer. A simple role enum (EXPLORE, BUILD_HARVESTER, BUILD_CHAIN, BUILD_SENTINEL, ATTACK) with clear transitions is sufficient.
- Do NOT build a generic finite state machine framework. Just use if/elif.

### DO NOT BUILD: Multi-file architecture
- The MASTER_ROADMAP proposed roles/, systems/, constants.py, utils.py
- This is over-engineering for a 400-line bot
- Single file is fine for competition. It compiles faster, is easier to debug, and has no import issues.

---

## 4. Pseudocode: Ideal Bot Structure

```
CONSTANTS:
    DIRS = all 8 directions (no CENTRE)
    SECTOR_DIRS = [N, NE, E, SE, S, SW, W, NW]  # assigned by builder ID

CLASS Player:
    __init__:
        core_pos = None
        my_id = None
        role = None          # "explore" | "chain" | "sentinel" | "attack"
        target_ore = None    # Position of ore we are walking toward
        chain_from = None    # Position of harvester we are chaining from
        chain_built = 0      # number of chain conveyors built
        harvesters_built = 0
        stuck_counter = 0
        last_pos = None
        enemy_dir = None

    run(c):
        etype = c.get_entity_type()
        if CORE: _run_core(c)
        elif BUILDER_BOT: _run_builder(c)
        elif SENTINEL: _run_sentinel(c)

    # ============ CORE ============
    _run_core(c):
        if action_cooldown != 0: return
        round = c.get_current_round()
        
        # Builder count curve (see section 5)
        builders = unit_count - 1
        cap = builder_cap_for_round(round)
        if builders >= cap: return
        
        ti = global_resources[0]
        cost = builder_bot_cost[0]
        if ti < cost + 20: return
        
        # Spawn on any available core tile
        for d in DIRS:
            sp = core_pos.add(d)
            if can_spawn(sp):
                spawn_builder(sp)
                return

    # ============ SENTINEL ============
    _run_sentinel(c):
        if cooldown != 0 or ammo < 10: return
        for eid in nearby_entities:
            if enemy and can_fire(pos_of(eid)):
                fire(pos_of(eid))
                return

    # ============ BUILDER ============
    _run_builder(c):
        pos = c.get_position()
        
        # One-time init
        if my_id is None:
            my_id = c.get_id()
            detect_core_pos(c)
            assign_role(c)
        
        # Stuck detection
        update_stuck(pos)
        if stuck > 20:
            reset_role_to_explore()
        
        # Scan vision for ore
        scan_for_ore(c)
        
        # Role dispatch
        if role == "explore":    _explore(c, pos)
        elif role == "chain":    _build_chain(c, pos)
        elif role == "sentinel": _build_sentinel_setup(c, pos)
        elif role == "attack":   _attack(c, pos)

    # ---- Role: EXPLORE ----
    _explore(c, pos):
        # Walk outward in assigned sector direction
        # Build roads to move through empty tiles
        # When adjacent to Ti ore:
        #   if can afford harvester:
        #       build_harvester(ore_pos)
        #       harvesters_built += 1
        #       chain_from = ore_pos
        #       role = "chain"
        #   else:
        #       target_ore = ore_pos  # remember, come back when rich
        
        # Navigate in sector direction, building roads as needed
        sector_dir = SECTOR_DIRS[my_id % 8]
        target = Position(pos.x + sector_dir.dx * 30, pos.y + sector_dir.dy * 30)
        nav_with_roads(c, pos, target)

    # ---- Role: CHAIN ----
    _build_chain(c, pos):
        # Walk from harvester toward core, building conveyors
        
        # Check if we have reached the core (dist <= 2 from any core tile)
        if pos.distance_squared(core_pos) <= 8:  # within core's 3x3 footprint
            # Chain complete! Go back to exploring
            role = "explore"
            chain_from = None
            # Maybe transition to sentinel builder if enough harvesters
            if harvesters_built >= 4 and my_id % 4 == 1:
                role = "sentinel"
            return
        
        # Build conveyor on current tile facing toward core
        face_dir = pos.direction_to(core_pos)
        if face_dir == CENTRE: 
            role = "explore"
            return
        
        if action_cooldown == 0:
            # Destroy any existing road to make room for conveyor
            bid = get_tile_building_id(pos)
            if bid is not None and get_entity_type(bid) == ROAD:
                destroy(pos)
                return
            
            # Build conveyor if tile is empty
            if can_build_conveyor(pos, face_dir):
                build_conveyor(pos, face_dir)
                chain_built += 1
        
        # Move toward core
        if move_cooldown == 0:
            next_dir = direction_toward_core(pos)
            
            # Check for wall ahead -> BRIDGE
            next_pos = pos.add(next_dir)
            if is_wall(next_pos):
                try_build_bridge(c, pos, next_dir)
                return
            
            # Move if possible, build road if needed
            if can_move(next_dir):
                move(next_dir)
            else:
                # Try building road on target tile
                if can_build_road(next_pos):
                    build_road(next_pos)
                else:
                    # Try adjacent directions
                    for alt in [next_dir.rotate_left(), next_dir.rotate_right()]:
                        if can_move(alt): move(alt); return
                        alt_pos = pos.add(alt)
                        if can_build_road(alt_pos):
                            build_road(alt_pos)
                            return

    # ---- Bridge Building ----
    try_build_bridge(c, pos, blocked_dir):
        # Find a tile beyond the wall within bridge range (dist^2 <= 9)
        # Try 2 and 3 tiles ahead in the blocked direction
        dx, dy = blocked_dir.delta()
        for dist in [2, 3]:
            target = Position(pos.x + dx*dist, pos.y + dy*dist)
            if target.distance_squared(pos) > 9: continue
            
            # Check target is not a wall (needs to be within vision)
            if not is_in_vision(target): continue
            if get_tile_env(target) == WALL: continue
            
            # Build bridge on an adjacent empty tile
            for bd in DIRS:
                bp = pos.add(bd)
                if can_build_bridge(bp, target):
                    build_bridge(bp, target)
                    return True
        
        # Bridge failed -- try going around the wall
        for alt in [blocked_dir.rotate_left(), blocked_dir.rotate_right(),
                     blocked_dir.rotate_left().rotate_left()]:
            if can_move(alt): move(alt); return True
            alt_pos = pos.add(alt)
            if can_build_road(alt_pos): build_road(alt_pos); return True
        
        return False

    # ---- Role: SENTINEL SETUP ----
    _build_sentinel_setup(c, pos):
        # Find a resource chain near core
        # Build: Splitter on the chain -> branch Conv -> Sentinel
        # Pattern from splitter_test:
        #   Chain: ... -> Conv(facing_dir) -> Splitter(facing_dir) -> ...
        #   Branch: Splitter outputs to perpendicular -> Conv(perp_dir) -> Sentinel
        # Sentinel faces AWAY from ammo entry direction
        
        # This is a one-time setup. After building, role -> "explore"
        ...

    # ---- Role: ATTACK ----
    _attack(c, pos):
        # Walk toward enemy core (from symmetry detection)
        # Attack any enemy building on current tile
        # Simple: just navigate and attack
        ...

    # ============ HELPERS ============
    nav_with_roads(c, pos, target):
        # BFS toward target (bounded to ~200 nodes for CPU)
        # If BFS finds path: move in that direction
        # If next tile needs road: build road, then move next round
        # If wall: try bridge, then try going around

    direction_toward_core(pos):
        # Simple: pos.direction_to(core_pos)
        # Could be smarter with BFS but direction_to works 80% of the time

    assign_role(c):
        # All builders start as "explore"
        role = "explore"
        # But some get redirected based on game state:
        # After round 500 + 6 harvesters: builder ID % 6 == 5 -> "attack"

    builder_cap_for_round(round):
        if round <= 15: return 3
        if round <= 60: return 5
        if round <= 200: return 7
        if round <= 500: return 9
        return 10
```

### Key Design Decisions in This Pseudocode:

1. **Conveyors are built ON THE TILE THE BUILDER IS STANDING ON**, facing toward core. The builder then moves toward core and repeats. This means the chain is built from harvester toward core as the builder walks home.

2. **Bridges are reactive, not planned.** When a builder hits a wall during chain-building, it tries to bridge over. No pre-planned bridge placement.

3. **Sentinels use the proven splitter_test pattern.** Splitter branches resources from an existing chain to a sentinel.

4. **Roles are simple strings, not a framework.** Transitions are explicit: explore -> chain -> explore (loop), or explore -> sentinel (one-time).

5. **No marker protocol.** Builders spread by sector assignment (my_id % 8).

---

## 5. Ideal Builder Count Curve

| Round | Target Builders | Why |
|-------|----------------|-----|
| 1 | 1 | First spawn |
| 5 | 2 | Second spawn |
| 10 | 3 | Third spawn -- now 3 explorers fanning out |
| 15 | 3 | Hold at 3 while they find first ore patches |
| 30 | 4 | Economy starting, can afford 4th builder |
| 60 | 5 | 2-3 harvesters running, income supports more builders |
| 100 | 6 | Should have 4+ harvesters, strong income |
| 200 | 7 | Peak economy phase, all harvesters connected |
| 300 | 8 | Late expansion, reaching distant ore |
| 500+ | 9-10 | Max useful builders (more = diminishing returns + scale bloat) |

### Why This Curve:

- **Builder cost is 30 Ti base, +20% scale each.** At scale 200%, a builder costs 60 Ti. At scale 300%, it costs 90 Ti. Spawning too many builders too early inflates scale before harvesters are producing.
- **Each builder uses ~30 Ti to explore** (roads, failed builds, etc.). 3 builders exploring = 90 Ti spent on exploration. With 500 Ti starting capital, that leaves 410 Ti for the first 3 harvesters (20 Ti each = 60 Ti) and conveyor chains (~3 Ti each, ~5-10 conveyors per chain = 15-30 Ti each).
- **Blue Dragon has 15+ builders** but also 22 harvesters funding them. We need to reach 8+ harvesters before scaling builders past 7.
- **Diminishing returns past 10 builders.** Each builder adds +20% scale. 10 builders = +200% scale just from builders. At that point, new harvesters cost 60+ Ti and take much longer to pay back.

### Core Spawning Logic:

```python
def builder_cap(rnd, harvesters):
    # Base curve
    if rnd <= 15: base = 3
    elif rnd <= 60: base = 5
    elif rnd <= 200: base = 7
    elif rnd <= 500: base = 9
    else: base = 10
    
    # Don't outpace economy: max builders = harvesters + 3
    # (always at least 3 explorers even with 0 harvesters)
    return min(base, harvesters + 3)
```

The `harvesters + 3` cap prevents spawning 7 builders when you only have 2 harvesters. Each builder costs 30+ Ti and produces nothing until it finds ore. More builders than your economy can support = wasted Ti.

**Problem: how does the core know how many harvesters exist?**
Without markers, it cannot. Options:
- (a) Use the round-based curve only (simpler, slightly wasteful)
- (b) Core counts HARVESTER entities in its vision (only sees nearby ones)
- (c) Use a marker on a core tile to report harvester count

Option (a) is fine for the MVP. The round-based curve approximates the economy well enough.

---

## 6. Harvester Targets

| Round | Target Harvesters | Cumulative Ti from Harvesters | Notes |
|-------|-------------------|-------------------------------|-------|
| 30 | 1 | ~75 Ti | First harvester by round 15-30 |
| 60 | 2-3 | ~225 Ti | Builders finding more ore |
| 100 | 4 | ~500 Ti | Economy self-sustaining |
| 150 | 5-6 | ~1,000 Ti | Can afford sentinels now |
| 200 | 6-8 | ~1,800 Ti | Core economy established |
| 300 | 8-10 | ~3,500 Ti | Expanding to distant ore |
| 500 | 10-14 | ~8,000 Ti | Mid-game peak expansion |
| 1000 | 14-18 | ~20,000 Ti | Late game |
| 2000 | 18-22 | ~40,000+ Ti | Blue Dragon territory |

### Math:
- Each harvester produces 1 stack (10 Ti) every 4 rounds
- That is 2.5 Ti/round per harvester
- 10 harvesters = 25 Ti/round from harvesting alone
- Plus 2.5 Ti/round from passive income (10 Ti every 4 rounds)
- Over 2000 rounds with 10 average harvesters: ~50,000 Ti total income
- Blue Dragon collects 30,000+ Ti with 22 harvesters. Our numbers check out.

### How to Get There:
- **Round 1-30:** 3 builders exploring 3 directions. Each should find ore within 10-20 tiles of core on most maps. First harvester by round 15-25.
- **Round 30-100:** Builders alternate between finding ore and building chains. Each harvester takes ~10 rounds to find ore + build + chain back.
- **Round 100-200:** 5-7 builders all looking for ore. Some ore is farther away and requires bridges.
- **Round 200+:** Builders are expanding to distant ore clusters. Chains are longer, bridges more common.

### Critical Insight: Harvester Output vs Chain Cost
- A harvester costs 20 Ti and pays back 10 Ti in 4 rounds, 20 Ti in 8 rounds. ROI = 8 rounds.
- A conveyor chain of length 5 costs 15 Ti. Total harvester + chain = 35 Ti, pays back in 14 rounds.
- A conveyor chain of length 10 costs 30 Ti. Total = 50 Ti, pays back in 20 rounds.
- A bridge costs 20 Ti but saves ~3-5 conveyors (9-15 Ti) by skipping walls. Bridge is worth it when the wall gap would require a 7+ conveyor detour.

**Rule of thumb: Build harvesters aggressively even if the chain is long. A 20-conveyor chain costs 60 Ti + 20 Ti harvester = 80 Ti, pays back in 32 rounds. That is still profitable by round 100 if built early enough.**

---

## 7. Correct Conveyor Chain Topology

### The Answer: **Star Topology (Individual Radial Chains)**

Each harvester gets its own dedicated conveyor chain running directly to the core. The chains radiate outward from the core like spokes on a wheel.

```
        Harv3
          |
          v  (conveyors facing south toward core)
          |
Harv1 -> Conv -> Conv -> CORE <- Conv <- Conv <- Harv2
                           ^
                           |
                         Conv
                           ^
                           |
                         Harv4
```

### Why Star, Not Trunk or Tree:

**Star (individual chains):**
- Simple to build: builder walks from harvester to core, one conveyor per tile
- No contention: each chain carries exactly one harvester's output
- No single point of failure: destroying one chain only affects one harvester
- Easy to extend: new harvester = new chain, no modifications to existing infrastructure
- Predictable throughput: 1 stack per 4 rounds per chain, guaranteed

**Trunk line (all harvesters feed into one main line):**
- Bottleneck: conveyors can only hold one stack at a time. If 5 harvesters feed into one line, 4/5 stacks are blocked until the line clears.
- Single point of failure: destroy any part of the trunk and ALL harvesters are cut off
- Complex to build: requires merging multiple inputs into one line
- NOT how Blue Dragon does it (they have 308 conveyors for 22 harvesters = ~14 conveyors per harvester, suggesting individual chains)

**Tree (merge nearby chains into shared trunks):**
- Better throughput than trunk but still has contention
- Complex merge logic needed
- Not worth the complexity for the MVP

### Star Topology Implementation:

```
For each harvester at position H:
1. Builder stands on H
2. face_dir = H.direction_to(core)
3. Builder moves 1 tile toward core
4. At each tile:
   a. If empty: build conveyor facing toward core, then move toward core
   b. If road: destroy it, build conveyor, move
   c. If wall ahead: build bridge over wall, then continue
   d. If existing conveyor facing toward core: skip (chain already exists from another harvester sharing this segment -- this is OK, conveyors accept from 3 sides)
   e. If within dist 2 of core center: done, chain complete
```

### Handling Chain Convergence:

When two chains from different harvesters converge near the core, their conveyors may occupy adjacent tiles. This is FINE -- conveyors accept resources from 3 non-output sides. If two conveyors both face SOUTH and are side by side, they do not interfere. Each carries its own harvester's output independently.

If two chains need to cross the SAME tile (e.g., both need to place a conveyor at position X but facing different directions), the second builder should:
1. Check if a conveyor already exists at X
2. If it faces roughly toward core (within 45 degrees): skip this tile, the resource will still flow
3. If it faces away from core: route around by going 1 tile sideways, then continuing toward core

### Splitter Integration:

When building a chain near the core, one conveyor should be replaced with a splitter to branch resources to a sentinel:

```
Harvester -> Conv -> Conv -> SPLITTER -> Conv -> Core
                                |
                                v (branch)
                              Conv -> Sentinel
```

The splitter accepts from behind (from the chain direction) and outputs to 3 forward directions: one continues to core, one goes to the sentinel branch, one goes to wherever (can be wasted on a third direction, or feed a second sentinel).

**Splitter placement should be ~3-5 tiles from core.** Close enough that the sentinel defends core, far enough that the harvester chain has room.

---

## Summary: The Build Order

```
Phase 1 (Round 1-30): EXPLORE AND HARVEST
  - Spawn 3 builders
  - Explore in 3 directions using roads
  - Build first harvester on Ti ore
  - Build conveyor chain from first harvester to core
  - Result: 1-2 harvesters, economy starting

Phase 2 (Round 30-100): EXPAND ECONOMY
  - Spawn 2 more builders (total 5)
  - Find more ore, build more harvesters
  - Build chains from each harvester to core
  - Use bridges when walls block chains
  - Result: 4+ harvesters, stable income

Phase 3 (Round 100-300): DEFEND AND SCALE
  - Spawn 2 more builders (total 7)
  - Build splitter on one chain near core
  - Build 2-3 armed sentinels via splitter branches
  - Continue expanding harvesters
  - Result: 6-8 harvesters, armed defense

Phase 4 (Round 300-2000): GRIND AND ATTACK
  - Continue expanding to distant ore
  - Optionally send 1 attacker toward enemy
  - Maintain and repair chains if enemy attacks
  - Result: 10-15+ harvesters, 15,000+ Ti collected
```

---

## Appendix: Conveyor Direction Rules (Critical Reference)

A conveyor has a **facing direction** (the direction it outputs resources).

- **Accepts resources from:** The 3 tiles on non-output sides. If a conveyor faces EAST, it accepts from NORTH, SOUTH, and WEST tiles (and their diagonal variants -- any tile that is not the EAST-side tile).
- **Outputs resources to:** The tile in the facing direction. If facing EAST, outputs to the tile directly east.
- **A conveyor holds 1 stack at a time.** It will not accept a new stack until the current one is output.
- **Resources move at end of round.** Conveyors push their held stack to the output tile's building (if any).

**Common mistake:** Building a conveyor facing NORTH at position (5,5) when the core is at (5,8). This conveyor outputs NORTH (toward y=4) -- AWAY from core. Resources flow backward.

**Correct approach:** Always use `pos.direction_to(core_pos)` to determine conveyor facing direction. This gives the correct 8-directional compass heading from the conveyor to the core.

**Edge case:** If `direction_to` returns CENTRE (conveyor is on core), do not build a conveyor there. The chain is already complete.

---

*Analysis complete. This is the blueprint. Now build it.*
