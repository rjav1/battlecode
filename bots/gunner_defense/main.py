"""Gunner Defense bot -- cheap turret spam with automatic ammo via conveyors.

Strategy:
- 4 builders, d.opposite() conveyor economy (roads for exploration)
- After round 150, one builder places 3-4 gunners at chokepoints facing enemy
- Gunners sit on existing conveyor chains = automatic Ti ammo from harvesters
- Auto-fire: get_gunner_target() -> fire() every round
- 10 Ti cost, 2 ammo/shot, fires every round = 5x DPS per Ti vs sentinels
"""

from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]


class Player:
    def __init__(self):
        self.core_pos = None
        self.enemy_dir = None
        self.target = None
        self.stuck = 0
        self.last_pos = None
        self.explore_idx = 0
        self.my_id = None
        self.harvesters_built = 0
        self.role = None
        self._w = None
        self._h = None
        self._spawn_count = 0
        # Gunner builder state
        self.gunner_targets = []
        self.gunner_idx = 0
        self.gunners_built = 0

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)
        elif t == EntityType.GUNNER:
            self._gunner(c)

    # ------------------------------------------------------------------ Core
    def _core(self, c):
        if self.core_pos is None:
            self.core_pos = c.get_position()
            self._w = c.get_map_width()
            self._h = c.get_map_height()
            self.enemy_dir = self.core_pos.direction_to(
                Position(self._w // 2, self._h // 2))
            if self.enemy_dir == Direction.CENTRE:
                self.enemy_dir = Direction.EAST

        if c.get_action_cooldown() != 0:
            return
        if self._spawn_count >= 4:
            return
        ti = c.get_global_resources()[0]
        cost = c.get_builder_bot_cost()[0]
        if ti < cost + 20:
            return
        pos = c.get_position()
        for d in DIRS:
            sp = pos.add(d)
            if c.can_spawn(sp):
                c.spawn_builder(sp)
                self._spawn_count += 1
                return

    # ------------------------------------------------------------------ Gunner
    def _gunner(self, c):
        if c.get_action_cooldown() != 0:
            return
        if c.get_ammo_amount() < 2:
            return
        tgt = c.get_gunner_target()
        if tgt is not None and c.can_fire(tgt):
            c.fire(tgt)

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
                        self.enemy_dir = self.core_pos.direction_to(
                            Position(self._w // 2, self._h // 2))
                        if self.enemy_dir == Direction.CENTRE:
                            self.enemy_dir = Direction.EAST
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

        # Role assignment: builder 0 becomes gunner_builder after round 150
        if self.role is None:
            if self.my_id is not None and self.my_id % 4 == 0:
                self.role = "gunner_builder"
            else:
                self.role = "miner"

        if self.role == "gunner_builder" and rnd >= 150:
            self._build_gunners(c, pos, rnd)
        else:
            self._mine(c, pos)

    # ------------------------------------------------------------------ Mining
    def _mine(self, c, pos):
        if c.get_action_cooldown() == 0:
            ore = self._best_adj_ore(c, pos)
            if ore is not None:
                ti = c.get_global_resources()[0]
                if ti >= c.get_harvester_cost()[0] + 15:
                    c.build_harvester(ore)
                    self.harvesters_built += 1
                    self.target = None
                    return

        ore_tiles = []
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
                ore_tiles.append(t)

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
            self._nav(c, pos, self.target)
        else:
            self._explore(c, pos)

    # ------------------------------------------------------------------ Gunner placement
    def _build_gunners(self, c, pos, rnd):
        """Place gunners adjacent to existing conveyor chains, facing enemy."""
        # First, still mine if we haven't built harvesters
        if self.harvesters_built < 2:
            self._mine(c, pos)
            return

        # Plan gunner targets if not yet done
        if not self.gunner_targets and self.core_pos and self.enemy_dir:
            self._plan_gunner_positions(c)

        if self.gunner_idx >= len(self.gunner_targets):
            # All gunners placed, become miner again
            self.role = "miner"
            self._mine(c, pos)
            return

        target_pos, target_dir = self.gunner_targets[self.gunner_idx]

        # Skip if occupied
        try:
            if c.is_in_vision(target_pos) and c.get_tile_building_id(target_pos) is not None:
                self.gunner_idx += 1
                return
        except Exception:
            pass

        # Walk to target
        if pos.distance_squared(target_pos) > 2:
            self._nav(c, pos, target_pos)
            return

        if c.get_action_cooldown() != 0:
            return

        ti = c.get_global_resources()[0]
        if ti < c.get_gunner_cost()[0] + 20:
            return

        # Try building with planned direction
        if c.can_build_gunner(target_pos, target_dir):
            c.build_gunner(target_pos, target_dir)
            self.gunner_idx += 1
            self.gunners_built += 1
            return

        # Try alternative directions facing generally toward enemy
        for d in self._enemy_facing_dirs():
            if c.can_build_gunner(target_pos, d):
                c.build_gunner(target_pos, d)
                self.gunner_idx += 1
                self.gunners_built += 1
                return

        # Can't build here, skip
        self.gunner_idx += 1

    def _plan_gunner_positions(self, c):
        """Find positions adjacent to our conveyor chains, facing enemy approach.

        Gunners need to be on a conveyor chain (or adjacent to one with conveyors
        feeding into them) for automatic ammo delivery. We look for existing
        conveyors and pick tiles next to them that have clear line of sight
        toward the enemy.
        """
        core = self.core_pos
        ed = self.enemy_dir
        w, h = self._w, self._h

        # Find all our conveyors in vision
        our_conveyors = []
        for eid in c.get_nearby_buildings():
            try:
                if (c.get_entity_type(eid) == EntityType.CONVEYOR
                        and c.get_team(eid) == c.get_team()):
                    our_conveyors.append(c.get_position(eid))
            except Exception:
                continue

        candidates = []

        # Strategy 1: Place gunners on tiles adjacent to conveyors,
        # on the enemy-facing side of our economy
        for conv_pos in our_conveyors:
            # Only consider conveyors that are between core and enemy
            if core:
                d_to_enemy = conv_pos.distance_squared(self._enemy_mirror())
                d_core_enemy = core.distance_squared(self._enemy_mirror())
                # Conveyor should be on the enemy-facing half
                if d_to_enemy > d_core_enemy:
                    continue

            # Try placing gunner on tiles adjacent to this conveyor
            for d in DIRS:
                gp = conv_pos.add(d)
                if not self._in_bounds(gp):
                    continue
                try:
                    if not c.is_in_vision(gp):
                        continue
                    if not c.is_tile_empty(gp):
                        continue
                    if c.get_tile_env(gp) == Environment.WALL:
                        continue
                except Exception:
                    continue

                # Score: prefer tiles closer to enemy approach and farther from core
                score = 0
                if core:
                    score += gp.distance_squared(core)  # farther from core = better
                    score -= gp.distance_squared(self._enemy_mirror()) // 2

                candidates.append((score, gp))

        # Strategy 2: If no good conveyor-adjacent spots, plan positions
        # along the enemy approach where we can build conveyor + gunner
        if len(candidates) < 2 and core:
            for dist in [4, 5, 6]:
                p = core
                for _ in range(dist):
                    p = p.add(ed)
                if self._in_bounds(p):
                    try:
                        if c.is_in_vision(p) and c.is_tile_empty(p):
                            candidates.append((dist * 10, p))
                    except Exception:
                        pass
                # Also try perpendicular offsets
                for side in [ed.rotate_left().rotate_left(),
                             ed.rotate_right().rotate_right()]:
                    sp = p.add(side)
                    if self._in_bounds(sp):
                        try:
                            if c.is_in_vision(sp) and c.is_tile_empty(sp):
                                candidates.append((dist * 10 - 1, sp))
                        except Exception:
                            pass

        # Sort by score descending, take top 4
        candidates.sort(key=lambda x: -x[0])

        # Deduplicate
        seen = set()
        targets = []
        for score, gp in candidates:
            key = (gp.x, gp.y)
            if key in seen:
                continue
            seen.add(key)
            # Face toward enemy
            face_dir = gp.direction_to(self._enemy_mirror())
            if face_dir == Direction.CENTRE:
                face_dir = ed
            targets.append((gp, face_dir))
            if len(targets) >= 4:
                break

        self.gunner_targets = targets

    def _enemy_mirror(self):
        """Estimate enemy core position from map symmetry."""
        if not self.core_pos:
            return Position(self._w // 2, self._h // 2)
        cx, cy = self.core_pos.x, self.core_pos.y
        w, h = self._w, self._h
        return Position(w - 1 - cx, h - 1 - cy)

    def _enemy_facing_dirs(self):
        """Return directions roughly facing toward enemy."""
        ed = self.enemy_dir
        if not ed:
            return DIRS
        return [ed, ed.rotate_left(), ed.rotate_right(),
                ed.rotate_left().rotate_left(), ed.rotate_right().rotate_right()]

    # ------------------------------------------------------------------ Navigation
    def _nav(self, c, pos, target):
        """Navigate toward target, building conveyors with d.opposite() facing."""
        dirs = self._rank(pos, target)
        w, h = self._w or c.get_map_width(), self._h or c.get_map_height()

        for d in dirs:
            nxt = pos.add(d)
            if nxt.x < 0 or nxt.x >= w or nxt.y < 0 or nxt.y >= h:
                continue
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                cc = c.get_conveyor_cost()[0]
                if ti >= cc + 10:
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
            if ti >= rc + 10:
                for d in dirs:
                    nxt = pos.add(d)
                    if not self._in_bounds(nxt):
                        continue
                    if c.can_build_road(nxt):
                        c.build_road(nxt)
                        return

    def _explore(self, c, pos):
        idx = ((self.my_id or 0) * 3 + self.explore_idx
               + c.get_current_round() // 150) % len(DIRS)
        d = DIRS[idx]
        dx, dy = d.delta()
        far = Position(pos.x + dx * 15, pos.y + dy * 15)
        self._nav(c, pos, far)

    def _best_adj_ore(self, c, pos):
        best, bd = None, 10**9
        for d in Direction:
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

    def _in_bounds(self, p):
        return 0 <= p.x < (self._w or 50) and 0 <= p.y < (self._h or 50)
