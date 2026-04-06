"""buzzing bees - economy-first bot with directed conveyor chains."""

import sys
from collections import deque
from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]


def perp_left(d):
    return d.rotate_left().rotate_left()


def perp_right(d):
    return d.rotate_right().rotate_right()


class Player:
    def __init__(self):
        self.core_pos = None
        self.my_id = None
        self.role = None  # 'economy', 'attacker'
        self.target = None
        self.last_pos = None
        self.stuck = 0
        self.explore_idx = 0
        self.harvesters_built = 0
        # Chain building state
        self.chain_mode = False  # True when building conveyor chain back to core
        self.chain_from = None  # Harvester position (start of chain)
        self.chain_steps = 0
        self.chain_last_pos = None  # Last position where we built a conveyor
        # Sentinel state
        self.sentinel_built = False
        # Symmetry cache
        self._enemy_dir = None

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)
        elif t == EntityType.SENTINEL:
            self._sentinel(c)

    # ------------------------------------------------------------------ Core
    def _core(self, c):
        if c.get_action_cooldown() != 0:
            return
        rnd = c.get_current_round()
        builders = c.get_unit_count() - 1
        cap = 3 if rnd <= 20 else (5 if rnd <= 100 else (7 if rnd <= 300 else 8))
        if builders >= cap:
            return
        ti = c.get_global_resources()[0]
        cost = c.get_builder_bot_cost()[0]
        if ti < cost + 30:
            return
        pos = c.get_position()
        for d in DIRS:
            sp = pos.add(d)
            if c.can_spawn(sp):
                c.spawn_builder(sp)
                return

    # -------------------------------------------------------------- Sentinel
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

    # --------------------------------------------------------------- Builder
    def _builder(self, c):
        pos = c.get_position()
        rnd = c.get_current_round()

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

        # Assign role once
        if self.role is None:
            if (self.my_id or 0) % 5 == 4 and rnd > 500:
                self.role = 'attacker'
            else:
                self.role = 'economy'

        # Stuck detection
        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck = 0
        self.last_pos = pos
        if self.stuck > 20:
            self.target = None
            self.chain_mode = False
            self.stuck = 0
            self.explore_idx += 1

        if self.role == 'attacker' and self.harvesters_built >= 3:
            self._attack(c, pos)
            return

        # Economy builder logic
        self._economy(c, pos, rnd)

    # ------------------------------------------------------------ Economy
    def _economy(self, c, pos, rnd):
        # Scan vision for ore tiles
        ore_tiles = []
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
                ore_tiles.append(t)

        # MODE: Building conveyor chain from harvester back to core
        if self.chain_mode:
            self._build_chain(c, pos, rnd)
            return

        # P1: Build harvester on adjacent Ti ore
        if c.get_action_cooldown() == 0:
            ore = self._best_adj_ore(c, pos)
            if ore is not None:
                ti = c.get_global_resources()[0]
                if ti >= c.get_harvester_cost()[0] + 10:
                    c.build_harvester(ore)
                    self.harvesters_built += 1
                    self.target = None
                    # Start chain-building mode
                    if self.core_pos:
                        self.chain_mode = True
                        self.chain_from = ore
                        self.chain_steps = 0
                        self.chain_last_pos = ore  # chain starts at harvester
                    return

        # P2: Pick nearest visible ore to walk toward
        if ore_tiles:
            best, bd = None, 10 ** 9
            for t in ore_tiles:
                d = pos.distance_squared(t)
                if d < bd:
                    best, bd = t, d
            self.target = best
        elif self.target is not None and c.is_in_vision(self.target):
            if c.get_tile_building_id(self.target) is not None:
                self.target = None

        # P3: Navigate toward target or explore
        if self.target is not None:
            self._walk_to(c, pos, self.target)
        else:
            self._explore(c, pos)

    # ------------------------------------------------------- Chain building
    def _build_chain(self, c, pos, rnd):
        """Walk from harvester toward core, building conveyors along the way.

        Strategy: at each tile, build a conveyor facing toward core, then step
        toward core.  When the builder is adjacent to the core the chain is done.
        """
        if not self.core_pos or not self.chain_from:
            self.chain_mode = False
            return

        # Safety: abandon chain after too many steps or if stuck
        if self.chain_steps >= 30:
            self.chain_mode = False
            return

        # Done: adjacent to core (dist_sq <= 8 covers 3x3 footprint adjacency)
        if pos.distance_squared(self.core_pos) <= 8:
            # Build one last conveyor here pointing at core
            d_to_core = pos.direction_to(self.core_pos)
            if d_to_core != Direction.CENTRE and c.get_action_cooldown() == 0:
                # Destroy road if present
                bid = c.get_tile_building_id(pos)
                if bid is not None:
                    try:
                        if c.get_entity_type(bid) == EntityType.ROAD:
                            if c.can_destroy(pos):
                                c.destroy(pos)
                                return
                    except Exception:
                        pass
                if c.can_build_conveyor(pos, d_to_core):
                    c.build_conveyor(pos, d_to_core)
            self.chain_mode = False
            return

        # If on a tile with existing conveyor/splitter heading toward core, done
        bid = c.get_tile_building_id(pos)
        if bid is not None:
            try:
                bt = c.get_entity_type(bid)
                if bt in (EntityType.CONVEYOR, EntityType.SPLITTER):
                    self.chain_mode = False
                    return
            except Exception:
                pass

        d_to_core = pos.direction_to(self.core_pos)
        if d_to_core == Direction.CENTRE:
            self.chain_mode = False
            return

        # Step A: Try to build conveyor at current position facing toward core
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            cc = c.get_conveyor_cost()[0]
            if ti >= cc + 5:
                # Destroy road at current pos if needed
                if bid is not None:
                    try:
                        if c.get_entity_type(bid) == EntityType.ROAD:
                            if c.can_destroy(pos):
                                c.destroy(pos)
                                return
                    except Exception:
                        pass
                if c.can_build_conveyor(pos, d_to_core):
                    c.build_conveyor(pos, d_to_core)
                    self.chain_steps += 1
                    # Now try to move toward core in the same turn
                    if c.get_move_cooldown() == 0 and c.can_move(d_to_core):
                        c.move(d_to_core)
                    return

        # Step B: Move toward core (even if we couldn't build yet)
        if c.get_move_cooldown() == 0:
            for try_d in [d_to_core, d_to_core.rotate_left(), d_to_core.rotate_right()]:
                if c.can_move(try_d):
                    c.move(try_d)
                    return
            # Need to build road to walk
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                rc = c.get_road_cost()[0]
                if ti >= rc + 5:
                    for try_d in [d_to_core, d_to_core.rotate_left(), d_to_core.rotate_right()]:
                        nxt = pos.add(try_d)
                        if c.can_build_road(nxt):
                            c.build_road(nxt)
                            return
            # Try bridge over walls
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                bc = c.get_bridge_cost()[0]
                if ti >= bc + 15:
                    for try_d in [d_to_core, d_to_core.rotate_left(), d_to_core.rotate_right()]:
                        for step in range(2, 4):
                            dx, dy = try_d.delta()
                            bt = Position(pos.x + dx * step, pos.y + dy * step)
                            if bt.distance_squared(pos) > 9:
                                continue
                            for bd in DIRS:
                                bp = pos.add(bd)
                                if c.can_build_bridge(bp, bt):
                                    c.build_bridge(bp, bt)
                                    return

    # --------------------------------------------------------- Walking/Nav
    def _walk_to(self, c, pos, target):
        """Walk toward target, building roads as needed."""
        if c.get_move_cooldown() != 0 and c.get_action_cooldown() != 0:
            return

        d = pos.direction_to(target)
        if d == Direction.CENTRE:
            return

        # Try direct and nearby directions
        for try_d in [d, d.rotate_left(), d.rotate_right(),
                      d.rotate_left().rotate_left(), d.rotate_right().rotate_right()]:
            if c.get_move_cooldown() == 0 and c.can_move(try_d):
                c.move(try_d)
                return

        # Can't move -- build road to make tile walkable
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            rc = c.get_road_cost()[0]
            if ti >= rc + 5:
                for try_d in [d, d.rotate_left(), d.rotate_right()]:
                    nxt = pos.add(try_d)
                    if c.can_build_road(nxt):
                        c.build_road(nxt)
                        return

        # Bridge fallback for walls
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            bc = c.get_bridge_cost()[0]
            if ti >= bc + 20:
                for try_d in [d, d.rotate_left(), d.rotate_right()]:
                    for step in range(2, 4):
                        dx, dy = try_d.delta()
                        bt = Position(pos.x + dx * step, pos.y + dy * step)
                        if bt.distance_squared(pos) > 9:
                            continue
                        for bd in DIRS:
                            bp = pos.add(bd)
                            if c.can_build_bridge(bp, bt):
                                c.build_bridge(bp, bt)
                                return

    def _explore(self, c, pos):
        """Explore outward, rotating direction over time."""
        idx = ((self.my_id or 0) * 3 + self.explore_idx
               + c.get_current_round() // 150) % len(DIRS)
        d = DIRS[idx]
        dx, dy = d.delta()
        far = Position(pos.x + dx * 20, pos.y + dy * 20)
        self._walk_to(c, pos, far)

    # -------------------------------------------------------------- Attack
    def _attack(self, c, pos):
        """Walk toward enemy core, attack enemy buildings."""
        if c.get_action_cooldown() == 0:
            bid = c.get_tile_building_id(pos)
            if bid is not None:
                try:
                    if c.get_team(bid) != c.get_team():
                        if c.can_fire(pos):
                            c.fire(pos)
                            return
                except Exception:
                    pass
        enemy_pos = self._get_enemy_core_pos(c)
        if enemy_pos:
            self._walk_to(c, pos, enemy_pos)

    # ------------------------------------------------------------ Helpers
    def _best_adj_ore(self, c, pos):
        """Find best adjacent ore tile to build harvester on. Prefer closer to core."""
        best, bd = None, 10 ** 9
        for d in Direction:
            p = pos.add(d)
            if c.can_build_harvester(p):
                dist = p.distance_squared(self.core_pos) if self.core_pos else 0
                if dist < bd:
                    best, bd = p, dist
        return best

    def _get_enemy_direction(self, c):
        """Detect map symmetry and return direction toward enemy core."""
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
                return m
        return mirrors[0]
