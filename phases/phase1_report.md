# Phase 1 Report: Economic Engine

## What Was Built

A pure titanium economy bot at `bots/buzzing/main.py` (~150 lines). Single file, no external dependencies.

### Architecture
- **Core**: Spawns builders progressively (2 early, up to 8 late game)
- **Builder**: BFS-guided navigation + greedy fallback, builds conveyor chains from ore to core
- **Conveyor chain**: Each conveyor faces `d.opposite()` (back toward builder's origin), creating connected chains from harvesters to core
- **Exploration**: ID-diversified outward exploration when no ore visible

### Key Design Decisions
1. **BFS within vision** for wall avoidance, with multi-direction fallback (v1-style) to avoid road over-building
2. **Conveyors preferred over roads** — roads only as last resort when ALL 8 directions fail for both conveyors and movement
3. **Pre-computed vision data** — single pass over `get_nearby_tiles()` builds passable set for BFS and ore list, minimizing API calls
4. **Resource reserves** — builder keeps 15 Ti buffer, core keeps 50 Ti, preventing resource starvation

## Test Results

### Default Maps (all seeds tested)

| Map | Default Seed | Seed 42 | Seed 123 | Ti Mined (default) |
|-----|-------------|---------|----------|-------------------|
| default_small1 | WIN | WIN | WIN | 24,190 |
| default_small2 | WIN | WIN | WIN | 23,980 |
| default_medium1 | WIN | WIN | WIN | 19,200 |
| default_medium2 | WIN | WIN* | WIN | 26,130 |
| default_large1 | WIN | WIN | WIN | 18,880 |
| default_large2 | WIN | WIN | WIN | 37,460 |

*default_medium2 seed 42 showed inconsistent results across runs (engine non-determinism), but won on majority of attempts.

### Competitive Maps

| Map | Default Seed | Seed 99 | Ti Mined (default) |
|-----|-------------|---------|-------------------|
| arena | WIN | WIN | 23,580 |
| hourglass | WIN | WIN | 24,760 |
| corridors | WIN | WIN | 14,700 |
| settlement | WIN | WIN | 38,600 |
| wasteland | WIN | LOSS* | 12,260 |
| face | WIN | — | 4,980 |
| cubes | WIN | — | 29,100 |
| butterfly | WIN | — | 33,420 |

*Wasteland is seed-dependent: some positions have better ore access than others.

### Additional Maps

| Map | Result | Notes |
|-----|--------|-------|
| galaxy | WIN | 9,700 mined |
| binary_tree | WIN | 4,850 mined |
| cold | WIN | 8,700 mined |
| sierpinski_evil | LOSS | 0 mined both teams — 66 fragmented regions |
| cinnamon_roll | LOSS | 0 mined both teams — spiral walls |

### Self-Play
- `buzzing vs buzzing`: Runs without crashes. Symmetric performance.

### CPU
- No timeouts on any map including cubes (50x50, largest map).

## Assumptions Tested

1. **Diagonal movement through wall corners**: YES, works. BFS with 8-directional movement navigates fragmented maps (wasteland, butterfly).
2. **Conveyor chain delivery**: YES, resources flow through `d.opposite()` conveyor chains to core. Verified 24K+ Ti mined on multiple maps.
3. **Harvester placement**: Works on ore tiles adjacent to walls. `can_build_harvester` handles edge cases.
4. **Builder walking on conveyors**: YES, builders walk on conveyors regardless of facing direction or team.
5. **Action + move cooldown**: Confirmed mutually exclusive per round. Build OR move, never both.
6. **Core tile walkability**: YES, builders walk freely on allied core tiles.

## Known Limitations

1. **Wasteland inconsistency**: Seed-dependent on wasteland due to asymmetric ore access. Some seeds get 0 mined.
2. **Highly fragmented maps** (sierpinski_evil, cinnamon_roll): Can't deliver resources when ore requires very long winding paths through 60+ wall regions.
3. **Chain gaps**: When builder walks through existing passable tiles (roads from earlier exploration), those tiles don't have conveyors, creating gaps in the resource chain.
4. **No bridges**: Blue Dragon uses 33+ bridges for cross-terrain resource transport. We use 0.
5. **No sentinels**: No military defense. Any bot with turrets will have free reign.
6. **No inter-unit communication**: Builders don't coordinate, may target the same ore.

## Reviewer Findings

### Code Quality Review
- **Chain gaps confirmed**: Conveyors at `d.opposite()` create chains along builder paths, but gaps occur when builders walk through roads/existing tiles without building conveyors
- **Harvester output not guaranteed connected**: Builder may be on a road (not conveyor) when placing harvester, so output has nowhere to go
- **Broad except clause**: Fixed to `continue` with comment
- **Ti competition**: Multiple builders check shared pool independently - no coordination
- **CPU budget**: ~120 FFI calls per builder per round. Safe for now but monitor with higher builder counts

### Strategic Review
- **Conveyor topology is accidental, not intentional** - BD builds 308 purpose-built conveyors vs our pathfinding conveyors
- **Zero bridges** (BD uses 33) - critical for fragmented maps
- **Builder cap too low** (max 8 vs BD's 15+)
- **Zero military** - any opponent with sentinels walks to our core unopposed
- **Phase 2 should prioritize intentional chain routing, then bridges, then sentinels**

## Phase 2 Priorities (informed by reviews)

1. **Intentional conveyor routing**: After harvester, walk back building conveyors to ensure connected chain
2. **Bridges** for cross-terrain resource transport (33 bridges = Blue Dragon's key advantage)
3. **Sentinel defense** (2-4 by round 150, positioned toward enemy)
4. **Raise builder cap** to 12-15 by endgame
5. **Marker-based communication** for builder coordination
6. **Splitters** for conveyor merge points
