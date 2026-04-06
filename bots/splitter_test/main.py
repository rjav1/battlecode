"""Splitter test bot - empirically tests whether splitter -> sentinel ammo delivery works."""

import sys
from cambc import Controller, Direction, EntityType, Environment, Position

DIRECTIONS = [d for d in Direction if d != Direction.CENTRE]


def stderr(msg):
    print(msg, file=sys.stderr)


def perp_left(d):
    """Get perpendicular direction (90 degrees left)."""
    return d.rotate_left().rotate_left()


def perp_right(d):
    """Get perpendicular direction (90 degrees right)."""
    return d.rotate_right().rotate_right()


class Player:
    def __init__(self):
        self.spawned = False
        self.step = 0
        self.core_pos = None
        self.harvester_pos = None
        self.ore_pos = None
        self.built = {}
        self.chain_dir = None
        self.branch_dir = None
        self.positions = {}
        self.explore_dir = Direction.NORTH
        self.explore_stuck = 0
        self.last_pos = None

    def run(self, c: Controller) -> None:
        etype = c.get_entity_type()
        if etype == EntityType.CORE:
            if not self.spawned:
                pos = c.get_position()
                for d in Direction:
                    sp = pos.add(d)
                    if c.can_spawn(sp):
                        c.spawn_builder(sp)
                        self.spawned = True
                        stderr(f"Round {c.get_current_round()}: Spawned builder at {sp}")
                        return
        elif etype == EntityType.BUILDER_BOT:
            self._run_builder(c)
        elif etype == EntityType.SENTINEL:
            rnd = c.get_current_round()
            ammo = c.get_ammo_amount()
            ammo_type = c.get_ammo_type()
            stderr(f"Round {rnd}: SENTINEL ammo={ammo} type={ammo_type}")
            if ammo > 0:
                stderr(f"Round {rnd}: *** SUCCESS! AMMO DELIVERED VIA SPLITTER! ***")

    def _run_builder(self, c):
        rnd = c.get_current_round()
        my_pos = c.get_position()

        if self.core_pos is None:
            for eid in c.get_nearby_entities():
                try:
                    if c.get_entity_type(eid) == EntityType.CORE and c.get_team(eid) == c.get_team():
                        self.core_pos = c.get_position(eid)
                        break
                except Exception:
                    pass

        # Always scan for ore
        if self.ore_pos is None:
            for tile in c.get_nearby_tiles():
                try:
                    if c.get_tile_env(tile) == Environment.ORE_TITANIUM:
                        self.ore_pos = tile
                        stderr(f"Round {rnd}: Found Ti ore at {tile}")
                        self.step = 1
                        break
                except Exception:
                    pass

        if self.step == 0:
            self._explore(c, rnd, my_pos)
        elif self.step == 1:
            if my_pos.distance_squared(self.ore_pos) <= 2:
                self.step = 2
            else:
                self._walk_to(c, self.ore_pos, my_pos, rnd)
        elif self.step == 2:
            self._build_harvester(c, rnd, my_pos)
        elif self.step == 3:
            self._build_chain(c, rnd, my_pos)
        elif self.step == 4:
            self._observe(c, rnd, my_pos)

    def _explore(self, c, rnd, my_pos):
        if self.last_pos == my_pos:
            self.explore_stuck += 1
            if self.explore_stuck > 2:
                self.explore_dir = self.explore_dir.rotate_right().rotate_right()
                self.explore_stuck = 0
        else:
            self.explore_stuck = 0
        self.last_pos = my_pos

        w = c.get_map_width()
        h = c.get_map_height()

        def in_bounds(p):
            return 0 <= p.x < w and 0 <= p.y < h

        d = self.explore_dir
        if c.can_move(d):
            c.move(d)
            return
        pos = my_pos.add(d)
        if not in_bounds(pos):
            self.explore_dir = d.rotate_right().rotate_right()
            return
        try:
            if c.get_tile_env(pos) == Environment.WALL:
                self.explore_dir = d.rotate_right().rotate_right()
                return
        except Exception:
            self.explore_dir = d.rotate_right().rotate_right()
            return
        if c.is_tile_empty(pos):
            if c.can_build_road(pos):
                c.build_road(pos)
                if c.can_move(d):
                    c.move(d)
                return
        # Try alternate
        for alt in [d.rotate_right(), d.rotate_left()]:
            pos2 = my_pos.add(alt)
            if not in_bounds(pos2):
                continue
            if c.can_move(alt):
                c.move(alt)
                return
            try:
                if c.is_tile_empty(pos2) and c.can_build_road(pos2):
                    c.build_road(pos2)
                    if c.can_move(alt):
                        c.move(alt)
                    return
            except Exception:
                pass

    def _walk_to(self, c, target, my_pos, rnd):
        d = my_pos.direction_to(target)
        if d == Direction.CENTRE:
            return
        for try_d in [d, d.rotate_left(), d.rotate_right(),
                      d.rotate_left().rotate_left(), d.rotate_right().rotate_right()]:
            if c.can_move(try_d):
                c.move(try_d)
                return
        for try_d in [d, d.rotate_left(), d.rotate_right()]:
            pos = my_pos.add(try_d)
            try:
                if c.is_tile_empty(pos) and c.can_build_road(pos):
                    c.build_road(pos)
                    if c.can_move(try_d):
                        c.move(try_d)
                    return
            except Exception:
                pass

    def _build_harvester(self, c, rnd, my_pos):
        if c.can_build_harvester(self.ore_pos):
            c.build_harvester(self.ore_pos)
            self.harvester_pos = self.ore_pos
            stderr(f"Round {rnd}: Built HARVESTER at {self.ore_pos}")
            self.step = 3
            self._plan_layout(c, rnd, my_pos)
        else:
            if my_pos.distance_squared(self.ore_pos) > 2:
                self._walk_to(c, self.ore_pos, my_pos, rnd)

    def _plan_layout(self, c, rnd, my_pos):
        """Plan positions for all buildings, checking for walls/obstacles."""
        hp = self.harvester_pos
        core = self.core_pos if self.core_pos else Position(hp.x, hp.y + 5)

        # Try different chain directions to find one where all positions are buildable
        # Start with direction toward core
        base_dir = hp.direction_to(core)
        if base_dir == Direction.CENTRE:
            base_dir = Direction.SOUTH

        # Try all 8 directions for the chain
        for i in range(8):
            chain_dir = base_dir
            for _ in range(i):
                chain_dir = chain_dir.rotate_right()

            conv1 = hp.add(chain_dir)
            splitter = conv1.add(chain_dir)

            # Try both perpendicular directions for branch
            for branch_dir in [perp_left(chain_dir), perp_right(chain_dir)]:
                branch = splitter.add(branch_dir)
                sentinel = branch.add(branch_dir)

                # Check all positions are in bounds and empty (or at least potentially buildable)
                try:
                    all_ok = True
                    for p in [conv1, splitter, branch, sentinel]:
                        env = c.get_tile_env(p)
                        if env == Environment.WALL:
                            all_ok = False
                            break
                        # Check it's empty (no existing building)
                        if not c.is_tile_empty(p):
                            all_ok = False
                            break

                    if all_ok:
                        self.chain_dir = chain_dir
                        self.branch_dir = branch_dir
                        self.positions = {
                            "conv1": conv1,
                            "splitter": splitter,
                            "branch": branch,
                            "sentinel": sentinel,
                        }
                        stderr(f"Round {rnd}: Layout plan: chain_dir={chain_dir} branch_dir={branch_dir}")
                        stderr(f"  conv1={conv1} splitter={splitter} branch={branch} sentinel={sentinel}")
                        return
                except Exception:
                    pass

        # Fallback: just use SOUTH chain with WEST branch
        self.chain_dir = Direction.SOUTH
        self.branch_dir = Direction.WEST
        conv1 = hp.add(Direction.SOUTH)
        splitter = conv1.add(Direction.SOUTH)
        branch = splitter.add(Direction.WEST)
        sentinel = branch.add(Direction.WEST)
        self.positions = {"conv1": conv1, "splitter": splitter, "branch": branch, "sentinel": sentinel}
        stderr(f"Round {rnd}: Fallback layout: conv1={conv1} splitter={splitter} branch={branch} sentinel={sentinel}")

    def _build_chain(self, c, rnd, my_pos):
        """Build conv1 -> splitter -> branch -> sentinel one at a time."""
        if not self.positions:
            self._plan_layout(c, rnd, my_pos)
            return

        cd = self.chain_dir
        bd = self.branch_dir

        # Step 1: conv1
        if "conv1" not in self.built:
            pos = self.positions["conv1"]
            if my_pos.distance_squared(pos) > 2:
                self._walk_to(c, pos, my_pos, rnd)
                return
            # If there's an existing building (road from exploration), destroy it first
            bid = c.get_tile_building_id(pos)
            if bid is not None:
                try:
                    btype = c.get_entity_type(bid)
                    if btype == EntityType.ROAD:
                        if c.can_destroy(pos):
                            c.destroy(pos)
                            stderr(f"Round {rnd}: Destroyed road at {pos} to make room for conv1")
                            return
                except Exception:
                    pass
            if c.is_tile_empty(pos) and c.can_build_conveyor(pos, cd):
                eid = c.build_conveyor(pos, cd)
                self.built["conv1"] = eid
                stderr(f"Round {rnd}: Built CONV1 at {pos} facing {cd}")
            else:
                stderr(f"Round {rnd}: Can't build conv1 at {pos} empty={c.is_tile_empty(pos)} bid={c.get_tile_building_id(pos)} dist={my_pos.distance_squared(pos)}, replanning")
                self.positions = {}
            return

        # Step 2: splitter
        if "splitter" not in self.built:
            pos = self.positions["splitter"]
            if my_pos.distance_squared(pos) > 2:
                self._walk_to(c, pos, my_pos, rnd)
                return
            if c.is_tile_empty(pos) and c.can_build_splitter(pos, cd):
                eid = c.build_splitter(pos, cd)
                self.built["splitter"] = eid
                stderr(f"Round {rnd}: Built SPLITTER at {pos} facing {cd}")
            else:
                stderr(f"Round {rnd}: Can't build splitter at {pos}")
            return

        # Step 3: branch conveyor
        if "branch" not in self.built:
            pos = self.positions["branch"]
            if my_pos.distance_squared(pos) > 2:
                self._walk_to(c, pos, my_pos, rnd)
                return
            if c.is_tile_empty(pos) and c.can_build_conveyor(pos, bd):
                eid = c.build_conveyor(pos, bd)
                self.built["branch"] = eid
                stderr(f"Round {rnd}: Built BRANCH at {pos} facing {bd}")
            else:
                stderr(f"Round {rnd}: Can't build branch at {pos}")
            return

        # Step 4: sentinel
        if "sentinel" not in self.built:
            pos = self.positions["sentinel"]
            if my_pos.distance_squared(pos) > 2:
                self._walk_to(c, pos, my_pos, rnd)
                return

            # Face the sentinel in the branch direction (away from where ammo enters)
            # Ammo enters from branch_dir.opposite(), so facing branch_dir ensures
            # the ammo side is NOT the facing side -> accepted
            face = bd
            if c.is_tile_empty(pos) and c.can_build_sentinel(pos, face):
                eid = c.build_sentinel(pos, face)
                self.built["sentinel"] = eid
                stderr(f"Round {rnd}: Built SENTINEL at {pos} facing {face}")
                stderr(f"Round {rnd}: INFRASTRUCTURE COMPLETE! Watching for ammo...")
                self.step = 4
            else:
                # Try all faces
                for d in DIRECTIONS:
                    if d == bd.opposite():
                        continue  # skip facing toward ammo (would block delivery)
                    if c.is_tile_empty(pos) and c.can_build_sentinel(pos, d):
                        eid = c.build_sentinel(pos, d)
                        self.built["sentinel"] = eid
                        stderr(f"Round {rnd}: Built SENTINEL at {pos} facing {d} (alt)")
                        self.step = 4
                        return
                stderr(f"Round {rnd}: Can't build sentinel at {pos}")
            return

    def _observe(self, c, rnd, my_pos):
        if rnd % 4 == 0:
            ti, ax = c.get_global_resources()
            stderr(f"Round {rnd}: Ti={ti} Ax={ax}")
            for eid in c.get_nearby_buildings():
                try:
                    etype = c.get_entity_type(eid)
                    epos = c.get_position(eid)
                    if etype == EntityType.SPLITTER:
                        res = c.get_stored_resource(eid)
                        stderr(f"  Splitter@{epos} stored={res}")
                    elif etype == EntityType.CONVEYOR:
                        res = c.get_stored_resource(eid)
                        d = c.get_direction(eid)
                        stderr(f"  Conv@{epos} dir={d} stored={res}")
                    elif etype == EntityType.HARVESTER:
                        stderr(f"  Harv@{epos}")
                except Exception:
                    pass
