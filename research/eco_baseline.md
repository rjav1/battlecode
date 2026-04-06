# Economy Baseline: eco_opponent vs starter — April 6, 2026

## Overview

The `eco_opponent` bot uses `d.opposite()` conveyor chains with pure economy (no military, no attacks). These numbers represent the **ceiling for pure economy** — the Ti mining rate we should approach as we add features.

All matches: seed 1, 2000 rounds, eco_opponent as Player 1 vs starter.

## Results Table

| Map | Size | Ti Ore | Ti Mined | Ti Final | Buildings | Efficiency | Ti/Round |
|-----|------|--------|----------|----------|-----------|------------|----------|
| default_small1 | 20x20 | 10 | 24,280 | 28,510 | 99 | 117% | 12.1 |
| default_medium1 | 30x30 | 20 | 39,970 | 42,142 | 204 | 106% | 20.0 |
| default_large1 | 40x40 | 20 | 18,290 | 18,263 | 337 | 100% | 9.1 |
| settlement | 50x38 | 148 | 23,960 | 17,793 | 549 | 74% | 12.0 |
| cold | 37x37 | 115 | 23,230 | 22,812 | 217 | 98% | 11.6 |
| landscape | 30x30 | 76 | 16,560 | 16,451 | 191 | 99% | 8.3 |
| corridors | 31x31 | 32 | 9,930 | 14,879 | 25 | 150% | 5.0 |
| face | 20x20 | 8 | 9,840 | 13,540 | 126 | 138% | 4.9 |
| arena | 25x25 | 10 | 29,110 | 32,339 | 173 | 111% | 14.6 |
| cubes | 50x50 | 134 | 28,490 | 26,111 | 340 | 92% | 14.2 |
| starry_night | 50x41 | 126 | 51,150 | 35,189 | 587 | 69% | 25.6 |
| dna | 21x50 | 78 | 26,200 | 28,698 | 106 | 110% | 13.1 |

**Column definitions:**
- **Ti Ore**: Total titanium ore tiles on the map (both sides)
- **Ti Mined**: Total Ti extracted from harvesters and delivered to core
- **Ti Final**: Ti in bank at end (mined + passive - spent on buildings/units)
- **Buildings**: Total buildings placed by game end
- **Efficiency**: Ti Final / (Ti Mined + passive income). >100% means passive income exceeds building costs. <100% means we spent more on buildings than we earned from mining.
- **Ti/Round**: Ti Mined / 2000 rounds — average mining income per round

## Key Observations

### Top Performers (Ti/Round > 12)
- **starry_night**: 25.6 Ti/round (51,150 mined) — richest harvest, but 587 buildings and only 69% efficiency. Heavy conveyor waste.
- **default_medium1**: 20.0 Ti/round (39,970 mined) — excellent ratio with moderate buildings.
- **arena**: 14.6 Ti/round (29,110 mined) — small map, close ore, efficient chains.
- **cubes**: 14.2 Ti/round (28,490 mined) — large map but ore-rich.
- **dna**: 13.1 Ti/round (26,200 mined) — elongated map, good reach.

### Mid Performers (Ti/Round 8-12)
- **default_small1**: 12.1 Ti/round — good for a 10-ore map, very efficient (117%).
- **settlement**: 12.0 Ti/round — 148 ore tiles but only mining at 12/round. 549 buildings (74% efficiency). Lots of wasted conveyors exploring the huge map.
- **cold**: 11.6 Ti/round — 115 ore, large deposits, reasonable.

### Weak Performers (Ti/Round < 8)
- **default_large1**: 9.1 Ti/round — only 20 ore on a 40x40 map, long distances.
- **landscape**: 8.3 Ti/round — walls create long paths, 76 ore but hard to reach.
- **corridors**: 5.0 Ti/round — maze-like, only 25 buildings total (most conveyors blocked by walls?).
- **face**: 4.9 Ti/round — only 8 ore tiles, scarce resources.

### Efficiency Patterns
- **High efficiency (>110%)**: corridors (150%), face (138%), default_small1 (117%), arena (111%), dna (110%). These maps have short conveyor chains or low building counts, so passive income covers building costs.
- **Low efficiency (<80%)**: starry_night (69%), settlement (74%). These large maps generate many wasted conveyors during exploration. The bot spends heavily on infrastructure that doesn't contribute to mining.

## Passive Income Baseline

Without ANY mining, passive income = 10 Ti every 4 rounds = 2.5 Ti/round = 5,000 Ti over 2000 rounds. Starting Ti = 500. So a bot that mines nothing and builds nothing ends with ~5,500 Ti.

## Mining Rates by Harvester Count

Each harvester on a Ti ore tile produces 1 stack (10 Ti) every 4 rounds = 2.5 Ti/round per harvester. To achieve:
- 10 Ti/round: need 4 connected harvesters
- 20 Ti/round: need 8 connected harvesters
- 25 Ti/round: need 10 connected harvesters

starry_night's 25.6 Ti/round implies ~10 harvesters consistently producing.

## Conveyor Cost Analysis

Each conveyor costs 3 Ti base (scales up with building count). At 100 conveyors, cost scale is at +100% (6 Ti per conveyor). Average cost across a game with ~200 conveyors: roughly 4.5 Ti each = ~900 Ti total. This is modest compared to mining income of 10,000-50,000.

The bigger cost is on maps like starry_night (587 buildings) and settlement (549 buildings) where exploration creates hundreds of dead-end conveyors. At average cost ~5 Ti each, that's 2,500-3,000 Ti wasted.

## Recommendations for buzzing

1. **Target: match or beat eco_opponent's Ti/Round on every map.** Current buzzing (broken) mines 0. Even pre-regression buzzing (~16,690 on landscape) was below eco_opponent's baseline.

2. **Focus on reducing building count on large maps.** settlement and starry_night have 549-587 buildings — lots of wasted conveyors. A smarter exploration pattern (roads for scouting, conveyors only on proven paths) could reduce this by 50%.

3. **corridors underperforms (5.0 Ti/round).** Only 25 buildings suggests the bot can't navigate the maze well. BFS pathfinding may need improvement for regular grid patterns.

4. **face underperforms (4.9 Ti/round).** Only 8 ore tiles — every single one needs to be harvested. The bot may be missing tiles or not reaching far ones.

5. **Military features (sentinels, attackers) should cost < 5% of mining income.** On a map mining 20,000 Ti, that's a 1,000 Ti budget for military. 2 sentinels (60 Ti) + 1 attacker builder (30 Ti) is well within budget. The main concern is opportunity cost (lost harvesting time, not Ti spent).
