# Turtle Strategy Results

## Overview

The turtle bot uses a pure defense + economy strategy with NO offensive units. It wins by Resource Victory at the 2000-round limit by out-mining the opponent.

**Record vs starter bot: 5 wins / 1 loss (6 maps)**

## Per-Map Results

### default_medium1 (30x30)
| Metric | Value |
|--------|-------|
| **Result** | WIN (Resources, turn 2000) |
| **Ti mined** | 9,760 |
| **Total Ti** | 13,771 vs 2,562 |
| **Harvesters** | 5 |
| **Barriers** | 0 (defender found splitter target instead) |
| **Sentinels** | 1 (via splitter at R60) |
| **Notes** | Strong economy, 5:1 Ti advantage |

### settlement (large map)
| Metric | Value |
|--------|-------|
| **Result** | WIN (Resources, turn 2000) |
| **Ti mined** | 18,260 |
| **Total Ti** | 14,975 vs 559 |
| **Harvesters** | 20+ |
| **Barriers** | 0 |
| **Sentinels** | 1 (via splitter at R60) |
| **Notes** | Best mining performance, massive 27:1 advantage |

### cold
| Metric | Value |
|--------|-------|
| **Result** | LOSS (Resources, turn 2000) |
| **Ti mined** | 0 |
| **Total Ti** | 3,853 vs 414 |
| **Harvesters** | 11 (none connected to core) |
| **Barriers** | 0 |
| **Sentinels** | 1 |
| **Notes** | Wall barrier between ore and core prevents chain connection. Would need bridges. Still had more Ti from passive income but starter had fewer buildings so won tiebreaker on units/stored. |

### landscape
| Metric | Value |
|--------|-------|
| **Result** | WIN (Resources, turn 2000) |
| **Ti mined** | 9,810 |
| **Total Ti** | 10,464 vs 2,377 |
| **Harvesters** | 18+ |
| **Barriers** | 2 (at R282, R284) |
| **Sentinels** | 0 (defender spent time on barriers then mining) |
| **Notes** | Many harvesters, strong mining output |

### corridors
| Metric | Value |
|--------|-------|
| **Result** | WIN (Resources, turn 2000) |
| **Ti mined** | 9,960 |
| **Total Ti** | 12,157 vs 3,818 |
| **Harvesters** | 20 |
| **Barriers** | 0 |
| **Sentinels** | 1 (via splitter at R57) |
| **Notes** | Narrow map works well for L-shaped chains |

### face (20x25)
| Metric | Value |
|--------|-------|
| **Result** | WIN (Resources, turn 2000) |
| **Ti mined** | 9,880 |
| **Total Ti** | 14,408 vs 4,884 |
| **Harvesters** | 6 |
| **Barriers** | 0 |
| **Sentinels** | 0 |
| **Notes** | Smaller map, fewer ore tiles but efficient chains |

## Summary Statistics

| Map | Result | Ti Mined | Harvesters | Barriers | Sentinels |
|-----|--------|----------|------------|----------|-----------|
| default_medium1 | WIN | 9,760 | 5 | 0 | 1 |
| settlement | WIN | 18,260 | 20+ | 0 | 1 |
| cold | LOSS | 0 | 11 | 0 | 1 |
| landscape | WIN | 9,810 | 18+ | 2 | 0 |
| corridors | WIN | 9,960 | 20 | 0 | 1 |
| face | WIN | 9,880 | 6 | 0 | 0 |

## Strategy Analysis

### What works:
1. **L-shaped conveyor chains** (horizontal then vertical) ensure connectivity - each conveyor outputs into the next one
2. **Unique explore directions** per builder (based on entity ID) prevents crowding
3. **Build-and-move** on same turn for road construction enables efficient exploration
4. **Splitter-based sentinel delivery** works when conveyors exist near core
5. **Pure economy focus** produces 10,000-18,000 Ti mined on open maps

### What doesn't work:
1. **Walls blocking chain paths** (cold map) - need bridges to cross walls
2. **Barrier placement** rarely triggers - defenders often become miners early or find splitter targets first
3. **Late harvesters** on some maps - first harvester around R10-35 depending on ore proximity

### Improvement opportunities:
- Add bridge support for maps with walls between ore and core
- More aggressive barrier placement before sentinel
- Second sentinel via another splitter
- Earlier harvester timing by prioritizing nearby ore
