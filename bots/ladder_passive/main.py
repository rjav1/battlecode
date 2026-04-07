"""ladder_passive: Ultra-minimal eco bot. 2 builders, zero military.
Nearest-ore targeting, d.opposite() conveyors only.
Tests whether buzzing's extra features help vs minimal strategy.
"""
from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]


class Player:
    def __init__(self):
        self.core_pos = None
        self.my_id = None
        self.target = None
        self.harvesters_built = 0
        self.ore_cap = 4
        self.explore_idx = 0
        self.stuck = 0
        self.last_pos = None

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)

    def _core(self, c):
        ti = c.get_global_resources()[0]
        if c.get_unit_count() < 3 and ti >= 30 and c.get_action_cooldown() == 0:
            pos = c.get_position()
            for d in DIRS:
                if c.can_spawn(pos.add(d)):
                    c.spawn_builder(pos.add(d))
                    return

    def _builder(self, c):
        if self.my_id is None:
            self.my_id = c.get_id()
        if self.core_pos is None:
            for eid in c.get_nearby_entities():
                try:
                    if c.get_entity_type(eid) == EntityType.CORE and c.get_team(eid) == c.get_team():
                        self.core_pos = c.get_position(eid)
                        break
                except Exception:
                    continue
            if self.core_pos is None:
                return

        pos = c.get_position()
        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck = 0
        self.last_pos = pos
        if self.stuck > 6:
            self.target = None
            self.stuck = 0
            self.explore_idx += 1

        ore_tiles = []
        for tp in c.get_nearby_tiles():
            try:
                if (c.get_tile_env(tp) == Environment.ORE_TITANIUM
                        and c.get_tile_building_id(tp) is None):
                    ore_tiles.append(tp)
            except Exception:
                pass

        ti = c.get_global_resources()[0]
        rnd = c.get_current_round()

        # Build harvester on adjacent ore
        if c.get_action_cooldown() == 0 and self.harvesters_built < self.ore_cap:
            for tp in ore_tiles:
                if pos.distance_squared(tp) <= 2 and ti >= 20:
                    if c.can_build_harvester(tp):
                        c.build_harvester(tp)
                        self.harvesters_built += 1
                        self.target = None
                        return

        # Pick nearest target ore
        if ore_tiles:
            best, best_d = None, 999999
            for tp in ore_tiles:
                d = pos.distance_squared(tp)
                if d < best_d:
                    best_d, best = d, tp
            if self.harvesters_built < self.ore_cap:
                self.target = best

        if self.target:
            self._nav(c, pos, self.target, ti)
        else:
            self._explore(c, pos, ti, rnd)

    def _nav(self, c, pos, target, ti, ti_reserve=5):
        w, h = c.get_map_width(), c.get_map_height()
        dirs = sorted(DIRS, key=lambda d: pos.add(d).distance_squared(target))
        for d in dirs:
            nxt = pos.add(d)
            if not (0 <= nxt.x < w and 0 <= nxt.y < h):
                continue
            cc = c.get_conveyor_cost()[0]
            if c.get_action_cooldown() == 0 and ti >= cc + ti_reserve:
                if c.can_build_conveyor(nxt, d.opposite()):
                    c.build_conveyor(nxt, d.opposite())
                    return
            if c.get_move_cooldown() == 0 and c.can_move(d):
                c.move(d)
                return

    def _explore(self, c, pos, ti, rnd):
        w, h = c.get_map_width(), c.get_map_height()
        mid = self.my_id or 0
        sector = (mid * 7 + self.explore_idx * 3 + rnd // 50) % len(DIRS)
        d = DIRS[sector]
        dx, dy = d.delta()
        cx = self.core_pos.x if self.core_pos else pos.x
        cy = self.core_pos.y if self.core_pos else pos.y
        reach = max(w, h)
        far = Position(max(0, min(w-1, cx + dx*reach)), max(0, min(h-1, cy + dy*reach)))
        self._nav(c, pos, far, ti, ti_reserve=50)
