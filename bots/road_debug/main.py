"""Debug bot to test road building mechanics."""
import sys
from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]
BUILDER_CAP = 2


class Player:
    def __init__(self):
        self.core_pos = None
        self.my_id = None
        self._w = None
        self._h = None
        self.did_debug = False

    def run(self, c):
        t = c.get_entity_type()
        if t == EntityType.CORE:
            if self.core_pos is None:
                self.core_pos = c.get_position()
                self._w = c.get_map_width()
                self._h = c.get_map_height()
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                cost = c.get_builder_bot_cost()[0]
                if ti >= cost + 5 and c.get_unit_count() - 1 < BUILDER_CAP:
                    pos = c.get_position()
                    for d in DIRS:
                        sp = pos.add(d)
                        if c.can_spawn(sp):
                            c.spawn_builder(sp)
                            return
        elif t == EntityType.BUILDER_BOT:
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
                        pass

            pos = c.get_position()
            rnd = c.get_current_round()

            if not self.did_debug and rnd >= 3:
                self.did_debug = True
                print("rnd=" + str(rnd) + " id=" + str(self.my_id) + " pos=" + str(pos), file=sys.stderr)
                print("  act_cd=" + str(c.get_action_cooldown()) + " move_cd=" + str(c.get_move_cooldown()), file=sys.stderr)
                w = self._w or 50
                h = self._h or 50
                for d in DIRS:
                    nxt = pos.add(d)
                    if not (0 <= nxt.x < w and 0 <= nxt.y < h):
                        continue
                    mv = c.can_move(d)
                    rd = c.can_build_road(nxt)
                    env = c.get_tile_env(nxt)
                    bid = c.get_tile_building_id(nxt)
                    print("  d=" + d.name + " nxt=" + str(nxt) + " can_move=" + str(mv) + " can_road=" + str(rd) + " env=" + str(env) + " bld=" + str(bid), file=sys.stderr)

            # Try to build a road then move
            if c.get_action_cooldown() == 0:
                ti = c.get_global_resources()[0]
                rcost = c.get_road_cost()[0]
                if ti >= rcost:
                    for d in DIRS:
                        nxt = pos.add(d)
                        if c.can_build_road(nxt):
                            c.build_road(nxt)
                            print("rnd=" + str(rnd) + " built road at " + str(nxt), file=sys.stderr)
                            return

            if c.get_move_cooldown() == 0:
                for d in DIRS:
                    if c.can_move(d):
                        c.move(d)
                        print("rnd=" + str(rnd) + " moved " + d.name + " to " + str(pos.add(d)), file=sys.stderr)
                        return
