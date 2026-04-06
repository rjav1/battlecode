"""Barrier Wall bot ("Fortress") — pure economy + defensive barrier wall.

Strategy:
- 3 builders, d.opposite() conveyor economy
- After round 60, builds 10-15 barriers in a wall facing the enemy
- No sentinels, no attacks — models opponents who invest heavily in defense
"""

from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]


class Player:
    def __init__(self):
        self.core_pos = None
        self.enemy_dir = None
        self.target = None
        self.stuck = 0
        self.last_pos = None
        self.explore_idx = 0
        self.my_id = None
        self.harvesters_built = 0
        self.role = None  # "miner" or "wall_builder"
        self._w = None
        self._h = None
        self._spawn_count = 0
        # Wall builder state
        self.wall_targets = []
        self.wall_idx = 0

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)

    # ------------------------------------------------------------------ Core
    def _core(self, c):
        if self.core_pos is None:
            self.core_pos = c.get_position()
            self._w = c.get_map_width()
            self._h = c.get_map_height()
            self.enemy_dir = self.core_pos.direction_to(
                Position(self._w // 2, self._h // 2))
            if self.enemy_dir == Direction.CENTRE:
                self.enemy_dir = Direction.EAST

        if c.get_action_cooldown() != 0:
            return
        if self._spawn_count >= 3:
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
                self._spawn_count += 1
                return

    # ------------------------------------------------------------------ Builder
    def _builder(self, c):
        pos = c.get_position()
        rnd = c.get_current_round()

        if self.my_id is None:
            self.my_id = c.get_id()
        if self._w is None:
            self._w = c.get_map_width()
            self._h = c.get_map_height()

        if self.core_pos is None:
            for eid in c.get_nearby_entities():
                try:
                    if (c.get_entity_type(eid) == EntityType.CORE
                            and c.get_team(eid) == c.get_team()):
                        self.core_pos = c.get_position(eid)
                        self.enemy_dir = self.core_pos.direction_to(
                            Position(self._w // 2, self._h // 2))
                        if self.enemy_dir == Direction.CENTRE:
                            self.enemy_dir = Direction.EAST
                        break
                except Exception:
                    continue

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

        # Assign role: 3rd builder (id % 3 == 2) becomes wall builder after round 60
        if self.role is None:
            if self.my_id % 3 == 2:
                self.role = "wall_builder"
            else:
                self.role = "miner"

        if self.role == "wall_builder" and rnd >= 60:
            self._build_wall(c, pos, rnd)
        else:
            self._mine(c, pos)

    # ------------------------------------------------------------------ Mining
    def _mine(self, c, pos):
        # Build harvester on adjacent ore
        if c.get_action_cooldown() == 0:
            ore = self._best_adj_ore(c, pos)
            if ore is not None:
                ti = c.get_global_resources()[0]
                if ti >= c.get_harvester_cost()[0] + 15:
                    c.build_harvester(ore)
                    self.harvesters_built += 1
                    self.target = None
                    return

        # Find nearest visible ore
        ore_tiles = []
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
                ore_tiles.append(t)

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
            self._nav(c, pos, self.target)
        else:
            self._explore(c, pos)

    # ------------------------------------------------------------------ Wall
    def _build_wall(self, c, pos, rnd):
        if not self.wall_targets and self.core_pos and self.enemy_dir:
            self._plan_wall()

        if self.wall_idx >= len(self.wall_targets):
            # Wall done, become miner
            self.role = "miner"
            self._mine(c, pos)
            return

        target = self.wall_targets[self.wall_idx]

        # Skip if already occupied
        try:
            if c.is_in_vision(target) and c.get_tile_building_id(target) is not None:
                self.wall_idx += 1
                return
        except Exception:
            pass

        # Walk to target
        if pos.distance_squared(target) > 2:
            self._nav(c, pos, target)
            return

        if c.get_action_cooldown() != 0:
            return

        ti = c.get_global_resources()[0]
        if ti < c.get_barrier_cost()[0] + 20:
            return

        if c.can_build_barrier(target):
            c.build_barrier(target)
            self.wall_idx += 1

    def _plan_wall(self):
        """Plan 10-15 barrier positions in a wall facing the enemy."""
        core = self.core_pos
        ed = self.enemy_dir
        w, h = self._w, self._h

        # Wall perpendicular to enemy direction, 3-4 tiles out
        perp_l = ed.rotate_left().rotate_left()
        perp_r = ed.rotate_right().rotate_right()

        targets = []
        for dist in [3, 4]:
            center = core
            for _ in range(dist):
                center = center.add(ed)

            # Place barriers along perpendicular line
            for side_dist in range(-3, 4):
                if side_dist < 0:
                    p = center
                    for _ in range(-side_dist):
                        p = p.add(perp_l)
                elif side_dist > 0:
                    p = center
                    for _ in range(side_dist):
                        p = p.add(perp_r)
                else:
                    p = center

                if 0 <= p.x < w and 0 <= p.y < h:
                    try:
                        targets.append(p)
                    except Exception:
                        pass

        # Deduplicate and limit
        seen = set()
        unique = []
        for t in targets:
            key = (t.x, t.y)
            if key not in seen:
                seen.add(key)
                unique.append(t)
        self.wall_targets = unique[:15]

    # ------------------------------------------------------------------ Navigation
    def _nav(self, c, pos, target):
        dirs = self._rank(pos, target)
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
                    nxt = pos.add(d)
                    if self._in_bounds(nxt) and c.can_build_road(nxt):
                        c.build_road(nxt)
                        return

    def _explore(self, c, pos):
        idx = ((self.my_id or 0) * 3 + self.explore_idx
               + c.get_current_round() // 150) % len(DIRS)
        d = DIRS[idx]
        dx, dy = d.delta()
        far = Position(pos.x + dx * 15, pos.y + dy * 15)
        self._nav(c, pos, far)

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

    def _in_bounds(self, p):
        return 0 <= p.x < self._w and 0 <= p.y < self._h
