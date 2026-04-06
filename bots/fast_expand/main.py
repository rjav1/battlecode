"""Fast Expand bot ("Greedy Economy") — aggressive economic expansion.

Strategy:
- 6 builders spawned by round 30 (aggressive expansion)
- d.opposite() conveyors, finds ore far from core
- Models opponents who out-expand us economically
- No military at all
"""

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
        self.harvesters_built = 0
        self._w = None
        self._h = None
        self._spawn_count = 0

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

        if c.get_action_cooldown() != 0:
            return

        rnd = c.get_current_round()
        # Aggressive spawning: 6 builders by round 30
        if self._spawn_count >= 6:
            # After 6 builders, spawn more later if economy allows
            if rnd < 200 or self._spawn_count >= 8:
                return
        ti = c.get_global_resources()[0]
        cost = c.get_builder_bot_cost()[0]
        # Low reserve early to get builders out fast
        reserve = 10 if rnd <= 30 else 40
        if ti < cost + reserve:
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

        # Build harvester on adjacent ore
        if c.get_action_cooldown() == 0:
            ore = self._best_adj_ore(c, pos)
            if ore is not None:
                ti = c.get_global_resources()[0]
                if ti >= c.get_harvester_cost()[0] + 10:
                    c.build_harvester(ore)
                    self.harvesters_built += 1
                    self.target = None
                    return

        # Find ore tiles, prefer ones FAR from core (expand outward)
        ore_tiles = []
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
                ore_tiles.append(t)

        if ore_tiles:
            # Prefer ore far from core (greedy expansion)
            best, bd = None, -1
            for t in ore_tiles:
                d = t.distance_squared(self.core_pos) if self.core_pos else 0
                # But not TOO far — within reasonable reach
                d_from_me = pos.distance_squared(t)
                score = d - d_from_me * 0.5  # balance distance vs reachability
                if score > bd:
                    best, bd = t, score
            self.target = best
        elif self.target and c.is_in_vision(self.target):
            if c.get_tile_building_id(self.target) is not None:
                self.target = None

        if self.target:
            self._nav(c, pos, self.target)
        else:
            self._explore(c, pos)

    # ------------------------------------------------------------------ Navigation
    def _nav(self, c, pos, target):
        dirs = self._rank(pos, target)
        for d in dirs:
            nxt = pos.add(d)
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                cc = c.get_conveyor_cost()[0]
                if ti >= cc + 10:
                    face = d.opposite()
                    if c.can_build_conveyor(nxt, face):
                        c.build_conveyor(nxt, face)
                        return
            if c.get_move_cooldown() == 0 and c.can_move(d):
                c.move(d)
                return

        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            rc = c.get_road_cost()[0]
            if ti >= rc + 5:
                for d in dirs:
                    nxt = pos.add(d)
                    if self._in_bounds(nxt) and c.can_build_road(nxt):
                        c.build_road(nxt)
                        return

    def _explore(self, c, pos):
        # Each builder explores a different direction, rotating over time
        idx = ((self.my_id or 0) * 2 + self.explore_idx
               + c.get_current_round() // 100) % len(DIRS)
        d = DIRS[idx]
        dx, dy = d.delta()
        far = Position(pos.x + dx * 20, pos.y + dy * 20)
        self._nav(c, pos, far)

    def _best_adj_ore(self, c, pos):
        best, bd = None, -1
        for d in Direction:
            p = pos.add(d)
            if c.can_build_harvester(p):
                # Prefer ore FAR from core
                dist = p.distance_squared(self.core_pos) if self.core_pos else 0
                if dist > bd:
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
