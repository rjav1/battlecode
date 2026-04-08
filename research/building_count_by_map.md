# Building Count by Map — V61 vs Starter

**Date:** 2026-04-08
**Setup:** buzzing (V61) vs starter, seed 1, each map
**All results:** buzzing wins every game (tiebreak on resources)

## Results

| Map | buzzing buildings | starter buildings | Bloat level |
|-----|:-----------------:|:-----------------:|-------------|
| corridors | **26** | 339 | LOW — nearly perfect |
| face | **160** | 186 | LOW — contained |
| default_medium1 | **176** | 648 | MEDIUM |
| arena | **204** | 350 | MEDIUM |
| gaussian | **231** | 263 | MEDIUM |
| hourglass | **271** | 351 | MEDIUM |
| galaxy | **362** | 748 | HIGH |
| binary_tree | **412** | 534 | HIGH |
| cold | **496** | 680 | HIGH |
| settlement | **658** | 649 | SEVERE — we exceed starter |

## Key Observations

### Severe bloat maps (400+)
- **settlement: 658 buildings** — we build MORE than starter (649). This is the worst case.
- **cold: 496** — confirmed bloat. Against barrier_wall (123 buildings) we showed up with 618. Now vs starter we build 496.
- **binary_tree: 412** — explains our 0-3 record there
- **galaxy: 362** — explains our 1-2 record

### Contained maps (corridors at 26)
- corridors is our best map (100% win rate) with only 26 buildings
- face is also clean at 160 buildings — 100% win rate
- The pattern is clear: **fewer buildings = better results**

### The starter bot as comparison
- Starter builds 186–748 buildings depending on map
- We beat starter everywhere but build nearly as many buildings on open maps
- Against lean opponents (barrier_wall: 101-123), our 400-658 building count is catastrophic for cost scaling

## Cost Scale Impact Estimate

Each conveyor/barrier: +1% scale. Each harvester: +5% scale. Each builder bot: +20% scale.
At 500 conveyors alone: cost scale = 1.0 + (500 × 0.01) = **6.0x base cost**.
At 6x scale: a harvester that costs 20 Ti base now costs **120 Ti**. A builder bot costs **180 Ti**.

This is why we can't keep up on economy — we price ourselves out of our own build queue.

## Map Categories by Bloat

**Under control (<200):** corridors, face, default_medium1, arena
**Moderate (200-400):** gaussian, hourglass, galaxy
**Bloated (400+):** binary_tree, cold, settlement

Note: default_medium1 looks OK vs starter (176) but against ladder_hybrid_defense (295 buildings) we still lose — the gap is delivery efficiency, not pure count.

## Root Cause Hypothesis

Large/open maps (settlement, cold, galaxy) cause the bot to lay down long road/conveyor chains to reach distant ore. Each chain adds dozens of buildings. Once the chain is built it's never pruned. Over 2000 rounds these chains accumulate into 400-658 building counts.

Tight/constrained maps (corridors, face) physically limit how many buildings can be placed — natural bloat prevention.

## Recommended Fix

1. **Destroy road segments that are no longer traversed** after a harvester chain is established
2. **Cap total conveyor/road count** — once we hit ~150, stop building new roads and prioritize harvester placement instead
3. **Shorter chains** — if BFS path to ore is >N tiles, skip that ore and find closer ore instead

A cap at 150 buildings would reduce cost scale from 6x to ~2.5x, making harvesters ~2.4x cheaper and allowing far more harvesting throughput.
