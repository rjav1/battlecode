"""Dual Competency Bot -- models Polska Gurom: rush on tight maps, economy on open.

Detects map size: tight (area <= 625) triggers rush+eco hybrid,
open maps trigger pure economy with late gunners.
"""

import random
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
        self.role = None  # 'eco', 'rush', or 'defense'
        self._enemy_core = None
        self._is_tight = None

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)

    # ── Core ──

    def _core(self, c):
        if self._is_tight is None:
            w = c.get_map_width()
            h = c.get_map_height()
            self._is_tight = (w * h) <= 625

        if c.get_action_cooldown() != 0:
            return

        units = c.get_unit_count() - 1
        rnd = c.get_current_round()
        ti = c.get_global_resources()[0]

        if self._is_tight:
            # Tight map: 5 total (2 rush + 3 eco), then slow growth
            if rnd <= 15:
                cap = 5
            elif rnd <= 100:
                cap = 8
            else:
                cap = 12
        else:
            # Open map: aggressive eco scaling
            if rnd <= 20:
                cap = 5
            elif rnd <= 60:
                cap = 10
            elif rnd <= 150:
                cap = 15
            else:
                cap = 20

        if units >= cap:
            return

        cost = c.get_builder_bot_cost()[0]
        if ti < cost + 2:
            return

        pos = c.get_position()
        best_sp = None
        for d in DIRS:
            sp = pos.add(d)
            if c.can_spawn(sp):
                if best_sp is None:
                    best_sp = sp

        if best_sp is not None:
            c.spawn_builder(best_sp)

    # ── Builder ──

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

        if self._is_tight is None:
            w = c.get_map_width()
            h = c.get_map_height()
            self._is_tight = (w * h) <= 625

        if self._enemy_core is None and self.core_pos is not None:
            w = c.get_map_width()
            h = c.get_map_height()
            self._enemy_core = Position(
                w - 1 - self.core_pos.x,
                h - 1 - self.core_pos.y
            )

        # Assign role
        if self.role is None:
            if self._is_tight:
                # First 2 builders rush, rest eco
                self.role = 'rush' if (self.my_id % 5) < 2 else 'eco'
            else:
                # Open map: all eco, some become defense later
                rnd = c.get_current_round()
                if rnd >= 300 and (self.my_id % 10) < 2:
                    self.role = 'defense'
                else:
                    self.role = 'eco'

        if self.role == 'rush':
            self._rush(c, pos)
        elif self.role == 'defense':
            self._defense(c, pos)
        else:
            self._eco(c, pos)

    # ── Rush ──

    def _rush(self, c, pos):
        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck = 0
        self.last_pos = pos

        if self.stuck > 15:
            self.stuck = 0
            self.explore_idx += 1

        # Attack enemy buildings
        if c.get_action_cooldown() == 0:
            bid = c.get_tile_building_id(pos)
            if bid is not None:
                try:
                    if c.get_team(bid) != c.get_team():
                        ti = c.get_global_resources()[0]
                        if ti >= 2 and c.can_fire(pos):
                            c.fire(pos)
                            return
                except Exception:
                    pass

        target = self._enemy_core
        if target is None:
            return

        dirs = self._rank(pos, target)

        if c.get_move_cooldown() == 0:
            for d in dirs:
                if c.can_move(d):
                    c.move(d)
                    return

        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            for d in dirs[:3]:
                nxt = pos.add(d)
                rc = c.get_road_cost()[0]
                if ti >= rc + 2 and c.can_build_road(nxt):
                    c.build_road(nxt)
                    return
                cc = c.get_conveyor_cost()[0]
                if ti >= cc + 2:
                    face = d.opposite()
                    if c.can_build_conveyor(nxt, face):
                        c.build_conveyor(nxt, face)
                        return

    # ── Defense: build gunners near core ──

    def _defense(self, c, pos):
        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck = 0
        self.last_pos = pos

        if self.stuck > 10:
            self.stuck = 0
            self.explore_idx += 1

        passable = set()
        for t in c.get_nearby_tiles():
            if c.get_tile_env(t) != Environment.WALL:
                passable.add(t)

        # Try to build gunner near core facing enemy
        if c.get_action_cooldown() == 0 and self.core_pos:
            ti = c.get_global_resources()[0]
            gc = c.get_gunner_cost()[0]
            if ti >= gc + 10:
                enemy_dir = pos.direction_to(self._enemy_core) if self._enemy_core else Direction.NORTH
                for d in Direction:
                    p = pos.add(d)
                    if c.can_build_gunner(p, enemy_dir):
                        c.build_gunner(p, enemy_dir)
                        # After building gunner, switch to eco
                        self.role = 'eco'
                        return

        # Navigate near core
        if self.core_pos:
            target = self.core_pos
            if pos.distance_squared(target) <= 20:
                # Close enough, try different spots
                idx = (self.my_id + self.explore_idx) % len(DIRS)
                d = DIRS[idx]
                target = self.core_pos.add(d).add(d).add(d)
            self._nav(c, pos, target, passable)

    # ── Economy ──

    def _eco(self, c, pos):
        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck = 0
        self.last_pos = pos

        if self.stuck > 12:
            self.target = None
            self.stuck = 0
            self.explore_idx += 1

        ore_tiles = []
        passable = set()
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e != Environment.WALL:
                passable.add(t)
                if e in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
                    if c.get_tile_building_id(t) is None:
                        ore_tiles.append(t)

        # Build harvester
        if c.get_action_cooldown() == 0:
            ore = self._best_adj_ore(c, pos)
            if ore is not None:
                ti = c.get_global_resources()[0]
                if ti >= c.get_harvester_cost()[0] + 2:
                    c.build_harvester(ore)
                    self.target = None
                    return

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
                if ti >= cc + 2:
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
            if ti >= rc + 2:
                for d in dirs:
                    if c.can_build_road(pos.add(d)):
                        c.build_road(pos.add(d))
                        return

    def _explore(self, c, pos, passable):
        rnd = c.get_current_round()
        rotation = rnd // 100
        idx = ((self.my_id or 0) * 7 + self.explore_idx + rotation) % len(DIRS)
        d = DIRS[idx]
        dx, dy = d.delta()
        far = Position(pos.x + dx * 20, pos.y + dy * 20)
        self._nav(c, pos, far, passable)

    def _best_adj_ore(self, c, pos):
        ti_best, ti_bd = None, 10**9
        ax_best, ax_bd = None, 10**9
        for d in Direction:
            p = pos.add(d)
            if c.can_build_harvester(p):
                env = c.get_tile_env(p)
                dist = p.distance_squared(self.core_pos) if self.core_pos else 0
                if env == Environment.ORE_TITANIUM and dist < ti_bd:
                    ti_best, ti_bd = p, dist
                elif env == Environment.ORE_AXIONITE and dist < ax_bd:
                    ax_best, ax_bd = p, dist
        return ti_best if ti_best is not None else ax_best

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
            cur, fd = queue.popleft()
            steps += 1
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
