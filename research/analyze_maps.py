#!/usr/bin/env python3
"""Analyze all 38 Battlecode 2026 map files."""

import os
import math
import json
from collections import deque

def decode_varint(data, offset):
    result = 0
    shift = 0
    while True:
        if offset >= len(data):
            break
        b = data[offset]
        result |= (b & 0x7F) << shift
        offset += 1
        if not (b & 0x80):
            break
        shift += 7
    return result, offset

def parse_map(filepath):
    data = open(filepath, 'rb').read()
    offset = 0
    width = None
    height = None
    rows = []
    cores = []
    symmetry = None

    while offset < len(data):
        tag_byte = data[offset]
        field_num = tag_byte >> 3
        wire_type = tag_byte & 0x7

        if wire_type == 0:
            val, offset = decode_varint(data, offset + 1)
            if field_num == 1:
                width = val
            elif field_num == 2:
                height = val
            elif field_num == 5:
                symmetry = val
        elif wire_type == 2:
            length, offset = decode_varint(data, offset + 1)
            content = data[offset:offset + length]
            if field_num == 3:
                inner_offset = 0
                while inner_offset < len(content):
                    inner_tag = content[inner_offset]
                    inner_wire = inner_tag & 0x7
                    if inner_wire == 2:
                        inner_len, inner_offset = decode_varint(content, inner_offset + 1)
                        row_data = content[inner_offset:inner_offset + inner_len]
                        rows.append(list(row_data))
                        inner_offset += inner_len
                    else:
                        inner_offset += 1
            elif field_num == 4:
                inner_offset = 0
                core_data = {}
                while inner_offset < len(content):
                    inner_tag = content[inner_offset]
                    inner_field = inner_tag >> 3
                    inner_wire = inner_tag & 0x7
                    if inner_wire == 0:
                        val, inner_offset = decode_varint(content, inner_offset + 1)
                        core_data[inner_field] = val
                    elif inner_wire == 2:
                        inner_len, inner_offset = decode_varint(content, inner_offset + 1)
                        sub = content[inner_offset:inner_offset + inner_len]
                        pos = {}
                        so = 0
                        while so < len(sub):
                            st = sub[so]
                            sf = st >> 3
                            sw = st & 0x7
                            if sw == 0:
                                v, so = decode_varint(sub, so + 1)
                                pos[sf] = v
                            else:
                                so += 1
                        core_data[f'sub_{inner_field}'] = pos
                        inner_offset += inner_len
                    else:
                        inner_offset += 1
                cores.append(core_data)
            offset += length
        else:
            offset += 1

    return width, height, rows, cores, symmetry


def bfs_distance(grid, w, h, start_x, start_y):
    """BFS from a point to all reachable tiles."""
    dist = {}
    queue = deque()
    dist[(start_x, start_y)] = 0
    queue.append((start_x, start_y))
    while queue:
        x, y = queue.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in dist:
                if grid[ny][nx] != 1:  # not wall
                    dist[(nx, ny)] = dist[(x, y)] + 1
                    queue.append((nx, ny))
    return dist


def find_chokepoints(grid, w, h):
    """Count narrow (1-2 cell wide) passages between wall segments."""
    choke_count = 0
    # Check rows
    for y in range(h):
        in_gap = False
        gap_width = 0
        had_wall_before = False
        for x in range(w):
            if grid[y][x] != 1:
                if not in_gap:
                    in_gap = True
                    gap_width = 1
                else:
                    gap_width += 1
            else:
                if in_gap and gap_width <= 2 and had_wall_before:
                    choke_count += 1
                in_gap = False
                gap_width = 0
                had_wall_before = True
    # Check columns
    for x in range(w):
        in_gap = False
        gap_width = 0
        had_wall_before = False
        for y in range(h):
            if grid[y][x] != 1:
                if not in_gap:
                    in_gap = True
                    gap_width = 1
                else:
                    gap_width += 1
            else:
                if in_gap and gap_width <= 2 and had_wall_before:
                    choke_count += 1
                in_gap = False
                gap_width = 0
                had_wall_before = True
    return choke_count


def find_open_regions(grid, w, h):
    """Flood-fill to find connected non-wall regions."""
    visited = set()
    regions = []
    for y in range(h):
        for x in range(w):
            if grid[y][x] != 1 and (x, y) not in visited:
                size = 0
                queue = deque()
                queue.append((x, y))
                visited.add((x, y))
                while queue:
                    cx, cy = queue.popleft()
                    size += 1
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited and grid[ny][nx] != 1:
                            visited.add((nx, ny))
                            queue.append((nx, ny))
                regions.append(size)
    return sorted(regions, reverse=True)


def render_grid(grid, w, h, core_positions):
    """Render grid as ASCII art."""
    cell_chars = {0: '.', 1: '#', 2: 'T', 3: 'A'}
    # Mark core 3x3 areas
    core_cells = set()
    for cx, cy in core_positions:
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                core_cells.add((cx + dx, cy + dy))

    lines = []
    for y in range(h):
        row = ''
        for x in range(w):
            if (x, y) in core_cells:
                # Check which core
                for i, (cx, cy) in enumerate(core_positions):
                    if abs(x - cx) <= 1 and abs(y - cy) <= 1:
                        if x == cx and y == cy:
                            row += str(i + 1)  # core center
                        else:
                            row += 'o'  # core area
                        break
            else:
                row += cell_chars.get(grid[y][x], '?')
        lines.append(row)
    return '\n'.join(lines)


def classify_map(data):
    """Classify map into strategic categories."""
    categories = []

    # Rush-friendly: short path, low walls, small/medium map
    if data['core_path'] is not None and data['core_path'] <= 25 and data['wall_pct'] < 15:
        categories.append('Rush-friendly')

    # Economy-friendly: lots of ore, large map, far cores
    if data['total_ore'] >= 40 and data['total'] >= 900:
        categories.append('Economy-friendly')

    # Choke-heavy: many chokepoints relative to map size, high wall %
    if data['wall_pct'] >= 15 or data['chokes'] >= 30:
        categories.append('Choke-heavy')

    # Weird: unusual geometry
    if data['num_regions'] > 3:
        categories.append('Fragmented')
    if data['w'] / data['h'] > 2 or data['h'] / data['w'] > 2:
        categories.append('Elongated')
    if data['total_ore'] <= 14:
        categories.append('Resource-scarce')

    if not categories:
        categories.append('Mixed')

    return categories


def main():
    maps_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'maps')
    all_data = {}

    for fname in sorted(os.listdir(maps_dir)):
        if not fname.endswith('.map26'):
            continue
        path = os.path.join(maps_dir, fname)
        name = fname.replace('.map26', '')

        w, h, rows, cores, sym = parse_map(path)
        grid = rows
        total = w * h
        walls = sum(1 for row in grid for c in row if c == 1)
        ti_ore = sum(1 for row in grid for c in row if c == 2)
        ax_ore = sum(1 for row in grid for c in row if c == 3)

        # Core positions
        core_positions = []
        for c in cores:
            if 'sub_3' in c:
                x = c['sub_3'].get(1, 0)
                y = c['sub_3'].get(2, 0)
                core_positions.append((x, y))

        # BFS distances from each core to nearest ore
        ore_dists = []
        for cx, cy in core_positions:
            distances = bfs_distance(grid, w, h, cx, cy)
            nearest_ti = float('inf')
            nearest_ax = float('inf')
            for y2 in range(h):
                for x2 in range(w):
                    if grid[y2][x2] == 2 and (x2, y2) in distances:
                        nearest_ti = min(nearest_ti, distances[(x2, y2)])
                    if grid[y2][x2] == 3 and (x2, y2) in distances:
                        nearest_ax = min(nearest_ax, distances[(x2, y2)])
            ore_dists.append({
                'nearest_ti': nearest_ti if nearest_ti != float('inf') else -1,
                'nearest_ax': nearest_ax if nearest_ax != float('inf') else -1
            })

        # BFS path between cores
        core_path_dist = None
        if len(core_positions) >= 2:
            cx, cy = core_positions[0]
            distances = bfs_distance(grid, w, h, cx, cy)
            tx, ty = core_positions[1]
            core_path_dist = distances.get((tx, ty), -1)

        # Euclidean distance
        core_euclid = None
        if len(core_positions) >= 2:
            dx = core_positions[0][0] - core_positions[1][0]
            dy = core_positions[0][1] - core_positions[1][1]
            core_euclid = round(math.sqrt(dx * dx + dy * dy), 1)

        sym_names = {0: 'rotational', 1: 'horizontal', 2: 'vertical'}
        sym_name = sym_names.get(sym, f'unknown({sym})')
        wall_pct = round(walls / total * 100, 1)

        chokes = find_chokepoints(grid, w, h)
        regions = find_open_regions(grid, w, h)

        # Ore clustering analysis
        ti_tiles = [(x, y) for y in range(h) for x in range(w) if grid[y][x] == 2]
        ax_tiles = [(x, y) for y in range(h) for x in range(w) if grid[y][x] == 3]

        colocation = 'N/A'
        if ti_tiles and ax_tiles:
            min_dist = float('inf')
            for tx, ty in ti_tiles[:30]:
                for ax, ay in ax_tiles[:30]:
                    d = abs(tx - ax) + abs(ty - ay)
                    min_dist = min(min_dist, d)
            if min_dist <= 2:
                colocation = 'co-located'
            elif min_dist <= 6:
                colocation = 'nearby'
            else:
                colocation = 'separated'

        # Ore spread: avg distance from map center
        ore_spread = 'N/A'
        if ti_tiles:
            avg_ti_x = sum(x for x, y in ti_tiles) / len(ti_tiles)
            avg_ti_y = sum(y for x, y in ti_tiles) / len(ti_tiles)
            center_x, center_y = w / 2, h / 2
            spread_dist = math.sqrt((avg_ti_x - center_x)**2 + (avg_ti_y - center_y)**2)
            if spread_dist < min(w, h) * 0.15:
                ore_spread = 'centered'
            else:
                ore_spread = 'distributed'

        ascii_grid = render_grid(grid, w, h, core_positions)

        all_data[name] = {
            'w': w, 'h': h, 'total': total,
            'walls': walls, 'wall_pct': wall_pct,
            'ti_ore': ti_ore, 'ax_ore': ax_ore, 'total_ore': ti_ore + ax_ore,
            'core_pos': core_positions,
            'core_euclid': core_euclid,
            'core_path': core_path_dist,
            'symmetry': sym_name,
            'ore_dists': ore_dists,
            'colocation': colocation,
            'ore_spread': ore_spread,
            'chokes': chokes,
            'num_regions': len(regions),
            'largest_region': regions[0] if regions else 0,
            'region_sizes': regions[:5],
            'region_pct': round(regions[0] / total * 100, 1) if regions else 0,
            'ascii': ascii_grid
        }

    # Classify all maps
    for name, d in all_data.items():
        d['categories'] = classify_map(d)

    # Output JSON for further processing
    output = {}
    for name, d in all_data.items():
        output[name] = {k: v for k, v in d.items() if k != 'ascii'}

    # Save JSON
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'map_data.json'), 'w') as f:
        json.dump(output, f, indent=2)

    # Save ASCII grids
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'map_grids.txt'), 'w') as f:
        for name in sorted(all_data.keys()):
            d = all_data[name]
            f.write(f"\n{'='*60}\n")
            f.write(f"{name} ({d['w']}x{d['h']}, {d['symmetry']})\n")
            f.write(f"Walls: {d['wall_pct']}% | Ti: {d['ti_ore']} | Ax: {d['ax_ore']} | Core dist: {d['core_path']}\n")
            f.write(f"Cores: {d['core_pos']} | Categories: {', '.join(d['categories'])}\n")
            f.write(f"{'='*60}\n")
            f.write(d['ascii'] + '\n')

    print("Analysis complete!")
    print(f"Processed {len(all_data)} maps")

    return all_data, output

if __name__ == '__main__':
    all_data, output = main()

    # Print summary table
    print(f"\n{'Name':<30} {'Size':<7} {'Sym':<12} {'Wall%':<6} {'Ti':<4} {'Ax':<4} {'Path':<5} {'Categories'}")
    print('-' * 120)
    for name in sorted(output.keys()):
        d = output[name]
        size = f"{d['w']}x{d['h']}"
        cats = ', '.join(d['categories'])
        path_str = str(d['core_path']) if d['core_path'] else '?'
        print(f"{name:<30} {size:<7} {d['symmetry']:<12} {d['wall_pct']:<6} {d['ti_ore']:<4} {d['ax_ore']:<4} {path_str:<5} {cats}")
