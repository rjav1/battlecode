"""Smart Defense bot: 1700 Elo Defender model.

Models a Diamond-tier defensive opponent:
- 4 builders, d.opposite() economy
- 8 barriers around core after round 80
- 2 gunners (NOT sentinels -- cheaper) after round 200, facing enemy
- Gunner auto-fire when ammo >= 2
- Target: 15-25K Ti while being hard to attack
"""

from collections import deque
from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]


class Player:
    def __init__(self):
        self.core_pos = None
        self.target = None
        self.stuck = 0
        self.last_pos = None
        self.explore_idx = 0
        self.my_id = None
        self.barriers_built = 0
        self.gunners_built = 0
        self.enemy_dir = None  # Direction toward enemy core

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)
        elif t == EntityType.GUNNER:
            self._gunner(c)

    def _core(self, c):
        if c.get_action_cooldown() != 0:
            return
        units = c.get_unit_count() - 1
        cap = 4  # Fixed at 4 builders -- economy + defense balance
        if units >= cap:
            return
        ti = c.get_global_resources()[0]
        cost = c.get_builder_bot_cost()[0]
        if ti < cost + 30:
            return
        pos = c.get_position()
        for d in DIRS:
            sp = pos.add(d)
            if c.can_spawn(sp):
                c.spawn_builder(sp)
                return

    def _gunner(self, c):
        """Auto-fire gunner when ammo >= 2."""
        if c.get_action_cooldown() != 0:
            return
        ammo = c.get_ammo_amount()
        if ammo >= 2:
            target = c.get_gunner_target()
            if target is not None and c.can_fire(target):
                c.fire(target)

    def _builder(self, c):
        pos = c.get_position()

        if self.my_id is None:
            self.my_id = c.get_id()

        if self.core_pos is None:
            for eid in c.get_nearby_entities():
                try:
                    if (c.get_entity_type(eid) == EntityType.CORE
                            and c.get_team(eid) == c.get_team()):
                        self.core_pos = c.get_position(eid)
                        break
                except Exception:
                    continue

        rnd = c.get_current_round()

        # Stuck detection
        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck = 0
        self.last_pos = pos
        if self.stuck > 12:
            self.target = None
            self.stuck = 0
            self.explore_idx += 1

        # Scan vision
        ore_tiles = []
        passable = set()
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e != Environment.WALL:
                passable.add(t)
                if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
                    ore_tiles.append(t)

        # Priority 1: Build barriers around core after round 80
        if rnd >= 80 and self.barriers_built < 8 and c.get_action_cooldown() == 0:
            if self.core_pos is not None:
                ti = c.get_global_resources()[0]
                bc = c.get_barrier_cost()[0]
                if ti >= bc + 20:
                    barrier = self._find_barrier_spot(c, pos)
                    if barrier is not None:
                        c.build_barrier(barrier)
                        self.barriers_built += 1
                        return

        # Priority 2: Build 2 gunners after round 200
        if rnd >= 200 and self.gunners_built < 2 and c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            gc = c.get_gunner_cost()[0]
            if ti >= gc + 30:
                gunner_spot = self._find_gunner_spot(c, pos)
                if gunner_spot is not None:
                    spot, face_dir = gunner_spot
                    c.build_gunner(spot, face_dir)
                    self.gunners_built += 1
                    return

        # Priority 3: Build harvester on adjacent Ti ore
        if c.get_action_cooldown() == 0:
            ore = self._best_adj_ore(c, pos)
            if ore is not None:
                ti = c.get_global_resources()[0]
                if ti >= c.get_harvester_cost()[0] + 15:
                    c.build_harvester(ore)
                    self.target = None
                    return

        # Navigate to ore
        if ore_tiles:
            best, bd = None, 10**9
            for t in ore_tiles:
                d = pos.distance_squared(t)
                if d < bd:
                    best, bd = t, d
            self.target = best
        elif self.target and c.is_in_vision(self.target):
            if c.get_tile_building_id(self.target) is not None:
                self.target = None

        if self.target:
            self._nav(c, pos, self.target, passable)
        else:
            self._explore(c, pos, passable)

    def _find_barrier_spot(self, c, builder_pos):
        """Find empty tile adjacent to core to place a barrier."""
        if self.core_pos is None:
            return None
        # Try tiles around the core at distance 2-3
        for radius in range(2, 5):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) != radius and abs(dy) != radius:
                        continue
                    p = Position(self.core_pos.x + dx, self.core_pos.y + dy)
                    if (builder_pos.distance_squared(p) <= 2
                            and c.can_build_barrier(p)):
                        return p
        return None

    def _find_gunner_spot(self, c, builder_pos):
        """Find spot for a gunner facing toward enemy."""
        if self.core_pos is None:
            return None
        # Infer enemy direction: map center is symmetric, enemy is opposite side
        map_cx = c.get_map_width() // 2
        map_cy = c.get_map_height() // 2
        if self.core_pos.x < map_cx:
            face_dir = Direction.EAST
        elif self.core_pos.x > map_cx:
            face_dir = Direction.WEST
        elif self.core_pos.y < map_cy:
            face_dir = Direction.SOUTH
        else:
            face_dir = Direction.NORTH

        # Place gunner in direction of enemy, adjacent to builder
        for d in DIRS:
            nxt = builder_pos.add(d)
            if c.can_build_gunner(nxt, face_dir):
                return (nxt, face_dir)
        return None

    def _nav(self, c, pos, target, passable):
        """Navigate toward target, building conveyors with d.opposite() facing."""
        dirs = self._rank(pos, target)
        bfs_dir = self._bfs_step(pos, target, passable)
        if bfs_dir is not None and bfs_dir != dirs[0]:
            dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]

        for d in dirs:
            nxt = pos.add(d)
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                cc = c.get_conveyor_cost()[0]
                if ti >= cc + 15:
                    face = d.opposite()
                    if c.can_build_conveyor(nxt, face):
                        c.build_conveyor(nxt, face)
                        return
            if c.get_move_cooldown() == 0 and c.can_move(d):
                c.move(d)
                return

        # Road fallback
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            rc = c.get_road_cost()[0]
            if ti >= rc + 10:
                for d in dirs:
                    if c.can_build_road(pos.add(d)):
                        c.build_road(pos.add(d))
                        return

    def _explore(self, c, pos, passable):
        idx = ((self.my_id or 0) * 3 + self.explore_idx
               + c.get_current_round() // 150) % len(DIRS)
        d = DIRS[idx]
        dx, dy = d.delta()
        far = Position(pos.x + dx * 15, pos.y + dy * 15)
        self._nav(c, pos, far, passable)

    def _best_adj_ore(self, c, pos):
        best, bd = None, 10**9
        for d in Direction:
            p = pos.add(d)
            if c.can_build_harvester(p):
                dist = p.distance_squared(self.core_pos) if self.core_pos else 0
                if dist < bd:
                    best, bd = p, dist
        return best

    def _rank(self, pos, target):
        d = pos.direction_to(target)
        if d == Direction.CENTRE:
            return DIRS[:]
        return [d, d.rotate_left(), d.rotate_right(),
                d.rotate_left().rotate_left(), d.rotate_right().rotate_right(),
                d.rotate_left().rotate_left().rotate_left(),
                d.rotate_right().rotate_right().rotate_right(),
                d.opposite()]

    def _bfs_step(self, pos, target, passable):
        queue = deque([(pos, None)])
        visited = {pos}
        best_dir, best_dist = None, pos.distance_squared(target)
        while queue:
            cur, fd = queue.popleft()
            for d in DIRS:
                nxt = cur.add(d)
                if nxt in visited or nxt not in passable:
                    continue
                visited.add(nxt)
                step = fd if fd is not None else d
                dist = nxt.distance_squared(target)
                if dist < best_dist:
                    best_dist = dist
                    best_dir = step
                if nxt == target:
                    return step
                queue.append((nxt, step))
        return best_dir
