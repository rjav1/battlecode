"""Realistic 1500 Elo Economy opponent -- models One More Time / KCPC-B.

Key behaviors modeled from nemesis replays:
- 40 builders (near unit cap of 49) for rapid map coverage
- d.opposite() conveyors forming connected chains to core
- Spends EVERYTHING: reserve = cost+2 only
- Builds harvesters on ALL ore types (Ti AND Ax)
- No military at all -- pure economy dominance
- Target: 40K+ Ti on settlement-class maps
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

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)

    # ── Core: spawn aggressively to 40 builders ──

    def _core(self, c):
        if c.get_action_cooldown() != 0:
            return

        units = c.get_unit_count() - 1  # exclude core
        rnd = c.get_current_round()

        # Aggressive ramp: 5 by r20, 10 by r50, 20 by r100, 40 by r300
        if rnd <= 20:
            cap = 5
        elif rnd <= 50:
            cap = 10
        elif rnd <= 100:
            cap = 20
        elif rnd <= 200:
            cap = 30
        else:
            cap = 40

        if units >= cap:
            return

        ti = c.get_global_resources()[0]
        cost = c.get_builder_bot_cost()[0]

        # Minimal reserve -- spend everything
        if ti < cost + 2:
            return

        pos = c.get_position()
        # Try to spawn toward nearest visible ore for first few builders
        best_sp = None
        best_dist = 10**9
        for d in DIRS:
            sp = pos.add(d)
            if c.can_spawn(sp):
                if best_sp is None:
                    best_sp = sp
                # Check nearby ore to bias spawn direction
                for t in c.get_nearby_tiles():
                    env = c.get_tile_env(t)
                    if env in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
                        if c.get_tile_building_id(t) is None:
                            dist = sp.distance_squared(t)
                            if dist < best_dist:
                                best_dist = dist
                                best_sp = sp

        if best_sp is not None:
            c.spawn_builder(best_sp)

    # ── Builder: find ore, build harvester, lay conveyors ──

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

        if self.stuck > 10:
            self.target = None
            self.stuck = 0
            self.explore_idx += 1

        # Scan for ore
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
                    self.target = None
                    return

        # Target nearest visible ore
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
        """Navigate toward target, building d.opposite() conveyors."""
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
        rnd = c.get_current_round()
        rotation = rnd // 100
        idx = ((self.my_id or 0) * 7 + self.explore_idx + rotation) % len(DIRS)
        d = DIRS[idx]
        dx, dy = d.delta()
        far = Position(pos.x + dx * 20, pos.y + dy * 20)
        self._nav(c, pos, far, passable)

    def _best_adj_ore(self, c, pos):
        """Adjacent ore: prefer Ti, then Ax, prefer closer to core."""
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
