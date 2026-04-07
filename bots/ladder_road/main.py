"""Ladder Road bot -- models The Defect's road+bridge economy.

From replay analysis: 19-40 harvesters, 6 bots, 25-31 roads, 29-33 bridges,
4-9 conveyors. Hard cap of 6 builders distinguishes this from ladder_eco (40 builders).

Key insight from working ladder_bridge bot:
- Conveyors must be built WHILE MOVING TOWARD ORE (d.opposite() faces back toward core)
- Bridges used for long-range hops when existing infrastructure is nearby
- Roads supplement movement when conveyor building is blocked

This bot:
1. Spawns exactly 6 builders
2. Each builder explores using standard d.opposite() conveyor navigation (same as buzzing)
3. After harvester: scans for nearby allied building within bridge range, builds bridge
   If no bridge target found, just continues (conveyors already laid on the way out)
4. Then continues exploring for more ore
5. Uses roads as fallback when conveyor can't be built (e.g., obstacle avoidance)
"""

from collections import deque
from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]
BRIDGE_RANGE_SQ = 9
BUILDER_CAP = 6


class Player:
    def __init__(self):
        self.core_pos = None
        self.target = None
        self.stuck = 0
        self.last_pos = None
        self.explore_idx = 0
        self.my_id = None
        self._w = None
        self._h = None
        self.built_harvester = False
        self.try_bridge = False     # True: attempt bridge after harvester

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)

    # ------------------------------------------------------------------ Core
    def _core(self, c):
        if self.core_pos is None:
            self.core_pos = c.get_position()
            self._w = c.get_map_width()
            self._h = c.get_map_height()

        if c.get_action_cooldown() != 0:
            return

        units = c.get_unit_count() - 1
        if units >= BUILDER_CAP:
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

    # ------------------------------------------------------------------ Builder
    def _builder(self, c):
        pos = c.get_position()
        rnd = c.get_current_round()

        if self.my_id is None:
            self.my_id = c.get_id()
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

        # Stuck detection
        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck = 0
        self.last_pos = pos

        if self.stuck > 15:
            self.target = None
            self.built_harvester = False
            self.try_bridge = False
            self.stuck = 0
            self.explore_idx += 1

        # After harvester: try to build a bridge to extend the chain (opportunistic)
        if self.try_bridge:
            self._attempt_bridge(c, pos)
            self.try_bridge = False
            # Fall through to continue exploring

        self._find_ore_and_harvest(c, pos, rnd)

    # ------------------------------------------------------------------ Find ore & harvest
    def _find_ore_and_harvest(self, c, pos, rnd):
        ore_tiles = []
        passable = set()
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e != Environment.WALL:
                passable.add(t)
                if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
                    ore_tiles.append(t)

        if c.get_action_cooldown() == 0:
            ore = self._best_adj_ore(c, pos)
            if ore is not None:
                ti = c.get_global_resources()[0]
                hcost = c.get_harvester_cost()[0]
                if ti >= hcost + 5:
                    c.build_harvester(ore)
                    self.built_harvester = True
                    self.try_bridge = True
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
            self._explore(c, pos, passable, rnd)

    # ------------------------------------------------------------------ Opportunistic bridge
    def _attempt_bridge(self, c, pos):
        """Try once to build a bridge from current pos to nearest allied building."""
        if c.get_action_cooldown() != 0:
            return

        ti = c.get_global_resources()[0]
        bcost = c.get_bridge_cost()[0]
        if ti < bcost + 5:
            return

        target = self._find_bridge_sink(c, pos)
        if target is not None and c.can_build_bridge(pos, target):
            c.build_bridge(pos, target)

    def _find_bridge_sink(self, c, pos):
        """Find nearest allied transport building or core within dist²≤9 of pos."""
        best_pos = None
        best_dist = BRIDGE_RANGE_SQ + 1

        for eid in c.get_nearby_buildings():
            try:
                if c.get_team(eid) != c.get_team():
                    continue
                etype = c.get_entity_type(eid)
                if etype in (EntityType.CONVEYOR, EntityType.SPLITTER,
                             EntityType.ARMOURED_CONVEYOR, EntityType.BRIDGE):
                    bp = c.get_position(eid)
                    d = pos.distance_squared(bp)
                    if d <= BRIDGE_RANGE_SQ and 0 < d < best_dist:
                        best_dist = d
                        best_pos = bp
            except Exception:
                continue

        if self.core_pos:
            d = pos.distance_squared(self.core_pos)
            if d <= BRIDGE_RANGE_SQ and d < best_dist:
                best_pos = self.core_pos

        return best_pos

    # ------------------------------------------------------------------ Navigation
    def _nav(self, c, pos, target, passable):
        """Navigate toward target. Primary: d.opposite() conveyors. Fallback: roads."""
        dirs = self._rank(pos, target)
        bfs_dir = self._bfs_step(pos, target, passable)
        if bfs_dir is not None and bfs_dir != dirs[0]:
            dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]

        for d in dirs:
            nxt = pos.add(d)
            # Build conveyor facing back toward where we came from (toward core)
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                cc = c.get_conveyor_cost()[0]
                if ti >= cc + 5:
                    face = d.opposite()
                    if c.can_build_conveyor(nxt, face):
                        c.build_conveyor(nxt, face)
                        return
            if c.get_move_cooldown() == 0 and c.can_move(d):
                c.move(d)
                return

        # Road fallback when conveyor can't be built
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            rc = c.get_road_cost()[0]
            if ti >= rc + 2:
                for d in dirs:
                    nxt = pos.add(d)
                    if (0 <= nxt.x < (self._w or 50) and 0 <= nxt.y < (self._h or 50)):
                        if c.can_build_road(nxt):
                            c.build_road(nxt)
                            return

    def _explore(self, c, pos, passable, rnd):
        rotation = rnd // 100
        idx = ((self.my_id or 0) * 7 + self.explore_idx + rotation) % len(DIRS)
        d = DIRS[idx]
        dx, dy = d.delta()
        w = self._w or 50
        h = self._h or 50
        far = Position(
            max(0, min(w - 1, pos.x + dx * 15)),
            max(0, min(h - 1, pos.y + dy * 15))
        )
        self._nav(c, pos, far, passable)

    def _best_adj_ore(self, c, pos):
        best, bd = None, 10**9
        for d in Direction:
            p = pos.add(d)
            if c.can_build_harvester(p):
                env = c.get_tile_env(p)
                if env == Environment.ORE_TITANIUM:
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
