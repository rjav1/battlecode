"""v42: Bridge-first harvester delivery — chain-join > core bridge for ALL harvesters.
Ax tiebreaker stuck detection (give up after 5 rounds stuck).

v39: Late-game Ax tiebreaker — one builder builds Ax harvester+foundry at round 1800+.

v37: Armed sentinel + attacker infra targeting + bridge shortcut.
- Splitter+branch+sentinel ammo at round 1000+ for late-game area denial.
- Attacker targets enemy conveyors/harvesters instead of core (500HP).
- Bridge shortcut for harvesters 3-5 tiles from core — direct resource delivery.

v36: Fix econ_cap ceiling — expand=15, balanced=12, tight=10. Expand cap 16.
Also enables gunners on tight maps (round 60) — was completely blocked before.

v34: Raise tight builder cap 7->15 for arena ore coverage.
v33: Cold builder cap 10->15, tight early barriers.
v31: Earlier gunner on expand maps for galaxy defense.
v30: Spawn first builder toward nearest ore — faster first harvester.
v29: Fix cold regression — marker only placed at distance > 2 (not adjacent).
v28: Marker-based ore claiming — prevents duplicate harvester targeting.
v27: Ore-density-aware maze detection for butterfly fragmented map.
v26: Nearest-ore scoring on tight maps for faster ore scaling.
v25: Distance-based explore Ti reserve + time-based builder ramp.
v24: Extend sector-based exploration to balanced maps.
v23: Sector-based exploration on large maps.
v22: Wall-density-adaptive ore scoring.
d.opposite() conveyors, BFS nav, builder scaling, bridge fallback,
gunner placement, attacker raider, symmetry detection, barriers.
"""

from collections import deque
from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]


def _perp_left(d):
    return d.rotate_left().rotate_left()


def _perp_right(d):
    return d.rotate_right().rotate_right()


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
        self.is_attacker = False
        self.fixing_chain = False
        self.fix_path = []
        self.fix_idx = 0
        self.gunner_placed = 0  # count of gunners built
        self._wall_density = None
        self._ore_density = None  # ore tiles / total tiles in vision (ore-rich map detection)
        self._claimed_pos = None    # Position of our placed claim marker
        self._marker_placed = False # Whether we've placed the marker this target
        self._sentinel_step = 0        # 0=find chain, 1=walk to it, 2=destroy+build splitter, 3=build branch, 4=build sentinel, 5=done
        self._sentinel_chain_pos = None  # position of the conveyor to replace
        self._sentinel_chain_dir = None  # facing direction of that conveyor
        self._sentinel_branch_dir = None # perpendicular direction for branch
        self._sentinel_positions = {}    # planned positions: splitter, branch, sentinel
        self._bridge_target = None       # ore tile needing a bridge shortcut next round

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

    def _core(self, c):
        # Detect map size on first round
        if not hasattr(self, 'map_mode'):
            w, h = c.get_map_width(), c.get_map_height()
            area = w * h
            if area <= 625:      # 25x25 or smaller
                self.map_mode = "tight"
            elif area >= 1600:   # 40x40 or larger
                self.map_mode = "expand"
            else:
                self.map_mode = "balanced"

        if c.get_action_cooldown() != 0:
            return
        units = c.get_unit_count() - 1
        rnd = c.get_current_round()
        if self.map_mode == "tight":
            cap = 3 if rnd <= 20 else (7 if rnd <= 100 else 15)
        elif self.map_mode == "expand":
            cap = 3 if rnd <= 30 else (6 if rnd <= 150 else (12 if rnd <= 400 else 16))
        else:  # balanced
            cap = 3 if rnd <= 25 else (5 if rnd <= 100 else (8 if rnd <= 300 else 10))
        pos = c.get_position()
        vis_harv = 0
        for eid in c.get_nearby_buildings():
            try:
                if (c.get_entity_type(eid) == EntityType.HARVESTER
                        and c.get_team(eid) == c.get_team()):
                    vis_harv += 1
            except Exception:
                pass
        if self.map_mode == "expand":
            time_floor = min(8 + rnd // 200, 15)
        elif self.map_mode == "balanced":
            time_floor = min(6 + rnd // 150, 12)
        else:
            time_floor = min(6 + rnd // 200, 10)
        econ_cap = max(time_floor, vis_harv * 3 + 4)
        cap = min(cap, econ_cap)
        if units >= cap:
            return
        ti = c.get_global_resources()[0]
        cost = c.get_builder_bot_cost()[0]
        if ti < cost + 2:
            return
        # Spawn first builders toward nearest visible ore for faster harvester placement.
        # Only bias when ore is very close (r²<=9, within 3 tiles) — far ore is
        # unreliable on maps with walls between core and ore clusters (e.g. cold).
        best_ore_dir = None
        if units == 0:  # only the very first builder
            best_dist = 10**9
            for tile in c.get_nearby_tiles():
                if c.get_tile_env(tile) in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
                    dist = pos.distance_squared(tile)
                    if dist <= 36:  # within vision range r²=36
                        d = pos.direction_to(tile)
                        if d != Direction.CENTRE and dist < best_dist:
                            best_dist = dist
                            best_ore_dir = d
        if best_ore_dir:
            spawn_dirs = [best_ore_dir] + [d for d in DIRS if d != best_ore_dir]
        else:
            spawn_dirs = DIRS
        for d in spawn_dirs:
            sp = pos.add(d)
            if c.can_spawn(sp):
                c.spawn_builder(sp)
                return

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

    def _gunner(self, c):
        if c.get_action_cooldown() != 0 or c.get_ammo_amount() < 2:
            return
        target = c.get_gunner_target()
        if target and c.can_fire(target):
            c.fire(target)

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
        if not hasattr(self, 'map_mode'):
            w, h = c.get_map_width(), c.get_map_height()
            area = w * h
            if area <= 625:
                self.map_mode = "tight"
            elif area >= 1600:
                self.map_mode = "expand"
            else:
                self.map_mode = "balanced"
        map_mode = self.map_mode
        if self.stuck > 12:
            self.target = None
            self.stuck = 0
            self.explore_idx += 1

        # Scan vision
        ore_tiles = []
        passable = set()
        wall_count = 0
        total_count = 0
        total_ore_count = 0  # includes occupied ore tiles
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            total_count += 1
            if e == Environment.WALL:
                wall_count += 1
            else:
                passable.add(t)
                if e in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
                    total_ore_count += 1
                    bid = c.get_tile_building_id(t)
                    if bid is None:
                        ore_tiles.append(t)
                    else:
                        try:
                            if c.get_entity_type(bid) == EntityType.MARKER:
                                ore_tiles.append(t)  # marker doesn't block ore
                        except Exception:
                            pass  # real building or enemy — skip

        rnd = c.get_current_round()

        # Lock in wall density after round 5 (builder has moved, better sample)
        if self._wall_density is None and rnd > 5 and total_count > 0:
            self._wall_density = wall_count / total_count
        # Lock in ore density at round 5 (same as wall density — snapshot near core)
        # High ore density early = ore-rich map like butterfly (15% ore tiles)
        if self._ore_density is None and rnd > 5 and total_count > 0:
            self._ore_density = total_ore_count / total_count

        # Early barrier anti-rush: builder places 1-2 barriers near core
        # Tight maps: second+ builder (id%5!=0) places barrier as first action
        # Other maps: wait for 1+ harvester first
        early_barrier_ok = (
            (map_mode == "tight" and rnd >= 5 and (self.my_id or 0) % 5 != 0)
            or self.harvesters_built >= 1
        )
        if (rnd <= 30 and self.core_pos
                and early_barrier_ok
                and not hasattr(self, '_early_barriers')
                and c.get_action_cooldown() == 0
                and pos.distance_squared(self.core_pos) <= 18):
            if not hasattr(self, '_early_barrier_count'):
                self._early_barrier_count = 0
            if self._early_barrier_count < 2:
                ti = c.get_global_resources()[0]
                bc = c.get_barrier_cost()[0]
                barrier_reserve = 5 if map_mode == "tight" else 20
                if ti >= bc + barrier_reserve:
                    enemy_dir = self._get_enemy_direction(c)
                    if enemy_dir:
                        edx, edy = enemy_dir.delta()
                        perp_l = enemy_dir.rotate_left().rotate_left()
                        perp_r = enemy_dir.rotate_right().rotate_right()
                        candidates = []
                        for dist in (2, 3):
                            cx = self.core_pos.x + edx * dist
                            cy = self.core_pos.y + edy * dist
                            center = Position(cx, cy)
                            candidates.append(center)
                            for pd in (perp_l, perp_r):
                                pdx, pdy = pd.delta()
                                candidates.append(Position(cx + pdx, cy + pdy))
                        for bp in candidates:
                            if pos.distance_squared(bp) <= 2:
                                try:
                                    if c.can_build_barrier(bp):
                                        c.build_barrier(bp)
                                        self._early_barrier_count += 1
                                        if self._early_barrier_count >= 2:
                                            self._early_barriers = True
                                        return
                                except Exception:
                                    pass
            else:
                self._early_barriers = True

        # Bridge shortcut: after building harvester, bridge to nearest infra or core
        # Priority: chain-join (nearest allied conveyor/bridge closer to core) > core tile
        if (self._bridge_target and self.core_pos
                and c.get_action_cooldown() == 0):
            ore = self._bridge_target
            built = False
            ti = c.get_global_resources()[0]
            bc = c.get_bridge_cost()[0]
            if ti >= bc + 5 and ore.distance_squared(self.core_pos) > 9:
                # First: bridge to nearest allied chain tile closer to core
                my_team = c.get_team()
                best_chain = None
                best_chain_dist = 10**9
                for eid in c.get_nearby_buildings():
                    try:
                        if (c.get_entity_type(eid) in (EntityType.CONVEYOR, EntityType.SPLITTER, EntityType.BRIDGE)
                                and c.get_team(eid) == my_team):
                            epos = c.get_position(eid)
                            if epos.distance_squared(self.core_pos) < ore.distance_squared(self.core_pos):
                                d = ore.distance_squared(epos)
                                if d < best_chain_dist:
                                    best_chain = epos
                                    best_chain_dist = d
                    except Exception:
                        pass
                if best_chain:
                    for bd in DIRS:
                        bp = ore.add(bd)
                        try:
                            if c.can_build_bridge(bp, best_chain):
                                c.build_bridge(bp, best_chain)
                                built = True
                                break
                        except Exception:
                            pass
                # Fallback: bridge to core tile
                if not built:
                    cx, cy = self.core_pos.x, self.core_pos.y
                    core_tiles = [Position(cx + dx, cy + dy)
                                  for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
                    for ct in sorted(core_tiles, key=lambda t: ore.distance_squared(t)):
                        for bd in DIRS:
                            bp = ore.add(bd)
                            try:
                                if c.can_build_bridge(bp, ct):
                                    c.build_bridge(bp, ct)
                                    built = True
                                    break
                            except Exception:
                                pass
                        if built:
                            break
            self._bridge_target = None
            if built:
                return

        # Attacker assignment: after round 500, 4+ harvesters, id%6==5
        if (not self.is_attacker and rnd > 500
                and self.harvesters_built >= 4
                and (self.my_id or 0) % 6 == 5):
            self.is_attacker = True
        if self.is_attacker:
            self._attack(c, pos, passable)
            return

        # Gunner builder: id%5==1, timing varies by map mode
        map_mode = getattr(self, 'map_mode', 'balanced')
        gunner_round = 30 if map_mode == "tight" else (120 if map_mode == "balanced" else 150)
        harv_req = 1 if map_mode == "tight" else 3
        if ((self.my_id or 0) % 5 == 1 and rnd > gunner_round
                and self.harvesters_built >= harv_req and self.core_pos
                and self.gunner_placed < 3
                and c.get_global_resources()[0] >= 20):
            if self._place_gunner(c, pos):
                return

        # Armed sentinel: splice splitter+branch+sentinel off existing chain
        if (not self.is_attacker
                and self._sentinel_step < 5
                and rnd >= 1000
                and self.harvesters_built >= 5
                and self.core_pos
                and map_mode != "tight"
                and c.get_global_resources()[0] >= 70):
            if self._place_armed_sentinel(c, pos):
                return

        # Late-game Ax tiebreaker: one builder seeks Ax ore at round 1800+
        if (not self.is_attacker
                and rnd >= 1800
                and (self.my_id or 0) % 6 == 2
                and not hasattr(self, '_ax_done')
                and self.core_pos):
            if self._build_ax_tiebreaker(c, pos):
                return

        # Barrier placement near core
        if (rnd >= 80 and self.core_pos
                and pos.distance_squared(self.core_pos) <= 20
                and c.get_action_cooldown() == 0
                and c.get_global_resources()[0] >= 50):
            if self._build_barriers(c, pos):
                return

        # Chain-fix mode: walk back fixing conveyors
        if self.fixing_chain and self.core_pos:
            self._fix_chain(c, pos)
            return

        # Build harvester on adjacent ore
        if c.get_action_cooldown() == 0:
            ore = self._best_adj_ore(c, pos)
            if ore is not None:
                ti = c.get_global_resources()[0]
                if ti >= c.get_harvester_cost()[0] + 5:
                    c.build_harvester(ore)
                    self.harvesters_built += 1
                    self.target = None
                    self._claimed_pos = None
                    self._marker_placed = False
                    self._bridge_target = ore  # attempt bridge shortcut next round
                    # Chain-fix for first 2 harvesters if path is winding
                    if (self.core_pos and len(self.fix_path) >= 4
                            and self.harvesters_built <= 2):
                        changes = 0
                        for i in range(1, len(self.fix_path) - 1):
                            d1 = self.fix_path[i-1].direction_to(self.fix_path[i])
                            d2 = self.fix_path[i].direction_to(self.fix_path[i+1])
                            if d1 != d2:
                                changes += 1
                        if changes >= 3:
                            self.fixing_chain = True
                            self.fix_idx = len(self.fix_path) - 1
                        else:
                            self.fix_path = []
                    else:
                        self.fix_path = []
                    return

        # Pick ore: wall-density-adaptive scoring
        # Maze/ore-rich maps: nearest to builder — core_dist misleads through walls
        # Open maps: core-proximate ore preferred — shorter conveyor chains
        is_maze = self._check_is_maze()
        use_nearest = is_maze or map_mode == "tight"
        if ore_tiles:
            best, bd = None, 10**9
            for t in ore_tiles:
                builder_dist = pos.distance_squared(t)
                if use_nearest:
                    score = builder_dist
                else:
                    core_dist = t.distance_squared(self.core_pos) if self.core_pos else 0
                    score = builder_dist + core_dist * 2
                # Prefer unclaimed tiles: penalize ore with another builder's marker
                if t != self._claimed_pos:
                    bid = c.get_tile_building_id(t)
                    if bid is not None:
                        try:
                            if (c.get_entity_type(bid) == EntityType.MARKER
                                    and c.get_team(bid) == c.get_team()):
                                score += 10000  # another builder is heading here
                        except Exception:
                            pass
                if score < bd:
                    best, bd = t, score
            if best != self.target:
                self.fix_path = []
                self._marker_placed = False
                self._claimed_pos = None
            self.target = best
        elif self.target and c.is_in_vision(self.target):
            bid = c.get_tile_building_id(self.target)
            if bid is not None:
                try:
                    # Only abandon target if a real building (not a marker) took the ore
                    if c.get_entity_type(bid) != EntityType.MARKER:
                        self.target = None
                except Exception:
                    self.target = None

        # Place claim marker on target ore only when not yet adjacent
        # (marker blocks harvester build when adjacent, so don't place within action range)
        if self.target and not self._marker_placed:
            if pos.distance_squared(self.target) > 2:  # not adjacent yet
                if c.can_place_marker(self.target):
                    c.place_marker(self.target, 1)
                    self._claimed_pos = self.target
                    self._marker_placed = True

        if self.target:
            self._nav(c, pos, self.target, passable)
        else:
            self._explore(c, pos, passable, rnd)

    # -------------------------------------------------------------- Nav
    def _nav(self, c, pos, target, passable, ti_reserve=5):
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
                if ti >= cc + ti_reserve:
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
                if self.target is not None and len(self.fix_path) < 30:
                    self.fix_path.append(pos)
                c.move(d)
                return

        # Bridge fallback (before road — bridges cross walls, roads don't)
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            bc = c.get_bridge_cost()[0]
            # Tight maps: slightly more aggressive; other maps: standard threshold
            map_mode = getattr(self, 'map_mode', 'balanced')
            bridge_threshold = bc + 10 if map_mode == "tight" else bc + 20
            if ti >= bridge_threshold:
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

    def _explore(self, c, pos, passable, rnd=0):
        w, h = c.get_map_width(), c.get_map_height()
        rnd = c.get_current_round()
        mid = self.my_id or 0
        area = w * h

        if area >= 1600:
            # Large maps: sector-based from core, target map edge, rotate slowly
            # Multiply ID by prime to spread sequential IDs across sectors
            sector = (mid * 7 + self.explore_idx * 3 + rnd // 200) % len(DIRS)
            d = DIRS[sector]
            dx, dy = d.delta()
            if self.core_pos:
                cx, cy = self.core_pos.x, self.core_pos.y
            else:
                cx, cy = pos.x, pos.y
            reach = max(w, h)
            tx = max(0, min(w - 1, cx + dx * reach))
            ty = max(0, min(h - 1, cy + dy * reach))
            far = Position(tx, ty)
        elif area > 625:
            # Balanced maps: sector from core, prime-spread IDs, quick rotation
            sector = (mid * 7 + self.explore_idx * 3 + rnd // 50) % len(DIRS)
            d = DIRS[sector]
            dx, dy = d.delta()
            if self.core_pos:
                cx, cy = self.core_pos.x, self.core_pos.y
            else:
                cx, cy = pos.x, pos.y
            reach = max(w, h)
            tx = max(0, min(w - 1, cx + dx * reach))
            ty = max(0, min(h - 1, cy + dy * reach))
            far = Position(tx, ty)
        else:
            # Tight maps (area <= 625): original spread pattern from builder position
            idx = (mid * 3 + self.explore_idx
                   + rnd // 100) % len(DIRS)
            d = DIRS[idx]
            dx, dy = d.delta()
            reach = max(w, h)
            far = Position(pos.x + dx * reach, pos.y + dy * reach)
        # Higher Ti reserve for exploration when far from core (less useful conveyors)
        # Exception: fragmented ore-rich maps (butterfly) need conveyors as walkways
        # Use conservative check: both high walls AND high ore density required
        core_dist_sq = pos.distance_squared(self.core_pos) if self.core_pos else 0
        if self._check_needs_low_reserve():
            explore_reserve = 5  # need conveyors as walkways in fragmented regions
        else:
            explore_reserve = 30 if core_dist_sq > 50 else 5
        self._nav(c, pos, far, passable, ti_reserve=explore_reserve)

    # -------------------------------------------------------- Gunner placement
    def _place_gunner(self, c, pos):
        """Place a gunner on any empty tile near core facing the enemy. No splitter, no chain destruction."""
        if c.get_action_cooldown() != 0:
            return False

        # Recount nearby gunners each call
        gunner_count = 0
        for eid in c.get_nearby_buildings():
            try:
                if (c.get_entity_type(eid) == EntityType.GUNNER
                        and c.get_team(eid) == c.get_team()):
                    gunner_count += 1
            except Exception:
                pass
        if gunner_count >= 3:
            return False

        ti = c.get_global_resources()[0]
        if ti < c.get_gunner_cost()[0] + 10:
            return False

        enemy_dir = self._get_enemy_direction(c)
        if not enemy_dir:
            return False

        enemy_target = self._get_enemy_core_pos(c) or self.core_pos.add(enemy_dir)

        # Try building adjacent to current position first, then walk toward core
        for d in self._rank(pos, enemy_target):
            sp = pos.add(d)
            if c.can_build_gunner(sp, enemy_dir):
                c.build_gunner(sp, enemy_dir)
                self.gunner_placed += 1
                return True

        # Walk toward core area to find a good spot
        if self.core_pos and pos.distance_squared(self.core_pos) > 25:
            self._walk_to(c, pos, self.core_pos)
            return True

        return False

    # -------------------------------------------------------- Armed sentinel
    def _place_armed_sentinel(self, c, pos):
        """Build splitter+branch+sentinel off an existing conveyor chain.

        Multi-round stateful build:
        Step 0: Find allied conveyor, plan layout (splitter, branch, sentinel positions)
        Step 1: Walk to the target conveyor
        Step 2: Destroy conveyor + build splitter (same turn — destroy has no cooldown)
        Step 3: Build branch conveyor perpendicular to chain
        Step 4: Build sentinel at end of branch
        """
        if self._sentinel_step == 0:
            # Find an allied conveyor to splice into
            best_conv = None
            best_dist = 10**9
            my_team = c.get_team()
            for eid in c.get_nearby_buildings():
                try:
                    if (c.get_entity_type(eid) == EntityType.CONVEYOR
                            and c.get_team(eid) == my_team):
                        epos = c.get_position(eid)
                        edir = c.get_direction(eid)
                        # Prefer conveyors closer to core (more resource flow)
                        core_dist = epos.distance_squared(self.core_pos) if self.core_pos else 0
                        # Check if at least one perpendicular direction has 2 empty tiles
                        for branch_dir in [_perp_left(edir), _perp_right(edir)]:
                            branch_pos = epos.add(branch_dir)
                            sentinel_pos = branch_pos.add(branch_dir)
                            try:
                                if (c.is_in_vision(branch_pos) and c.is_in_vision(sentinel_pos)
                                        and c.get_tile_env(branch_pos) != Environment.WALL
                                        and c.get_tile_env(sentinel_pos) != Environment.WALL
                                        and c.is_tile_empty(branch_pos)
                                        and c.is_tile_empty(sentinel_pos)):
                                    if core_dist < best_dist:
                                        best_dist = core_dist
                                        best_conv = (epos, edir, branch_dir, branch_pos, sentinel_pos)
                            except Exception:
                                pass
                except Exception:
                    pass
            if best_conv is None:
                return False
            self._sentinel_chain_pos, self._sentinel_chain_dir, self._sentinel_branch_dir, branch_p, sentinel_p = best_conv
            self._sentinel_positions = {"branch": branch_p, "sentinel": sentinel_p}
            self._sentinel_step = 1
            self.target = None
            self._claimed_pos = None
            self._marker_placed = False
            return True

        if self._sentinel_step == 1:
            # Walk to the target conveyor
            if pos.distance_squared(self._sentinel_chain_pos) <= 2:
                self._sentinel_step = 2
            else:
                self._walk_to(c, pos, self._sentinel_chain_pos)
                return True

        if self._sentinel_step == 2:
            # Destroy conveyor + build splitter in same turn
            if c.get_action_cooldown() != 0:
                return True
            if pos.distance_squared(self._sentinel_chain_pos) > 2:
                self._walk_to(c, pos, self._sentinel_chain_pos)
                return True
            try:
                if c.can_destroy(self._sentinel_chain_pos):
                    c.destroy(self._sentinel_chain_pos)
                if c.can_build_splitter(self._sentinel_chain_pos, self._sentinel_chain_dir):
                    c.build_splitter(self._sentinel_chain_pos, self._sentinel_chain_dir)
                    self._sentinel_step = 3
                else:
                    # Can't build splitter — give up
                    self._sentinel_step = 5
            except Exception:
                self._sentinel_step = 5
            return True

        if self._sentinel_step == 3:
            # Build branch conveyor
            branch_pos = self._sentinel_positions["branch"]
            if pos.distance_squared(branch_pos) > 2:
                self._walk_to(c, pos, branch_pos)
                return True
            if c.get_action_cooldown() != 0:
                return True
            try:
                if c.can_build_conveyor(branch_pos, self._sentinel_branch_dir):
                    c.build_conveyor(branch_pos, self._sentinel_branch_dir)
                    self._sentinel_step = 4
                else:
                    # Try the other perpendicular direction
                    alt_dir = _perp_right(self._sentinel_chain_dir) if self._sentinel_branch_dir == _perp_left(self._sentinel_chain_dir) else _perp_left(self._sentinel_chain_dir)
                    alt_branch = self._sentinel_chain_pos.add(alt_dir)
                    alt_sentinel = alt_branch.add(alt_dir)
                    if c.can_build_conveyor(alt_branch, alt_dir):
                        c.build_conveyor(alt_branch, alt_dir)
                        self._sentinel_branch_dir = alt_dir
                        self._sentinel_positions["branch"] = alt_branch
                        self._sentinel_positions["sentinel"] = alt_sentinel
                        self._sentinel_step = 4
                    else:
                        self._sentinel_step = 5
            except Exception:
                self._sentinel_step = 5
            return True

        if self._sentinel_step == 4:
            # Build sentinel
            sentinel_pos = self._sentinel_positions["sentinel"]
            if pos.distance_squared(sentinel_pos) > 2:
                self._walk_to(c, pos, sentinel_pos)
                return True
            if c.get_action_cooldown() != 0:
                return True
            try:
                if c.can_build_sentinel(sentinel_pos, self._sentinel_branch_dir):
                    c.build_sentinel(sentinel_pos, self._sentinel_branch_dir)
                    self._sentinel_step = 5
                else:
                    self._sentinel_step = 5
            except Exception:
                self._sentinel_step = 5
            return True

        return False

    # -------------------------------------------------------- Ax tiebreaker
    def _build_ax_tiebreaker(self, c, pos):
        """Late-game foundry for TB#1 insurance.

        Find Ax ore in vision. Build harvester + foundry + output conveyor
        as a self-contained mini-chain. The foundry sits between the Ax harvester
        and the existing conveyor network, receiving raw Ax from one side and
        Ti from an adjacent conveyor on the other side.

        Steps: 0=find Ax ore + plan, 1=walk to ore, 2=clear+build harvester,
               3=build foundry adjacent, 4=build output conveyor, done
        """

        if not hasattr(self, '_ax_step'):
            self._ax_step = 0
            self._ax_ore_pos = None
            self._ax_foundry_pos = None
            self._ax_foundry_dir = None  # direction from ore to foundry

        if self._ax_step == 0:
            my_team = c.get_team()
            # Skip if allied foundry exists
            for eid in c.get_nearby_buildings():
                try:
                    if (c.get_entity_type(eid) == EntityType.FOUNDRY
                            and c.get_team(eid) == my_team):
                        self._ax_done = True
                        return False
                except Exception:
                    pass
            # Find Ax ore tile (with or without buildings on it)
            best_ax = None
            best_dist = 10**9
            for t in c.get_nearby_tiles():
                if c.get_tile_env(t) == Environment.ORE_AXIONITE:
                    d = pos.distance_squared(t)
                    if d < best_dist:
                        best_dist = d
                        best_ax = t
            if best_ax is None:
                # Walk toward core to find Ax ore
                if not hasattr(self, '_ax_search_rounds'):
                    self._ax_search_rounds = 0
                self._ax_search_rounds += 1
                if self._ax_search_rounds > 100:
                    self._ax_done = True
                    return False
                self._walk_to(c, pos, self.core_pos)
                return True
            self._ax_ore_pos = best_ax
            # Plan foundry: prefer spot adjacent to ore AND near Ti conveyors
            my_team = c.get_team()
            best_fp = None
            best_fp_score = -1
            for fd in DIRS:
                fp = best_ax.add(fd)
                try:
                    if not c.is_in_vision(fp):
                        continue
                    if c.get_tile_env(fp) == Environment.WALL:
                        continue
                    adj_convs = 0
                    for d2 in DIRS:
                        adj2 = fp.add(d2)
                        if adj2 == best_ax:
                            continue
                        try:
                            bid2 = c.get_tile_building_id(adj2)
                            if bid2 is not None and c.get_team(bid2) == my_team:
                                if c.get_entity_type(bid2) in (EntityType.CONVEYOR, EntityType.SPLITTER):
                                    adj_convs += 1
                        except Exception:
                            pass
                    core_dist = fp.distance_squared(self.core_pos) if self.core_pos else 0
                    score = adj_convs * 1000 - core_dist
                    if score > best_fp_score:
                        best_fp_score = score
                        best_fp = fp
                except Exception:
                    pass
            if best_fp is None:
                self._ax_done = True
                return False
            self._ax_foundry_dir = best_ax.direction_to(best_fp)
            self._ax_foundry_pos = best_fp
            self._ax_step = 1

            return True

        if self._ax_step == 1:
            # Walk to Ax ore tile
            if pos.distance_squared(self._ax_ore_pos) > 2:
                self._walk_to(c, pos, self._ax_ore_pos)
                return True
            self._ax_step = 2

        if self._ax_step == 2:
            # Clear ore tile and build harvester
            if c.get_action_cooldown() != 0:
                return True
            if pos.distance_squared(self._ax_ore_pos) > 2:
                self._walk_to(c, pos, self._ax_ore_pos)
                return True
            # Check if harvester already exists on this tile
            bid = c.get_tile_building_id(self._ax_ore_pos)
            if bid is not None:
                try:
                    if (c.get_entity_type(bid) == EntityType.HARVESTER
                            and c.get_team(bid) == c.get_team()):
                        # Already has our harvester — skip to foundry
                        self._ax_step = 3
                        return True
                    # Something else — destroy it
                    if c.get_team(bid) == c.get_team():
                        if c.can_destroy(self._ax_ore_pos):
                            c.destroy(self._ax_ore_pos)
                    else:
                        self._ax_done = True
                        return False
                except Exception:
                    self._ax_done = True
                    return False
            ti = c.get_global_resources()[0]
            hc = c.get_harvester_cost()[0]
            if ti < hc + 50:
                return True
            if c.can_build_harvester(self._ax_ore_pos):
                c.build_harvester(self._ax_ore_pos)

                self._ax_step = 3
            else:
                self._ax_done = True
            return True

        if self._ax_step == 3:
            # Build foundry adjacent to harvester (toward core)
            if c.get_action_cooldown() != 0:
                return True
            ti = c.get_global_resources()[0]
            fc = c.get_foundry_cost()[0]
            if ti < fc + 5:
                return True
            fp = self._ax_foundry_pos
            if pos.distance_squared(fp) > 2:
                self._walk_to(c, pos, fp)
                return True
            # Clear the tile if needed
            bid = c.get_tile_building_id(fp)
            if bid is not None:
                try:
                    if c.get_team(bid) == c.get_team() and c.can_destroy(fp):
                        c.destroy(fp)
                except Exception:
                    pass
            if c.can_build_foundry(fp):
                c.build_foundry(fp)

                self._ax_step = 4
            else:
                # Try alternative positions around the ore
                for d in DIRS:
                    alt = self._ax_ore_pos.add(d)
                    if alt == fp:
                        continue
                    try:
                        if pos.distance_squared(alt) > 2:
                            continue
                        abid = c.get_tile_building_id(alt)
                        if abid is not None and c.get_team(abid) == c.get_team():
                            if c.can_destroy(alt):
                                c.destroy(alt)
                        if c.can_build_foundry(alt):
                            c.build_foundry(alt)
                            self._ax_foundry_pos = alt

                            self._ax_step = 4
                            break
                    except Exception:
                        pass
                else:
                    self._walk_to(c, pos, self._ax_ore_pos)
                    if not hasattr(self, '_ax_step3_tries'):
                        self._ax_step3_tries = 0
                    self._ax_step3_tries += 1
                    if self._ax_step3_tries > 20:
                        self._ax_done = True
            return True

        if self._ax_step == 4:
            # Build output conveyor from foundry toward core/existing chain
            if c.get_action_cooldown() != 0:
                return True
            ti = c.get_global_resources()[0]
            cc = c.get_conveyor_cost()[0]
            if ti < cc + 5:
                self._ax_done = True
                return True
            fp = self._ax_foundry_pos
            out_dir = fp.direction_to(self.core_pos)
            if out_dir == Direction.CENTRE:
                out_dir = self._ax_foundry_dir
            for d in [out_dir, out_dir.rotate_left(), out_dir.rotate_right(),
                      out_dir.rotate_left().rotate_left(), out_dir.rotate_right().rotate_right()]:
                out_pos = fp.add(d)
                try:
                    if pos.distance_squared(out_pos) > 2:
                        continue
                    if c.can_build_conveyor(out_pos, d):
                        c.build_conveyor(out_pos, d)

                        self._ax_done = True
                        return True
                except Exception:
                    pass
            # Can't build output — foundry is still there, maybe it'll connect
            self._ax_done = True
            return True

        return False

    # ------------------------------------------------------------ Barriers
    def _build_barriers(self, c, pos):
        """Place barriers on the enemy-facing side of core, 2-3 tiles out."""
        enemy_dir = self._get_enemy_direction(c)
        if not enemy_dir:
            return False

        # Count existing nearby barriers
        barrier_count = 0
        for eid in c.get_nearby_buildings():
            try:
                if (c.get_entity_type(eid) == EntityType.BARRIER
                        and c.get_team(eid) == c.get_team()):
                    barrier_count += 1
            except Exception:
                pass
        ti = c.get_global_resources()[0]
        max_barriers = 6 if ti < 500 else (10 if ti < 1000 else 15)
        if barrier_count >= max_barriers:
            return False

        if ti < c.get_barrier_cost()[0] + 15:
            return False

        dx, dy = enemy_dir.delta()
        # Perpendicular directions for spreading the wall
        perp_left = enemy_dir.rotate_left().rotate_left()
        perp_right = enemy_dir.rotate_right().rotate_right()

        # Try positions 2-3 tiles from core toward enemy, spread perpendicular
        # Skip every other perpendicular offset to leave gaps for builders
        for dist in (3, 2):
            cx = self.core_pos.x + dx * dist
            cy = self.core_pos.y + dy * dist
            center = Position(cx, cy)

            for offset in (0, -2, 2, -1, 1):
                pdx, pdy = (perp_right if offset > 0 else perp_left).delta()
                abs_off = abs(offset)
                bp = Position(center.x + pdx * abs_off, center.y + pdy * abs_off)

                # Skip odd offsets to leave gaps
                if abs(offset) == 1:
                    continue

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

    # ------------------------------------------------------------ Attack
    def _attack(self, c, pos, passable):
        """Attack enemy infrastructure. Priority: foundry > harvester > conveyor > other."""
        # Phase 1: Fire on enemy building on current tile
        if c.get_action_cooldown() == 0:
            bid = c.get_tile_building_id(pos)
            if bid is not None:
                try:
                    if c.get_team(bid) != c.get_team() and c.can_fire(pos):
                        c.fire(pos)
                        return
                except Exception:
                    pass

        # Phase 2: Move onto adjacent enemy conveyor (walkable!)
        if c.get_move_cooldown() == 0:
            w, h = c.get_map_width(), c.get_map_height()
            for d in DIRS:
                ap = pos.add(d)
                if ap.x < 0 or ap.x >= w or ap.y < 0 or ap.y >= h:
                    continue
                abid = c.get_tile_building_id(ap)
                if abid is not None:
                    try:
                        if c.get_team(abid) != c.get_team() and c.can_move(d):
                            c.move(d)
                            return
                    except Exception:
                        pass

        # Phase 3: Find nearest enemy building in vision, navigate toward it
        best_target = self._find_best_infra_target(c, pos)

        if best_target:
            self._nav_attacker(c, pos, best_target, passable, ti_reserve=30)
        else:
            # No enemy infra visible — navigate toward enemy core area to find targets
            enemy_pos = self._get_enemy_core_pos(c)
            if enemy_pos:
                self._nav_attacker(c, pos, enemy_pos, passable, ti_reserve=30)
            else:
                self._explore(c, pos, passable)

    def _find_best_infra_target(self, c, pos):
        """Scan nearby enemy buildings and return position of highest-priority target."""
        PRIORITY = {
            EntityType.FOUNDRY: 0,
            EntityType.HARVESTER: 1,
            EntityType.GUNNER: 2,
            EntityType.SENTINEL: 3,
            EntityType.BREACH: 4,
            EntityType.SPLITTER: 5,
            EntityType.CONVEYOR: 6,
            EntityType.ARMOURED_CONVEYOR: 7,
            EntityType.BARRIER: 8,
        }
        best = None
        best_score = float('inf')
        my_team = c.get_team()
        for eid in c.get_nearby_buildings():
            try:
                if c.get_team(eid) == my_team:
                    continue
                etype = c.get_entity_type(eid)
                if etype == EntityType.CORE:
                    continue  # skip core, too much HP
                epos = c.get_position(eid)
                pri = PRIORITY.get(etype, 9)
                dist = pos.distance_squared(epos)
                score = pri * 1000 + dist
                if score < best_score:
                    best_score = score
                    best = epos
            except Exception:
                pass
        return best

    def _nav_attacker(self, c, pos, target, passable, ti_reserve=20):
        """Navigate toward target without building conveyors. Uses roads for movement."""
        dirs = self._rank(pos, target)
        bfs_dir = self._bfs_step(pos, target, passable)
        if bfs_dir is not None and bfs_dir != dirs[0]:
            dirs = [bfs_dir] + [d for d in dirs if d != bfs_dir]

        w, h = c.get_map_width(), c.get_map_height()
        for d in dirs:
            nxt = pos.add(d)
            if nxt.x < 0 or nxt.x >= w or nxt.y < 0 or nxt.y >= h:
                continue
            # Move if the tile is passable for builder bots
            if c.get_move_cooldown() == 0 and c.can_move(d):
                c.move(d)
                return
            # Build road as walkable path (cheaper than conveyor, doesn't misdirect resources)
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                rc = c.get_road_cost()[0]
                if ti >= rc + ti_reserve and c.can_build_road(nxt):
                    c.build_road(nxt)
                    return

    # --------------------------------------------------------- Chain fix
    def _fix_chain(self, c, pos):
        """Walk back along recorded path, fixing conveyors behind us."""
        if self.fix_idx < 0:
            self.fixing_chain = False
            self.fix_path = []
            return

        # Fix the tile BEHIND us (fix_idx + 1) — within action radius
        behind_idx = self.fix_idx + 1
        if behind_idx < len(self.fix_path) and c.get_action_cooldown() == 0:
            behind_pos = self.fix_path[behind_idx]
            if pos.distance_squared(behind_pos) <= 2 and c.is_in_vision(behind_pos):
                correct_facing = behind_pos.direction_to(self.fix_path[self.fix_idx])
                if correct_facing != Direction.CENTRE:
                    bid = c.get_tile_building_id(behind_pos)
                    if bid is not None:
                        try:
                            et = c.get_entity_type(bid)
                            tm = c.get_team(bid)
                            if tm == c.get_team() and et == EntityType.CONVEYOR:
                                if c.get_direction(bid) != correct_facing:
                                    old_dir = c.get_direction(bid)
                                    c.destroy(behind_pos)
                                    if c.can_build_conveyor(behind_pos, correct_facing):
                                        c.build_conveyor(behind_pos, correct_facing)
                                    else:
                                        # Fallback: restore
                                        c.build_conveyor(behind_pos, old_dir)
                        except Exception:
                            pass

        # Advance along path toward core
        target = self.fix_path[self.fix_idx]
        if pos == target:
            self.fix_idx -= 1
            if self.fix_idx < 0:
                self.fixing_chain = False
                self.fix_path = []
            return

        d = pos.direction_to(target)
        if d == Direction.CENTRE:
            self.fix_idx -= 1
            return
        for try_d in [d, d.rotate_left(), d.rotate_right(),
                      d.rotate_left().rotate_left(), d.rotate_right().rotate_right()]:
            if c.get_move_cooldown() == 0 and c.can_move(try_d):
                c.move(try_d)
                return

        # Stuck — bail
        self.fixing_chain = False
        self.fix_path = []

    # ------------------------------------------------------------ Helpers
    def _check_is_maze(self):
        """Maze/fragmented map detection using wall density OR ore density.

        Wall density >15% catches high-wall maps (corridors, butterfly wing areas).
        Ore density >12% alone catches ore-rich maps like butterfly where the core
        area may appear locally open. Both thresholds are conservative to avoid
        false positives on maps like cold (high walls + moderate ore near core).
        """
        wall_maze = self._wall_density is not None and self._wall_density > 0.15
        ore_rich = self._ore_density is not None and self._ore_density > 0.12
        return wall_maze or ore_rich

    def _check_needs_low_reserve(self):
        """Whether to lower explore Ti reserve for maze-like navigation.

        More conservative than _check_is_maze: requires BOTH high wall density
        AND ore richness to avoid false-positives on maps like cold (has diamond
        walls creating local wall clusters near core) that need high explore_reserve
        to prevent wasteful conveyor sprawl far from ore.
        """
        wall_maze = self._wall_density is not None and self._wall_density > 0.15
        ore_rich = self._ore_density is not None and self._ore_density > 0.08
        return wall_maze and ore_rich

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
        steps = 0
        while queue and steps < 200:
            steps += 1
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
