"""Launcher Drop v2: Strong economy, then launch builders into enemy base.

Phase 1 (rounds 1-300): All builders do economy (harvesters + d.opposite() conveyors)
Phase 2 (round 300+): One builder walks toward enemy and builds launcher.
  Subsequent builders walk to launcher and get thrown at enemy conveyors/roads.
  Thrown builders attack enemy buildings (2 dmg for 2 Ti each hit).

Key insight: Builders can walk on ANY team's conveyors/roads. So enemy infra
IS passable as a launch target. We aim to land on enemy conveyors near their core.
"""

import sys
from collections import deque
from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]

# Marker protocol: launcher position encoded as x*100+y on tile near core
MARKER_LAUNCHER = 99999


class Player:
    def __init__(self):
        self.core_pos = None
        self.my_id = None
        self.harvesters_built = 0
        self.target = None
        self.stuck = 0
        self.last_pos = None
        self.explore_idx = 0
        self._enemy_dir = None
        self._enemy_core = None
        self.role = None  # "eco", "pioneer", "ammo"
        self.launched = False
        self.launcher_found = None  # cached launcher position
        self.spawn_count = 0  # core tracks spawns

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)
        elif t == EntityType.LAUNCHER:
            self._launcher(c)

    # ================================================================ CORE
    def _core(self, c):
        if c.get_action_cooldown() != 0:
            return
        rnd = c.get_current_round()
        units = c.get_unit_count() - 1  # exclude core
        ti = c.get_global_resources()[0]
        cost = c.get_builder_bot_cost()[0]

        # Eco phase: 3 builders
        if rnd <= 300:
            cap = 3
        else:
            # After 300: spawn more for launcher ops
            # Keep spawning ammo builders if we have resources
            cap = min(12, 3 + (rnd - 300) // 80)

        if units >= cap:
            return
        if ti < cost + 20:
            return

        pos = c.get_position()
        for d in DIRS:
            sp = pos.add(d)
            if c.can_spawn(sp):
                c.spawn_builder(sp)
                self.spawn_count += 1
                return

    # ================================================================ LAUNCHER TURRET
    def _launcher(self, c):
        """Pick up adjacent builder and throw toward enemy base."""
        if c.get_action_cooldown() != 0:
            return

        pos = c.get_position()
        enemy = self._get_enemy_core_pos(c)
        if not enemy:
            return

        # Find adjacent allied builder
        for d in DIRS:
            adj = pos.add(d)
            bot_id = c.get_tile_builder_bot_id(adj)
            if bot_id is None:
                continue
            try:
                if c.get_team(bot_id) != c.get_team():
                    continue
            except Exception:
                continue

            # Generate launch targets: prioritize tiles near enemy core
            # that are passable (enemy conveyors, roads, or their core tiles)
            targets = self._get_launch_targets(c, pos, enemy)
            for tgt in targets:
                if c.can_launch(adj, tgt):
                    print(f"LAUNCHING builder from {adj} to {tgt}!", file=sys.stderr)
                    c.launch(adj, tgt)
                    return

    def _get_launch_targets(self, c, launcher_pos, enemy_core):
        """Candidate landing positions in launcher range, sorted by proximity to enemy core.

        Scans ALL tiles within r^2=26 of launcher. can_launch will check passability.
        """
        candidates = []
        w, h = c.get_map_width(), c.get_map_height()
        for dx in range(-5, 6):
            for dy in range(-5, 6):
                tgt = Position(launcher_pos.x + dx, launcher_pos.y + dy)
                if tgt.x < 0 or tgt.x >= w or tgt.y < 0 or tgt.y >= h:
                    continue
                d2_launcher = launcher_pos.distance_squared(tgt)
                if d2_launcher > 26 or d2_launcher == 0:
                    continue
                d2_enemy = tgt.distance_squared(enemy_core)
                candidates.append((d2_enemy, tgt))
        candidates.sort()
        return [t for _, t in candidates]

    # ================================================================ BUILDER
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

        rnd = c.get_current_round()

        # Assign roles based on round and builder ID
        if self.role is None:
            if rnd <= 300:
                self.role = "eco"
            elif (self.my_id or 0) % 5 == 0:
                self.role = "pioneer"  # builds the launcher
            else:
                self.role = "ammo"  # walks to launcher to be thrown

        # Eco builders upgrade to ammo after round 500 if enough harvesters
        if self.role == "eco" and rnd > 500 and self.harvesters_built >= 3:
            if (self.my_id or 0) % 4 == 0:
                self.role = "ammo"

        # Stuck detection
        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck = 0
        self.last_pos = pos
        if self.stuck > 15:
            self.target = None
            self.stuck = 0
            self.explore_idx += 1

        # Thrown builder: attack mode
        if self.launched:
            self._attack(c, pos)
            return

        if self.role == "pioneer":
            self._pioneer(c, pos)
        elif self.role == "ammo":
            self._ammo(c, pos)
        else:
            self._eco_builder(c, pos)

    # ================================================================ ECO BUILDER
    def _eco_builder(self, c, pos):
        """Standard economy: find ore, build harvester, lay d.opposite() conveyors."""
        passable = set()
        ore_tiles = []
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e != Environment.WALL:
                passable.add(t)
                if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
                    ore_tiles.append(t)

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

        # Navigate to nearest ore
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

    # ================================================================ PIONEER
    def _pioneer(self, c, pos):
        """Walk toward enemy side and build a launcher. Use roads (cheap) to advance."""
        passable = set()
        for t in c.get_nearby_tiles():
            if c.get_tile_env(t) != Environment.WALL:
                passable.add(t)

        enemy = self._get_enemy_core_pos(c)
        if not enemy:
            self._explore(c, pos, passable)
            return

        # Check if we already have a launcher nearby
        for eid in c.get_nearby_buildings():
            try:
                if (c.get_entity_type(eid) == EntityType.LAUNCHER
                        and c.get_team(eid) == c.get_team()):
                    # Launcher exists, become ammo
                    self.role = "ammo"
                    self.launcher_found = c.get_position(eid)
                    self._ammo(c, pos)
                    return
            except Exception:
                continue

        ti = c.get_global_resources()[0]

        # Build launcher ONLY when enemy passable tiles are within throw range (r^2=26)
        # We need to find a spot where we can build launcher AND it can reach
        # enemy conveyors/roads for landing
        if self.core_pos and c.get_action_cooldown() == 0:
            # Find nearby enemy buildings -- their conveyors/roads are passable landing spots
            enemy_passable = []
            for eid in c.get_nearby_buildings():
                try:
                    if c.get_team(eid) != c.get_team():
                        etype = c.get_entity_type(eid)
                        epos = c.get_position(eid)
                        # Conveyors, roads, splitters are passable for our builders
                        if etype in (EntityType.CONVEYOR, EntityType.ROAD,
                                     EntityType.SPLITTER, EntityType.BRIDGE):
                            enemy_passable.append(epos)
                        # Core tiles are also passable? No, only allied core.
                except Exception:
                    pass
            # Only build launcher if we have enemy passable tiles within r^2=26
            # of potential launcher positions (adjacent tiles)
            can_reach = False
            if enemy_passable:
                for d in DIRS:
                    lp = pos.add(d)
                    for ep in enemy_passable:
                        if lp.distance_squared(ep) <= 26:
                            can_reach = True
                            break
                    if can_reach:
                        break
            if can_reach and ti >= c.get_launcher_cost()[0] + 30:
                for d in DIRS:
                    lp = pos.add(d)
                    if c.can_build_launcher(lp):
                        print(f"Building launcher at {lp}!", file=sys.stderr)
                        c.build_launcher(lp)
                        self.launcher_found = lp
                        # Place marker near core so ammo builders can find it
                        self.role = "ammo"
                        return

        # Navigate toward enemy using roads (cheaper than conveyors)
        self._nav_with_roads(c, pos, enemy, passable)

    # ================================================================ AMMO BUILDER
    def _ammo(self, c, pos):
        """Walk to the launcher and stand adjacent to be thrown."""
        passable = set()
        for t in c.get_nearby_tiles():
            if c.get_tile_env(t) != Environment.WALL:
                passable.add(t)

        # Look for launcher in vision
        for eid in c.get_nearby_buildings():
            try:
                if (c.get_entity_type(eid) == EntityType.LAUNCHER
                        and c.get_team(eid) == c.get_team()):
                    lpos = c.get_position(eid)
                    self.launcher_found = lpos
                    if pos.distance_squared(lpos) <= 2:
                        # Adjacent to launcher, wait to be thrown
                        return
                    # Walk toward launcher
                    self._nav(c, pos, lpos, passable)
                    return
            except Exception:
                continue

        # If we know launcher position from cache, head there
        if self.launcher_found:
            self._nav(c, pos, self.launcher_found, passable)
            return

        # No launcher found -- do eco while waiting
        self._eco_builder(c, pos)

    # ================================================================ ATTACK (thrown builder)
    def _attack(self, c, pos):
        """Thrown builder: attack enemy buildings, prioritize core."""
        w, h = c.get_map_width(), c.get_map_height()
        ti = c.get_global_resources()[0]

        # Attack building on our tile
        if c.get_action_cooldown() == 0:
            bid = c.get_tile_building_id(pos)
            if bid is not None:
                try:
                    if c.get_team(bid) != c.get_team():
                        if ti >= 2 and c.can_fire(pos):
                            c.fire(pos)
                            return
                except Exception:
                    pass

        # Find adjacent enemy buildings to move onto
        enemy_core_dir = None
        enemy_building_dir = None
        for d in DIRS:
            ap = pos.add(d)
            if ap.x < 0 or ap.x >= w or ap.y < 0 or ap.y >= h:
                continue
            abid = c.get_tile_building_id(ap)
            if abid is not None:
                try:
                    if c.get_team(abid) != c.get_team():
                        etype = c.get_entity_type(abid)
                        if etype == EntityType.CORE:
                            enemy_core_dir = d
                        elif enemy_building_dir is None:
                            enemy_building_dir = d
                except Exception:
                    pass

        # Prioritize core, then any building
        move_dir = enemy_core_dir or enemy_building_dir
        if move_dir and c.get_move_cooldown() == 0 and c.can_move(move_dir):
            c.move(move_dir)
            return

        # Navigate toward enemy core
        enemy = self._get_enemy_core_pos(c)
        if enemy:
            d = pos.direction_to(enemy)
            if d != Direction.CENTRE:
                for try_d in [d, d.rotate_left(), d.rotate_right(),
                              d.rotate_left().rotate_left(),
                              d.rotate_right().rotate_right()]:
                    if c.get_move_cooldown() == 0 and c.can_move(try_d):
                        c.move(try_d)
                        return
                    # Build road to navigate in enemy territory
                    nxt = pos.add(try_d)
                    if nxt.x < 0 or nxt.x >= w or nxt.y < 0 or nxt.y >= h:
                        continue
                    if c.get_action_cooldown() == 0 and ti >= c.get_road_cost()[0] + 2:
                        if c.can_build_road(nxt):
                            c.build_road(nxt)
                            return

    # ================================================================ NAVIGATION
    def _nav(self, c, pos, target, passable):
        """Navigate toward target, building conveyors with d.opposite() facing."""
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

    def _nav_with_roads(self, c, pos, target, passable):
        """Navigate using roads instead of conveyors (cheaper, no eco impact)."""
        dirs = self._rank(pos, target)
        bfs_dir = self._bfs_step(pos, target, passable)
        if bfs_dir is not None and bfs_dir != dirs[0]:
            dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]

        w, h = c.get_map_width(), c.get_map_height()
        for d in dirs:
            nxt = pos.add(d)
            if nxt.x < 0 or nxt.x >= w or nxt.y < 0 or nxt.y >= h:
                continue
            # Try to move first
            if c.get_move_cooldown() == 0 and c.can_move(d):
                c.move(d)
                return
            # Build road (1 Ti, very cheap)
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                rc = c.get_road_cost()[0]
                if ti >= rc + 5:
                    if c.can_build_road(nxt):
                        c.build_road(nxt)
                        return

    def _explore(self, c, pos, passable):
        idx = ((self.my_id or 0) * 3 + self.explore_idx
               + c.get_current_round() // 150) % len(DIRS)
        d = DIRS[idx]
        dx, dy = d.delta()
        far = Position(pos.x + dx * 15, pos.y + dy * 15)
        self._nav(c, pos, far, passable)

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
        count = 0
        while queue:
            cur, fd = queue.popleft()
            count += 1
            if count > 200:
                break
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
