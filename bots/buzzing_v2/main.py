"""Minimal economy bot — diagnostic experiment.
3 builders, conveyors only toward ore, roads for exploration, zero military.
"""

from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]


class Player:
    def __init__(self):
        self.core_pos = None
        self.target = None
        self.stuck = 0
        self.last_pos = None

    def run(self, c: Controller) -> None:
        t = c.get_entity_type()
        if t == EntityType.CORE:
            self._core(c)
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)

    def _core(self, c):
        if c.get_action_cooldown() != 0:
            return
        units = c.get_unit_count() - 1
        if units >= 3:
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

    def _builder(self, c):
        pos = c.get_position()
        if self.core_pos is None:
            for eid in c.get_nearby_entities():
                try:
                    if (c.get_entity_type(eid) == EntityType.CORE
                            and c.get_team(eid) == c.get_team()):
                        self.core_pos = c.get_position(eid)
                        break
                except Exception:
                    continue

        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck = 0
        self.last_pos = pos
        if self.stuck > 15:
            self.target = None
            self.stuck = 0

        # Build harvester on adjacent ore
        if c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            hc = c.get_harvester_cost()[0]
            if ti >= hc + 5:
                for d in DIRS:
                    p = pos.add(d)
                    if c.can_build_harvester(p):
                        c.build_harvester(p)
                        self.target = None
                        return

        # Find nearest visible ore
        ore_tiles = []
        passable = set()
        for t in c.get_nearby_tiles():
            e = c.get_tile_env(t)
            if e != Environment.WALL:
                passable.add(t)
                if e in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
                    bid = c.get_tile_building_id(t)
                    if bid is None:
                        score = pos.distance_squared(t)
                        if e == Environment.ORE_AXIONITE:
                            score += 50000
                        ore_tiles.append((score, t))

        if ore_tiles:
            ore_tiles.sort()
            self.target = ore_tiles[0][1]

        if self.target and c.is_in_vision(self.target):
            bid = c.get_tile_building_id(self.target)
            if bid is not None:
                try:
                    if c.get_entity_type(bid) != EntityType.MARKER:
                        self.target = None
                except Exception:
                    self.target = None

        if self.target:
            self._nav_to_ore(c, pos, self.target)
        else:
            self._explore(c, pos)

    def _nav_to_ore(self, c, pos, target):
        """Navigate toward ore target using d.opposite() conveyors."""
        dirs = self._rank(pos, target)
        w, h = c.get_map_width(), c.get_map_height()
        for d in dirs:
            nxt = pos.add(d)
            if nxt.x < 0 or nxt.x >= w or nxt.y < 0 or nxt.y >= h:
                continue
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                cc = c.get_conveyor_cost()[0]
                if ti >= cc + 5 and c.can_build_conveyor(nxt, d.opposite()):
                    c.build_conveyor(nxt, d.opposite())
                    return
            if c.get_move_cooldown() == 0 and c.can_move(d):
                c.move(d)
                return
        # Road fallback if conveyor blocked
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

    def _explore(self, c, pos):
        """No ore visible — walk toward map center via roads."""
        w, h = c.get_map_width(), c.get_map_height()
        center = Position(w // 2, h // 2)
        dirs = self._rank(pos, center)
        for d in dirs:
            nxt = pos.add(d)
            if nxt.x < 0 or nxt.x >= w or nxt.y < 0 or nxt.y >= h:
                continue
            if c.get_move_cooldown() == 0 and c.can_move(d):
                c.move(d)
                return
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                rc = c.get_road_cost()[0]
                if ti >= rc + 5 and c.can_build_road(nxt):
                    c.build_road(nxt)
                    return

    def _rank(self, pos, target):
        d = pos.direction_to(target)
        if d == Direction.CENTRE:
            return DIRS[:]
        return [d, d.rotate_left(), d.rotate_right(),
                d.rotate_left().rotate_left(), d.rotate_right().rotate_right(),
                d.rotate_left().rotate_left().rotate_left(),
                d.rotate_right().rotate_right().rotate_right(),
                d.opposite()]
