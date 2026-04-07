"""ladder_fast_rush: Models HAL9000 round-86 core kill strategy.
3 builders spawned immediately. Builders 0+1 rush enemy core via roads,
build gunner in range, feed ammo via conveyors. Builder 2 does economy.
"""
from collections import deque
from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]


class Player:
    def __init__(self):
        self.core_pos = None
        self.enemy_core = None
        self.my_id = None
        self.last_pos = None
        self.stuck = 0
        self.role = None  # "rush" or "eco"
        self.gunner_pos = None
        self.gunner_placed = False
        self.harvesters_built = 0
        self.target = None
        self.explore_idx = 0

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
        rnd = c.get_current_round()
        # Spawn 3 builders fast — 2 rushers + 1 eco
        cap = 3 if rnd <= 5 else (5 if rnd <= 200 else 8)
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

    def _gunner(self, c):
        if c.get_action_cooldown() != 0 or c.get_ammo_amount() < 2:
            return
        target = c.get_gunner_target()
        if target and c.can_fire(target):
            c.fire(target)

    def _infer_enemy_core(self, c):
        if self.enemy_core:
            return self.enemy_core
        if not self.core_pos:
            return None
        w, h = c.get_map_width(), c.get_map_height()
        cx, cy = self.core_pos.x, self.core_pos.y
        # Map is symmetric — reflect around center
        ex = w - 1 - cx
        ey = h - 1 - cy
        self.enemy_core = Position(ex, ey)
        return self.enemy_core

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

        # Assign role based on id: first 2 builders rush, rest eco
        if self.role is None:
            units = c.get_unit_count() - 1
            mid = self.my_id or 0
            self.role = "rush" if (mid % 3) < 2 else "eco"

        passable = set()
        ore_tiles = []
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e != Environment.WALL:
                passable.add(t)
                if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
                    ore_tiles.append(t)

        rnd = c.get_current_round()

        if self.role == "rush":
            self._rush(c, pos, passable, rnd)
        else:
            self._eco(c, pos, passable, ore_tiles, rnd)

    def _rush(self, c, pos, passable, rnd):
        enemy = self._infer_enemy_core(c)
        if not enemy:
            return

        # Check if we can place a gunner in range of enemy core
        if not self.gunner_placed and c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            gc = c.get_gunner_cost()[0]
            if ti >= gc + 10:
                # Try to place gunner on current or adjacent tile facing enemy
                enemy_dir = pos.direction_to(enemy)
                for gd in [enemy_dir, enemy_dir.rotate_left(), enemy_dir.rotate_right()]:
                    gp = pos.add(gd) if gd != Direction.CENTRE else pos
                    # Check if gunner on this tile can see enemy core
                    try:
                        tiles = c.get_attackable_tiles_from(gp, enemy_dir, EntityType.GUNNER)
                        if enemy in tiles or any(t.distance_squared(enemy) <= 4 for t in tiles):
                            if c.can_build_gunner(gp, enemy_dir):
                                c.build_gunner(gp, enemy_dir)
                                self.gunner_placed = True
                                self.gunner_pos = gp
                                return
                    except Exception:
                        pass

        # After placing gunner, build ammo conveyor from adjacent tile toward gunner
        if self.gunner_placed and self.gunner_pos and c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            cc = c.get_conveyor_cost()[0]
            if ti >= cc + 5:
                # Build conveyor adjacent to gunner on non-facing side
                enemy_dir = pos.direction_to(self.gunner_pos)
                for d in DIRS:
                    cp = self.gunner_pos.add(d)
                    # Don't block the facing direction
                    gunner_dir = self.gunner_pos.direction_to(self._infer_enemy_core(c))
                    if d == gunner_dir:
                        continue
                    if cp.distance_squared(pos) <= 2:
                        if c.can_build_conveyor(cp, d.opposite()):
                            c.build_conveyor(cp, d.opposite())
                            return

        # Navigate toward enemy core via roads
        if not enemy:
            return
        dirs = sorted(DIRS, key=lambda d: pos.add(d).distance_squared(enemy))
        bfs_dir = self._bfs_step(pos, enemy, passable)
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
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                rc = c.get_road_cost()[0]
                if ti >= rc + 2 and c.can_build_road(nxt):
                    c.build_road(nxt)
                    return

    def _eco(self, c, pos, passable, ore_tiles, rnd):
        # Simple economy: find ore, build harvester + conveyor chain
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

        if ore_tiles and not self.target:
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
            self._nav_eco(c, pos, self.target, passable)
        else:
            w, h = c.get_map_width(), c.get_map_height()
            mid = self.my_id or 0
            sector = (mid * 7 + self.explore_idx * 3 + rnd // 50) % len(DIRS)
            d = DIRS[sector]
            dx, dy = d.delta()
            cx = self.core_pos.x if self.core_pos else pos.x
            cy = self.core_pos.y if self.core_pos else pos.y
            far = Position(max(0, min(w-1, cx + dx*max(w,h))), max(0, min(h-1, cy + dy*max(w,h))))
            self._nav_eco(c, pos, far, passable, explore=True)

    def _nav_eco(self, c, pos, target, passable, explore=False):
        dirs = sorted(DIRS, key=lambda d: pos.add(d).distance_squared(target))
        bfs_dir = self._bfs_step(pos, target, passable)
        if bfs_dir and bfs_dir != dirs[0]:
            dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]
        w, h = c.get_map_width(), c.get_map_height()
        ti_reserve = 999999 if explore else 5
        for d in dirs:
            nxt = pos.add(d)
            if not (0 <= nxt.x < w and 0 <= nxt.y < h):
                continue
            if not explore and c.get_action_cooldown() == 0:
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
