"""Adaptive bot -- detects map size on round 1 and switches strategy.

Rush mode (small maps, area <= 625): fast aggression, quick economy, builder rush.
Expand mode (large maps, area >= 1600): maximum economy, barriers + sentinels late.
Balanced mode (medium maps): moderate economy, defenses after round 200, late attacker.
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
        self._enemy_core = None
        self._w = None
        self._h = None
        self._spawn_count = 0
        # Strategy: set by core on round 1, communicated via marker
        self.strategy = None
        # Sentinel infra state
        self.sent_step = 0
        self.sent_conv_pos = None
        self.sent_conv_dir = None
        self.sent_branch_pos = None
        self.sent_sentinel_pos = None
        self.sent_branch_dir = None
        self.is_attacker = False
        self._born_round = None

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)
        elif t == EntityType.SENTINEL:
            self._sentinel(c)
        elif t == EntityType.GUNNER:
            self._gunner(c)

    # ================================================================ CORE
    def _core(self, c):
        if self.core_pos is None:
            self.core_pos = c.get_position()
            self._w = c.get_map_width()
            self._h = c.get_map_height()

        # Classify map on round 1
        if self.strategy is None:
            area = self._w * self._h
            if area <= 625:
                self.strategy = "rush"
            elif area >= 1600:
                self.strategy = "expand"
            else:
                self.strategy = "balanced"
            # Encode strategy as marker on core tile: 1=rush, 2=balanced, 3=expand
            marker_val = {"rush": 1, "balanced": 2, "expand": 3}[self.strategy]
            if c.can_place_marker(self.core_pos):
                c.place_marker(self.core_pos, marker_val)

        if c.get_action_cooldown() != 0:
            return

        units = c.get_unit_count() - 1
        rnd = c.get_current_round()
        ti = c.get_global_resources()[0]
        cost = c.get_builder_bot_cost()[0]

        if self.strategy == "rush":
            cap = self._rush_cap(rnd, units)
            reserve = 5
        elif self.strategy == "expand":
            cap = self._expand_cap(rnd, units)
            reserve = 15
        else:
            cap = self._balanced_cap(rnd, units)
            reserve = 10

        if units >= cap:
            return
        if ti < cost + reserve:
            return

        pos = c.get_position()
        for d in DIRS:
            sp = pos.add(d)
            if c.can_spawn(sp):
                c.spawn_builder(sp)
                self._spawn_count += 1
                return

    def _rush_cap(self, rnd, units):
        # Rush: 5 builders immediately, then cap
        if rnd <= 20:
            return 5
        elif rnd <= 100:
            return 6
        else:
            return 8

    def _expand_cap(self, rnd, units):
        # Expand: start conservative, scale up
        if rnd <= 30:
            return 3
        elif rnd <= 100:
            return 5
        elif rnd <= 300:
            return 8
        elif rnd <= 600:
            return 10
        else:
            return 12

    def _balanced_cap(self, rnd, units):
        if rnd <= 20:
            return 4
        elif rnd <= 100:
            return 5
        elif rnd <= 300:
            return 7
        elif rnd <= 600:
            return 9
        else:
            return 11

    # ================================================================ GUNNER
    def _gunner(self, c):
        if c.get_action_cooldown() != 0 or c.get_ammo_amount() < 2:
            return
        tgt = c.get_gunner_target()
        if tgt is not None and c.can_fire(tgt):
            c.fire(tgt)

    # ================================================================ SENTINEL
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

    # ================================================================ BUILDER
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
                        break
                except Exception:
                    continue

        # Read strategy from marker on core tile
        if self.strategy is None and self.core_pos:
            try:
                mid = c.get_tile_building_id(self.core_pos)
                if mid is not None:
                    pass
                # Try reading marker on core position
                # Markers are separate from buildings -- check nearby tiles
                for t in c.get_nearby_tiles(dist_sq=2):
                    bid = c.get_tile_building_id(t)
                    if bid is not None:
                        try:
                            if c.get_entity_type(bid) == EntityType.MARKER:
                                val = c.get_marker_value(bid)
                                if val == 1:
                                    self.strategy = "rush"
                                elif val == 2:
                                    self.strategy = "balanced"
                                elif val == 3:
                                    self.strategy = "expand"
                                break
                        except Exception:
                            pass
            except Exception:
                pass
            # Fallback: classify from map size directly
            if self.strategy is None:
                area = self._w * self._h
                if area <= 625:
                    self.strategy = "rush"
                elif area >= 1600:
                    self.strategy = "expand"
                else:
                    self.strategy = "balanced"

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

        # Dispatch to strategy-specific builder logic
        if self.strategy == "rush":
            self._builder_rush(c, pos, rnd)
        elif self.strategy == "expand":
            self._builder_expand(c, pos, rnd)
        else:
            self._builder_balanced(c, pos, rnd)

    # -------------------------------------------------------- RUSH BUILDER
    def _builder_rush(self, c, pos, rnd):
        """Small map: quick 2 harvesters, then rush with remaining builders."""
        # Early builders do economy (first 2 harvesters)
        if self.harvesters_built < 2 and self._born_round and self._born_round <= 5:
            self._do_economy(c, pos, rnd)
            return

        # After 2 harvesters or late spawns: become attacker
        if not self.is_attacker and self.harvesters_built >= 2:
            self.is_attacker = True
        if not self.is_attacker and self._born_round and self._born_round > 5:
            self.is_attacker = True

        if self.is_attacker:
            # Build gunner facing enemy if near core and early
            if (rnd <= 60 and self.core_pos
                    and pos.distance_squared(self.core_pos) <= 8
                    and c.get_action_cooldown() == 0):
                if self._try_build_gunner(c, pos):
                    return
            self._attack(c, pos)
            return

        self._do_economy(c, pos, rnd)

    # -------------------------------------------------------- EXPAND BUILDER
    def _builder_expand(self, c, pos, rnd):
        """Large map: maximize harvesters, late barriers + sentinels."""
        # Sentinel builder: after round 300, 4+ harvesters
        if ((self.my_id or 0) % 5 == 1 and rnd > 300
                and self.harvesters_built >= 4 and self.core_pos
                and self.sent_step < 6
                and c.get_global_resources()[0] >= 150):
            if self._build_sentinel_infra(c, pos):
                return

        # Barrier placement: after round 200
        if (rnd >= 200 and self.core_pos
                and pos.distance_squared(self.core_pos) <= 20
                and c.get_action_cooldown() == 0
                and c.get_global_resources()[0] >= 60):
            if self._build_barriers(c, pos, max_barriers=8):
                return

        # Bridge for distant ore: if nearest ore is far
        if (rnd >= 100 and c.get_action_cooldown() == 0
                and c.get_global_resources()[0] >= 80):
            if self._try_build_bridge(c, pos):
                return

        self._do_economy(c, pos, rnd)

    # -------------------------------------------------------- BALANCED BUILDER
    def _builder_balanced(self, c, pos, rnd):
        """Medium map: 4+ harvesters, barriers at 200, sentinel at 300, attacker at 500."""
        # Attacker assignment after round 500
        if (not self.is_attacker and rnd > 500
                and self.harvesters_built >= 4
                and (self.my_id or 0) % 6 == 5):
            self.is_attacker = True
        if self.is_attacker:
            self._attack(c, pos)
            return

        # Sentinel builder
        if ((self.my_id or 0) % 5 == 1 and rnd > 200
                and self.harvesters_built >= 3 and self.core_pos
                and self.sent_step < 6
                and c.get_global_resources()[0] >= 150):
            if self._build_sentinel_infra(c, pos):
                return

        # Barrier placement: after round 150
        if (rnd >= 150 and self.core_pos
                and pos.distance_squared(self.core_pos) <= 20
                and c.get_action_cooldown() == 0
                and c.get_global_resources()[0] >= 50):
            if self._build_barriers(c, pos, max_barriers=4):
                return

        self._do_economy(c, pos, rnd)

    # ================================================================ ECONOMY
    def _do_economy(self, c, pos, rnd):
        """Shared economy logic: find ore, build harvesters, lay conveyors."""
        # Scan vision
        ore_tiles = []
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
                ore_tiles.append(t)

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
            self._nav(c, pos, self.target)
        else:
            self._explore(c, pos)

    # ================================================================ ATTACK
    def _attack(self, c, pos):
        """Rush toward enemy core, attacking buildings along the way."""
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

            # Move onto adjacent enemy buildings
            for d in DIRS:
                ap = pos.add(d)
                if not self._in_bounds(ap):
                    continue
                abid = c.get_tile_building_id(ap)
                if abid is not None:
                    try:
                        if c.get_team(abid) != c.get_team():
                            etype = c.get_entity_type(abid)
                            # Prioritize conveyors and harvesters
                            if etype in (EntityType.CONVEYOR, EntityType.SPLITTER,
                                         EntityType.HARVESTER, EntityType.ROAD,
                                         EntityType.ARMOURED_CONVEYOR):
                                if c.get_move_cooldown() == 0 and c.can_move(d):
                                    c.move(d)
                                    return
                    except Exception:
                        pass

        enemy_pos = self._get_enemy_core_pos(c)
        if enemy_pos:
            passable = set()
            for t in c.get_nearby_tiles():
                if c.get_tile_env(t) != Environment.WALL:
                    passable.add(t)
            self._nav(c, pos, enemy_pos)
        else:
            self._explore(c, pos)

    # ================================================================ GUNNER BUILD
    def _try_build_gunner(self, c, pos):
        """Try to build a gunner facing toward enemy."""
        ti = c.get_global_resources()[0]
        if ti < c.get_gunner_cost()[0] + 20:
            return False
        enemy_dir = self._get_enemy_direction(c)
        if not enemy_dir:
            return False
        # Count existing gunners
        gunner_count = 0
        for eid in c.get_nearby_buildings():
            try:
                if (c.get_entity_type(eid) == EntityType.GUNNER
                        and c.get_team(eid) == c.get_team()):
                    gunner_count += 1
            except Exception:
                pass
        if gunner_count >= 2:
            return False
        # Place gunner on adjacent empty tile
        for d in DIRS:
            gp = pos.add(d)
            if c.can_build_gunner(gp, enemy_dir):
                c.build_gunner(gp, enemy_dir)
                return True
        return False

    # ================================================================ BRIDGE
    def _try_build_bridge(self, c, pos):
        """Build a bridge to reach distant ore."""
        ti = c.get_global_resources()[0]
        bc = c.get_bridge_cost()[0]
        if ti < bc + 50:
            return False
        # Find distant ore in vision
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
                if pos.distance_squared(t) > 8:
                    # Try building bridge toward it
                    for d in DIRS:
                        bp = pos.add(d)
                        if bp.distance_squared(t) <= 9:
                            if c.can_build_bridge(bp, t):
                                c.build_bridge(bp, t)
                                return True
        return False

    # ================================================================ SENTINEL INFRA
    def _build_sentinel_infra(self, c, pos):
        """Splitter-based sentinel: find conveyor, destroy, build splitter+branch+sentinel."""
        if self.sent_step == 0:
            sent_count = 0
            for eid in c.get_nearby_buildings():
                try:
                    if (c.get_entity_type(eid) == EntityType.SENTINEL
                            and c.get_team(eid) == c.get_team()):
                        sent_count += 1
                except Exception:
                    pass
            max_sent = 2 if self.strategy == "balanced" else 3
            if sent_count >= max_sent:
                self.sent_step = 6
                return False
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

        if self.sent_step == 1:
            if pos.distance_squared(self.sent_conv_pos) > 2:
                self._walk_to(c, pos, self.sent_conv_pos)
                return True
            if c.can_destroy(self.sent_conv_pos):
                c.destroy(self.sent_conv_pos)
                self.sent_step = 2
            return True

        if self.sent_step == 2:
            if c.get_action_cooldown() != 0:
                return True
            if pos.distance_squared(self.sent_conv_pos) > 2:
                self._walk_to(c, pos, self.sent_conv_pos)
                return True
            ti = c.get_global_resources()[0]
            if ti < c.get_splitter_cost()[0] + 30:
                return True
            if c.can_build_splitter(self.sent_conv_pos, self.sent_conv_dir):
                c.build_splitter(self.sent_conv_pos, self.sent_conv_dir)
                self.sent_step = 3
            return True

        if self.sent_step == 3:
            if c.get_action_cooldown() != 0:
                return True
            if pos.distance_squared(self.sent_branch_pos) > 2:
                self._walk_to(c, pos, self.sent_branch_pos)
                return True
            ti = c.get_global_resources()[0]
            if ti < c.get_conveyor_cost()[0] + 30:
                return True
            if c.can_build_conveyor(self.sent_branch_pos, self.sent_branch_dir):
                c.build_conveyor(self.sent_branch_pos, self.sent_branch_dir)
                self.sent_step = 4
            return True

        if self.sent_step == 4:
            if c.get_action_cooldown() != 0:
                return True
            if pos.distance_squared(self.sent_sentinel_pos) > 2:
                self._walk_to(c, pos, self.sent_sentinel_pos)
                return True
            ti = c.get_global_resources()[0]
            if ti < c.get_sentinel_cost()[0] + 30:
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

        if self.sent_step == 5:
            self.sent_step = 0
            self.sent_conv_pos = None
            return False

        return False

    # ================================================================ BARRIERS
    def _build_barriers(self, c, pos, max_barriers=6):
        """Place barriers on the enemy-facing side of core."""
        enemy_dir = self._get_enemy_direction(c)
        if not enemy_dir:
            return False
        barrier_count = 0
        for eid in c.get_nearby_buildings():
            try:
                if (c.get_entity_type(eid) == EntityType.BARRIER
                        and c.get_team(eid) == c.get_team()):
                    barrier_count += 1
            except Exception:
                pass
        if barrier_count >= max_barriers:
            return False
        ti = c.get_global_resources()[0]
        if ti < c.get_barrier_cost()[0] + 40:
            return False
        dx, dy = enemy_dir.delta()
        perp_left = enemy_dir.rotate_left().rotate_left()
        perp_right = enemy_dir.rotate_right().rotate_right()
        for dist in (3, 2):
            cx = self.core_pos.x + dx * dist
            cy = self.core_pos.y + dy * dist
            center = Position(cx, cy)
            for offset in (0, -2, 2):
                pdx, pdy = (perp_right if offset > 0 else perp_left).delta()
                abs_off = abs(offset)
                bp = Position(center.x + pdx * abs_off, center.y + pdy * abs_off)
                if not c.is_in_vision(bp):
                    continue
                if pos.distance_squared(bp) > 2:
                    continue
                try:
                    if c.can_build_barrier(bp):
                        c.build_barrier(bp)
                        return True
                except Exception:
                    pass
        return False

    # ================================================================ NAVIGATION
    def _nav(self, c, pos, target):
        """Navigate toward target, building d.opposite() conveyors."""
        dirs = self._rank(pos, target)
        passable = set()
        for t in c.get_nearby_tiles():
            if c.get_tile_env(t) != Environment.WALL:
                passable.add(t)
        bfs_dir = self._bfs_step(pos, target, passable)
        if bfs_dir is not None and bfs_dir != dirs[0]:
            dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]

        for d in dirs:
            nxt = pos.add(d)
            if not self._in_bounds(nxt):
                continue
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                cc = c.get_conveyor_cost()[0]
                if ti >= cc + 5:
                    face = d.opposite()
                    # Destroy allied road to replace with conveyor
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
                    if not self._in_bounds(rp):
                        continue
                    if c.can_build_road(rp):
                        c.build_road(rp)
                        return

        # Bridge fallback
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            bc = c.get_bridge_cost()[0]
            if ti >= bc + 50:
                for d in dirs[:3]:
                    for step in range(2, 4):
                        ddx, ddy = d.delta()
                        bt = Position(pos.x + ddx * step, pos.y + ddy * step)
                        if bt.distance_squared(pos) > 9:
                            continue
                        for bd in DIRS:
                            bp = pos.add(bd)
                            if c.can_build_bridge(bp, bt):
                                c.build_bridge(bp, bt)
                                return

    def _explore(self, c, pos):
        idx = ((self.my_id or 0) * 3 + self.explore_idx
               + c.get_current_round() // 150) % len(DIRS)
        d = DIRS[idx]
        ddx, ddy = d.delta()
        far = Position(pos.x + ddx * 15, pos.y + ddy * 15)
        self._nav(c, pos, far)

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
            if ti >= rc + 5:
                for try_d in [d, d.rotate_left(), d.rotate_right()]:
                    nxt = pos.add(try_d)
                    if self._in_bounds(nxt) and c.can_build_road(nxt):
                        c.build_road(nxt)
                        return

    # ================================================================ HELPERS
    def _best_adj_ore(self, c, pos):
        best, bd = None, 10**9
        for d in DIRS:
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
        if self._w is None:
            self._w = c.get_map_width()
            self._h = c.get_map_height()
        w, h = self._w, self._h
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
        if self._enemy_core is not None:
            return self._enemy_core
        # Check if we can see enemy core directly
        for eid in c.get_nearby_entities():
            try:
                if (c.get_entity_type(eid) == EntityType.CORE
                        and c.get_team(eid) != c.get_team()):
                    self._enemy_core = c.get_position(eid)
                    return self._enemy_core
            except Exception:
                continue
        if not self.core_pos:
            return None
        if self._w is None:
            return None
        w, h = self._w, self._h
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
                self._enemy_core = m
                return m
        self._enemy_core = mirrors[0]
        return self._enemy_core

    def _in_bounds(self, p):
        if self._w is None:
            return True
        return 0 <= p.x < self._w and 0 <= p.y < self._h
