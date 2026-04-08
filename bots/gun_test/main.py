import sys
from cambc import Controller, Direction, EntityType, Environment, Position

DIRS = [d for d in Direction if d != Direction.CENTRE]

class Player:
    def __init__(self):
        self.core_pos = None
        self.done = False
        self.printed = False

    def run(self, c):
        t = c.get_entity_type()
        if t == EntityType.CORE:
            if c.get_action_cooldown() == 0 and c.get_unit_count() - 1 < 1:
                ti = c.get_global_resources()[0]
                cost = c.get_builder_bot_cost()[0]
                if ti >= cost + 2:
                    pos = c.get_position()
                    for d in DIRS:
                        if c.can_spawn(pos.add(d)):
                            c.spawn_builder(pos.add(d))
                            return
        elif t == EntityType.BUILDER_BOT:
            self._builder(c)
        elif t == EntityType.GUNNER:
            rnd = c.get_current_round()
            ammo = c.get_ammo_amount()
            if rnd % 50 == 0:
                print(f'Round {rnd}: gunner ammo={ammo}', file=sys.stderr)
            if c.get_action_cooldown() == 0 and ammo >= 2:
                t2 = c.get_gunner_target()
                if t2 and c.can_fire(t2):
                    c.fire(t2)
                    print(f'Round {rnd}: GUNNER FIRED at {t2}', file=sys.stderr)

    def _builder(self, c):
        pos = c.get_position()
        rnd = c.get_current_round()

        if self.core_pos is None:
            for eid in c.get_nearby_entities():
                try:
                    if c.get_entity_type(eid) == EntityType.CORE and c.get_team(eid) == c.get_team():
                        self.core_pos = c.get_position(eid)
                except Exception:
                    pass

        if self.done or self.core_pos is None: return
        w, h = c.get_map_width(), c.get_map_height()
        cx, cy = self.core_pos.x, self.core_pos.y
        enemy_cx, enemy_cy = w-1-cx, h-1-cy
        # Try ALL 9 tiles of the enemy core footprint
        enemy_tiles = [Position(enemy_cx+dx, enemy_cy+dy)
                       for dx in range(-1,2) for dy in range(-1,2)
                       if 0 <= enemy_cx+dx < w and 0 <= enemy_cy+dy < h]

        if rnd < 30: return
        if c.get_action_cooldown() != 0: return
        ti = c.get_global_resources()[0]
        if ti < c.get_gunner_cost()[0] + 5: return

        if not self.printed:
            self.printed = True
            print(f'Rnd {rnd}: core={self.core_pos} enemy=({enemy_cx},{enemy_cy})', file=sys.stderr)
            # Check (0,2) SE specifically (from our Python analysis)
            gp = Position(0, 2)
            for gdir in DIRS:
                try:
                    cg = c.can_build_gunner(gp, gdir)
                    if cg:
                        for et in enemy_tiles:
                            cf = c.can_fire_from(gp, gdir, EntityType.GUNNER, et)
                            if cf:
                                print(f'  FOUND: gunner at {gp} facing {gdir} fires at {et}', file=sys.stderr)
                except Exception as e:
                    print(f'  err at {gp} {gdir}: {e}', file=sys.stderr)

        # Exhaustive search: all positions within 8 tiles of own core, all directions, all enemy tiles
        for dx in range(-8, 9):
            for dy in range(-8, 9):
                gp = Position(cx+dx, cy+dy)
                if gp.x < 0 or gp.y < 0 or gp.x >= w or gp.y >= h: continue
                for gdir in DIRS:
                    try:
                        if not c.can_build_gunner(gp, gdir): continue
                        for et in enemy_tiles:
                            if c.can_fire_from(gp, gdir, EntityType.GUNNER, et):
                                c.build_gunner(gp, gdir)
                                self.done = True
                                print(f'Rnd {rnd}: GUNNER at {gp} facing {gdir} -> fires at {et}', file=sys.stderr)
                                return
                    except Exception:
                        pass
        if rnd == 30:
            print(f'Rnd {rnd}: no valid gunner+fire_from found in 17x17 grid', file=sys.stderr)
