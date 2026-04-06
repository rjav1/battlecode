"""Simple attacker bot: spawns builders and sends them toward the enemy core."""
from cambc import Controller, Direction, EntityType, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]

class Player:
    def __init__(self):
        self.target = None

    def run(self, c):
        if c.get_entity_type() == EntityType.CORE:
            if c.get_action_cooldown() == 0 and c.get_unit_count() < 6:
                pos = c.get_position()
                for d in DIRS:
                    if c.can_spawn(pos.add(d)):
                        c.spawn_builder(pos.add(d))
                        return
        elif c.get_entity_type() == EntityType.BUILDER_BOT:
            if self.target is None:
                w, h = c.get_map_width(), c.get_map_height()
                pos = c.get_position()
                self.target = Position(w - 1 - pos.x, h - 1 - pos.y)
            pos = c.get_position()
            d = pos.direction_to(self.target)
            if d == Direction.CENTRE:
                return
            nxt = pos.add(d)
            if c.can_move(d):
                c.move(d)
            elif c.get_action_cooldown() == 0:
                if c.can_build_road(nxt):
                    c.build_road(nxt)
