# Cambridge Battlecode - Complete Game Reference

This file contains every numeric constant, stat table, and mechanical detail from the official documentation. Use this as a quick-lookup reference.

## Game Constants (from `cambc/_types.py`)

```
MAX_TURNS                        = 2000
STACK_SIZE                       = 10     (resources move in stacks of 10)
STARTING_TITANIUM                = 500
STARTING_AXIONITE                = 0
MAX_TEAM_UNITS                   = 50     (including core)
PASSIVE_TITANIUM_AMOUNT          = 10
PASSIVE_TITANIUM_INTERVAL        = 4      (10 Ti every 4 rounds)
AXIONITE_CONVERSION_TITANIUM_RATE = 4     (1 refined Ax -> 4 Ti)
```

## Complete Entity Stats

### Units

| Entity | HP | Cost (Ti, Ax) | Vision r^2 | Action r^2 | Scale% | Special |
|--------|----|----|----|----|-----|----|
| Core | 500 | - | 36 | 8 (centre) | - | 3x3 footprint, spawns builders |
| Builder Bot | 30 | 30, 0 | 20 | 2 | +20% | Only mobile unit |
| Gunner | 40 | 10, 0 | 13 | 2 | +10% | Directional, rotatable |
| Sentinel | 30 | 30, 0 | 32 | 2 | +20% | Directional, stun capability |
| Breach | 60 | 15, 10 | 13 | 2 (atk r^2=5) | +10% | Directional, splash + friendly fire |
| Launcher | 30 | 20, 0 | 26 | 2 | +10% | No direction, throws bots |

### Buildings

| Entity | HP | Cost (Ti, Ax) | Scale% | Walkable | Notes |
|--------|----|----|-----|---|----|
| Conveyor | 20 | 3, 0 | +1% | Yes | Directional, accepts from 3 non-output sides |
| Splitter | 20 | 6, 0 | +1% | Yes* | Directional, accepts from behind, alternates 3 outputs |
| Bridge | 20 | 20, 0 | +10% | No | Target within dist^2 <= 9, bypasses direction rules |
| Armoured Conveyor | 50 | 5, 5 | +1% | Yes | Same as conveyor, 50 HP |
| Harvester | 30 | 20, 0 | +5% | No | Must be on ore, outputs every 4 rounds |
| Foundry | 50 | 40, 0 | +100% | No | Ti + Raw Ax -> Refined Ax, any-side I/O |
| Road | 5 | 1, 0 | +0.5% | Yes | Cheapest walkable tile |
| Barrier | 30 | 3, 0 | +1% | No | Defensive wall |
| Marker | 1 | free | 0% | N/A | u32 value, comms only |

*Splitter walkability: conveyors of any variant are walkable

## Combat Stats

### Gunner
```
Damage:             10 base, 30 with refined axionite ammo
Reload:             1 round
Ammo per shot:      2
Attack pattern:     Forward ray up to vision range (r^2 = 13)
Rotation cost:      10 Ti + 1 turn action cooldown
Line-of-sight:      Walls block (untargetable). Builder bots & buildings block (targetable).
                    Markers: targetable but NON-blocking. Empty tiles: skipped.
```

### Sentinel
```
Damage:             18
Reload:             3 rounds
Ammo per shot:      10
Attack pattern:     All tiles within 1 Chebyshev distance of forward line, within vision (r^2 = 32)
Stun (refined Ax):  +5 to action cooldown AND move cooldown of directly-hit units
```

### Breach
```
Damage:             40 direct + 20 splash (8 surrounding tiles)
Reload:             1 round
Ammo per shot:      5 (REFINED AXIONITE ONLY)
Attack pattern:     180-degree cone in facing direction, within r^2 = 5
Friendly fire:      YES on splash damage (not on self)
```

### Launcher
```
Damage:             N/A (throws builder bots)
Reload:             1 round
Ammo:               None required
Range:              Vision r^2 = 26
Target:             Must be a passable tile
```

### Builder Bot Combat
```
Attack:             2 damage to building on OWN tile only, costs 2 Ti
Heal:               4 HP to all friendlies on target tile, costs 1 Ti
Self-destruct:      0 damage dealt
```

## Resource Flow

### Titanium
```
Starting:     500
Passive:      +10 every 4 rounds
Sources:      Ti ore -> Harvester -> Conveyor chain -> Core
              Refined Ax -> Core conversion (1 Ax = 4 Ti)
```

### Axionite
```
Starting:     0
Sources:      Ax ore -> Harvester -> Raw Axionite
Refining:     Foundry: 1 Ti stack + 1 Raw Ax stack -> 1 Refined Ax stack
WARNING:      Raw Ax fed to core or turrets = DESTROYED (wasted)
```

### Harvester Output
```
Frequency:          Every 4 rounds (first output on build round)
Output size:        1 stack (10 resources)
Direction priority: Least-recently-used output direction
Placement:          MUST be on ore tile (ORE_TITANIUM or ORE_AXIONITE)
```

### Foundry Process
```
Step 1: Titanium stack enters via conveyor -> stored
Step 2: Raw axionite stack enters -> reaction begins
Step 3: Refined axionite stack outputs to adjacent accepting building
I/O:    Accepts input and produces output from ANY side
```

## Cost Scaling Formula

```
scaled_cost = floor(scale_percent / 100 * base_cost)
```

Scale starts at 100% (1.0x). Each entity built adds to scale. Destroying an entity reverses its contribution.

### Scale Contributions (sorted by impact)
```
Foundry:                 +100%
Builder Bot, Sentinel:   +20%
Bridge, Gunner, Breach, Launcher, Harvester*: +10% (*Harvester is +5%)
Conveyor, Barrier:       +1%
Road:                    +0.5%
```

Correction: Harvester is +5%, not +10%.

## Movement Rules

Builder bots can walk on:
- Conveyors (any variant, any direction, either team)
- Roads (either team)
- Allied core tiles

Builder bots CANNOT walk on:
- Empty tiles
- Walls
- Barriers
- Harvesters
- Foundries
- Bridges
- Enemy core

Move cooldown: +1 per step, decreases by 1 per round end.

## Radii Reference (squared distances)

```
Core vision:           36    (6 tiles)
Core action:            8    (~2.8 tiles, from centre)
Core spawning:          2    (~1.4 tiles, from centre)
Builder vision:        20    (~4.5 tiles)
Gunner vision/attack:  13    (~3.6 tiles)
Sentinel vision/attack: 32   (~5.7 tiles)
Breach vision:         13    (~3.6 tiles)
Breach attack:          5    (~2.2 tiles)
Launcher vision/throw: 26    (~5.1 tiles)
Bridge target:          9    (3 tiles)
Standard action:        2    (~1.4 tiles - adjacent including diagonal)
```

## Tiebreaker Order (after 2000 rounds)

1. Total refined axionite delivered to core
2. Total titanium delivered to core
3. Number of living harvesters
4. Total axionite currently stored
5. Total titanium currently stored
6. Random coinflip

Note: `c.convert(...)` moves Ax from "Ax collected" stat to "Ti collected" stat.

## Enums

```python
Team:         A, B
EntityType:   BUILDER_BOT, CORE, GUNNER, SENTINEL, BREACH, LAUNCHER,
              CONVEYOR, SPLITTER, ARMOURED_CONVEYOR, BRIDGE,
              HARVESTER, FOUNDRY, ROAD, BARRIER, MARKER
ResourceType: TITANIUM, RAW_AXIONITE, REFINED_AXIONITE
Environment:  EMPTY, WALL, ORE_TITANIUM, ORE_AXIONITE
Direction:    NORTH, NORTHEAST, EAST, SOUTHEAST, SOUTH, SOUTHWEST,
              WEST, NORTHWEST, CENTRE
```
