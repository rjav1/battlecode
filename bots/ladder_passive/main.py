"""ladder_passive: Ultra-minimal bot. 2 builders, zero military.
d.opposite() conveyors laid during navigation. Targets nearest 3-4 ore tiles.
Tests whether buzzing's extra features actually help vs doing less.
"""
import sys
from collections import deque
from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]


class Player:
    def __init__(self):
        self.core_pos = None
        self.my_id = None
        self.target = None
        self.harvesters_built = 0
        self.ore_cap = 4
        self.stuck = 0
        self.last_pos = None

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)

    def _core(self, c):
        ti = c.get_global_resources()[0]
        n = c.get_unit_count()
        if n < 3 and ti >= 30 and c.get_action_cooldown() == 0:
            pos = c.get_position()
            for d in DIRS:
                sp = pos.add(d)
                if c.can_spawn(sp):
                    c.spawn_builder(sp)
                    break

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
        rnd = c.get_current_round()
        if rnd <= 5:
            print(f"[passive rnd={rnd}] pos={pos} core={self.core_pos} target={self.target} move_cd={c.get_move_cooldown()} act_cd={c.get_action_cooldown()}", file=sys.stderr)

        # Find core
        if self.core_pos is None:
            for eid in c.get_nearby_entities():
                try:
                    if c.get_entity_type(eid) == EntityType.CORE and c.get_team(eid) == c.get_team():
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
        if self.stuck > 8:
            self.target = None
            self.stuck = 0

        # Scan nearby tiles
        passable = set()
        ore_tiles = []
        for tp in c.get_nearby_tiles():
            try:
                env = c.get_tile_env(tp)
                if env == Environment.WALL:
                    continue
                passable.add(tp)
                if env == Environment.ORE_TITANIUM:
                    bid = c.get_tile_building_id(tp)
                    if bid is None:
                        ore_tiles.append(tp)
            except Exception:
                pass

        ti = c.get_global_resources()[0]

        # Build harvester on adjacent ore
        if c.get_action_cooldown() == 0 and self.harvesters_built < self.ore_cap:
            for tp in ore_tiles:
                if pos.distance_squared(tp) <= 2 and ti >= 20:
                    if c.can_build_harvester(tp):
                        c.build_harvester(tp)
                        self.harvesters_built += 1
                        self.target = None
                        return

        # Pick target
        if self.target is None and self.harvesters_built < self.ore_cap and ore_tiles:
            best, best_d = None, 999999
            for tp in ore_tiles:
                d = pos.distance_squared(tp)
                if d < best_d:
                    best_d, best = d, tp
            self.target = best

        if self.target is None:
            # No ore visible — explore outward from core
            if c.get_move_cooldown() == 0 and self.core_pos:
                # Move away from core to find ore
                away_d = self.core_pos.direction_to(pos) if pos != self.core_pos else DIRS[0]
                for d in [away_d, away_d.rotate_left(), away_d.rotate_right()] + DIRS:
                    nxt = pos.add(d)
                    if nxt not in passable:
                        if c.get_action_cooldown() == 0 and ti >= 3:
                            try:
                                core_d = nxt.direction_to(self.core_pos)
                                if c.can_build_conveyor(nxt, core_d):
                                    c.build_conveyor(nxt, core_d)
                                    return
                            except Exception:
                                pass
                        continue
                    if c.can_move(d):
                        c.move(d)
                        return
            return

        # If adjacent to target, wait for action cooldown to build harvester
        if pos.distance_squared(self.target) <= 2:
            return

        # Navigate toward target using BFS
        bfs_d = self._bfs_step(pos, self.target, passable)
        dirs = sorted(DIRS, key=lambda d: pos.add(d).distance_squared(self.target))
        if bfs_d and bfs_d != dirs[0]:
            dirs = [bfs_d] + [d for d in dirs if d != bfs_d]

        for d in dirs:
            nxt = pos.add(d)
            if nxt not in passable and nxt != self.target:
                # Try building conveyor here so we can walk on it
                if c.get_action_cooldown() == 0 and ti >= 3:
                    try:
                        core_d = nxt.direction_to(self.core_pos) if self.core_pos else d.opposite()
                        if c.can_build_conveyor(nxt, core_d):
                            c.build_conveyor(nxt, core_d)
                            return
                    except Exception:
                        pass
                continue

            if c.get_move_cooldown() == 0 and c.can_move(d):
                # Before moving, place conveyor on current tile pointing toward core
                if c.get_action_cooldown() == 0 and ti >= 3 and self.core_pos:
                    try:
                        core_d = pos.direction_to(self.core_pos)
                        if c.can_build_conveyor(pos, core_d):
                            c.build_conveyor(pos, core_d)
                    except Exception:
                        pass
                c.move(d)
                return

            # Build conveyor on next tile if not passable
            if nxt not in passable and c.get_action_cooldown() == 0 and ti >= 3:
                try:
                    core_d = nxt.direction_to(self.core_pos) if self.core_pos else d.opposite()
                    if c.can_build_conveyor(nxt, core_d):
                        c.build_conveyor(nxt, core_d)
                        return
                except Exception:
                    pass
