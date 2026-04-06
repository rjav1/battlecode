# Cambridge Battlecode - Strategy Guide

## Game Phases

### Early Game (Rounds 1-100)
**Priority:** Economy setup. Every round without harvesters is wasted income.

- Spawn 3-5 builder bots immediately
- Send builders to nearest ore tiles (use `c.get_tile_env()` to scan)
- Build harvesters on ore, then conveyor chains back to core
- Prioritize titanium ore first (Ti funds everything)
- Build roads as pathways for builder movement
- Keep builder count low early - each costs 30 Ti AND adds +20% scale

### Mid Game (Rounds 100-800)
**Priority:** Expand economy, begin defensive infrastructure, scout enemy.

- Establish multiple harvester sites
- Build axionite foundry if Ax ore is accessible (but remember +100% scale!)
- Start placing turrets at key chokepoints
- Use markers to coordinate builder activities
- Consider conveyor networks for turret ammo supply
- Monitor `c.get_scale_percent()` — if costs are rising fast, slow down building

### Late Game (Rounds 800-2000)
**Priority:** Push enemy core or maximize tiebreaker stats.

- Refined axionite delivered to core is tiebreaker #1
- Titanium delivered to core is tiebreaker #2
- Living harvesters count for tiebreaker #3
- Consider offensive pushes with launcher + builder bot combos
- Breach turrets deal massive damage but need refined Ax ammo supply chain

## Economy Fundamentals

### Conveyor Chain Design
```
[Harvester on Ore] -> [Conveyor →] -> [Conveyor →] -> ... -> [Core]
```

- Conveyors accept from 3 non-output sides, output in facing direction
- Resources move 1 tile per round (at round end), in stacks of 10
- A harvester outputs every 4 rounds — one conveyor chain per harvester is sufficient
- Multiple harvesters can feed into a single conveyor trunk line

### Splitter Usage
```
                          [Conveyor ↑] (to turret)
                              ↑
[Harvester] -> [Conveyor →] -> [Splitter →] -> [Conveyor →] (to core)
                              ↓
                          [Conveyor ↓] (to another turret)
```

- Splitters alternate output across 3 forward directions
- Accept input from behind ONLY
- Useful for distributing resources to multiple turrets

### Bridge Usage
- Bridges teleport resources up to distance^2 = 9 (3 tiles)
- Use to jump over walls, obstacles, or enemy territory
- Expensive (20 Ti, +10% scale) — use sparingly
- Can feed any building from any direction (bypasses normal conveyor rules)

### Foundry Pipeline
```
[Ti Harvester] -> [Conveyor chain] -> [Foundry] -> [Conveyor chain] -> [Core or Turret]
                                         ↑
[Ax Harvester] -> [Conveyor chain] ------+
```

- Foundry needs BOTH Ti and Raw Ax inputs
- Ti enters first (stored), then Raw Ax triggers conversion
- Output: Refined Ax stack
- +100% scaling — building 1 foundry doubles all future costs!
- Only build if you have strong Ax ore access AND need refined Ax

## Defensive Strategies

### Turret Placement

**Gunner (cheap, versatile):**
- 10 Ti, fires every round, 10 damage (30 with refined Ax)
- Best for forward defense — shoots in a line
- Place facing likely enemy approach directions
- Remember: walls block line of sight
- Ammo: 2 per shot (Ti or raw Ax work, but refined Ax triples damage)

**Sentinel (area denial):**
- 30 Ti, fires every 3 rounds, 18 damage
- Covers wide swath (1 Chebyshev distance from forward line)
- Refined Ax ammo adds +5 stun to action AND move cooldown — devastating
- Best behind chokepoints where enemies funnel
- High ammo cost (10 per shot)

**Breach (siege weapon):**
- 15 Ti + 10 refined Ax to build
- 40 direct + 20 splash damage, 180-degree cone
- REQUIRES refined Ax ammo (5 per shot)
- Has FRIENDLY FIRE on splash — leave space around targets
- Short range (r^2 = 5) — place close to expected combat zone

**Launcher (utility):**
- 20 Ti, throws builder bots up to r^2 = 26
- No ammo needed
- Offensive: throw builders into enemy base to destroy buildings
- Defensive: reposition builders quickly

### Barrier Walls
- 30 HP for only 3 Ti — excellent HP/cost ratio
- Use to funnel enemies into turret kill zones
- Block enemy conveyor paths
- Protect key infrastructure (harvesters, foundries)

## Offensive Strategies

### Builder Bot Raids
- Build roads or conveyors toward enemy base
- Send builder bots to `c.destroy()` enemy buildings (no cooldown cost!)
- Builders can destroy ANY allied building repeatedly — enemy buildings require `c.fire()` (2 Ti, 2 damage, own tile only)
- Target: enemy conveyors (cut supply lines) > harvesters (cut income) > turrets (remove defense)

### Launcher Assault
- Build launcher near enemy territory
- Throw builder bots over walls/defenses directly into enemy base
- Thrown builders can immediately start destroying enemy buildings next turn
- Low cost, high disruption

### Core Rush
- Multiple builder bots converging on enemy core
- Each can fire on buildings (2 damage/round for 2 Ti) — but can only hit building ON their tile
- Core has 500 HP — need sustained assault
- Breach turrets near enemy core are more effective (40+20 damage)

## Communication (Markers)

Markers are the ONLY way units communicate. Each stores a u32 (0 to 4,294,967,295).

### Encoding Schemes

**Simple flag system:**
```python
# Encode: type in high bits, data in low bits
ENEMY_SPOTTED = 1 << 24
ORE_FOUND     = 2 << 24
BUILD_HERE    = 3 << 24

# Place marker with enemy position encoded
marker_val = ENEMY_SPOTTED | (enemy_x << 12) | enemy_y
c.place_marker(pos, marker_val)

# Read marker
val = c.get_marker_value(marker_id)
msg_type = val >> 24
if msg_type == 1:  # ENEMY_SPOTTED
    ex = (val >> 12) & 0xFFF
    ey = val & 0xFFF
```

**Round-stamped markers:**
```python
# Encode round number to let readers judge freshness
marker_val = (c.get_current_round() << 16) | data
```

### Marker Tactics
- Place markers at enemy positions you discover
- Use markers to claim build sites (prevent duplicate work)
- Markers have 1 HP — enemies can destroy them by building over
- Gunners can target markers (but markers don't block gunner line of sight)
- Any unit type can place markers (core, builders, turrets)

## Common Pitfalls

1. **Building too many foundries** — +100% scale EACH. Usually 1 is enough
2. **Forgetting to refine axionite** — Raw Ax fed to core/turrets is destroyed
3. **Conveyors feeding enemy** — Resources CAN flow to enemy buildings
4. **No walkable paths** — Builders can't move onto empty tiles, need roads/conveyors
5. **Exceeding unit cap** — 50 total including core. Check `c.get_unit_count()`
6. **Ignoring cost scaling** — Track `c.get_scale_percent()`, each building increases costs
7. **Breach friendly fire** — 20 splash damage hits YOUR units/buildings too
8. **Not using `can_*` checks** — Always check before acting to avoid wasting turns on GameError
9. **CPU timeout** — 2ms is tight. Avoid expensive pathfinding on large maps
10. **Shared state assumption** — Each Player instance is isolated. No globals between units
