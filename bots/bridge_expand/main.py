"""Bridge-first expansion bot v3.

Strategy: d.opposite() conveyors for reliable chains, aggressive bridge placement
to shortcut long chains. After building harvester far from core, insert bridges
along the conveyor chain every 3 tiles. Bridges teleport resources up to dist^2<=9.

Economy: 4 builders, d.opposite() conveyors, bridge shortcuts, target 5-10 bridges/game.
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
        self.bridges_built = 0
        self._enemy_dir = None
        # Chain-back state: after harvester, walk back to core laying bridges
        self.chain_back = False
        self.chain_steps = 0
        self.chain_conveyors = 0  # conveyors passed since last bridge
        # Track positions to bridge
        self.path_history = []  # recent positions for bridge targeting

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)

    # ---------------------------------------------------------------- Core
    def _core(self, c):
        if c.get_action_cooldown() != 0:
            return
        units = c.get_unit_count() - 1
        rnd = c.get_current_round()
        if rnd <= 20:
            cap = 4
        elif rnd <= 80:
            cap = 4
        elif rnd <= 200:
            cap = 6
        elif rnd <= 500:
            cap = 8
        else:
            cap = 10
        pos = c.get_position()
        vis_harv = 0
        for eid in c.get_nearby_buildings():
            try:
                if (c.get_entity_type(eid) == EntityType.HARVESTER
                        and c.get_team(eid) == c.get_team()):
                    vis_harv += 1
            except Exception:
                pass
        econ_cap = vis_harv * 2 + 4
        cap = min(cap, econ_cap)
        if units >= cap:
            return
        ti = c.get_global_resources()[0]
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

        # Track position history
        if not self.path_history or self.path_history[-1] != pos:
            self.path_history.append(pos)
            if len(self.path_history) > 30:
                self.path_history = self.path_history[-20:]

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
            self.chain_back = False

        # Scan vision
        ore_tiles = []
        passable = set()
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e != Environment.WALL:
                passable.add(t)
                if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
                    ore_tiles.append(t)

        # Chain-back mode: walk toward core, placing bridges to shortcut chain
        if self.chain_back and self.core_pos:
            if self._chain_back_mode(c, pos, passable):
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
                    # If far from core, enter chain-back mode to bridge
                    if (self.core_pos
                            and ore.distance_squared(self.core_pos) > 25
                            and self.bridges_built < 12):
                        self.chain_back = True
                        self.chain_steps = 0
                        self.chain_conveyors = 0
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

    # -------------------------------------------------------- Chain-back mode
    def _chain_back_mode(self, c, pos, passable):
        """Walk back toward core. Every 3 tiles of existing conveyors,
        place a bridge to shortcut the chain."""
        if not self.core_pos:
            self.chain_back = False
            return False

        if pos.distance_squared(self.core_pos) <= 8:
            self.chain_back = False
            return False

        self.chain_steps += 1
        if self.chain_steps > 50:
            self.chain_back = False
            return False

        ti = c.get_global_resources()[0]

        # Count conveyors we're passing over
        bid = c.get_tile_building_id(pos)
        if bid is not None:
            try:
                if (c.get_entity_type(bid) == EntityType.CONVEYOR
                        and c.get_team(bid) == c.get_team()):
                    self.chain_conveyors += 1
            except Exception:
                pass

        # Every 3 conveyors, try to place a bridge shortcut
        if (c.get_action_cooldown() == 0
                and self.chain_conveyors >= 3):
            bc = c.get_bridge_cost()[0]
            if ti >= bc + 15:
                if self._place_chain_bridge(c, pos):
                    self.chain_conveyors = 0
                    return True

        # Move toward core (walk on existing conveyors/roads)
        dirs = self._rank(pos, self.core_pos)
        if c.get_move_cooldown() == 0:
            for d in dirs:
                if c.can_move(d):
                    c.move(d)
                    return True

        # If can't move, build road to walk on
        if c.get_action_cooldown() == 0:
            rc = c.get_road_cost()[0]
            w, h = c.get_map_width(), c.get_map_height()
            if ti >= rc + 3:
                for d in dirs:
                    rp = pos.add(d)
                    if rp.x < 0 or rp.x >= w or rp.y < 0 or rp.y >= h:
                        continue
                    if c.can_build_road(rp):
                        c.build_road(rp)
                        return True

        # Try bridge to jump over obstacles
        if c.get_action_cooldown() == 0:
            bc = c.get_bridge_cost()[0]
            if ti >= bc + 15:
                if self._place_chain_bridge(c, pos):
                    self.chain_conveyors = 0
                    return True

        return True  # Stay in chain-back mode

    def _place_chain_bridge(self, c, pos):
        """Place a bridge that shortcuts toward core."""
        if not self.core_pos:
            return False

        core_dir = pos.direction_to(self.core_pos)
        if core_dir == Direction.CENTRE:
            return False

        best_bp = None
        best_bt = None
        best_dist = pos.distance_squared(self.core_pos)

        for bd in DIRS:
            bp = pos.add(bd)
            # Try targets 1-3 tiles toward core from bridge
            for td in [core_dir, core_dir.rotate_left(), core_dir.rotate_right(),
                       core_dir.rotate_left().rotate_left(),
                       core_dir.rotate_right().rotate_right()]:
                for step in range(1, 4):
                    tdx, tdy = td.delta()
                    bt = Position(bp.x + tdx * step, bp.y + tdy * step)
                    if bp.distance_squared(bt) > 9:
                        continue
                    if c.can_build_bridge(bp, bt):
                        dist = bt.distance_squared(self.core_pos)
                        if dist < best_dist:
                            best_dist = dist
                            best_bp = bp
                            best_bt = bt

        if best_bp and best_bt:
            c.build_bridge(best_bp, best_bt)
            self.bridges_built += 1
            return True
        return False

    # -------------------------------------------------------- Navigation
    def _nav(self, c, pos, target, passable):
        """Navigate toward target, building d.opposite() conveyors for reliable chains."""
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
                    # Destroy allied road so we can place conveyor
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

        # Bridge fallback for impassable terrain
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
                        for bd in DIRS:
                            bp = pos.add(bd)
                            if c.can_build_bridge(bp, bt):
                                c.build_bridge(bp, bt)
                                self.bridges_built += 1
                                return

    def _explore(self, c, pos, passable):
        idx = ((self.my_id or 0) * 3 + self.explore_idx
               + c.get_current_round() // 150) % len(DIRS)
        d = DIRS[idx]
        dx, dy = d.delta()
        far = Position(pos.x + dx * 15, pos.y + dy * 15)
        self._nav(c, pos, far, passable)

    # -------------------------------------------------------- Helpers
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
