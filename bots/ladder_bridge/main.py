"""Bridge Economy Bot -- models Blue Dragon's bridge-heavy economy approach.

Spawns 15-20 builders. Each builder finds ore, builds harvester, then builds
a bridge from the harvester back to the nearest allied conveyor/core tile.
Uses bridges for ALL connections. Pure economy, no military.
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
        self.built_harvester = False
        self.bridge_target = None  # position to build bridge at

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)

    # ── Core ──

    def _core(self, c):
        if c.get_action_cooldown() != 0:
            return
        units = c.get_unit_count() - 1
        rnd = c.get_current_round()

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

        ti = c.get_global_resources()[0]
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
                # Bias toward ore
                for t in c.get_nearby_tiles():
                    env = c.get_tile_env(t)
                    if env in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
                        if c.get_tile_building_id(t) is None:
                            if best_sp is None or sp.distance_squared(t) < best_sp.distance_squared(t):
                                best_sp = sp
                                break

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

        # Stuck detection
        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck = 0
        self.last_pos = pos

        if self.stuck > 12:
            self.target = None
            self.built_harvester = False
            self.bridge_target = None
            self.stuck = 0
            self.explore_idx += 1

        # Phase 1: If we haven't built a harvester, find ore and build one
        if not self.built_harvester:
            self._find_and_build_harvester(c, pos)
            return

        # Phase 2: After harvester, try to build a bridge back toward core
        if self.bridge_target is not None:
            self._build_bridge_back(c, pos)
            return

        # Phase 3: Done with this cycle, find more ore
        self.built_harvester = False
        self._find_and_build_harvester(c, pos)

    def _find_and_build_harvester(self, c, pos):
        ore_tiles = []
        passable = set()
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e != Environment.WALL:
                passable.add(t)
                if e in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
                    if c.get_tile_building_id(t) is None:
                        ore_tiles.append(t)

        # Build harvester on adjacent ore
        if c.get_action_cooldown() == 0:
            ore = self._best_adj_ore(c, pos)
            if ore is not None:
                ti = c.get_global_resources()[0]
                if ti >= c.get_harvester_cost()[0] + 2:
                    c.build_harvester(ore)
                    self.built_harvester = True
                    # Now find a bridge target: nearest allied conveyor or core tile
                    self.bridge_target = self._find_bridge_sink(c, ore)
                    self.target = None
                    return

        # Target nearest visible ore, with randomization
        if ore_tiles:
            random.shuffle(ore_tiles)
            best, bd = None, 10**9
            for t in ore_tiles[:8]:  # pick from top few
                d = pos.distance_squared(t)
                if d < bd:
                    best, bd = t, d
            self.target = best

        if self.target:
            self._nav(c, pos, self.target, passable)
        else:
            self._explore(c, pos, passable)

    def _find_bridge_sink(self, c, harvester_pos):
        """Find nearest allied conveyor/core tile to bridge to from harvester."""
        best_pos = None
        best_dist = 10**9
        for eid in c.get_nearby_buildings():
            try:
                if c.get_team(eid) != c.get_team():
                    continue
                etype = c.get_entity_type(eid)
                if etype in (EntityType.CONVEYOR, EntityType.SPLITTER,
                             EntityType.ARMOURED_CONVEYOR, EntityType.BRIDGE):
                    bp = c.get_position(eid)
                    d = harvester_pos.distance_squared(bp)
                    if d < best_dist:
                        best_dist = d
                        best_pos = bp
            except Exception:
                continue
        # Also consider core tiles
        if self.core_pos:
            d = harvester_pos.distance_squared(self.core_pos)
            if d < best_dist:
                best_pos = self.core_pos
        return best_pos

    def _build_bridge_back(self, c, pos):
        """Try to build a bridge from current position toward bridge_target."""
        passable = set()
        for t in c.get_nearby_tiles():
            if c.get_tile_env(t) != Environment.WALL:
                passable.add(t)

        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            bc = c.get_bridge_cost()[0]
            if ti >= bc + 2:
                # Try building bridge on adjacent empty tiles pointing toward target
                for d in Direction:
                    bp = pos.add(d)
                    if self.bridge_target and c.can_build_bridge(bp, self.bridge_target):
                        c.build_bridge(bp, self.bridge_target)
                        self.bridge_target = None
                        return
                # If bridge target too far, try bridging toward any nearby conveyor
                for eid in c.get_nearby_buildings(dist_sq=9):
                    try:
                        if c.get_team(eid) != c.get_team():
                            continue
                        etype = c.get_entity_type(eid)
                        if etype in (EntityType.CONVEYOR, EntityType.ARMOURED_CONVEYOR):
                            target_p = c.get_position(eid)
                            for dd in Direction:
                                bp = pos.add(dd)
                                if c.can_build_bridge(bp, target_p):
                                    c.build_bridge(bp, target_p)
                                    self.bridge_target = None
                                    return
                    except Exception:
                        continue

            # Also lay conveyors as fallback
            cc = c.get_conveyor_cost()[0]
            if ti >= cc + 2 and self.core_pos:
                d = pos.direction_to(self.core_pos)
                if d != Direction.CENTRE:
                    nxt = pos.add(d)
                    face = d.opposite()
                    if c.can_build_conveyor(nxt, face):
                        c.build_conveyor(nxt, face)
                        return

        # Navigate toward core to find bridge-able position
        if self.core_pos:
            self._nav(c, pos, self.core_pos, passable)
        else:
            self.bridge_target = None

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

        # Road fallback
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            rc = c.get_road_cost()[0]
            if ti >= rc + 2:
                for d in dirs:
                    if c.can_build_road(pos.add(d)):
                        c.build_road(pos.add(d))
                        return

    def _explore(self, c, pos, passable):
        idx = ((self.my_id or 0) * 7 + self.explore_idx) % len(DIRS)
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
