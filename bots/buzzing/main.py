"""buzzing bees - economy-first bot with d.opposite() conveyor chains.

Key insight: builders walk outward from core, laying conveyors facing BACK
(d.opposite()). When a harvester is built at the end, resources flow back
along the trail to core. Proven to deliver 36,000+ Ti.

Additions over pure eco:
- Separate explore nav (roads) vs ore nav (conveyors) to reduce waste
- Sentinel defense (splitter pattern, after 3 harvesters)
- Attacker role (after round 700, 4+ harvesters)
- Aggressive builder spawning (3 by round 20, up to 8)
"""

from collections import deque
from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]


class Player:
    def __init__(self):
        self.core_pos = None
        self.target = None
        self.last_pos = None
        self.stuck = 0
        self.explore_idx = 0
        self.my_id = None
        self.harvesters_built = 0
        self._enemy_dir = None

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)
        elif t == EntityType.SENTINEL:
            self._sentinel(c)

    # ------------------------------------------------------------------ Core
    def _core(self, c):
        if c.get_action_cooldown() != 0:
            return
        rnd = c.get_current_round()
        units = c.get_unit_count() - 1
        cap = 3 if rnd <= 20 else (5 if rnd <= 100 else (7 if rnd <= 300 else 8))
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

    # -------------------------------------------------------------- Sentinel
    def _sentinel(self, c):
        if c.get_action_cooldown() != 0 or c.get_ammo_amount() < 10:
            return
        for eid in c.get_nearby_entities():
            try:
                if c.get_team(eid) != c.get_team():
                    epos = c.get_position(eid)
                    if c.can_fire(epos):
                        c.fire(epos)
                        return
            except Exception:
                continue

    # --------------------------------------------------------------- Builder
    def _builder(self, c):
        pos = c.get_position()
        rnd = c.get_current_round()

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

        # Stuck detection
        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck = 0
        self.last_pos = pos
        if self.stuck > 15:
            self.target = None
            self.stuck = 0
            self.explore_idx += 1

        # Pre-compute vision
        passable = set()
        ore_tiles = []
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e != Environment.WALL:
                passable.add(t)
                if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
                    ore_tiles.append(t)

        # Sentinel builder role (1 in 5 builders, after round 300)
        if (rnd > 300 and (self.my_id or 0) % 5 == 1
                and self.harvesters_built >= 2
                and self.core_pos
                and pos.distance_squared(self.core_pos) <= 25):
            if self._try_place_sentinel(c, pos):
                return

        # Attacker role (1 in 5 builders, after round 700)
        if (rnd > 700 and (self.my_id or 0) % 5 == 4
                and self.harvesters_built >= 4):
            self._attack(c, pos, passable)
            return

        # P1: Build harvester on adjacent Ti ore
        if c.get_action_cooldown() == 0:
            ore = self._best_adj_ore(c, pos)
            if ore is not None:
                ti = c.get_global_resources()[0]
                if ti >= c.get_harvester_cost()[0] + 10:
                    c.build_harvester(ore)
                    self.harvesters_built += 1
                    self.target = None
                    return

        # P2: Pick nearest visible ore
        if ore_tiles:
            best, bd = None, 10 ** 9
            for t in ore_tiles:
                d = pos.distance_squared(t)
                if d < bd:
                    best, bd = t, d
            self.target = best
        elif self.target is not None and c.is_in_vision(self.target):
            if c.get_tile_building_id(self.target) is not None:
                self.target = None

        # P3: Navigate — always lay conveyors to maintain trail to core
        if self.target is not None:
            self._nav_conveyor(c, pos, self.target, passable)
        else:
            self._nav_explore(c, pos, passable)

    # -------------------------------------------------- Conveyor navigation
    def _nav_conveyor(self, c, pos, target, passable):
        """Navigate toward ore, building conveyors with d.opposite() facing.
        Creates a conveyor trail pointing back toward core."""
        bfs_dir = self._bfs_step(pos, target, passable)
        dirs = self._rank(pos, target)
        if bfs_dir is not None and bfs_dir != dirs[0]:
            dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]

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

        # Bridge fallback
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            bc = c.get_bridge_cost()[0]
            if ti >= bc + 20:
                for d in dirs[:3]:
                    for step in range(2, 4):
                        dx, dy = d.delta()
                        bt = Position(pos.x + dx * step, pos.y + dy * step)
                        if bt.distance_squared(pos) > 9:
                            continue
                        for bd in DIRS:
                            bp = pos.add(bd)
                            if c.can_build_bridge(bp, bt):
                                c.build_bridge(bp, bt)
                                return

        # Road fallback
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            rc = c.get_road_cost()[0]
            if ti >= rc + 5:
                for d in dirs:
                    if c.can_build_road(pos.add(d)):
                        c.build_road(pos.add(d))
                        return

    # ------------------------------------------------------- Explore navigation
    def _nav_explore(self, c, pos, passable):
        """Explore outward, laying conveyors to maintain trail back to core."""
        idx = ((self.my_id or 0) * 3 + self.explore_idx
               + c.get_current_round() // 150) % len(DIRS)
        d = DIRS[idx]
        dx, dy = d.delta()
        target = Position(pos.x + dx * 20, pos.y + dy * 20)
        self._nav_conveyor(c, pos, target, passable)

    # ------------------------------------------------------------ Sentinels
    def _try_place_sentinel(self, c, pos):
        if c.get_action_cooldown() != 0 or not self.core_pos:
            return False
        if pos.distance_squared(self.core_pos) > 25:
            return False
        ti = c.get_global_resources()[0]
        cost = c.get_sentinel_cost()[0]
        if ti < cost + 80:
            return False
        sent_count = 0
        for eid in c.get_nearby_buildings():
            try:
                if (c.get_entity_type(eid) == EntityType.SENTINEL
                        and c.get_team(eid) == c.get_team()):
                    sent_count += 1
            except Exception:
                pass
        if sent_count >= 3:
            return False
        enemy_dir = self._get_enemy_direction(c)
        if not enemy_dir:
            return False
        target_pos = Position(
            self.core_pos.x + enemy_dir.delta()[0] * 5,
            self.core_pos.y + enemy_dir.delta()[1] * 5)
        for d in self._rank(pos, target_pos):
            sp = pos.add(d)
            if c.can_build_sentinel(sp, enemy_dir):
                c.build_sentinel(sp, enemy_dir)
                return True
        return False

    # -------------------------------------------------------------- Attack
    def _attack(self, c, pos, passable):
        if c.get_action_cooldown() == 0:
            bid = c.get_tile_building_id(pos)
            if bid is not None:
                try:
                    if c.get_team(bid) != c.get_team():
                        if c.can_fire(pos):
                            c.fire(pos)
                            return
                except Exception:
                    pass
        enemy_pos = self._get_enemy_core_pos(c)
        if enemy_pos:
            self._nav_conveyor(c, pos, enemy_pos, passable)

    # ------------------------------------------------------------ Helpers
    def _best_adj_ore(self, c, pos):
        best, bd = None, 10 ** 9
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

    def _get_enemy_direction(self, c):
        if self._enemy_dir is not None:
            return self._enemy_dir
        if not self.core_pos:
            return None
        w, h = c.get_map_width(), c.get_map_height()
        cx, cy = self.core_pos.x, self.core_pos.y
        scores = [0, 0, 0]
        mirrors = [
            Position(w - 1 - cx, h - 1 - cy),
            Position(w - 1 - cx, cy),
            Position(cx, h - 1 - cy),
        ]
        for t in c.get_nearby_tiles():
            env = c.get_tile_env(t)
            candidates = [
                Position(w - 1 - t.x, h - 1 - t.y),
                Position(w - 1 - t.x, t.y),
                Position(t.x, h - 1 - t.y),
            ]
            for i, m in enumerate(candidates):
                if c.is_in_vision(m) and c.get_tile_env(m) == env:
                    scores[i] += 1
        best = scores.index(max(scores))
        enemy = mirrors[best]
        d = self.core_pos.direction_to(enemy)
        self._enemy_dir = d if d != Direction.CENTRE else Direction.NORTH
        return self._enemy_dir

    def _get_enemy_core_pos(self, c):
        if not self.core_pos:
            return None
        w, h = c.get_map_width(), c.get_map_height()
        cx, cy = self.core_pos.x, self.core_pos.y
        enemy_dir = self._get_enemy_direction(c)
        if not enemy_dir:
            return None
        mirrors = [
            Position(w - 1 - cx, h - 1 - cy),
            Position(w - 1 - cx, cy),
            Position(cx, h - 1 - cy),
        ]
        for m in mirrors:
            d = Position(cx, cy).direction_to(m)
            if d == enemy_dir:
                return m
        return mirrors[0]
