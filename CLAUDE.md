# Cambridge Battlecode 2026 - Project Context

## Objective

Build a competitive Python bot for Cambridge Battlecode, a turn-based strategy game where autonomous mining fleets battle on Titan (Saturn's moon). The goal: **harvest resources, build infrastructure, and destroy the enemy core** - or accumulate more resources by round 2000.

**Game platform:** https://game.battlecode.cam
**Competition site:** https://battlecode.cam
**Full docs:** https://docs.battlecode.cam (sitemap: https://docs.battlecode.cam/sitemap.xml)
**LLM-optimized docs:** https://docs.battlecode.cam/llms.txt
**Discord:** https://discord.gg/xHCygPeAq8

## Team & Competition Status

- **Team:** buzzing bees (ID: d26cf1d1-efc6-45d2-ac75-bfba4ce4aadc)
- **Player:** craig (owner, sole member — team allows up to 4)
- **Bracket:** International (eligible for all-expenses-paid trip to Cambridge for finalists)
- **Current status:** Unrated, rank #486 of 572, 0 matches played, NO submissions yet

### Schedule (key dates)
| Date | Event | Status |
|------|-------|--------|
| Apr 5 | Sprint 3 tournament stream | Done |
| Apr 11 | Sprint 4 submission snapshot | Upcoming |
| Apr 12 | Sprint 4 tournament stream | Upcoming |
| Apr 20 | International qualifier | Upcoming |
| Apr 29 | Submissions freeze + UK qualifier + Novice tournament | Upcoming |
| May 5 | Live finals | Upcoming |

### Rating Ranks
| Rank | Elo |
|------|-----|
| Grandmaster | 2400+ |
| Master | 2200+ |
| Candidate Master | 2000+ |
| Diamond | 1800+ |
| Emerald | 1600+ |
| Gold | 1500+ |
| Silver | 1400+ |
| Bronze | <1400 |

100+ matches required to earn a rank. New teams start at 1500 Elo.

### Platform Tabs
- **Home** — Dashboard with rank, schedule, featured games, rating chart
- **Ladder** — Ranked team leaderboard (filterable: All/Main/Novice, All/UK/Int'l)
- **Matches** — Live matches + match history (filterable by type, team, date)
- **Tournaments** — Sprint tournament brackets and results
- **Team** — Team info, members (1/4), match history
- **Submissions** — Upload .zip with main.py+Player class, manage bot versions
- **Test Runs** — Private `cambc test-run` results (2ms CPU enforced, AWS Graviton3)
- **Visualiser** — Browser replay viewer (zoom, bot-step mode, speed control, indicators)
- **Map Editor** — Create custom .map26 files
- **Settings** — Account settings

## Project Structure

```
battlecode/
  bots/           # Bot directories (each has main.py with a Player class)
    starter/      # Default starter bot
      main.py     # Entry point - Player.run(c: Controller) called each round per unit
  maps/           # .map26 files for local testing (38 maps available)
  cambc/          # SDK - types, CLI, engine bindings
    _types.py     # All enums, constants, Position, Direction, Controller stub
  cambc.toml      # Config: bots_dir, maps_dir, replay path, seed
```

## CLI Commands

```bash
cambc run <bot_a> <bot_b> [map] [--watch] [--seed N] [--replay PATH]  # Local match (no time limit)
cambc watch replay.replay26                                            # Open visualizer
cambc test-run <bot_a> <bot_b> [map]                                   # Remote match (2ms enforced)
cambc submit ./my_bot/                                                 # Upload to ladder
cambc login / cambc logout                                             # Auth
cambc matches / cambc match <id>                                       # Match history
cambc unrated <opponent_team_id>                                       # Challenge (unrated)
cambc map-editor                                                       # Map editor
```

## Bot Architecture

```python
from cambc import Controller, Direction, EntityType, Environment, Position, GameConstants

class Player:
    def __init__(self):
        pass  # Instance vars persist across rounds for THIS unit only

    def run(self, c: Controller) -> None:
        etype = c.get_entity_type()
        if etype == EntityType.CORE:
            # Core logic
        elif etype == EntityType.BUILDER_BOT:
            # Builder logic
        elif etype == EntityType.GUNNER:
            # Turret logic (gunner/sentinel/breach/launcher)
```

**Key constraints:**
- Each unit gets its own `Player` instance - NO shared globals between units
- 2ms CPU per unit per round (5% refillable buffer)
- 1 GB memory limit per bot process
- Only Python standard library (no numpy, no external packages)
- All imports must be at file top level (no runtime file I/O)
- Communication between units: **markers only** (u32 value per tile)
- Max submission: 5 MB zip, 50 MB uncompressed, 500 files

## Game Rules

### Victory Conditions
- **Instant win:** Destroy the enemy core (500 HP)
- **After 2000 rounds**, tiebreakers in order:
  1. Total refined axionite delivered to core
  2. Total titanium delivered to core
  3. Number of living harvesters
  4. Total axionite currently stored
  5. Total titanium currently stored
  6. Coinflip

### Map
- Rectangular grid, 20x20 to 50x50
- (0,0) is northwest corner
- Guaranteed symmetric (reflection or rotation)
- Cell types: Empty, Wall (impassable), Titanium ore, Axionite ore

### Turn Order
Each round, units act in spawn order. After all units act, resources are distributed between buildings.

### Matches
- Each match = 5 games on different maps with unique seeds
- Winner = team that wins majority of games
- Ladder uses Elo rating (start 1500), matchmaking every 10 minutes

---

## Resources

### Titanium (Ti)
- **Starting:** 500 Ti
- **Passive income:** 10 Ti every 4 rounds
- **Sources:** Titanium ore via harvesters -> conveyors -> core
- **Uses:** Building everything, healing (1 Ti), builder attack (2 Ti), gunner rotate (10 Ti)

### Axionite (Ax)
- **Two forms:** Raw (mined from ore) and Refined (produced by foundries)
- **Raw axionite is DESTROYED if fed directly to core or turrets** - must refine first!
- **Refining:** Foundry takes 1 Ti stack + 1 Raw Ax stack -> 1 Refined Ax stack
- **Conversion:** Core can convert refined Ax to Ti at 1 Ax = 4 Ti ratio
- **Uses:** Armoured conveyors (5 Ax), Breach turrets (10 Ax), enhanced turret damage

### Resource Distribution
- Resources move in **stacks of 10** at end of round
- Each stack has a unique ID (queryable)
- **WARNING:** Resources CAN be sent to enemy buildings via misplaced conveyors

### Cost Scaling
`cost = floor(scale * base_cost)` — scale starts at 1.0 and increases additively per entity built:

| Entity | Scale Increase |
|--------|---------------|
| Road | +0.5% |
| Conveyor, Barrier | +1% |
| Harvester | +5% |
| Bridge, Gunner, Breach, Launcher | +10% |
| Builder Bot, Sentinel | +20% |
| Foundry | +100% |

Destroying entities reverses their scaling contribution.

---

## Units & Buildings Reference

### Core
| Stat | Value |
|------|-------|
| HP | 500 |
| Footprint | 3x3 |
| Vision r^2 | 36 |
| Action r^2 | 8 (from centre) |
| Spawning r^2 | 2 (from centre) |

- Spawns 1 builder bot per round on any of its 9 tiles
- `convert(amount)`: refined Ax -> Ti (1:4 ratio)
- Unrefined axionite delivered to core is **destroyed**

### Builder Bot (only mobile unit)
| Stat | Value |
|------|-------|
| HP | 30 |
| Cost | 30 Ti |
| Vision r^2 | 20 |
| Action r^2 | 2 |
| Scale | +20% |

- **Movement:** Adjacent tiles (8 directions), move cooldown +1 per step
- **Can only walk on:** Conveyors (any variant/direction/team), Roads (either team), Allied core
- **Build:** Any building/turret on empty tile within action radius
- **Heal:** 4 HP to all friendly entities on tile, costs 1 Ti + action cooldown
- **Attack:** 2 damage to building on own tile, costs 2 Ti + action cooldown
- **Destroy:** Remove allied building within action radius (no cooldown cost, repeatable)
- **Self-destruct:** No damage dealt
- **Markers:** 1 per round, no cooldown cost

### Transport Buildings

| Building | HP | Cost (Ti, Ax) | Scale | Notes |
|----------|----|----|-------|-------|
| Conveyor | 20 | 3, 0 | +1% | Accepts from 3 non-output sides, outputs in facing direction |
| Splitter | 20 | 6, 0 | +1% | Accepts from behind only, alternates output between 3 forward directions |
| Bridge | 20 | 20, 0 | +10% | Outputs to target within distance^2 <= 9, bypasses direction restrictions |
| Armoured Conveyor | 50 | 5, 5 | +1% | Same as conveyor but 50 HP, requires refined Ax |

### Production Buildings

| Building | HP | Cost (Ti, Ax) | Scale | Notes |
|----------|----|----|-------|-------|
| Harvester | 30 | 20, 0 | +5% | Must be on ore tile, outputs 1 stack every 4 rounds (first output immediate) |
| Foundry | 50 | 40, 0 | +100% | Takes 1 Ti stack + 1 Raw Ax stack -> 1 Refined Ax stack. Accepts/outputs any side |

### Utility Buildings

| Building | HP | Cost (Ti, Ax) | Scale | Notes |
|----------|----|----|-------|-------|
| Road | 5 | 1, 0 | +0.5% | Walkable by builder bots |
| Barrier | 30 | 3, 0 | +1% | Blocks paths, high HP for cost |
| Marker | 1 | free | none | Stores u32 value, only comms mechanism, 1/round, any unit can place |

### Turrets

All turrets except launcher face one of 8 directions. Ammo fed via conveyors from non-facing directions. Turrets only accept resources when completely empty.

**If a builder bot stands on a building, turret attacks on that tile hit ONLY the builder bot.**

| Turret | HP | Cost (Ti, Ax) | Vision r^2 | Damage | Reload | Ammo/Shot | Scale |
|--------|----|----|----|----|----|----|-------|
| Gunner | 40 | 10, 0 | 13 | 10 (30 w/ Ax) | 1 round | 2 | +10% |
| Sentinel | 30 | 30, 0 | 32 | 18 | 3 rounds | 10 | +20% |
| Breach | 60 | 15, 10 | 13 (atk r^2=5) | 40 direct + 20 splash | 1 round | 5 (refined Ax only) | +10% |
| Launcher | 30 | 20, 0 | 26 | N/A (throws bots) | 1 round | none | +10% |

**Gunner:** Fires along forward ray. Walls block but are untargetable. Builder bots and non-marker buildings block and are targetable. Markers are targetable but don't block. Rotation costs 10 Ti + 1 turn cooldown.

**Sentinel:** Hits all tiles within 1 king-move (Chebyshev distance) of the forward line, within vision range. Refined Ax ammo adds +5 to action AND move cooldown of directly-hit units (stun).

**Breach:** 180-degree cone in facing direction. 40 damage to target + 20 splash to 8 surrounding tiles. **Has friendly fire on splash.** Requires refined axionite ammo.

**Launcher:** Picks up adjacent builder bot and throws to target tile within range. No ammo needed. Target must be passable. No facing direction.

---

## Controller API Quick Reference

### Info Queries
```python
c.get_team(id=None) -> Team              # Entity team (or self)
c.get_position(id=None) -> Position       # Entity position (or self)
c.get_id() -> int                         # This unit's ID
c.get_entity_type(id=None) -> EntityType  # Entity type (or self)
c.get_hp(id=None) -> int                  # Current HP
c.get_max_hp(id=None) -> int              # Max HP
c.get_action_cooldown() -> int            # Must be 0 to act
c.get_move_cooldown() -> int              # Must be 0 to move
c.get_direction(id=None) -> Direction     # Facing dir (conveyors/turrets)
c.get_vision_radius_sq(id=None) -> int    # Vision radius squared
```

### Turret-Specific
```python
c.get_ammo_amount() -> int                      # Current ammo held
c.get_ammo_type() -> ResourceType | None        # Loaded ammo type
c.get_gunner_target() -> Position | None         # Closest targetable tile on forward line
c.get_attackable_tiles() -> list[Position]       # Raw attack pattern (ignores ammo/cooldown/occupancy)
c.get_attackable_tiles_from(pos, dir, type) -> list[Position]  # Hypothetical turret pattern
```

### Building/Tile Queries
```python
c.get_bridge_target(id) -> Position              # Bridge output target
c.get_stored_resource(id=None) -> ResourceType | None  # Resource in conveyor/splitter/bridge/foundry
c.get_stored_resource_id(id=None) -> int | None  # Resource stack ID
c.get_tile_env(pos) -> Environment               # EMPTY, WALL, ORE_TITANIUM, ORE_AXIONITE
c.get_tile_building_id(pos) -> int | None        # Building on tile
c.get_tile_builder_bot_id(pos) -> int | None     # Bot on tile
c.is_tile_empty(pos) -> bool                     # No building and not wall
c.is_tile_passable(pos) -> bool                  # Bot could stand here
c.is_in_vision(pos) -> bool                      # Within vision radius
```

### Nearby Queries
```python
c.get_nearby_tiles(dist_sq=None) -> list[Position]    # Tiles within dist (default: vision)
c.get_nearby_entities(dist_sq=None) -> list[int]      # All entity IDs
c.get_nearby_buildings(dist_sq=None) -> list[int]     # Building IDs
c.get_nearby_units(dist_sq=None) -> list[int]         # Unit IDs
```

### Map & Game State
```python
c.get_map_width() -> int
c.get_map_height() -> int
c.get_current_round() -> int                    # Starts at 1
c.get_global_resources() -> tuple[int, int]     # (titanium, axionite)
c.get_scale_percent() -> float                  # Current cost scale (100.0 = base)
c.get_unit_count() -> int                       # Living units including core
c.get_cpu_time_elapsed() -> int                 # Microseconds used this turn
```

### Cost Getters (all return tuple[int, int] = (Ti, Ax))
```python
c.get_conveyor_cost()    c.get_splitter_cost()      c.get_bridge_cost()
c.get_armoured_conveyor_cost()  c.get_harvester_cost()  c.get_road_cost()
c.get_barrier_cost()     c.get_gunner_cost()        c.get_sentinel_cost()
c.get_breach_cost()      c.get_launcher_cost()      c.get_foundry_cost()
c.get_builder_bot_cost()
```

### Actions

```python
# Movement (builder bot only)
c.move(direction) -> None
c.can_move(direction) -> bool

# Building (returns entity ID)
c.build_conveyor(pos, direction)       c.can_build_conveyor(pos, direction)
c.build_splitter(pos, direction)       c.can_build_splitter(pos, direction)
c.build_bridge(pos, target)            c.can_build_bridge(pos, target)
c.build_armoured_conveyor(pos, dir)    c.can_build_armoured_conveyor(pos, dir)
c.build_harvester(pos)                 c.can_build_harvester(pos)
c.build_road(pos)                      c.can_build_road(pos)
c.build_barrier(pos)                   c.can_build_barrier(pos)
c.build_gunner(pos, direction)         c.can_build_gunner(pos, direction)
c.build_sentinel(pos, direction)       c.can_build_sentinel(pos, direction)
c.build_breach(pos, direction)         c.can_build_breach(pos, direction)
c.build_launcher(pos)                  c.can_build_launcher(pos)
c.build_foundry(pos)                   c.can_build_foundry(pos)
c.build(entity_type, pos, extra=None)  c.can_build(entity_type, pos, extra=None)

# Healing & Destruction
c.heal(pos)           c.can_heal(pos)       # 4 HP to all friendlies, 1 Ti
c.destroy(pos)        c.can_destroy(pos)    # Remove allied building, no cooldown
c.self_destruct()                            # Kill self, no damage
c.resign()                                   # Forfeit game

# Markers
c.place_marker(pos, value)   c.can_place_marker(pos)   # 1/round, u32 value
c.get_marker_value(id) -> int

# Combat
c.fire(target)        c.can_fire(target)              # Turret or builder self-tile attack
c.rotate(direction)   c.can_rotate(direction)          # Gunner only, 10 Ti
c.launch(bot_pos, target)  c.can_launch(bot_pos, target)  # Launcher only
c.can_fire_from(pos, dir, turret_type, target) -> bool  # Hypothetical check

# Core
c.convert(amount)                          # Refined Ax -> Ti (1:4)
c.spawn_builder(pos) -> int                # Spawn on core tile
c.can_spawn(pos) -> bool
```

### Debug
```python
c.draw_indicator_line(pos_a, pos_b, r, g, b)  # Debug line in replay
c.draw_indicator_dot(pos, r, g, b)             # Debug dot in replay
print(...)                                      # Captured in replay per-unit
import sys; print(..., file=sys.stderr)         # Real-time console output
```

---

## Helper Types

### Position (NamedTuple)
```python
pos = Position(x, y)
pos.add(Direction.NORTH)           # -> Position offset by direction
pos.distance_squared(other)        # -> int
pos.direction_to(other)            # -> Direction (nearest 45-degree)
```

### Direction (Enum)
```python
# NORTH, NORTHEAST, EAST, SOUTHEAST, SOUTH, SOUTHWEST, WEST, NORTHWEST, CENTRE
d.delta()          # -> (dx, dy)
d.rotate_left()    # 45 degrees CCW
d.rotate_right()   # 45 degrees CW
d.opposite()       # 180 degrees
```

### GameConstants
All numeric constants are available as `GameConstants.MAX_TURNS`, `GameConstants.STACK_SIZE`, etc. See `cambc/_types.py` for the complete list.

---

## Key Strategic Notes

1. **Economy is everything early game** - Harvesters on ore tiles + conveyor chains to core = resource flow
2. **Raw axionite is useless until refined** - Must build foundry (Ti + Raw Ax -> Refined Ax). Foundry has +100% scaling so build sparingly
3. **Builder bots need walkable tiles** - Roads or conveyors must exist before they can move there
4. **50 unit cap includes core** - Max 49 additional units (builders + turrets)
5. **Cost scaling is global and additive** - Every building increases future costs. Destroying enemies reduces THEIR costs
6. **Markers are the ONLY inter-unit communication** - Plan marker encoding schemes carefully
7. **Maps are symmetric** - You can infer enemy core location from your own
8. **Conveyors can feed enemy buildings** - Be careful with placement near borders
9. **Turrets need ammo delivered via conveyors** - Except launchers (no ammo needed)
10. **Breach has friendly fire on splash** - Don't place friendly units adjacent to breach targets
11. **Sentinel stun is very powerful** - +5 action AND move cooldown with refined Ax ammo
12. **Launcher throws builder bots** - Can be used offensively to infiltrate enemy base

## Development Workflow

1. Create bot in `bots/<name>/main.py`
2. Test locally: `cambc run <name> starter --watch`
3. Test with time limits: `cambc test-run <name> starter`
4. Submit: `cambc submit bots/<name>/`
