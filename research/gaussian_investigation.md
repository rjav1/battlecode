# Gaussian Map Investigation

Date: 2026-04-06

## Test Results

### buzzing vs smart_eco — gaussian seed 1
**Winner: smart_eco**
```
Titanium: buzzing 16825 (14910 mined) | smart_eco 28775 (25010 mined)
Units: 8 | 8
Buildings: 238 | 117
```
Gap: smart_eco mines 68% more Ti (+10100). Building count 238 vs 117 — buzzing spends 2x more on conveyors.

### buzzing vs balanced — gaussian seed 1
**Winner: balanced (catastrophic loss)**
```
Titanium: buzzing 9491 (7940 mined) | balanced 33502 (29720 mined)
Units: 8 | 5
Buildings: 236 | 133
```
`balanced` bot mines 3.7x more Ti with only 5 units. This is a fundamental pathology.

---

## Map Analysis

**Dimensions:** 35x20 (area=700) → classified as **balanced** mode (area between 625 and 1600).

**Ore inventory:**
- Ti ore: 12 tiles (6 per side, symmetric)
- Ax ore: 4 tiles (2 per side, symmetric)
- Total ore: 16 tiles
- Wall tiles: 85

**ASCII map** (T=Ti ore, A=Ax ore, #=wall):
```
 0: ...................................
 1: ................###................
 2: ..............##...##..............
 3: ............###.....###............
 4: ...........#...........#...........
 5: ..........#.....A.A.....#..........
 6: .........##.A.........A.##.........
 7: .........#...............#.........
 8: ........#......#...#......#........
 9: ........#......#...#......#........
10: .......##..T....#.#....T..##.......
11: .......#...TT...#.#...TT...#.......
12: ......##....T...#.#...T....##......
13: ......#.........#.#.........#......
14: ......#........##.##........#......
15: .....#.........#...#.........#.....
16: ....##.......T.#...#.T.......##....
17: ...##..........#...#..........##...  <- CORES at (10,17) and (24,17)
18: ..##..T........#...#........T..##..
19: ##.............#...#.............##
```

**Core positions:** (10,17) and (24,17) — near the **bottom edge** (y=17 out of 20).

**Ore distances from Core1 at (10,17):**
| Tile | Distance² | Notes |
|------|-----------|-------|
| (13,16) | 10 | Closest — outside ring, easy |
| (6,18) | 17 | Outside ring, easy |
| (12,12) | 29 | Inside gaussian ring |
| (12,11) | 40 | Inside ring |
| (11,10) | 50 | Deep inside ring |
| (11,10) | 50 | Deep inside ring |

---

## Root Cause Analysis

### 1. Map classified as "balanced" but behaves like a maze/tight map

gaussian is 35×20. The short dimension is only 20 tiles. Buzzing's `map_mode` uses `area=700` → "balanced". But:
- Effective playfield depth: 20 rows (10 usable per side after symmetry)
- Ore is all within 7 tiles of core (d²≤50)
- 85 wall tiles form a gaussian-distribution ring that must be navigated around

This is structurally a **tight maze** map, not an open balanced map. The balanced explore logic assumes a roughly square map and fans out to `reach=max(w,h)=35` tiles — which overshoots the entire map height.

### 2. Balanced explore logic fans builders in wrong directions

Core at (10,17), map is 35 wide × 20 tall. Explore targets:
- NORTH: `(10, 17-35) = (10,-18)` — off map, clamped to (10,0)
- But the map is only 20 rows, so "north" puts builders at row 0 in ~10 steps
- Builders pile up at the map's north edge, not finding ore clusters inside the ring

All ore for Core1 is at x=6-13, y=10-18 — basically due north and slightly toward center. But builders going NORTHEAST, NORTHWEST, EAST etc. hit the ring walls and bounce around.

### 3. Gaussian ring walls force long maze paths → 2x conveyor overhead

Getting from core (10,17) to the Ti cluster at (11-12, 10-12) requires navigating through the ring gap at around x=7, y=13. BFS finds this path but it's ~10 steps with direction changes. That's 10+ conveyors at 3 Ti each = 30+ Ti per harvester path. smart_eco lays the same conveyors but with 6+ builders going faster, depleting the maze paths sooner.

Result: buzzing builds 238 buildings vs smart_eco's 117, spending ~360 Ti extra on conveyors.

### 4. econ_cap throttles builder spawning

With gaussian classified as balanced, econ_cap = `max(time_floor, vis_harv*3+4)`. Core vision r²=36 barely reaches the ring, so harvesters placed inside (at rows 10-12) are often outside vision. `vis_harv` stays near 0-1 → cap stays near 7 → builder spawning is throttled below the raw time cap.

### 5. Building count explosion = Ti sink

238 buildings vs 117 for smart_eco. At avg ~3 Ti/building, that's ~360 extra Ti spent on buildings — enough to fund 4-5 extra harvesters at current scale.

---

## Key Insight: min(w,h) is the right classification metric

gaussian: min(35,20) = 20 → effectively a "tight" map in terms of builder travel distance.
default_medium1: likely ~30×30, min=30 → truly balanced.
cold: 37×37 → truly balanced.

Using `area = w*h = 700` to classify gaussian as "balanced" is wrong. A 35×20 map has the same area as a 26×27 map but completely different geometry.

---

## Recommended Fixes

### Fix 1: Add short-dimension classification (CRITICAL)

```python
w, h = c.get_map_width(), c.get_map_height()
area = w * h
short_dim = min(w, h)
if area <= 625 or short_dim <= 22:   # tight OR shallow
    self.map_mode = "tight"
elif area >= 1600 and short_dim > 30: # truly large and square-ish
    self.map_mode = "expand"
else:
    self.map_mode = "balanced"
```

This reclassifies gaussian (min=20) as "tight", which uses:
- Simpler position-relative exploration
- Less aggressive conveyor building
- Appropriate builder caps

### Fix 2: Remove econ_cap formula (HIGH PRIORITY — applies to all maps)

```python
# Remove: vis_harv counting loop and econ_cap calculation
# Keep: time-based cap only
```

The formula is broken because core vision doesn't reliably see far/blocked harvesters.

### Fix 3: Raise Ax ore penalty or exploit it

Gaussian has Ax ore at rows 5-6 (inside the ring), Ti ore at rows 10-12 and 16/18. The Ax ore is actually FARTHER from core than Ti ore. Buzzing's +50000 Ax penalty means it correctly ignores Ax here. No change needed.

---

## Summary

Gaussian loses because:
1. **Wrong map mode** — 35×20 classified as "balanced" but is behaviorally tight/maze
2. **Explore logic overshoots** — targets 35 tiles away on a 20-row-tall map
3. **Maze walls create 2x conveyor overhead** — 238 vs 117 buildings
4. **econ_cap throttles builder spawns** — same bug as other maps

Primary fix: classify by `min(w,h)` not `w*h`. Any map with `min(w,h) <= 22` should use tight mode. This alone should fix the explore overshooting and reduce conveyor waste.
