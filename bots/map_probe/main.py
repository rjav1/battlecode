import sys
from cambc import Controller, Direction, EntityType, Environment, Position

class Player:
    def run(self, c: Controller):
        if c.get_entity_type() != EntityType.CORE:
            return
        rnd = c.get_current_round()
        if rnd != 1:
            return
        w, h = c.get_map_width(), c.get_map_height()
        area = w * h
        short = min(w, h)
        if area <= 625 or short <= 22:
            mode = 'tight'
        elif area >= 1600:
            mode = 'expand'
        else:
            mode = 'balanced'
        
        ore_ti = 0
        ore_ax = 0
        walls = 0
        pos = c.get_position()
        for tile in c.get_nearby_tiles():  # use default vision
            env = c.get_tile_env(tile)
            if env == Environment.ORE_TITANIUM:
                ore_ti += 1
            elif env == Environment.ORE_AXIONITE:
                ore_ax += 1
            elif env == Environment.WALL:
                walls += 1
        print(f'MAP_PROBE: {w}x{h} area={area} mode={mode} Ti_ore_visible={ore_ti} Ax_ore={ore_ax} walls={walls} core_at={pos}')
