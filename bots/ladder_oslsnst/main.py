"""ladder_oslsnst: Models oslsnst dual strategy.
Tight maps: 2 attackers walk to enemy core, build gunner, feed ammo.
Open maps: pure economy 6 builders.
"""
from collections import deque
from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]


def _bfs(c, start, goal_fn, passable_fn, max_dist=200):
    visited = {start}
    q = deque([(start, [])])
    while q:
        pos, path = q.popleft()
        if goal_fn(pos):
            return path
        if len(path) >= max_dist:
            continue
        for d in DIRS:
            nb = pos.add(d)
            if nb not in visited and passable_fn(nb):
                visited.add(nb)
                q.append((nb, path + [d]))
    return []


class Player:
    def __init__(self):
        self.core_pos = None
        self.my_id = None
        self.map_mode = None
        self.enemy_core = None
        self.target = None
        self.harvesters_built = 0
        self.gunner_built = False
        self.role = None  # 'attacker' or 'eco'

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)

    def _core(self, c):
        if self.map_mode is None:
            w, h = c.get_map_width(), c.get_map_height()
            area = w * h
            short_dim = min(w, h)
            self.map_mode = 'tight' if (area <= 625 or short_dim <= 22) else 'open'
            self.core_pos = c.get_position()
            # Infer enemy core (rotation symmetry fallback to reflection)
            cx, cy = self.core_pos.x, self.core_pos.y
            mx, my = (w - 1) / 2, (h - 1) / 2
            self.enemy_core = Position(round(2 * mx - cx), round(2 * my - cy))

        rnd = c.get_current_round()
        ti = c.get_global_resources()[0]
        n = c.get_unit_count()
        pos = c.get_position()

        # Tight: spawn 2 attackers + 1 eco, Open: spawn up to 6 eco builders
        cap = 3 if self.map_mode == 'tight' else 7
        if n < cap and ti >= 30:
            for d in DIRS:
                sp = pos.add(d)
                if c.can_spawn(sp):
                    c.spawn_builder(sp)
                    break

    def _builder(self, c):
        if self.core_pos is None:
            # Find core
            for bid in c.get_nearby_buildings():
                if c.get_entity_type(bid) == EntityType.CORE and c.get_team(bid) == c.get_team():
                    self.core_pos = c.get_position(bid)
                    break
            if self.core_pos is None:
                return

        if self.my_id is None:
            self.my_id = c.get_id()
            w, h = c.get_map_width(), c.get_map_height()
            area = w * h
            short_dim = min(w, h)
            self.map_mode = 'tight' if (area <= 625 or short_dim <= 22) else 'open'
            cx, cy = self.core_pos.x, self.core_pos.y
            mx, my = (w - 1) / 2, (h - 1) / 2
            self.enemy_core = Position(round(2 * mx - cx), round(2 * my - cy))
            # Assign role: first 2 builders attack on tight maps
            mid = self.my_id % 10
            if self.map_mode == 'tight' and mid < 4:
                self.role = 'attacker'
            else:
                self.role = 'eco'

        if self.role == 'attacker':
            self._attack(c)
        else:
            self._eco(c)

    def _attack(self, c):
        rnd = c.get_current_round()
        pos = c.get_position()
        ti = c.get_global_resources()[0]

        # Wait until round 30 then move toward enemy
        if rnd < 30:
            return

        ec = self.enemy_core
        if ec is None:
            return

        # Build gunner if close enough and not yet built
        if not self.gunner_built and pos.distance_squared(ec) <= 20 and ti >= 10:
            facing = pos.direction_to(ec)
            for d in DIRS:
                gp = pos.add(d)
                if c.can_build_gunner(gp, facing):
                    c.build_gunner(gp, facing)
                    self.gunner_built = True
                    return

        # Feed ammo (Ti stacks): build conveyor toward gunner if adjacent
        if self.gunner_built:
            # Stay near gunner to feed ammo via conveyors — just stay put
            return

        # Navigate toward enemy core along conveyors/roads
        def passable(p):
            try:
                env = c.get_tile_env(p)
                if env == Environment.WALL:
                    return False
                bid = c.get_tile_building_id(p)
                if bid is not None:
                    bt = c.get_entity_type(bid)
                    if bt in (EntityType.CONVEYOR, EntityType.ROAD,
                               EntityType.ARMOURED_CONVEYOR, EntityType.CORE):
                        return True
                    return False
                return False
            except Exception:
                return False

        if c.get_move_cooldown() > 0:
            return

        # Build road forward if stuck
        best_d = pos.direction_to(ec)
        for d in [best_d, best_d.rotate_left(), best_d.rotate_right()]:
            np = pos.add(d)
            if c.can_move(d):
                c.move(d)
                return
            if ti >= 5:
                try:
                    if c.can_build_road(np):
                        c.build_road(np)
                        return
                except Exception:
                    pass

    def _eco(self, c):
        pos = c.get_position()
        ti = c.get_global_resources()[0]

        if c.get_move_cooldown() > 0 and c.get_action_cooldown() > 0:
            return

        # Find nearest unoccupied ore
        if self.target is None or c.get_action_cooldown() == 0:
            best = None
            best_d = 999999
            for tp in c.get_nearby_tiles():
                env = c.get_tile_env(tp)
                if env == Environment.ORE_TITANIUM:
                    bid = c.get_tile_building_id(tp)
                    if bid is None:
                        d = pos.distance_squared(tp)
                        if d < best_d:
                            best_d = d
                            best = tp
            if best:
                self.target = best

        if self.target is None:
            return

        # If on target, build harvester
        if pos == self.target:
            if c.get_action_cooldown() == 0 and ti >= 20:
                if c.can_build_harvester(pos):
                    c.build_harvester(pos)
                    self.harvesters_built += 1
                    self.target = None
                    return
            # Build conveyor back toward core
            if c.get_action_cooldown() == 0 and ti >= 3:
                core_d = pos.direction_to(self.core_pos)
                back = core_d.opposite()
                cp = pos.add(back)
                try:
                    if c.can_build_conveyor(cp, back.opposite()):
                        c.build_conveyor(cp, back.opposite())
                except Exception:
                    pass
            return

        # Navigate to target using d.opposite() conveyors
        if c.get_move_cooldown() > 0:
            return

        target_d = pos.direction_to(self.target)
        np = pos.add(target_d)

        if c.can_move(target_d):
            c.move(target_d)
        elif ti >= 3:
            try:
                if c.can_build_conveyor(np, target_d.opposite()):
                    c.build_conveyor(np, target_d.opposite())
            except Exception:
                pass
