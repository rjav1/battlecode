"""Turtle bot - pure defense + economy, win by Resource Victory at 2000 rounds.

Strategy:
- Spawn 3 builders immediately, scale to 6 by round 150
- Each builder explores a unique direction, builds harvesters on Ti ore found
- L-shaped conveyor chains (horizontal then vertical) back to core
- One builder assigned as defender: builds barriers around core then sentinel
- NO offense - win purely by out-mining the opponent
"""

import sys
from cambc import Controller, Direction, EntityType, Environment, Position

DIRECTIONS = [d for d in Direction if d != Direction.CENTRE]


def stderr(msg):
    print(msg, file=sys.stderr)


class Player:
    def __init__(self):
        self.core_pos = None
        self.enemy_dir = None
        self.spawn_count = 0
        # Builder
        self.explore_dir = None
        self.phase = "explore"
        self.harvester_pos = None
        self.chain_cursor = None
        self.chains_built = 0
        self.explore_stuck = 0
        self.last_pos = None
        self.role = None  # "miner" or "defender"
        # Defender
        self.barrier_targets = []
        self.barrier_idx = 0
        self.def_phase = "barriers"  # barriers, find_conv, destroy, splitter, branch, sentinel, done
        self.conv_pos = None
        self.conv_dir = None
        self.branch_dir = None
        self.branch_pos = None
        self.sentinel_pos = None

    def run(self, c: Controller) -> None:
        etype = c.get_entity_type()
        if etype == EntityType.CORE:
            self._run_core(c)
        elif etype == EntityType.BUILDER_BOT:
            self._run_builder(c)

    # ------------------------------------------------------------------ CORE
    def _run_core(self, c):
        rnd = c.get_current_round()
        pos = c.get_position()

        if self.core_pos is None:
            self.core_pos = pos
            w, h = c.get_map_width(), c.get_map_height()
            self.enemy_dir = pos.direction_to(Position(w // 2, h // 2))
            if self.enemy_dir == Direction.CENTRE:
                self.enemy_dir = Direction.EAST

        max_b = 3 if rnd < 150 else 6
        ti, _ = c.get_global_resources()
        bcost = c.get_builder_bot_cost()[0]

        if self.spawn_count < max_b and ti >= bcost + 20:
            for d in Direction:
                sp = pos.add(d)
                if c.can_spawn(sp):
                    c.spawn_builder(sp)
                    self.spawn_count += 1
                    return

        if rnd % 500 == 0:
            stderr(f"R{rnd}: Ti={ti} scale={c.get_scale_percent():.0f}%")

    # ------------------------------------------------------------------ BUILDER
    def _run_builder(self, c):
        rnd = c.get_current_round()
        my_pos = c.get_position()

        if self.core_pos is None:
            for eid in c.get_nearby_entities():
                try:
                    if c.get_entity_type(eid) == EntityType.CORE and c.get_team(eid) == c.get_team():
                        self.core_pos = c.get_position(eid)
                        w, h = c.get_map_width(), c.get_map_height()
                        self.enemy_dir = self.core_pos.direction_to(Position(w // 2, h // 2))
                        if self.enemy_dir == Direction.CENTRE:
                            self.enemy_dir = Direction.EAST
                        break
                except Exception:
                    pass

        if self.explore_dir is None:
            bid = c.get_id()
            idx = bid % len(DIRECTIONS)
            self.explore_dir = DIRECTIONS[idx]

        if self.role is None:
            bid = c.get_id()
            # 4th unit (id % 8 == 3) is defender, rest are miners
            if bid % 8 == 3:
                self.role = "defender"
            else:
                self.role = "miner"

        if self.role == "defender":
            self._run_defender(c, rnd, my_pos)
        else:
            self._run_miner(c, rnd, my_pos)

    # ------------------------------------------------------------------ MINER
    def _run_miner(self, c, rnd, my_pos):
        if self.phase == "explore":
            self._explore_and_harvest(c, rnd, my_pos)
        elif self.phase == "chain_back":
            self._build_chain(c, rnd, my_pos)
        elif self.phase == "find_more":
            self.phase = "explore"
            self.harvester_pos = None
            self.chain_cursor = None
            self.explore_dir = self.explore_dir.rotate_right().rotate_right()

    def _explore_and_harvest(self, c, rnd, my_pos):
        w, h = c.get_map_width(), c.get_map_height()
        for d in Direction:
            pos = my_pos.add(d)
            if not (0 <= pos.x < w and 0 <= pos.y < h):
                continue
            try:
                if c.get_tile_env(pos) == Environment.ORE_TITANIUM:
                    bid = c.get_tile_building_id(pos)
                    if bid is None and c.can_build_harvester(pos):
                        c.build_harvester(pos)
                        self.harvester_pos = pos
                        self.chain_cursor = pos
                        self.phase = "chain_back"
                        stderr(f"R{rnd}: HARV {pos}")
                        return
            except Exception:
                pass
        self._walk_explore(c, rnd, my_pos)

    def _walk_explore(self, c, rnd, my_pos):
        w, h = c.get_map_width(), c.get_map_height()
        d = self.explore_dir
        if self.last_pos == my_pos:
            self.explore_stuck += 1
            if self.explore_stuck > 5:
                self.explore_dir = d.rotate_right().rotate_right()
                self.explore_stuck = 0
                d = self.explore_dir
        else:
            self.explore_stuck = 0
        self.last_pos = my_pos

        for try_d in [d, d.rotate_left(), d.rotate_right()]:
            if c.can_move(try_d):
                c.move(try_d)
                return
        if c.get_action_cooldown() > 0:
            return
        for try_d in [d, d.rotate_left(), d.rotate_right(),
                      d.rotate_left().rotate_left(), d.rotate_right().rotate_right()]:
            pos = my_pos.add(try_d)
            if not (0 <= pos.x < w and 0 <= pos.y < h):
                continue
            try:
                env = c.get_tile_env(pos)
                if env == Environment.WALL or env in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
                    continue
            except Exception:
                continue
            if c.can_build_road(pos):
                c.build_road(pos)
                if c.can_move(try_d):
                    c.move(try_d)
                return
        self.explore_dir = d.rotate_right().rotate_right()

    def _build_chain(self, c, rnd, my_pos):
        """L-shaped conveyor chain: align X, then Y. Each conv faces next step dir."""
        core = self.core_pos
        if core is None or self.chain_cursor is None:
            self.phase = "find_more"
            return
        cur = self.chain_cursor
        w, h = c.get_map_width(), c.get_map_height()

        if cur.distance_squared(core) <= 2:
            stderr(f"R{rnd}: Chain done ({self.chains_built+1})")
            self.chains_built += 1
            self.phase = "find_more"
            return

        dx = core.x - cur.x
        dy = core.y - cur.y
        dirs_to_try = []
        if abs(dx) > 0:
            dirs_to_try.append(Direction.EAST if dx > 0 else Direction.WEST)
        if abs(dy) > 0:
            dirs_to_try.append(Direction.SOUTH if dy > 0 else Direction.NORTH)
        if not dirs_to_try:
            self.phase = "find_more"
            return

        for step_dir in dirs_to_try:
            nxt = cur.add(step_dir)
            if not (0 <= nxt.x < w and 0 <= nxt.y < h):
                continue
            try:
                env = c.get_tile_env(nxt)
                if env == Environment.WALL or env in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
                    continue
            except Exception:
                continue

            bid = c.get_tile_building_id(nxt)
            if bid is not None:
                try:
                    bt = c.get_entity_type(bid)
                    bteam = c.get_team(bid)
                    if bt == EntityType.CORE and bteam == c.get_team():
                        self.chains_built += 1
                        self.phase = "find_more"
                        return
                    if bt == EntityType.ROAD and bteam == c.get_team():
                        if my_pos.distance_squared(nxt) <= 2 and c.get_action_cooldown() == 0:
                            c.destroy(nxt)
                            return
                        elif my_pos.distance_squared(nxt) > 2:
                            self._walk_toward(c, nxt, my_pos, rnd)
                            return
                        return
                    if bt in (EntityType.CONVEYOR, EntityType.SPLITTER) and bteam == c.get_team():
                        self.chain_cursor = nxt
                        return
                except Exception:
                    pass
                continue

            # Determine facing: look ahead to next step from nxt
            dx2 = core.x - nxt.x
            dy2 = core.y - nxt.y
            if abs(dx2) > 0:
                facing = Direction.EAST if dx2 > 0 else Direction.WEST
            elif abs(dy2) > 0:
                facing = Direction.SOUTH if dy2 > 0 else Direction.NORTH
            else:
                facing = step_dir

            if my_pos.distance_squared(nxt) > 2:
                self._walk_toward(c, nxt, my_pos, rnd)
                return
            if c.get_action_cooldown() > 0:
                return
            if c.can_build_conveyor(nxt, facing):
                c.build_conveyor(nxt, facing)
                self.chain_cursor = nxt
                d2 = my_pos.direction_to(nxt)
                if d2 != Direction.CENTRE and c.can_move(d2):
                    c.move(d2)
                return
            else:
                ti, _ = c.get_global_resources()
                if ti < 3:
                    return
                continue

        self.phase = "find_more"

    # ------------------------------------------------------------------ DEFENDER
    def _run_defender(self, c, rnd, my_pos):
        # Wait until round 50 so economy gets started first
        if rnd < 50:
            self._run_miner(c, rnd, my_pos)
            return

        if self.def_phase == "barriers":
            self._build_barriers(c, rnd, my_pos)
        elif self.def_phase == "find_conv":
            self._find_conv(c, rnd, my_pos)
        elif self.def_phase == "destroy":
            self._destroy_conv(c, rnd, my_pos)
        elif self.def_phase == "splitter":
            self._build_splitter(c, rnd, my_pos)
        elif self.def_phase == "branch":
            self._build_branch_conv(c, rnd, my_pos)
        elif self.def_phase == "sentinel":
            self._build_sentinel(c, rnd, my_pos)
        elif self.def_phase == "done":
            # After defense is built, become a miner
            self.role = "miner"
            self.phase = "explore"

    def _build_barriers(self, c, rnd, my_pos):
        core = self.core_pos
        if core is None:
            self.def_phase = "done"
            return
        if not self.barrier_targets:
            ed = self.enemy_dir if self.enemy_dir else Direction.EAST
            dirs = [ed, ed.rotate_left(), ed.rotate_right()]
            w, h = c.get_map_width(), c.get_map_height()
            for d in dirs:
                for dist in [2, 3]:
                    p = core
                    for _ in range(dist):
                        p = p.add(d)
                    if 0 <= p.x < w and 0 <= p.y < h:
                        try:
                            env = c.get_tile_env(p)
                            if env == Environment.EMPTY and c.get_tile_building_id(p) is None:
                                self.barrier_targets.append(p)
                        except Exception:
                            pass
            self.barrier_targets = self.barrier_targets[:6]

        if self.barrier_idx >= len(self.barrier_targets):
            stderr(f"R{rnd}: {self.barrier_idx} barriers built")
            self.def_phase = "find_conv"
            return

        pos = self.barrier_targets[self.barrier_idx]
        if c.get_tile_building_id(pos) is not None:
            self.barrier_idx += 1
            return
        if my_pos.distance_squared(pos) > 2:
            self._walk_toward(c, pos, my_pos, rnd)
            return
        if c.get_action_cooldown() > 0:
            return
        if c.can_build_barrier(pos):
            c.build_barrier(pos)
            stderr(f"R{rnd}: BARRIER {pos}")
            self.barrier_idx += 1

    def _find_conv(self, c, rnd, my_pos):
        """Find a conveyor near core to convert to splitter for sentinel ammo."""
        core = self.core_pos
        best_pos = None
        best_dist = 999999

        for eid in c.get_nearby_buildings():
            try:
                if c.get_entity_type(eid) != EntityType.CONVEYOR:
                    continue
                if c.get_team(eid) != c.get_team():
                    continue
                epos = c.get_position(eid)
                edir = c.get_direction(eid)
                dist = epos.distance_squared(core) if core else 999
                if dist <= 2 or dist >= best_dist:
                    continue
                w, h = c.get_map_width(), c.get_map_height()
                for bd in [self._perp_left(edir), self._perp_right(edir)]:
                    bp = epos.add(bd)
                    sp = bp.add(bd)
                    if not (0 <= bp.x < w and 0 <= bp.y < h and 0 <= sp.x < w and 0 <= sp.y < h):
                        continue
                    try:
                        if (c.get_tile_env(bp) not in (Environment.WALL, Environment.ORE_TITANIUM, Environment.ORE_AXIONITE) and
                            c.get_tile_env(sp) not in (Environment.WALL, Environment.ORE_TITANIUM, Environment.ORE_AXIONITE) and
                            c.get_tile_building_id(bp) is None and
                            c.get_tile_building_id(sp) is None):
                            best_pos = epos
                            best_dist = dist
                            self.conv_dir = edir
                            self.branch_dir = bd
                            self.branch_pos = bp
                            self.sentinel_pos = sp
                    except Exception:
                        pass
            except Exception:
                pass

        if best_pos:
            self.conv_pos = best_pos
            self.def_phase = "destroy"
            stderr(f"R{rnd}: Splitter target {best_pos}")
        else:
            self.def_phase = "done"

    def _destroy_conv(self, c, rnd, my_pos):
        pos = self.conv_pos
        if my_pos.distance_squared(pos) > 2:
            self._walk_toward(c, pos, my_pos, rnd)
            return
        bid = c.get_tile_building_id(pos)
        if bid is not None:
            if c.can_destroy(pos):
                c.destroy(pos)
                self.def_phase = "splitter"
        else:
            self.def_phase = "splitter"

    def _build_splitter(self, c, rnd, my_pos):
        pos = self.conv_pos
        if my_pos.distance_squared(pos) > 2:
            self._walk_toward(c, pos, my_pos, rnd)
            return
        if c.get_action_cooldown() > 0:
            return
        if c.can_build_splitter(pos, self.conv_dir):
            c.build_splitter(pos, self.conv_dir)
            stderr(f"R{rnd}: SPLITTER {pos}")
            self.def_phase = "branch"

    def _build_branch_conv(self, c, rnd, my_pos):
        pos = self.branch_pos
        if my_pos.distance_squared(pos) > 2:
            self._walk_toward(c, pos, my_pos, rnd)
            return
        if c.get_action_cooldown() > 0:
            return
        bid = c.get_tile_building_id(pos)
        if bid is not None:
            if c.can_destroy(pos):
                c.destroy(pos)
            return
        if c.can_build_conveyor(pos, self.branch_dir):
            c.build_conveyor(pos, self.branch_dir)
            stderr(f"R{rnd}: BRANCH {pos}")
            self.def_phase = "sentinel"

    def _build_sentinel(self, c, rnd, my_pos):
        pos = self.sentinel_pos
        if my_pos.distance_squared(pos) > 2:
            self._walk_toward(c, pos, my_pos, rnd)
            return
        if c.get_action_cooldown() > 0:
            return
        bid = c.get_tile_building_id(pos)
        if bid is not None:
            if c.can_destroy(pos):
                c.destroy(pos)
            return
        face = self.enemy_dir if self.enemy_dir else Direction.EAST
        if face == self.branch_dir.opposite():
            face = self.branch_dir
        if c.can_build_sentinel(pos, face):
            c.build_sentinel(pos, face)
            stderr(f"R{rnd}: SENTINEL {pos}")
            self.def_phase = "done"

    # ------------------------------------------------------------------ MOVEMENT
    def _walk_toward(self, c, target, my_pos, rnd):
        d = my_pos.direction_to(target)
        if d == Direction.CENTRE:
            return
        w, h = c.get_map_width(), c.get_map_height()
        if c.get_move_cooldown() > 0:
            return
        for try_d in [d, d.rotate_left(), d.rotate_right()]:
            if c.can_move(try_d):
                c.move(try_d)
                return
        if c.get_action_cooldown() > 0:
            return
        for try_d in [d, d.rotate_left(), d.rotate_right(),
                      d.rotate_left().rotate_left(), d.rotate_right().rotate_right()]:
            pos = my_pos.add(try_d)
            if not (0 <= pos.x < w and 0 <= pos.y < h):
                continue
            try:
                env = c.get_tile_env(pos)
                if env == Environment.WALL or env in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
                    continue
            except Exception:
                continue
            if c.can_build_road(pos):
                c.build_road(pos)
                if c.can_move(try_d):
                    c.move(try_d)
                return

    # ------------------------------------------------------------------ HELPERS
    def _perp_left(self, d):
        return d.rotate_left().rotate_left()

    def _perp_right(self, d):
        return d.rotate_right().rotate_right()
