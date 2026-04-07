"""Balanced bot ("1600 Elo Average") — typical mid-tier opponent.

Strategy:
- 4 builders
- d.opposite() conveyors + harvesters
- 4 barriers after round 100
- 1 attacker after round 400
- Models a typical mid-tier opponent
"""

from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]


class Player:
    def __init__(self):
        self.core_pos = None
        self.enemy_dir = None
        self.enemy_core_pos = None
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
        self._sym_candidates = None
        self._my_sym_idx = 0
        # Defense state
        self.barrier_targets = []
        self.barrier_idx = 0
        # Attack state
        self._born_round = None

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

        rnd = c.get_current_round()
        units = c.get_unit_count() - 1

        # Spawn 4 builders early, then 1 attacker after round 400
        if rnd <= 400:
            if units >= 4:
                return
        else:
            if units >= 5:
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
        if self._born_round is None:
            self._born_round = rnd
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

        if self._sym_candidates is None and self.core_pos:
            cx, cy = self.core_pos.x, self.core_pos.y
            w, h = self._w, self._h
            self._sym_candidates = [
                Position(w - 1 - cx, h - 1 - cy),
                Position(w - 1 - cx, cy),
                Position(cx, h - 1 - cy),
            ]

        # Detect enemy core
        for eid in c.get_nearby_entities():
            try:
                if (c.get_entity_type(eid) == EntityType.CORE
                        and c.get_team(eid) != c.get_team()):
                    self.enemy_core_pos = c.get_position(eid)
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
            if self.role == "attacker":
                self._my_sym_idx = (self._my_sym_idx + 1) % 3

        # Assign role
        if self.role is None:
            if self._born_round and self._born_round > 350:
                self.role = "attacker"
                self._my_sym_idx = (self.my_id or 0) % 3
            elif self.my_id and self.my_id % 4 == 0:
                self.role = "defender"
            else:
                self.role = "miner"

        if self.role == "attacker":
            self._attack(c, pos, rnd)
        elif self.role == "defender" and rnd >= 100:
            self._defend(c, pos, rnd)
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

    # ------------------------------------------------------------------ Defense
    def _defend(self, c, pos, rnd):
        if not self.barrier_targets and self.core_pos and self.enemy_dir:
            self._plan_barriers()

        if self.barrier_idx >= len(self.barrier_targets):
            # Barriers done, become miner
            self.role = "miner"
            self._mine(c, pos)
            return

        target = self.barrier_targets[self.barrier_idx]

        try:
            if c.is_in_vision(target) and c.get_tile_building_id(target) is not None:
                self.barrier_idx += 1
                return
        except Exception:
            pass

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
            self.barrier_idx += 1

    def _plan_barriers(self):
        core = self.core_pos
        ed = self.enemy_dir
        w, h = self._w, self._h
        perp_l = ed.rotate_left().rotate_left()
        perp_r = ed.rotate_right().rotate_right()

        targets = []
        center = core
        for _ in range(3):
            center = center.add(ed)

        for offset in range(-1, 2):
            if offset < 0:
                p = center
                for _ in range(-offset):
                    p = p.add(perp_l)
            elif offset > 0:
                p = center
                for _ in range(offset):
                    p = p.add(perp_r)
            else:
                p = center
            if 0 <= p.x < w and 0 <= p.y < h:
                targets.append(p)

        # Add one more row
        center2 = core
        for _ in range(4):
            center2 = center2.add(ed)
        if 0 <= center2.x < w and 0 <= center2.y < h:
            targets.append(center2)

        self.barrier_targets = targets[:4]

    # ------------------------------------------------------------------ Attack
    def _attack(self, c, pos, rnd):
        # If on enemy building, attack it
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            if ti >= 2:
                bid = c.get_tile_building_id(pos)
                if bid is not None:
                    try:
                        if c.get_team(bid) != c.get_team():
                            if c.can_fire(pos):
                                c.fire(pos)
                                return
                    except Exception:
                        pass

        # Walk toward enemy core
        rush_target = self.enemy_core_pos
        if rush_target is None and self._sym_candidates:
            rush_target = self._sym_candidates[self._my_sym_idx]

        if rush_target:
            self.target = rush_target
            self._walk_to(c, pos, rush_target)
        else:
            self._explore(c, pos)

    def _walk_to(self, c, pos, target):
        if c.get_move_cooldown() != 0:
            return
        d = pos.direction_to(target)
        if d == Direction.CENTRE:
            return
        attempts = [d, d.rotate_left(), d.rotate_right(),
                    d.rotate_left().rotate_left(), d.rotate_right().rotate_right()]
        for try_d in attempts:
            if c.can_move(try_d):
                c.move(try_d)
                return
            nxt = pos.add(try_d)
            if c.get_action_cooldown() == 0 and self._in_bounds(nxt):
                ti = c.get_global_resources()[0]
                rc = c.get_road_cost()[0]
                if ti >= rc + 30:
                    if c.can_build_road(nxt):
                        c.build_road(nxt)
                        if c.can_move(try_d):
                            c.move(try_d)
                        return

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
        rnd = c.get_current_round()
        idx = ((self.my_id or 0) * 7 + rnd) % len(DIRS)
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
