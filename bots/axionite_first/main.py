"""Axionite-First Economy Bot v3

Strategy: Standard Ti economy PLUS harvest Ax ore + foundry for TB#1.
All builders harvest both ore types. One builder dedicated to foundry placement.
Foundry placed inline with existing conveyor chain near core.

Win condition: TB#1 (refined axionite delivered to core) beats pure Ti bots.
"""

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
        self.foundry_built = False
        self.foundry_pos = None
        self._enemy_dir = None
        self._enemy_core = None
        self.has_ax_harvester = False
        self.is_attacker = False
        self.foundry_target = None  # conveyor pos to replace with foundry

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)

    # ---------------------------------------------------------------- Core
    def _core(self, c):
        # Do NOT convert refined axionite -- we want TB#1 score!
        if c.get_action_cooldown() != 0:
            return

        units = c.get_unit_count() - 1
        rnd = c.get_current_round()
        ti = c.get_global_resources()[0]

        if rnd <= 30:
            cap = 3
        elif rnd <= 100:
            cap = 5
        elif rnd <= 300:
            cap = 7
        elif rnd <= 600:
            cap = 10
        else:
            cap = 12

        pos = c.get_position()
        vis_harv = 0
        for eid in c.get_nearby_buildings():
            try:
                if (c.get_entity_type(eid) == EntityType.HARVESTER
                        and c.get_team(eid) == c.get_team()):
                    vis_harv += 1
            except Exception:
                pass
        econ_cap = vis_harv * 2 + 3
        cap = min(cap, econ_cap)

        if units >= cap:
            return

        cost = c.get_builder_bot_cost()[0]
        if ti < cost + 10:
            return

        for d in DIRS:
            sp = pos.add(d)
            if c.can_spawn(sp):
                c.spawn_builder(sp)
                return

    # ---------------------------------------------------------------- Builder
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

        # Scan for existing infrastructure
        for eid in c.get_nearby_buildings():
            try:
                if c.get_team(eid) != c.get_team():
                    continue
                etype = c.get_entity_type(eid)
                if etype == EntityType.FOUNDRY:
                    self.foundry_built = True
                    self.foundry_pos = c.get_position(eid)
                elif etype == EntityType.HARVESTER:
                    hpos = c.get_position(eid)
                    if c.get_tile_env(hpos) == Environment.ORE_AXIONITE:
                        self.has_ax_harvester = True
            except Exception:
                pass

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

        # Scan vision for ore tiles
        ti_ore_tiles = []
        ax_ore_tiles = []
        passable = set()
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e != Environment.WALL:
                passable.add(t)
                if c.get_tile_building_id(t) is None:
                    if e == Environment.ORE_TITANIUM:
                        ti_ore_tiles.append(t)
                    elif e == Environment.ORE_AXIONITE:
                        ax_ore_tiles.append(t)

        rnd = c.get_current_round()

        # Attacker (late game)
        if (not self.is_attacker and rnd > 500
                and self.harvesters_built >= 4
                and (self.my_id or 0) % 6 == 5):
            self.is_attacker = True
        if self.is_attacker:
            self._attack(c, pos, passable)
            return

        # Foundry builder: id%3==1, after round 80, enough Ti
        if (not self.foundry_built
                and (self.my_id or 0) % 3 == 1
                and rnd >= 80
                and c.get_global_resources()[0] >= c.get_foundry_cost()[0] + 20):
            if self._try_build_foundry(c, pos, passable):
                return

        # Build harvester on adjacent ore (both types!)
        if c.get_action_cooldown() == 0:
            ore = self._best_adj_ore(c, pos)
            if ore is not None:
                ti = c.get_global_resources()[0]
                hcost = c.get_harvester_cost()[0]
                if ti >= hcost + 15:
                    c.build_harvester(ore)
                    self.harvesters_built += 1
                    if c.get_tile_env(ore) == Environment.ORE_AXIONITE:
                        self.has_ax_harvester = True
                    self.target = None
                    return

        # Target selection: all builders seek BOTH ore types
        # Prefer Ax ore if we haven't built an Ax harvester yet
        all_ore = ti_ore_tiles + ax_ore_tiles
        if not self.has_ax_harvester and ax_ore_tiles:
            # Prefer Ax ore, but don't ignore nearby Ti
            best, bd = None, 10**9
            for t in ax_ore_tiles:
                d = pos.distance_squared(t)
                if d < bd:
                    best, bd = t, d
            # Only override if Ax is reasonably close
            if bd < 100:
                self.target = best
            elif all_ore:
                best, bd = None, 10**9
                for t in all_ore:
                    d = pos.distance_squared(t)
                    if d < bd:
                        best, bd = t, d
                self.target = best
        elif all_ore:
            best, bd = None, 10**9
            for t in all_ore:
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

    # --------------------------------------------------------- Foundry
    def _try_build_foundry(self, c, pos, passable):
        """Build foundry by replacing a conveyor near core.

        The foundry accepts from any side and outputs from any side.
        By placing it on an existing conveyor tile, it sits inline with
        the resource chain: harvesters -> conveyors -> [foundry] -> conveyors -> core.
        """
        if not self.core_pos:
            return False

        # If we already have a target conveyor to replace, go there
        if self.foundry_target is not None:
            # Check it's still valid
            bid = c.get_tile_building_id(self.foundry_target)
            if bid is None:
                # Tile is clear, try to build foundry
                if pos.distance_squared(self.foundry_target) <= 2:
                    if c.get_action_cooldown() == 0 and c.can_build_foundry(self.foundry_target):
                        c.build_foundry(self.foundry_target)
                        self.foundry_built = True
                        self.foundry_pos = self.foundry_target
                        self.foundry_target = None
                        return True
                self._walk_to(c, pos, self.foundry_target)
                return True
            else:
                try:
                    if (c.get_entity_type(bid) == EntityType.CONVEYOR
                            and c.get_team(bid) == c.get_team()):
                        # Walk to it and destroy
                        if pos.distance_squared(self.foundry_target) <= 2:
                            if c.can_destroy(self.foundry_target):
                                c.destroy(self.foundry_target)
                                return True
                        self._walk_to(c, pos, self.foundry_target)
                        return True
                    else:
                        # Something else is there now, reset
                        self.foundry_target = None
                except Exception:
                    self.foundry_target = None

        # Find a conveyor near core to replace
        best_conv_pos = None
        best_dist = 10**9
        for eid in c.get_nearby_buildings():
            try:
                if c.get_team(eid) != c.get_team():
                    continue
                if c.get_entity_type(eid) != EntityType.CONVEYOR:
                    continue
                epos = c.get_position(eid)
                d2 = epos.distance_squared(self.core_pos)
                if 4 <= d2 <= 36 and d2 < best_dist:
                    best_dist = d2
                    best_conv_pos = epos
            except Exception:
                pass

        if best_conv_pos is not None:
            self.foundry_target = best_conv_pos
            self._walk_to(c, pos, best_conv_pos)
            return True

        # No conveyor found near core. Try building foundry on any empty tile near core
        if c.get_action_cooldown() == 0:
            for d in DIRS:
                fp = pos.add(d)
                if not c.can_build_foundry(fp):
                    continue
                if self.core_pos:
                    dist = fp.distance_squared(self.core_pos)
                    if dist < 2 or dist > 36:
                        continue
                c.build_foundry(fp)
                self.foundry_built = True
                self.foundry_pos = fp
                return True

        # Navigate toward core to find spots
        if self.core_pos:
            self._nav(c, pos, self.core_pos, passable)
            return True

        return False

    # ------------------------------------------------------- Ore selection
    def _best_adj_ore(self, c, pos):
        """Pick best adjacent ore tile to build harvester on.
        Prioritizes Ax ore if we have no Ax harvester.
        """
        best, bd = None, 10**9
        best_is_ax = False

        for d in DIRS:
            p = pos.add(d)
            if not c.can_build_harvester(p):
                continue
            env = c.get_tile_env(p)
            is_ax = (env == Environment.ORE_AXIONITE)
            dist = p.distance_squared(self.core_pos) if self.core_pos else 0

            if is_ax and not self.has_ax_harvester:
                if not best_is_ax or dist < bd:
                    best, bd = p, dist
                    best_is_ax = True
            elif not best_is_ax:
                if dist < bd:
                    best, bd = p, dist

        return best

    # ---------------------------------------------------------------- Nav
    def _nav(self, c, pos, target, passable):
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

        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            bc = c.get_bridge_cost()[0]
            if ti >= bc + 50:
                for d in dirs[:3]:
                    for step in range(2, 4):
                        dx, dy = d.delta()
                        bt = Position(pos.x + dx * step, pos.y + dy * step)
                        if bt.distance_squared(pos) > 9:
                            continue
                        for bd_dir in DIRS:
                            bp = pos.add(bd_dir)
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
            w, h = c.get_map_width(), c.get_map_height()
            for d in DIRS:
                ap = pos.add(d)
                if ap.x < 0 or ap.x >= w or ap.y < 0 or ap.y >= h:
                    continue
                abid = c.get_tile_building_id(ap)
                if abid is not None:
                    try:
                        if c.get_team(abid) != c.get_team():
                            if c.get_move_cooldown() == 0 and c.can_move(d):
                                c.move(d)
                                return
                    except Exception:
                        pass
        enemy_pos = self._get_enemy_core_pos(c)
        if enemy_pos:
            self._nav(c, pos, enemy_pos, passable)
        else:
            self._explore(c, pos, passable)

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
            w, h = c.get_map_width(), c.get_map_height()
            ti = c.get_global_resources()[0]
            rc = c.get_road_cost()[0]
            if ti >= rc + 5:
                for try_d in [d, d.rotate_left(), d.rotate_right()]:
                    nxt = pos.add(try_d)
                    if nxt.x < 0 or nxt.x >= w or nxt.y < 0 or nxt.y >= h:
                        continue
                    if c.can_build_road(nxt):
                        c.build_road(nxt)
                        return

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
        if self._enemy_core is not None:
            return self._enemy_core
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
                self._enemy_core = m
                return m
        self._enemy_core = mirrors[0]
        return self._enemy_core
