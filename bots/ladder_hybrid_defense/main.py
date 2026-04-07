"""ladder_hybrid_defense: Models nus robot husk (1542 Elo).
Economy + 3-4 barriers near core + 2 sentinels by round 400.
6-8 builders, d.opposite() conveyors, defensive positioning.
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
        self.my_id = None
        self.explore_idx = 0
        self.harvesters_built = 0
        self.sentinel_built = 0
        self._barriers_placed = False
        self._sentinel_phase = 0  # 0=seek, 1=build_sent, 2=build_ammo

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)
        elif t == EntityType.SENTINEL:
            self._sentinel(c)

    def _core(self, c):
        if c.get_action_cooldown() != 0:
            return
        units = c.get_unit_count() - 1
        rnd = c.get_current_round()
        cap = 4 if rnd <= 30 else (6 if rnd <= 200 else 8)
        if units >= cap:
            return
        ti = c.get_global_resources()[0]
        cost = c.get_builder_bot_cost()[0]
        if ti < cost + 5:
            return
        pos = c.get_position()
        for d in DIRS:
            sp = pos.add(d)
            if c.can_spawn(sp):
                c.spawn_builder(sp)
                return

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

    def _get_enemy_dir(self, c):
        if not self.core_pos:
            return None
        w, h = c.get_map_width(), c.get_map_height()
        ex = w - 1 - self.core_pos.x
        ey = h - 1 - self.core_pos.y
        return self.core_pos.direction_to(Position(ex, ey))

    def _bfs_step(self, pos, target, passable):
        if pos == target:
            return None
        q = deque([(pos, None)])
        visited = {pos}
        while q:
            cur, first = q.popleft()
            for d in DIRS:
                nxt = cur.add(d)
                if nxt == target:
                    return first or d
                if nxt in passable and nxt not in visited:
                    visited.add(nxt)
                    q.append((nxt, first or d))
        return None

    def _builder(self, c):
        pos = c.get_position()
        if self.my_id is None:
            self.my_id = c.get_id()

        if self.core_pos is None:
            for eid in c.get_nearby_entities():
                try:
                    if c.get_entity_type(eid) == EntityType.CORE and c.get_team(eid) == c.get_team():
                        self.core_pos = c.get_position(eid)
                        break
                except Exception:
                    continue

        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck = 0
        self.last_pos = pos
        if self.stuck > 12:
            self.target = None
            self.stuck = 0
            self.explore_idx += 1

        passable = set()
        ore_tiles = []
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e != Environment.WALL:
                passable.add(t)
                if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
                    ore_tiles.append(t)

        rnd = c.get_current_round()
        mid = self.my_id or 0

        # Barrier builder: id%5==0, place 4 barriers near core on enemy-facing side
        if (mid % 5 == 0 and not self._barriers_placed and self.core_pos
                and rnd <= 60 and c.get_action_cooldown() == 0
                and pos.distance_squared(self.core_pos) <= 20):
            enemy_dir = self._get_enemy_dir(c)
            if enemy_dir:
                dx, dy = enemy_dir.delta()
                barrier_count = 0
                for dist in (3, 4):
                    for lateral in (-1, 0, 1):
                        pdx, pdy = enemy_dir.rotate_left().rotate_left().delta()
                        bp = Position(
                            self.core_pos.x + dx * dist + pdx * lateral,
                            self.core_pos.y + dy * dist + pdy * lateral
                        )
                        if pos.distance_squared(bp) <= 2:
                            ti = c.get_global_resources()[0]
                            bc = c.get_barrier_cost()[0]
                            if ti >= bc + 20 and c.can_build_barrier(bp):
                                c.build_barrier(bp)
                                barrier_count += 1
                                if barrier_count >= 1:
                                    return
                if barrier_count == 0:
                    self._barriers_placed = True

        # Sentinel builder: id%5==1, build 2 sentinels at round 200+
        if (mid % 5 == 1 and self.sentinel_built < 2 and rnd >= 200
                and self.harvesters_built >= 2 and self.core_pos
                and c.get_global_resources()[0] >= 60):
            if self._place_sentinel(c, pos, passable):
                return

        # Economy: build harvester on adjacent ore
        if c.get_action_cooldown() == 0:
            for t in ore_tiles:
                if pos.distance_squared(t) <= 2:
                    ti = c.get_global_resources()[0]
                    hc = c.get_harvester_cost()[0]
                    if ti >= hc + 5:
                        c.build_harvester(t)
                        self.harvesters_built += 1
                        self.target = None
                        return

        # Pick ore target
        if ore_tiles:
            best, bd = None, 10**9
            for t in ore_tiles:
                score = pos.distance_squared(t)
                if self.core_pos:
                    score += t.distance_squared(self.core_pos)
                if score < bd:
                    best, bd = t, score
            self.target = best

        if self.target and c.is_in_vision(self.target):
            bid = c.get_tile_building_id(self.target)
            if bid is not None:
                try:
                    if c.get_entity_type(bid) != EntityType.MARKER:
                        self.target = None
                except Exception:
                    self.target = None

        if self.target:
            self._nav(c, pos, self.target, passable)
        else:
            self._explore(c, pos, passable, rnd)

    def _place_sentinel(self, c, pos, passable):
        if not self.core_pos:
            return False
        enemy_dir = self._get_enemy_dir(c)
        if not enemy_dir:
            return False

        # Target: 5 tiles from core in enemy direction, ±2 lateral offset
        dx, dy = enemy_dir.delta()
        pdx, pdy = enemy_dir.rotate_left().rotate_left().delta()
        offset = (self.sentinel_built * 2 - 1) if self.sentinel_built > 0 else 0
        sp = Position(
            self.core_pos.x + dx * 5 + pdx * offset,
            self.core_pos.y + dy * 5 + pdy * offset
        )

        # Walk to sentinel position
        if pos.distance_squared(sp) > 2:
            self._nav(c, pos, sp, passable)
            return True

        # Place sentinel
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            sc = c.get_sentinel_cost()[0]
            if ti >= sc + 10:
                for d in DIRS:
                    tp = pos.add(d)
                    if c.can_build_sentinel(tp, enemy_dir):
                        c.build_sentinel(tp, enemy_dir)
                        self.sentinel_built += 1
                        return True
        return False

    def _nav(self, c, pos, target, passable, ti_reserve=5):
        dirs = sorted(DIRS, key=lambda d: pos.add(d).distance_squared(target))
        bfs_dir = self._bfs_step(pos, target, passable)
        if bfs_dir and bfs_dir != dirs[0]:
            dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]
        w, h = c.get_map_width(), c.get_map_height()
        for d in dirs:
            nxt = pos.add(d)
            if not (0 <= nxt.x < w and 0 <= nxt.y < h):
                continue
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                cc = c.get_conveyor_cost()[0]
                if ti >= cc + ti_reserve and c.can_build_conveyor(nxt, d.opposite()):
                    c.build_conveyor(nxt, d.opposite())
                    return
            if c.get_move_cooldown() == 0 and c.can_move(d):
                c.move(d)
                return
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            rc = c.get_road_cost()[0]
            if ti >= rc + 2:
                for d in dirs:
                    rp = pos.add(d)
                    if c.can_build_road(rp):
                        c.build_road(rp)
                        return

    def _explore(self, c, pos, passable, rnd):
        w, h = c.get_map_width(), c.get_map_height()
        mid = self.my_id or 0
        sector = (mid * 7 + self.explore_idx * 3 + rnd // 50) % len(DIRS)
        d = DIRS[sector]
        dx, dy = d.delta()
        cx = self.core_pos.x if self.core_pos else pos.x
        cy = self.core_pos.y if self.core_pos else pos.y
        reach = min(w, h) // 2
        far = Position(max(0, min(w-1, cx + dx*reach)), max(0, min(h-1, cy + dy*reach)))
        self._nav(c, pos, far, passable, ti_reserve=50)
