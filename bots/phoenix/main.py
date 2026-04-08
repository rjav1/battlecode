"""Phoenix v2: Roads outbound, conveyors inbound.
Builder walks to ore via roads, builds harvester, walks BACK toward core
building conveyors (facing core-ward). Bridges when close enough.
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
        self.harvesters_built = 0
        self._chain_mode = False  # True = walking back to core building conveyors

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
        w, h = c.get_map_width(), c.get_map_height()
        area = w * h
        if area <= 625:
            cap = 3 if rnd <= 20 else (5 if rnd <= 100 else 7)
        elif area >= 1600:
            cap = 3 if rnd <= 30 else (5 if rnd <= 150 else 10)
        else:
            cap = 3 if rnd <= 25 else (4 if rnd <= 100 else 7)
        scale = c.get_scale_percent()
        if scale > 200.0:
            cap = min(cap, 3)
        elif scale > 160.0:
            cap = min(cap, 5)
        if units >= cap:
            return
        ti = c.get_global_resources()[0]
        cost = c.get_builder_bot_cost()[0]
        if ti < cost + 5:
            return
        pos = c.get_position()
        best_ore_dir = None
        if units == 0:
            best_dist = 10**9
            for tile in c.get_nearby_tiles():
                if c.get_tile_env(tile) in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
                    dist = pos.distance_squared(tile)
                    if dist <= 36:
                        d = pos.direction_to(tile)
                        if d != Direction.CENTRE and dist < best_dist:
                            best_dist = dist
                            best_ore_dir = d
        spawn_dirs = [best_ore_dir] + [d for d in DIRS if d != best_ore_dir] if best_ore_dir else DIRS
        for d in spawn_dirs:
            sp = pos.add(d)
            if c.can_spawn(sp):
                c.spawn_builder(sp)
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

        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck = 0
        self.last_pos = pos
        if self.stuck > 12:
            self.target = None
            self._chain_mode = False
            self.stuck = 0
            self.explore_idx += 1

        rnd = c.get_current_round()

        # Scan vision
        ore_tiles = []
        passable = set()
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e != Environment.WALL:
                passable.add(t)
                if e in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
                    bid = c.get_tile_building_id(t)
                    if bid is None:
                        ore_tiles.append(t)
                    else:
                        try:
                            if c.get_entity_type(bid) == EntityType.MARKER:
                                ore_tiles.append(t)
                        except Exception:
                            pass

        # CHAIN MODE: walk toward core building conveyors (delivery chain)
        import sys
        if self._chain_mode and rnd <= 100:
            print(f"R{rnd} CHAIN pos={pos} core_dist={pos.distance_squared(self.core_pos) if self.core_pos else -1} harv={self.harvesters_built} cd={c.get_action_cooldown()}", file=sys.stderr)
        if self._chain_mode and self.core_pos:
            # Check if we can bridge to core or existing chain
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                bc = c.get_bridge_cost()[0]
                if ti >= bc + 5:
                    # Try bridge to core tiles or allied chain
                    targets = self._get_bridge_targets(c, pos)
                    for tgt in targets:
                        for d in DIRS:
                            bp = pos.add(d)
                            try:
                                if c.can_build_bridge(bp, tgt):
                                    c.build_bridge(bp, tgt)
                                    self._chain_mode = False
                                    return
                            except Exception:
                                pass

            # Already on/near core? Chain complete
            if self.core_pos and pos.distance_squared(self.core_pos) <= 8:
                self._chain_mode = False
            else:
                # Walk toward core, building conveyors (facing core-ward)
                self._nav_conveyors(c, pos, self.core_pos, passable)
                return

        # Build harvester on adjacent ore (opportunistic: even during chain mode)
        if c.get_action_cooldown() == 0:
            ore = self._best_adj_ore(c, pos)
            if ore is not None:
                ti = c.get_global_resources()[0]
                if ti >= c.get_harvester_cost()[0] + 5:
                    c.build_harvester(ore)
                    self.harvesters_built += 1
                    self.target = None
                    self._chain_mode = True  # switch to chain mode
                    print(f"R{rnd} HARVESTER at {ore} core_dist={ore.distance_squared(self.core_pos) if self.core_pos else -1}", file=sys.stderr)
                    return

        # Pick target ore
        if ore_tiles and self.core_pos:
            best, bd = None, 10**9
            for t in ore_tiles:
                builder_dist = pos.distance_squared(t)
                core_dist = t.distance_squared(self.core_pos)
                score = builder_dist + core_dist * 3
                if c.get_tile_env(t) == Environment.ORE_AXIONITE:
                    score += 50000
                if score < bd:
                    best, bd = t, score
            self.target = best
        elif self.target and c.is_in_vision(self.target):
            bid = c.get_tile_building_id(self.target)
            if bid is not None:
                try:
                    if c.get_entity_type(bid) != EntityType.MARKER:
                        self.target = None
                except Exception:
                    self.target = None

        if self.target:
            self._nav_roads(c, pos, self.target, passable)
        else:
            self._explore(c, pos, passable)

    def _get_bridge_targets(self, c, pos):
        """Get sorted list of bridge targets (core tiles + allied chain tiles)."""
        targets = []
        my_team = c.get_team()
        if self.core_pos:
            cx, cy = self.core_pos.x, self.core_pos.y
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    targets.append(Position(cx + dx, cy + dy))
        for eid in c.get_nearby_buildings():
            try:
                if (c.get_entity_type(eid) in (EntityType.CONVEYOR, EntityType.BRIDGE,
                                                EntityType.SPLITTER)
                        and c.get_team(eid) == my_team):
                    epos = c.get_position(eid)
                    if epos.distance_squared(self.core_pos) < pos.distance_squared(self.core_pos):
                        targets.append(epos)
            except Exception:
                pass
        targets.sort(key=lambda t: pos.distance_squared(t))
        return targets

    def _nav_conveyors(self, c, pos, target, passable):
        """Navigate toward target building d.opposite() conveyors (delivery chain)."""
        dirs = self._rank(pos, target)
        bfs_dir = self._bfs_step(pos, target, passable)
        if bfs_dir is not None and bfs_dir != dirs[0]:
            dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]
        w, h = c.get_map_width(), c.get_map_height()
        for d in dirs:
            nxt = pos.add(d)
            if nxt.x < 0 or nxt.x >= w or nxt.y < 0 or nxt.y >= h:
                continue
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                cc = c.get_conveyor_cost()[0]
                if ti >= cc + 5:
                    face = d.opposite()
                    # Destroy road to make room for conveyor
                    bid = c.get_tile_building_id(nxt)
                    if bid is not None:
                        try:
                            if (c.get_entity_type(bid) == EntityType.ROAD
                                    and c.get_team(bid) == c.get_team()):
                                if c.can_destroy(nxt):
                                    c.destroy(nxt)
                        except Exception:
                            pass
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
            if ti >= rc + 5:
                for d in dirs:
                    rp = pos.add(d)
                    if rp.x < 0 or rp.x >= w or rp.y < 0 or rp.y >= h:
                        continue
                    if c.can_build_road(rp):
                        c.build_road(rp)
                        return

    def _nav_roads(self, c, pos, target, passable):
        """Navigate toward target using ROADS only."""
        dirs = self._rank(pos, target)
        bfs_dir = self._bfs_step(pos, target, passable)
        if bfs_dir is not None and bfs_dir != dirs[0]:
            dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]
        w, h = c.get_map_width(), c.get_map_height()
        for d in dirs:
            nxt = pos.add(d)
            if nxt.x < 0 or nxt.x >= w or nxt.y < 0 or nxt.y >= h:
                continue
            if c.get_move_cooldown() == 0 and c.can_move(d):
                c.move(d)
                return
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                rc = c.get_road_cost()[0]
                if ti >= rc + 5 and c.can_build_road(nxt):
                    c.build_road(nxt)
                    return
        # Bridge fallback for walls
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
                            try:
                                if c.can_build_bridge(bp, bt):
                                    c.build_bridge(bp, bt)
                                    return
                            except Exception:
                                pass

    def _explore(self, c, pos, passable):
        w, h = c.get_map_width(), c.get_map_height()
        mid = self.my_id or 0
        sector = (mid * 7 + self.explore_idx * 3 + c.get_current_round() // 80) % len(DIRS)
        d = DIRS[sector]
        dx, dy = d.delta()
        cx, cy = (self.core_pos.x, self.core_pos.y) if self.core_pos else (pos.x, pos.y)
        reach = max(w, h)
        tx = max(0, min(w - 1, cx + dx * reach))
        ty = max(0, min(h - 1, cy + dy * reach))
        self._nav_roads(c, pos, Position(tx, ty), passable)

    def _best_adj_ore(self, c, pos):
        best, bd = None, 10**9
        for d in DIRS:
            p = pos.add(d)
            if c.can_build_harvester(p):
                dist = p.distance_squared(self.core_pos) if self.core_pos else 0
                if c.get_tile_env(p) == Environment.ORE_AXIONITE:
                    dist += 100000
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
        steps = 0
        while queue and steps < 200:
            steps += 1
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
