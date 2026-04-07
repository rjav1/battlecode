"""ladder_mergeconflict: Models MergeConflict (1521 Elo).
Pure economy, 2-3 builders only, direct chains, minimal conveyor waste.
Key stats: 32 conveyors, 7 harvesters, 2394 Ti/harvester efficiency.
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

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)

    def _core(self, c):
        if c.get_action_cooldown() != 0:
            return
        units = c.get_unit_count() - 1
        rnd = c.get_current_round()
        # MergeConflict: very low builder count — 2 early, 3 after harvesters established
        cap = 2 if rnd <= 100 else 3
        if units >= cap:
            return
        ti = c.get_global_resources()[0]
        cost = c.get_builder_bot_cost()[0]
        if ti < cost + 2:
            return
        pos = c.get_position()
        for d in DIRS:
            sp = pos.add(d)
            if c.can_spawn(sp):
                c.spawn_builder(sp)
                return

    def _bfs_step(self, pos, target, passable):
        if pos == target:
            return None
        q = deque([(pos, None)])
        visited = {pos}
        w_h = 10000
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
        if self.stuck > 10:
            self.target = None
            self.stuck = 0
            self.explore_idx += 1

        passable = set()
        ore_tiles = []
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e != Environment.WALL:
                passable.add(t)
                if e in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
                    if c.get_tile_building_id(t) is None:
                        if e == Environment.ORE_TITANIUM:
                            ore_tiles.append(t)

        rnd = c.get_current_round()

        # Build harvester on adjacent ore
        if c.get_action_cooldown() == 0 and ore_tiles:
            for t in ore_tiles:
                if pos.distance_squared(t) <= 2:
                    ti = c.get_global_resources()[0]
                    hc = c.get_harvester_cost()[0]
                    if ti >= hc + 5:
                        c.build_harvester(t)
                        self.harvesters_built += 1
                        self.target = None
                        return

        # Pick nearest ore target (core-proximate when open)
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

    def _explore(self, c, pos, passable, rnd):
        w, h = c.get_map_width(), c.get_map_height()
        mid = self.my_id or 0
        sector = (mid * 7 + self.explore_idx * 3 + rnd // 50) % len(DIRS)
        d = DIRS[sector]
        dx, dy = d.delta()
        if self.core_pos:
            cx, cy = self.core_pos.x, self.core_pos.y
        else:
            cx, cy = pos.x, pos.y
        reach = max(w, h)
        far = Position(max(0, min(w-1, cx + dx*reach)), max(0, min(h-1, cy + dy*reach)))
        # ti_reserve=50: build conveyors sparingly during explore to stay mobile
        self._nav(c, pos, far, passable, ti_reserve=50)

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

        # Road fallback when stuck
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            rc = c.get_road_cost()[0]
            if ti >= rc + 2:
                for d in dirs:
                    rp = pos.add(d)
                    if c.can_build_road(rp):
                        c.build_road(rp)
                        return

    def _nav_no_build(self, c, pos, target, passable):
        dirs = sorted(DIRS, key=lambda d: pos.add(d).distance_squared(target))
        bfs_dir = self._bfs_step(pos, target, passable)
        if bfs_dir and bfs_dir != dirs[0]:
            dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]
        w, h = c.get_map_width(), c.get_map_height()
        for d in dirs:
            nxt = pos.add(d)
            if not (0 <= nxt.x < w and 0 <= nxt.y < h):
                continue
            if c.get_move_cooldown() == 0 and c.can_move(d):
                c.move(d)
                return
        # Road fallback only
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            rc = c.get_road_cost()[0]
            if ti >= rc + 2:
                for d in dirs:
                    rp = pos.add(d)
                    if c.can_build_road(rp):
                        c.build_road(rp)
                        return
