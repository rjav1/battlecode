"""Debug bot: prints harvester and conveyor activity to stderr."""

import sys
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
        self.harvesters_built = 0
        self.conveyors_built = 0

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)

    def _core(self, c):
        if c.get_action_cooldown() != 0:
            return
        rnd = c.get_current_round()
        if rnd % 100 == 1:
            ti, ax = c.get_global_resources()
            print(f"[CORE R{rnd}] Ti={ti} Ax={ax} units={c.get_unit_count()} scale={c.get_scale_percent():.1f}%", file=sys.stderr)
        units = c.get_unit_count() - 1
        cap = 3 if rnd <= 50 else 5
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
                print(f"[CORE R{rnd}] Spawned builder at {sp}", file=sys.stderr)
                return

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
            if rnd <= 200:
                print(f"[B{self.my_id} R{rnd}] STUCK at {pos}, resetting target", file=sys.stderr)
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

        # Build harvester on adjacent ore
        if c.get_action_cooldown() == 0:
            for d in Direction:
                p = pos.add(d)
                if c.can_build_harvester(p):
                    ti = c.get_global_resources()[0]
                    hcost = c.get_harvester_cost()[0]
                    if ti >= hcost + 10:
                        c.build_harvester(p)
                        self.harvesters_built += 1
                        self.target = None
                        print(f"[B{self.my_id} R{rnd}] HARVESTER #{self.harvesters_built} at {p} (cost={hcost}, ti_left={ti-hcost})", file=sys.stderr)
                        return
                    elif rnd <= 200:
                        print(f"[B{self.my_id} R{rnd}] Can build harvester at {p} but too poor: ti={ti} cost={hcost}", file=sys.stderr)

        if ore_tiles and rnd <= 100:
            print(f"[B{self.my_id} R{rnd}] See {len(ore_tiles)} ore tiles, nearest at dist^2={min(pos.distance_squared(t) for t in ore_tiles)}", file=sys.stderr)

        # Pick nearest visible ore
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

    def _nav(self, c, pos, target, passable):
        dirs = self._rank(pos, target)
        bfs_dir = self._bfs_step(pos, target, passable)
        if bfs_dir is not None and bfs_dir != dirs[0]:
            dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]

        for d in dirs:
            nxt = pos.add(d)
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                cc = c.get_conveyor_cost()[0]
                if ti >= cc + 10 and self.core_pos:
                    face = nxt.direction_to(self.core_pos)
                    if face == Direction.CENTRE:
                        face = d.opposite()
                    if c.can_build_conveyor(nxt, face):
                        c.build_conveyor(nxt, face)
                        self.conveyors_built += 1
                        return
            if c.get_move_cooldown() == 0 and c.can_move(d):
                c.move(d)
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

    def _explore(self, c, pos, passable):
        idx = ((self.my_id or 0) * 3 + self.explore_idx
               + c.get_current_round() // 150) % len(DIRS)
        d = DIRS[idx]
        dx, dy = d.delta()
        far = Position(pos.x + dx * 15, pos.y + dy * 15)
        self._nav(c, pos, far, passable)

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
