# Minimal Bot Experiment: Is Simpler Better?

## Date: 2026-04-08
## Hypothesis: Our 662-line buzzing bot's features are net negative. A ~100-line minimal economy bot would win by avoiding scale inflation.

---

## buzzing_v2 Design (97 lines)

- 3 builders max (hard cap)
- Each builder: walk toward nearest visible ore, build harvester, walk to next ore
- d.opposite() conveyors ONLY when walking to ore target (not exploring)
- When no ore visible: walk toward map center via roads
- Zero military, zero barriers, zero bridges, zero BFS, zero markers

---

## Results: buzzing_v2 vs buzzing (10 maps, seed 42)

| Map | Winner | v2 Ti (mined) | buzzing Ti (mined) | v2 Bldgs | buzzing Bldgs |
|-----|--------|---------------|-------------------|----------|---------------|
| default_small1 | **buzzing** | 9,741 (4,980) | 23,141 (19,540) | 67 | 118 |
| default_small2 | **buzzing** | 17,092 (11,780) | 39,934 (39,690) | 16 | 201 |
| default_medium1 | **buzzing** | 5,242 (0) | 8,648 (9,790) | 23 | 412 |
| default_medium2 | **buzzing** | 5,198 (0) | 23,217 (24,260) | 48 | 402 |
| default_large1 | **buzzing** | 5,386 (0) | 22,572 (27,370) | 7 | 455 |
| arena | **buzzing_v2** | 28,920 (24,170) | 12,363 (9,910) | 72 | 217 |
| binary_tree | **buzzing** | 5,228 (0) | 27,756 (24,680) | 21 | 103 |
| butterfly | **buzzing_v2** | 39,804 (34,840) | 38,281 (34,390) | 28 | 41 |
| cold | **buzzing** | 5,198 (0) | 20,244 (25,730) | 90 | 547 |
| hooks | **buzzing** | 5,034 (0) | 30,893 (31,970) | 49 | 388 |

### Score: buzzing wins 8-2

---

## Analysis

### buzzing_v2 catastrophic failures (0 Ti mined on 5 maps)

On default_medium1, default_medium2, default_large1, binary_tree, and hooks, buzzing_v2 mined **0 titanium**. The 3 builders couldn't find ore or couldn't establish working chains. This means:

1. **3 builders is too few for medium/large maps** -- ore is beyond initial vision, and with no exploration strategy (just "walk to center"), builders never reach it.
2. **No BFS navigation** -- builders get stuck on walls without BFS. buzzing's BFS (line 589) is critical for wall-heavy maps.
3. **Road-based exploration fails** -- roads don't form delivery chains, so even if builders find ore and build harvesters, resources can't reach core without conveyors on the return path.

### buzzing_v2 wins (arena, butterfly)

- **arena**: Tight map, ore very close to core. 3 builders + short conveyor chains = efficient. buzzing over-spawns 8+ builders on this map.
- **butterfly**: Ore-rich map. 3 builders find ore quickly, short chains work. buzzing barely edges it (34,390 vs 34,840 mined) but v2 wins on accumulated Ti.

### Key observation: buzzing's building counts

buzzing builds 100-547 buildings on medium/large maps. Even at 1% scale per conveyor, 400+ buildings means costs are 5x+ base. Yet it STILL mines 20-30k Ti and wins convincingly. The scale inflation is bad but the alternative (not reaching ore at all) is worse.

---

## Conclusions

### 1. Our features are NOT net negative
buzzing wins 8/10 maps. The 662-line architecture (BFS, exploration, marker claiming, bridge shortcuts, barriers) is genuinely valuable. A stripped-down bot fails catastrophically on most maps.

### 2. Scale inflation is real but secondary
buzzing builds 400+ buildings on large maps but still mines 20-30k Ti. The scale inflation hurts efficiency but doesn't prevent functioning. The minimal bot's 0 Ti on 5 maps proves that REACHING ore matters more than COST of reaching it.

### 3. The real problem is on tight/ore-rich maps
buzzing_v2 wins on arena and butterfly -- the maps where ore is close to core and 3 builders suffice. This confirms that buzzing over-builds on tight maps. The fix isn't "simplify everything" but "be smarter about tight maps specifically."

### 4. BFS navigation is load-bearing
Without BFS, builders get stuck on walls and mine 0 Ti on 5/10 maps. BFS (200-step limit, line 594) is one of buzzing's most critical features.

### 5. 3 builders is too few for medium/large maps
The hard cap of 3 fails completely on maps where ore is far from core. The current econ_cap system (scale with harvesters) is closer to correct than a hard cap.

---

## Actionable Insights

1. **Don't simplify the architecture** -- it's load-bearing. BFS, exploration, bridges are all needed.
2. **Tight-map builder cap could help** -- on arena/butterfly, buzzing over-spawns. A map-specific cap of 3-4 builders on tight maps with nearby ore could help.
3. **Scale-based spawning gate** -- rather than a hard builder cap, gate on `c.get_scale_percent()`. When scale > 200%, stop spawning. This adapts to all maps.
4. **The 1600 Elo gap is NOT about architecture simplification** -- it's about spending Ti wisely (sentinels, fewer conveyors on tight maps) while keeping the exploration engine for large maps.
