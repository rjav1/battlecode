# New Test Bots - Sanity Test Results

Created 2026-04-06.

## Bots Created

### 1. `ladder_bridge` — Bridge Economy Bot
- Models Blue Dragon's bridge-heavy approach
- Spawns 15-20 builders, each finds ore, builds harvester, then bridges back to nearest conveyor/core
- Falls back to d.opposite() conveyors when bridges can't be placed
- Pure economy, no military

### 2. `ladder_dual` — Dual Competency Bot
- Models Polska Gurom: rush on tight maps, economy on open
- Tight maps (area <= 625): 2 rushers + eco builders
- Open maps: pure eco with late gunners (round 300+)
- Rushers attack enemy buildings, build roads to advance

### 3. `ladder_mega_eco` — Super Economy Bot
- Models MergeConflict/One More Time pure economy
- Aggressive builder spawning (up to 45 units)
- Minimal reserves, reinvests everything
- Zero military, d.opposite() conveyors

## Sanity Test Results

| Match | Map | Winner | Score |
|-------|-----|--------|-------|
| buzzing vs ladder_bridge | default_medium1 | **ladder_bridge** | 5679 vs 4546 Ti (tiebreak) |
| buzzing vs ladder_dual | face | **buzzing** | 8948 vs 7792 Ti (tiebreak) |
| buzzing vs ladder_mega_eco | default_medium1 | **buzzing** | 10849 vs 313 Ti stored (mega_eco mined 4950 but spent it all) |
| ladder_mega_eco vs starter | default_medium1 | **ladder_mega_eco** | 4960 mined, 35 units |

## Key Observations

- **ladder_bridge** is a genuine threat on medium maps — it beat buzzing on default_medium1
- **ladder_dual** works as intended but is weaker than buzzing on open maps
- **ladder_mega_eco** mines heavily (4950 Ti on default_medium1) but overspends on units/buildings, ending with low stored Ti
- Settlement map appears to have no reachable ore for either side — both ladder_eco and ladder_mega_eco mine 0 there

## Usage

```bash
cambc.bat run buzzing ladder_bridge <map>
cambc.bat run buzzing ladder_dual <map>
cambc.bat run buzzing ladder_mega_eco <map>
```
