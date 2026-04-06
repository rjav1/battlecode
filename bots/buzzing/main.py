"""buzzing bees - economy bot with sentinels and attacker.

d.opposite() conveyors for resource delivery (proven 30K+ Ti).
Splitter-based sentinel ammo (proven pattern from splitter_test).
Attacker walks toward enemy core after economy established.
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
        self._enemy_dir = None
        # Splitter-sentinel state machine
        self.sent_step = 0  # 0=idle, 1=destroy, 2=splitter, 3=branch, 4=sentinel, 5=reset
        self.sent_conv_pos = None
        self.sent_conv_dir = None
        self.sent_branch_pos = None
        self.sent_sentinel_pos = None
        self.sent_branch_dir = None

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
        cap = 3 if rnd <= 50 else (5 if rnd <= 300 else 7)
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

        # Scan vision
        ore_tiles = []
        passable = set()
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e != Environment.WALL:
                passable.add(t)
                if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
                    ore_tiles.append(t)

        rnd = c.get_current_round()

        # Sentinel builder: id%5==1, after round 1000, near core, 200+ Ti
        if ((self.my_id or 0) % 5 == 1 and rnd > 1000
                and self.harvesters_built >= 3 and self.core_pos
                and self.sent_step < 6
                and (self.sent_step > 0 or pos.distance_squared(self.core_pos) <= 36)
                and c.get_global_resources()[0] >= 200):
            if self._build_sentinel_infra(c, pos):
                return

        # Attacker: id%4==2, after round 500, 4+ harvesters
        if ((self.my_id or 0) % 4 == 2 and rnd > 500
                and self.harvesters_built >= 4):
            self._attack(c, pos, passable)
            return

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

    # -------------------------------------------------------------- Nav
    def _nav(self, c, pos, target, passable):
        """Navigate toward target, building conveyors with d.opposite() facing."""
        dirs = self._rank(pos, target)
        bfs_dir = self._bfs_step(pos, target, passable)
        if bfs_dir is not None and bfs_dir != dirs[0]:
            dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]

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
                    if c.can_build_road(pos.add(d)):
                        c.build_road(pos.add(d))
                        return

        # Bridge fallback (only when flush with Ti)
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            bc = c.get_bridge_cost()[0]
            if ti >= bc + 200:
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

    def _explore(self, c, pos, passable):
        idx = ((self.my_id or 0) * 3 + self.explore_idx
               + c.get_current_round() // 150) % len(DIRS)
        d = DIRS[idx]
        dx, dy = d.delta()
        far = Position(pos.x + dx * 15, pos.y + dy * 15)
        self._nav(c, pos, far, passable)

    # -------------------------------------------------------- Sentinel infra
    def _build_sentinel_infra(self, c, pos):
        """Splitter-based sentinel: find conveyor, destroy, build splitter+branch+sentinel."""
        # Count sentinels, cap at 2
        if self.sent_step == 0:
            sent_count = 0
            for eid in c.get_nearby_buildings():
                try:
                    if (c.get_entity_type(eid) == EntityType.SENTINEL
                            and c.get_team(eid) == c.get_team()):
                        sent_count += 1
                except Exception:
                    pass
            if sent_count >= 2:
                self.sent_step = 6
                return False
            # Find conveyor near core to replace
            best_conv = None
            best_dist = 10**9
            for eid in c.get_nearby_buildings():
                try:
                    if (c.get_entity_type(eid) == EntityType.CONVEYOR
                            and c.get_team(eid) == c.get_team()):
                        epos = c.get_position(eid)
                        if self.core_pos:
                            d2 = epos.distance_squared(self.core_pos)
                            if 4 < d2 < 50 and d2 < best_dist:
                                best_dist = d2
                                best_conv = eid
                except Exception:
                    pass
            if best_conv is None:
                return False
            self.sent_conv_pos = c.get_position(best_conv)
            self.sent_conv_dir = c.get_direction(best_conv)
            cd = self.sent_conv_dir
            for branch_dir in [cd.rotate_left().rotate_left(),
                               cd.rotate_right().rotate_right()]:
                bp = self.sent_conv_pos.add(branch_dir)
                sp = bp.add(branch_dir)
                try:
                    if (c.get_tile_env(bp) != Environment.WALL
                            and c.get_tile_env(sp) != Environment.WALL
                            and c.is_tile_empty(bp)
                            and c.is_tile_empty(sp)):
                        self.sent_branch_pos = bp
                        self.sent_sentinel_pos = sp
                        self.sent_branch_dir = branch_dir
                        self.sent_step = 1
                        return False
                except Exception:
                    pass
            return False

        # Step 1: Walk to conveyor, destroy it
        if self.sent_step == 1:
            if pos.distance_squared(self.sent_conv_pos) > 2:
                self._walk_to(c, pos, self.sent_conv_pos)
                return True
            if c.can_destroy(self.sent_conv_pos):
                c.destroy(self.sent_conv_pos)
                self.sent_step = 2
            return True

        # Step 2: Build splitter
        if self.sent_step == 2:
            if c.get_action_cooldown() != 0:
                return True
            if pos.distance_squared(self.sent_conv_pos) > 2:
                self._walk_to(c, pos, self.sent_conv_pos)
                return True
            ti = c.get_global_resources()[0]
            if ti < c.get_splitter_cost()[0] + 50:
                return True
            if c.can_build_splitter(self.sent_conv_pos, self.sent_conv_dir):
                c.build_splitter(self.sent_conv_pos, self.sent_conv_dir)
                self.sent_step = 3
            return True

        # Step 3: Build branch conveyor
        if self.sent_step == 3:
            if c.get_action_cooldown() != 0:
                return True
            if pos.distance_squared(self.sent_branch_pos) > 2:
                self._walk_to(c, pos, self.sent_branch_pos)
                return True
            ti = c.get_global_resources()[0]
            if ti < c.get_conveyor_cost()[0] + 50:
                return True
            if c.can_build_conveyor(self.sent_branch_pos, self.sent_branch_dir):
                c.build_conveyor(self.sent_branch_pos, self.sent_branch_dir)
                self.sent_step = 4
            return True

        # Step 4: Build sentinel
        if self.sent_step == 4:
            if c.get_action_cooldown() != 0:
                return True
            if pos.distance_squared(self.sent_sentinel_pos) > 2:
                self._walk_to(c, pos, self.sent_sentinel_pos)
                return True
            ti = c.get_global_resources()[0]
            if ti < c.get_sentinel_cost()[0] + 50:
                return True
            face = self.sent_branch_dir
            if c.can_build_sentinel(self.sent_sentinel_pos, face):
                c.build_sentinel(self.sent_sentinel_pos, face)
                self.sent_step = 5
            else:
                for d in DIRS:
                    if d == self.sent_branch_dir.opposite():
                        continue
                    if c.can_build_sentinel(self.sent_sentinel_pos, d):
                        c.build_sentinel(self.sent_sentinel_pos, d)
                        self.sent_step = 5
                        break
            return True

        # Step 5: Reset for next sentinel
        if self.sent_step == 5:
            self.sent_step = 0
            self.sent_conv_pos = None
            return False

        return False

    # ------------------------------------------------------------ Attack
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
            self._nav(c, pos, enemy_pos, passable)

    # ------------------------------------------------------------ Helpers
    def _walk_to(self, c, pos, target):
        d = pos.direction_to(target)
        if d == Direction.CENTRE:
            return
        for try_d in [d, d.rotate_left(), d.rotate_right(),
                      d.rotate_left().rotate_left(), d.rotate_right().rotate_right()]:
            if c.get_move_cooldown() == 0 and c.can_move(try_d):
                c.move(try_d)
                return
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            rc = c.get_road_cost()[0]
            if ti >= rc + 10:
                for try_d in [d, d.rotate_left(), d.rotate_right()]:
                    nxt = pos.add(try_d)
                    if c.can_build_road(nxt):
                        c.build_road(nxt)
                        return

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
