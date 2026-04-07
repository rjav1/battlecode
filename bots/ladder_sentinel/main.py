"""Ladder Sentinel bot — models Polska Gurom's sentinel-heavy defense.

Architecture:
- Core spawns up to 5 builders total
- Builders 1-3: pure economy (d.opposite() conveyors, harvest ore)
- Builder 4 (round 300+): sentinel builder — places sentinels facing enemy
- Builder 5 (round 500+): second sentinel builder
- Sentinel ammo via splitter: harvester -> conveyor -> splitter -> conveyor -> sentinel
- Sentinels placed 4-5 tiles from core toward enemy direction
- Symmetry detection to determine enemy direction
"""

from collections import deque
from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]

SENTINEL_CAP = 6   # max sentinels to build total


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
        self._enemy_dir = None
        # Sentinel builder state
        self.role = None          # "miner" | "sentinel_builder"
        self.sentinel_plan = []   # list of dicts: sent_pos, sent_dir, ammo_chain
        self.sentinel_idx = 0     # which sentinel we're working on
        self.phase = "sentinel"   # "sentinel" | "ammo" | "done"
        self.ammo_chain_idx = 0

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

        rnd = c.get_current_round()
        units = c.get_unit_count() - 1  # exclude core

        # Builder cap: ramp up like smart_eco, 2 will transition to sentinel builders
        if rnd <= 30:    cap = 4
        elif rnd <= 100: cap = 6
        elif rnd <= 200: cap = 7
        else:            cap = 8
        if units >= cap:
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
        if self.stuck > 12:
            self.target = None
            self.stuck = 0
            self.explore_idx += 1

        # Assign role: builder 4 (id%5==3) becomes sentinel builder at r300
        # builder 5 (id%5==4) becomes sentinel builder at r500
        if self.role is None:
            slot = self.my_id % 5
            if slot == 3:
                self.role = "sentinel_builder_early"  # activates at r300
            elif slot == 4:
                self.role = "sentinel_builder_late"   # activates at r500
            else:
                self.role = "miner"

        if self.role == "sentinel_builder_early" and rnd >= 300:
            self._do_sentinel_work(c, pos, rnd)
        elif self.role == "sentinel_builder_late" and rnd >= 500:
            self._do_sentinel_work(c, pos, rnd)
        else:
            self._mine(c, pos)

    # ------------------------------------------------------------------ Mining
    def _mine(self, c, pos):
        passable = set()
        ore_tiles = []
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e != Environment.WALL:
                passable.add(t)
                if e in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
                    if c.get_tile_building_id(t) is None:
                        ore_tiles.append(t)

        if c.get_action_cooldown() == 0:
            ore = self._best_adj_ore(c, pos)
            if ore is not None:
                ti = c.get_global_resources()[0]
                if ti >= c.get_harvester_cost()[0] + 5:
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

    # ------------------------------------------------------------------ Sentinel building
    def _do_sentinel_work(self, c, pos, rnd):
        if not self._enemy_dir:
            self._detect_enemy_dir(c)
        if not self._enemy_dir or not self.core_pos:
            self._mine(c, pos)
            return

        if not self.sentinel_plan:
            self._plan_sentinels()

        if self.sentinel_idx >= len(self.sentinel_plan):
            self.role = "miner"
            self._mine(c, pos)
            return

        s = self.sentinel_plan[self.sentinel_idx]
        sent_pos = s["sent_pos"]
        sent_dir = s["sent_dir"]
        ammo_chain = s["ammo_chain"]

        if self.phase == "sentinel":
            self._place_sentinel(c, pos, sent_pos, sent_dir)
        elif self.phase == "ammo":
            self._place_ammo_chain(c, pos, ammo_chain)
        else:
            self.sentinel_idx += 1
            self.phase = "sentinel"
            self.ammo_chain_idx = 0

    def _place_sentinel(self, c, pos, sent_pos, sent_dir):
        passable = set()
        for t in c.get_nearby_tiles():
            if c.get_tile_env(t) != Environment.WALL:
                passable.add(t)

        if c.is_in_vision(sent_pos):
            bid = c.get_tile_building_id(sent_pos)
            if bid is not None:
                self.phase = "ammo"
                return

        if pos.distance_squared(sent_pos) > 2:
            self._nav(c, pos, sent_pos, passable)
            return

        if c.get_action_cooldown() != 0:
            return

        ti = c.get_global_resources()[0]
        if ti < c.get_sentinel_cost()[0] + 30:
            return

        if c.can_build_sentinel(sent_pos, sent_dir):
            c.build_sentinel(sent_pos, sent_dir)
            self.phase = "ammo"
        else:
            # Try all directions except facing toward ammo input
            for d in DIRS:
                if c.can_build_sentinel(sent_pos, d):
                    c.build_sentinel(sent_pos, d)
                    self.phase = "ammo"
                    return

    def _place_ammo_chain(self, c, pos, ammo_chain):
        passable = set()
        for t in c.get_nearby_tiles():
            if c.get_tile_env(t) != Environment.WALL:
                passable.add(t)

        for i, (cp, cd) in enumerate(ammo_chain):
            if not c.is_in_vision(cp):
                self._nav(c, pos, cp, passable)
                return
            bid = c.get_tile_building_id(cp)
            if bid is not None:
                continue  # already placed
            # Need to place this piece
            if pos.distance_squared(cp) > 2:
                self._nav(c, pos, cp, passable)
                return
            if c.get_action_cooldown() != 0:
                return
            ti = c.get_global_resources()[0]
            is_splitter = (i == len(ammo_chain) - 1)
            if is_splitter:
                cost = c.get_splitter_cost()[0]
                if ti >= cost + 5 and c.can_build_splitter(cp, cd):
                    c.build_splitter(cp, cd)
            else:
                cost = c.get_conveyor_cost()[0]
                if ti >= cost + 5 and c.can_build_conveyor(cp, cd):
                    c.build_conveyor(cp, cd)
            return

        # All placed
        self.phase = "done"

    def _plan_sentinels(self):
        """Plan up to SENTINEL_CAP sentinels with ammo chains.

        Sentinels placed 4-5 tiles from core toward enemy, spread perpendicular.
        Each gets: harvester-chain conveyor -> splitter -> 1 conveyor -> sentinel.
        """
        core = self.core_pos
        ed = self._enemy_dir
        w, h = self._w, self._h

        perp_l = ed.rotate_left().rotate_left()
        perp_r = ed.rotate_right().rotate_right()

        # Candidate positions: center column + perpendicular offsets
        slots = [
            (4, 0, None),     # 4 fwd, center
            (4, 2, perp_l),   # 4 fwd, 2 left
            (4, 2, perp_r),   # 4 fwd, 2 right
            (5, 0, None),     # 5 fwd, center
            (5, 3, perp_l),   # 5 fwd, 3 left
            (5, 3, perp_r),   # 5 fwd, 3 right
        ]

        edx, edy = ed.delta()
        plan = []

        for fwd, side, side_dir in slots:
            if len(plan) >= SENTINEL_CAP:
                break
            p = Position(core.x + edx * fwd, core.y + edy * fwd)
            if side > 0 and side_dir:
                sdx, sdy = side_dir.delta()
                p = Position(p.x + sdx * side, p.y + sdy * side)

            if not (0 <= p.x < w and 0 <= p.y < h):
                continue

            sent_dir = ed  # face enemy

            # Ammo chain: from 1 tile past core toward sentinel, ending with splitter
            # Splitter sits directly behind sentinel, faces toward sentinel (ed)
            # Chain: core+1 fwd -> ... -> splitter at sent_pos.add(ed.opposite())
            splitter_pos = p.add(ed.opposite())
            if not (0 <= splitter_pos.x < w and 0 <= splitter_pos.y < h):
                continue

            chain = self._make_chain(core, splitter_pos, ed, w, h)
            if chain:
                plan.append({
                    "sent_pos": p,
                    "sent_dir": sent_dir,
                    "ammo_chain": chain,
                })

        self.sentinel_plan = plan

    def _make_chain(self, core, splitter_pos, sent_dir, w, h):
        """Walk from core toward splitter_pos, building conveyor chain.

        Conveyors face back toward core (d.opposite() of step direction).
        Last element is the splitter facing sent_dir (outputs toward sentinel).
        Returns list of (pos, facing_dir) or empty if no valid path.
        """
        chain = []
        cur = core
        visited = {cur}

        for _ in range(12):
            step_dir = cur.direction_to(splitter_pos)
            if step_dir == Direction.CENTRE:
                break
            nxt = cur.add(step_dir)
            if not (0 <= nxt.x < w and 0 <= nxt.y < h):
                break
            if nxt in visited:
                break
            visited.add(nxt)

            if nxt == splitter_pos:
                chain.append((nxt, sent_dir))
                break
            else:
                chain.append((nxt, step_dir.opposite()))
            cur = nxt

        return chain

    # ------------------------------------------------------------------ Enemy detection
    def _detect_enemy_dir(self, c):
        """Symmetry-based enemy direction detection (from buzzing bot)."""
        if not self.core_pos:
            return
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

    # ------------------------------------------------------------------ Navigation
    def _nav(self, c, pos, target, passable):
        dirs = self._rank(pos, target)
        bfs_dir = self._bfs_step(pos, target, passable)
        if bfs_dir is not None and bfs_dir != dirs[0]:
            dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]

        ti = c.get_global_resources()[0]
        cc = c.get_conveyor_cost()[0]
        for d in dirs:
            nxt = pos.add(d)
            if c.get_action_cooldown() == 0 and ti >= cc + 5:
                face = d.opposite()
                if c.can_build_conveyor(nxt, face):
                    c.build_conveyor(nxt, face)
                    return
            if c.get_move_cooldown() == 0 and c.can_move(d):
                c.move(d)
                return

        if c.get_action_cooldown() == 0:
            rc = c.get_road_cost()[0]
            if ti >= rc + 5:
                for d in dirs:
                    nxt = pos.add(d)
                    if 0 <= nxt.x < (self._w or 50) and 0 <= nxt.y < (self._h or 50):
                        if c.can_build_road(nxt):
                            c.build_road(nxt)
                            return

    def _explore(self, c, pos, passable):
        rnd = c.get_current_round()
        rotation = rnd // 150
        idx = ((self.my_id or 0) * 3 + self.explore_idx + rotation) % len(DIRS)
        d = DIRS[idx]
        dx, dy = d.delta()
        far = Position(pos.x + dx * 15, pos.y + dy * 15)
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
