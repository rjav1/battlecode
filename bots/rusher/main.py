"""Rusher bot -- infrastructure sabotage + economy.

Economy: find Ti ore, build harvester, lay conveyor chain to core.
Attack: rush to enemy, walk on/destroy their conveyors and roads.
"""

import sys
from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]


class Player:
    def __init__(self):
        self.core_pos = None
        self.enemy_core_pos = None
        self.my_id = None
        self.role = None
        self.target = None
        self.last_pos = None
        self.stuck = 0
        self.harvesters_built = 0
        # Chain state: build conveyors from harvester_pos toward core
        self.chain_target = None   # harvester position
        self.chain_cursor = None   # where the next conveyor goes
        self.chain_count = 0
        self._w = None
        self._h = None
        self._spawn_count = 0
        self._sym_candidates = None
        self._my_sym_idx = 0
        self._born_round = None

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)
        elif t == EntityType.GUNNER:
            self._gunner_act(c)

    # ------------------------------------------------------------------ Core
    def _core(self, c):
        if self.core_pos is None:
            self.core_pos = c.get_position()
        if self._w is None:
            self._w = c.get_map_width()
            self._h = c.get_map_height()

        if c.get_action_cooldown() != 0:
            return

        units = c.get_unit_count()
        if units >= 50:
            return

        rnd = c.get_current_round()
        ti = c.get_global_resources()[0]
        cost = c.get_builder_bot_cost()[0]

        if rnd <= 8:
            if units - 1 >= 4:
                return
            if ti < cost:
                return
        else:
            cap = 6 if rnd <= 100 else 8 if rnd <= 300 else 10
            if units - 1 >= cap:
                return
            if ti < cost + 60:
                return

        pos = c.get_position()
        for d in DIRS:
            sp = pos.add(d)
            if c.can_spawn(sp):
                c.spawn_builder(sp)
                self._spawn_count += 1
                return

    # -------------------------------------------------------------- Gunner
    def _gunner_act(self, c):
        if c.get_action_cooldown() != 0 or c.get_ammo_amount() < 2:
            return
        tgt = c.get_gunner_target()
        if tgt is not None and c.can_fire(tgt):
            c.fire(tgt)

    # --------------------------------------------------------------- Builder
    def _builder(self, c):
        pos = c.get_position()
        rnd = c.get_current_round()

        if self.my_id is None:
            self.my_id = c.get_id()
        if self._born_round is None:
            self._born_round = rnd
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

        if self._sym_candidates is None and self.core_pos:
            cx, cy = self.core_pos.x, self.core_pos.y
            w, h = self._w, self._h
            self._sym_candidates = [
                Position(w - 1 - cx, h - 1 - cy),
                Position(w - 1 - cx, cy),
                Position(cx, h - 1 - cy),
            ]

        for eid in c.get_nearby_entities():
            try:
                if (c.get_entity_type(eid) == EntityType.CORE
                        and c.get_team(eid) != c.get_team()):
                    self.enemy_core_pos = c.get_position(eid)
                    break
            except Exception:
                continue

        if self.role is None:
            if self._born_round <= 2:
                self.role = 'economy'
            else:
                self.role = 'attacker'
                self._my_sym_idx = (self.my_id or 0) % 3

        # Stuck
        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck = 0
        self.last_pos = pos

        if self.stuck > 15:
            self.target = None
            self.chain_target = None
            self.stuck = 0
            if self.role == 'attacker':
                self._my_sym_idx = (self._my_sym_idx + 1) % 3
            if self.role == 'economy' and hasattr(self, '_explore_dir_idx'):
                self._explore_dir_idx = (self._explore_dir_idx + 1) % len(DIRS)

        if self.role == 'economy':
            self._economy(c, pos, rnd)
        else:
            self._attack(c, pos, rnd)

    # ------------------------------------------------------------ Economy
    def _economy(self, c, pos, rnd):
        # Chain-building mode: building conveyors from harvester to core
        if self.chain_target is not None:
            self._build_chain(c, pos, rnd)
            return

        # Build harvester on adjacent Ti ore
        if c.get_action_cooldown() == 0 and self.harvesters_built < 4:
            for d in Direction:
                t = pos.add(d)
                try:
                    if not c.can_build_harvester(t):
                        continue
                    if c.get_tile_env(t) != Environment.ORE_TITANIUM:
                        continue
                except Exception:
                    continue
                ti = c.get_global_resources()[0]
                if ti >= c.get_harvester_cost()[0]:
                    c.build_harvester(t)
                    self.harvesters_built += 1
                    self.target = None
                    # Set up chain: cursor starts at harvester, go toward core
                    if self.core_pos:
                        # Find the first conveyor position: adjacent to harvester, toward core
                        d_to_core = t.direction_to(self.core_pos)
                        if d_to_core != Direction.CENTRE:
                            first_conv = t.add(d_to_core)
                            self.chain_target = t  # harvester pos
                            self.chain_cursor = first_conv
                            self.chain_count = 0
                    return

        # Walk toward nearest Ti ore
        best_ore = None
        best_dist = 10**9
        for t in c.get_nearby_tiles():
            try:
                e = c.get_tile_env(t)
                if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
                    d = pos.distance_squared(t)
                    if d < best_dist:
                        best_dist = d
                        best_ore = t
            except Exception:
                continue

        if best_ore:
            self.target = best_ore
        elif self.target:
            try:
                if c.is_in_vision(self.target) and c.get_tile_building_id(self.target) is not None:
                    self.target = None
            except Exception:
                self.target = None

        if self.target:
            self._walk_to(c, pos, self.target)
        else:
            self._explore_for_ore(c, pos)

    # ------------------------------------------------------- Chain building
    def _build_chain(self, c, pos, rnd):
        """Build conveyors one at a time from harvester toward core.

        chain_cursor = the next position where a conveyor should go.
        Builder walks to within action range of cursor, builds conveyor,
        then advances cursor toward core.
        """
        if not self.core_pos:
            self.chain_target = None
            return
        if self.chain_count >= 25:
            self.chain_target = None
            return

        cursor = self.chain_cursor
        if cursor is None:
            self.chain_target = None
            return

        # Check if cursor is on/adjacent to core (chain complete)
        cdx = abs(cursor.x - self.core_pos.x)
        cdy = abs(cursor.y - self.core_pos.y)
        if cdx <= 1 and cdy <= 1:
            # Cursor is ON the core footprint -- build last conveyor before core
            # The last conveyor should be 1 step before cursor, but cursor
            # IS on the core, so the previous conveyor already outputs into core.
            # Chain is complete!
            self.chain_target = None
            return

        # Need to be within action range (r^2=2) of cursor to build there
        dsq = pos.distance_squared(cursor)
        if dsq > 2:
            # Walk toward cursor
            self._walk_to(c, pos, cursor)
            return

        if c.get_action_cooldown() != 0:
            return

        ti = c.get_global_resources()[0]
        cc = c.get_conveyor_cost()[0]
        if ti < cc + 3:
            return

        # Check cursor tile
        try:
            env = c.get_tile_env(cursor)
            if env == Environment.WALL:
                # Try adjacent tiles
                d_to_core = cursor.direction_to(self.core_pos)
                for alt_d in [d_to_core.rotate_left(), d_to_core.rotate_right()]:
                    alt = Position(cursor.x + alt_d.delta()[0], cursor.y + alt_d.delta()[1])
                    try:
                        if c.get_tile_env(alt) != Environment.WALL:
                            self.chain_cursor = alt
                            return
                    except Exception:
                        continue
                self.chain_target = None
                return
        except Exception:
            self.chain_target = None
            return

        # Check for existing building at cursor
        bid = c.get_tile_building_id(cursor)
        if bid is not None:
            try:
                bt = c.get_entity_type(bid)
                if bt == EntityType.ROAD:
                    if c.can_destroy(cursor):
                        c.destroy(cursor)
                        return
                elif bt in (EntityType.CONVEYOR, EntityType.SPLITTER):
                    # Chain connects to existing infrastructure!
                    self.chain_target = None
                    return
                else:
                    # Skip this tile
                    d_to_core = cursor.direction_to(self.core_pos)
                    if d_to_core != Direction.CENTRE:
                        self.chain_cursor = cursor.add(d_to_core)
                    else:
                        self.chain_target = None
                    return
            except Exception:
                pass

        # Build conveyor at cursor facing toward core
        d_to_core = cursor.direction_to(self.core_pos)
        if d_to_core == Direction.CENTRE:
            self.chain_target = None
            return

        if c.can_build_conveyor(cursor, d_to_core):
            c.build_conveyor(cursor, d_to_core)
            self.chain_count += 1
            # Advance cursor
            nxt = cursor.add(d_to_core)
            self.chain_cursor = nxt
            # Move onto the new conveyor so we can reach the next cursor
            d_to_conv = pos.direction_to(cursor)
            if d_to_conv != Direction.CENTRE and c.can_move(d_to_conv):
                c.move(d_to_conv)
        else:
            # Can't build here, try alternate
            for alt_d in [d_to_core.rotate_left(), d_to_core.rotate_right()]:
                alt = cursor.add(alt_d)
                if c.can_build_conveyor(cursor, alt_d):
                    c.build_conveyor(cursor, alt_d)
                    self.chain_count += 1
                    self.chain_cursor = alt
                    d_to_conv = pos.direction_to(cursor)
                    if d_to_conv != Direction.CENTRE and c.can_move(d_to_conv):
                        c.move(d_to_conv)
                    return
            # Give up
            self.chain_target = None

    # ------------------------------------------------------------ Attack
    def _attack(self, c, pos, rnd):
        # If on enemy building, attack it
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            if ti >= 2:
                bid = c.get_tile_building_id(pos)
                if bid is not None:
                    try:
                        if c.get_team(bid) != c.get_team():
                            if c.can_fire(pos):
                                c.fire(pos)
                                return
                    except Exception:
                        pass

        # Find walkable enemy buildings
        best_target = None
        best_prio = -1
        best_dist = 10**9

        for eid in c.get_nearby_entities():
            try:
                if c.get_team(eid) != c.get_team():
                    etype = c.get_entity_type(eid)
                    epos = c.get_position(eid)

                    if etype in (EntityType.CONVEYOR, EntityType.SPLITTER,
                                 EntityType.ARMOURED_CONVEYOR):
                        prio = 5
                    elif etype == EntityType.ROAD:
                        prio = 4
                    elif etype == EntityType.CORE:
                        prio = 1
                        self.enemy_core_pos = epos
                    else:
                        prio = 0

                    dist = pos.distance_squared(epos)
                    if prio > best_prio or (prio == best_prio and dist < best_dist):
                        best_target = epos
                        best_prio = prio
                        best_dist = dist
            except Exception:
                continue

        if best_target and best_prio >= 4:
            self.target = best_target
            if pos.distance_squared(best_target) <= 2:
                d = pos.direction_to(best_target)
                if d != Direction.CENTRE and c.can_move(d):
                    c.move(d)
                    return
            self._walk_to(c, pos, best_target)
            return

        rush_target = self.enemy_core_pos
        if rush_target is None and self._sym_candidates:
            rush_target = self._sym_candidates[self._my_sym_idx]

        if rush_target:
            self.target = rush_target
            self._walk_to(c, pos, rush_target)
        else:
            self._explore(c, pos)

    # --------------------------------------------------------- Navigation
    def _walk_to(self, c, pos, target):
        if c.get_move_cooldown() != 0:
            return

        d = pos.direction_to(target)
        if d == Direction.CENTRE:
            return

        attempts = [d, d.rotate_left(), d.rotate_right(),
                    d.rotate_left().rotate_left(), d.rotate_right().rotate_right()]

        for try_d in attempts:
            nxt = pos.add(try_d)
            if not self._in_bounds(nxt):
                continue

            if c.can_move(try_d):
                c.move(try_d)
                return

            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                rc = c.get_road_cost()[0]
                # Attackers need more Ti reserve to avoid starving economy
                min_reserve = 30 if self.role == 'attacker' else 5
                if ti >= rc + min_reserve:
                    try:
                        if c.get_tile_env(nxt) == Environment.WALL:
                            continue
                    except Exception:
                        continue
                    if c.can_build_road(nxt):
                        c.build_road(nxt)
                        if c.can_move(try_d):
                            c.move(try_d)
                        return

    def _explore(self, c, pos):
        if self._sym_candidates:
            self._walk_to(c, pos, self._sym_candidates[0])
        elif self._w and self._h:
            self._walk_to(c, pos, Position(self._w // 2, self._h // 2))

    def _explore_for_ore(self, c, pos):
        """Economy builder: walk away from core to find ore tiles."""
        if not self.core_pos:
            self._explore(c, pos)
            return

        # Simply walk away from core. Different builders go different dirs.
        if not hasattr(self, '_explore_dir_idx'):
            self._explore_dir_idx = (self.my_id or 0) % len(DIRS)

        d = DIRS[self._explore_dir_idx]
        dx, dy = d.delta()
        dist = 12
        tgt = Position(
            max(1, min(self._w - 2, self.core_pos.x + dx * dist)),
            max(1, min(self._h - 2, self.core_pos.y + dy * dist))
        )

        # If we've reached this target, rotate
        if pos.distance_squared(tgt) <= 4:
            self._explore_dir_idx = (self._explore_dir_idx + 1) % len(DIRS)

        self._walk_to(c, pos, tgt)

    def _in_bounds(self, p):
        return 0 <= p.x < self._w and 0 <= p.y < self._h
