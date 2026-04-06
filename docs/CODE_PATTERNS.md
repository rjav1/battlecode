# Cambridge Battlecode - Code Patterns & Recipes

Common patterns for bot development. All code uses only Python standard library.

## Bot Skeleton

```python
import random
import sys
from cambc import (
    Controller, Direction, EntityType, Environment,
    Position, GameConstants, ResourceType, Team
)

DIRS = [d for d in Direction if d != Direction.CENTRE]

class Player:
    def __init__(self):
        self.role = None  # assigned on first run

    def run(self, c: Controller) -> None:
        etype = c.get_entity_type()
        if etype == EntityType.CORE:
            self.run_core(c)
        elif etype == EntityType.BUILDER_BOT:
            self.run_builder(c)
        elif etype in (EntityType.GUNNER, EntityType.SENTINEL, EntityType.BREACH):
            self.run_turret(c)

    def run_core(self, c: Controller) -> None:
        pass

    def run_builder(self, c: Controller) -> None:
        pass

    def run_turret(self, c: Controller) -> None:
        pass
```

## Core Patterns

### Spawn builders with budget awareness
```python
def run_core(self, c: Controller) -> None:
    ti, ax = c.get_global_resources()
    bot_cost = c.get_builder_bot_cost()[0]
    unit_count = c.get_unit_count()

    # Spawn if we can afford it and haven't hit cap
    if ti >= bot_cost and unit_count < GameConstants.MAX_TEAM_UNITS:
        for d in random.sample(DIRS, len(DIRS)):
            pos = c.get_position().add(d)
            if c.can_spawn(pos):
                c.spawn_builder(pos)
                break

    # Convert excess refined Ax to Ti
    if ax > 20:
        c.convert(ax - 10)
```

### Adaptive spawn rate
```python
def run_core(self, c: Controller) -> None:
    rnd = c.get_current_round()
    ti, ax = c.get_global_resources()
    unit_count = c.get_unit_count()

    # More builders early, fewer later
    max_builders = 5 if rnd < 50 else 3 if rnd < 200 else 2
    current_builders = unit_count - 1  # subtract core

    if current_builders < max_builders and ti >= c.get_builder_bot_cost()[0]:
        # ... spawn logic
```

## Builder Patterns

### Find and harvest nearest ore
```python
def run_builder(self, c: Controller) -> None:
    pos = c.get_position()

    # Check adjacent tiles for ore to harvest
    for d in DIRS:
        adj = pos.add(d)
        if not c.is_in_vision(adj):
            continue
        env = c.get_tile_env(adj)
        if env in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
            if c.can_build_harvester(adj):
                c.build_harvester(adj)
                return
```

### Build conveyor chain toward target
```python
def build_conveyor_toward(self, c: Controller, pos: Position, target: Position) -> bool:
    """Build a conveyor at pos pointing toward target."""
    direction = pos.direction_to(target)
    if direction == Direction.CENTRE:
        return False
    if c.can_build_conveyor(pos, direction):
        c.build_conveyor(pos, direction)
        return True
    return False
```

### Movement with pathfinding
```python
def move_toward(self, c: Controller, target: Position) -> bool:
    """Try to move toward target, with fallback directions."""
    pos = c.get_position()
    if c.get_move_cooldown() > 0:
        return False

    best_dir = pos.direction_to(target)
    if best_dir == Direction.CENTRE:
        return False

    # Try best direction, then adjacent rotations
    for d in [best_dir, best_dir.rotate_left(), best_dir.rotate_right(),
              best_dir.rotate_left().rotate_left(), best_dir.rotate_right().rotate_right()]:
        if c.can_move(d):
            c.move(d)
            return True

    # Try building a road to make the path walkable
    for d in [best_dir, best_dir.rotate_left(), best_dir.rotate_right()]:
        move_pos = pos.add(d)
        if c.can_build_road(move_pos):
            c.build_road(move_pos)
            if c.can_move(d):
                c.move(d)
                return True

    return False
```

### Random exploration with road building
```python
def explore(self, c: Controller) -> None:
    """Move randomly, building roads as needed."""
    if c.get_move_cooldown() > 0 or c.get_action_cooldown() > 0:
        return
    dirs = random.sample(DIRS, len(DIRS))
    for d in dirs:
        target = c.get_position().add(d)
        if c.can_build_road(target):
            c.build_road(target)
        if c.can_move(d):
            c.move(d)
            return
```

## Scanning Patterns

### Find ore in vision
```python
def find_ore_tiles(c: Controller) -> list[tuple[Position, Environment]]:
    """Return all visible ore tiles sorted by distance."""
    pos = c.get_position()
    ore = []
    for tile in c.get_nearby_tiles():
        env = c.get_tile_env(tile)
        if env in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
            ore.append((tile, env))
    ore.sort(key=lambda t: pos.distance_squared(t[0]))
    return ore
```

### Find unharvested ore (no harvester built yet)
```python
def find_unharvested_ore(c: Controller) -> list[Position]:
    """Return visible ore tiles that don't have a harvester."""
    result = []
    for tile in c.get_nearby_tiles():
        env = c.get_tile_env(tile)
        if env in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
            building_id = c.get_tile_building_id(tile)
            if building_id is None:
                result.append(tile)
    return result
```

### Detect enemies
```python
def find_enemies(c: Controller) -> list[tuple[int, Position, EntityType]]:
    """Return all visible enemy entities."""
    my_team = c.get_team()
    enemies = []
    for eid in c.get_nearby_entities():
        if c.get_team(eid) != my_team:
            enemies.append((eid, c.get_position(eid), c.get_entity_type(eid)))
    return enemies
```

### Infer enemy core location (maps are symmetric)
```python
def estimate_enemy_core(c: Controller) -> Position:
    """Estimate enemy core position using map symmetry."""
    my_pos = c.get_position()  # call from core
    w = c.get_map_width()
    h = c.get_map_height()
    # Reflection symmetry (most common): opposite corner
    return Position(w - 1 - my_pos.x, h - 1 - my_pos.y)
```

## Turret Patterns

### Auto-fire gunner
```python
def run_turret(self, c: Controller) -> None:
    if c.get_entity_type() == EntityType.GUNNER:
        target = c.get_gunner_target()
        if target and c.can_fire(target):
            c.fire(target)
```

### Sentinel with target scanning
```python
def run_sentinel(self, c: Controller) -> None:
    if c.get_action_cooldown() > 0 or c.get_ammo_amount() < GameConstants.SENTINEL_AMMO_COST:
        return
    # Check attackable tiles for enemies
    for tile in c.get_attackable_tiles():
        if c.can_fire(tile):
            c.fire(tile)
            return
```

## Marker Communication Patterns

### Bit-packed marker protocol
```python
# Message types (top 4 bits)
MSG_ENEMY    = 0x1  # Enemy spotted at position
MSG_ORE      = 0x2  # Ore found at position
MSG_CLAIM    = 0x3  # Builder claiming a build site
MSG_HELP     = 0x4  # Builder requesting assistance
MSG_RALLY    = 0x5  # Rally point

def encode_marker(msg_type: int, x: int, y: int, extra: int = 0) -> int:
    """Encode message into u32: [type:4][extra:8][x:10][y:10]"""
    return (msg_type << 28) | (extra << 20) | (x << 10) | y

def decode_marker(val: int) -> tuple[int, int, int, int]:
    """Decode u32 into (type, extra, x, y)."""
    msg_type = (val >> 28) & 0xF
    extra = (val >> 20) & 0xFF
    x = (val >> 10) & 0x3FF
    y = val & 0x3FF
    return msg_type, extra, x, y
```

### Read nearby markers
```python
def read_markers(c: Controller) -> list[tuple[int, int, Position]]:
    """Read all visible friendly markers, return (id, value, position)."""
    my_team = c.get_team()
    markers = []
    for eid in c.get_nearby_entities():
        if c.get_entity_type(eid) == EntityType.MARKER and c.get_team(eid) == my_team:
            val = c.get_marker_value(eid)
            pos = c.get_position(eid)
            markers.append((eid, val, pos))
    return markers
```

## Resource Management

### Check if we can afford something
```python
def can_afford(c: Controller, cost: tuple[int, int]) -> bool:
    ti, ax = c.get_global_resources()
    return ti >= cost[0] and ax >= cost[1]
```

### Budget-aware building
```python
def try_build_with_budget(c: Controller, pos: Position, reserve_ti: int = 50) -> bool:
    """Build a harvester only if we have budget above reserve."""
    ti, ax = c.get_global_resources()
    cost = c.get_harvester_cost()
    if ti - cost[0] >= reserve_ti and c.can_build_harvester(pos):
        c.build_harvester(pos)
        return True
    return False
```

## CPU Time Management

```python
def run(self, c: Controller) -> None:
    # Check remaining time before expensive operations
    elapsed = c.get_cpu_time_elapsed()  # microseconds
    if elapsed > 1500:  # 1.5ms of 2ms used
        return  # bail out, save buffer

    # Do cheap stuff first, expensive stuff last
    self.do_critical_actions(c)

    if c.get_cpu_time_elapsed() < 1000:
        self.do_scanning(c)

    if c.get_cpu_time_elapsed() < 1500:
        self.do_planning(c)
```

## Debugging

```python
# Print to replay (viewable per-unit in visualizer)
print(f"Round {c.get_current_round()}: at {c.get_position()}, ti={c.get_global_resources()[0]}")

# Print to console in real-time
import sys
print(f"DEBUG: {msg}", file=sys.stderr)

# Visual debug indicators (visible in replay)
c.draw_indicator_dot(target_pos, 255, 0, 0)        # Red dot
c.draw_indicator_line(my_pos, target, 0, 255, 0)    # Green line
```

## Anti-Patterns to Avoid

```python
# BAD: No can_* check — wastes turn on GameError
c.build_harvester(pos)  # Might raise GameError!

# GOOD: Always check first
if c.can_build_harvester(pos):
    c.build_harvester(pos)

# BAD: Expensive loop every round
for x in range(c.get_map_width()):
    for y in range(c.get_map_height()):  # O(2500) on 50x50 map
        ...

# GOOD: Use get_nearby_tiles (bounded by vision)
for tile in c.get_nearby_tiles():
    ...

# BAD: Assuming globals are shared
global enemy_positions  # This does NOT work between units!

# GOOD: Use markers for inter-unit communication
c.place_marker(pos, encoded_value)

# BAD: Building without checking scale
c.build_foundry(pos)  # +100% scale!

# GOOD: Check if scale is acceptable
if c.get_scale_percent() < 300:
    c.build_foundry(pos)
```
