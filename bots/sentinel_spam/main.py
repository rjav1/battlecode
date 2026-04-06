"""Sentinel Spam bot ("Gunline") — economy + heavy turret defense.

Strategy:
- 4 builders, basic d.opposite() conveyor economy
- After round 150, builds 4-6 sentinels (unarmed, as obstacles + vision)
- Models opponents with heavy turret defense
- Tests if our attacker can get past sentinels
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
        self.role = None
        self._w = None
        self._h = None
        self._spawn_count = 0
        # Sentinel builder state
        self.sentinel_targets = []
        self.sentinel_idx = 0

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
        if self._spawn_count >= 4:
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

        # Assign role: builder 0 becomes sentinel_builder after round 150
        if self.role is None:
            if self.my_id % 4 == 0:
                self.role = "sentinel_builder"
            else:
                self.role = "miner"

        if self.role == "sentinel_builder" and rnd >= 150:
            self._build_sentinels(c, pos, rnd)
        else:
            self._mine(c, pos)

    # ------------------------------------------------------------------ Mining
    def _mine(self, c, pos):
        if c.get_action_cooldown() == 0:
            ore = self._best_adj_ore(c, pos)
            if ore is not None:
                ti = c.get_global_resources()[0]
                if ti >= c.get_harvester_cost()[0] + 15:
                    c.build_harvester(ore)
                    self.harvesters_built += 1
                    self.target = None
                    return

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

    # ------------------------------------------------------------------ Sentinels
    def _build_sentinels(self, c, pos, rnd):
        if not self.sentinel_targets and self.core_pos and self.enemy_dir:
            self._plan_sentinels()

        if self.sentinel_idx >= len(self.sentinel_targets):
            # All sentinels placed, become miner
            self.role = "miner"
            self._mine(c, pos)
            return

        target_pos, target_dir = self.sentinel_targets[self.sentinel_idx]

        # Skip if occupied
        try:
            if c.is_in_vision(target_pos) and c.get_tile_building_id(target_pos) is not None:
                self.sentinel_idx += 1
                return
        except Exception:
            pass

        # Walk to target
        if pos.distance_squared(target_pos) > 2:
            self._nav(c, pos, target_pos)
            return

        if c.get_action_cooldown() != 0:
            return

        ti = c.get_global_resources()[0]
        if ti < c.get_sentinel_cost()[0] + 30:
            return

        if c.can_build_sentinel(target_pos, target_dir):
            c.build_sentinel(target_pos, target_dir)
            self.sentinel_idx += 1

    def _plan_sentinels(self):
        """Plan 4-6 sentinel positions in an arc facing the enemy."""
        core = self.core_pos
        ed = self.enemy_dir
        w, h = self._w, self._h

        perp_l = ed.rotate_left().rotate_left()
        perp_r = ed.rotate_right().rotate_right()

        targets = []
        # Place sentinels at distance 4-5 from core, spread along the front
        for dist in [4, 5]:
            center = core
            for _ in range(dist):
                center = center.add(ed)

            for offset, side_dir in [
                (0, None),
                (2, perp_l),
                (2, perp_r),
            ]:
                if offset == 0:
                    p = center
                else:
                    p = center
                    for _ in range(offset):
                        p = p.add(side_dir)

                if 0 <= p.x < w and 0 <= p.y < h:
                    targets.append((p, ed))

        # Deduplicate
        seen = set()
        unique = []
        for pos, facing in targets:
            key = (pos.x, pos.y)
            if key not in seen:
                seen.add(key)
                unique.append((pos, facing))
        self.sentinel_targets = unique[:6]

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
