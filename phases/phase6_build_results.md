# Phase 6 Economy Fix - Build Results

## Changes Implemented

1. **Roads for exploration** - `_nav` builds roads (1 Ti, +0.5% scale) instead of conveyors (3 Ti, +1% scale) for pathfinding movement
2. **Conveyor chains only for harvester->core** - After building a harvester, builder walks back toward core placing conveyors facing toward core. Stops when: adjacent to core, finds existing conveyor facing core, or after 20 steps max
3. **Faster builder spawning** - Cap: 3 by round 30, 5 by round 150, 7 by round 400, 8 after (was: 2 by 40, 4 by 200, 6 by 500, 8 after)
4. **Deferred military** - Sentinel timing 200->300, attacker activation 400->700, attacker harvester req 2->4

## Test Results: buzzing vs starter

| Map | Winner | buzzing Ti | starter Ti | buzzing Buildings | starter Buildings |
|-----|--------|-----------|-----------|------------------|------------------|
| landscape | **buzzing** | 2963 | 4601 | 338 | 354 |
| battlebot | **buzzing** | 4020 | 4528 | 181 | 279 |
| cold | starter | 3732 | 1557 | 343 | 662 |
| corridors | starter | 3420 | 2801 | 178 | 469 |
| default_medium1 | **buzzing** | 3946 | 3775 | 240 | 525 |
| settlement | starter | 2790 | 217 | 422 | 1014 |
| arena | starter | 4414 | 4141 | 173 | 385 |
| face | **buzzing** | 4494 | 4842 | 117 | 229 |

**Record: 4 wins, 4 losses vs starter**

## Mirror Match

| Map | Winner | P1 Ti | P2 Ti | P1 Buildings | P2 Buildings |
|-----|--------|-------|-------|-------------|-------------|
| default_medium1 | buzzing (P1) | 4005 | 4174 | 172 | 198 |

## Analysis

- All games show "0 mined" for Ti -- neither bot is successfully mining Ti from harvesters and delivering to core. The Ti values shown are remaining passive income (500 start + 10 every 4 rounds = ~5500 max by round 2000)
- Building counts are significantly reduced (117-422 vs old 391+ on cold alone in phase 5), indicating cost scaling improvement
- On maps we lose, starter builds MORE buildings (469-1014) meaning its conveyors actually form functional delivery chains by volume
- The resource victory tiebreak checks Ti delivered to core first, then remaining Ti. Since neither bot mines, it falls to remaining Ti -- the bot that spent less on buildings wins
- Wins happen when buzzing conserves more Ti by building fewer structures
- Losses happen on maps where starter's mass-conveyor approach costs less total despite higher count (likely because starter's conveyors are cheaper early before scale ramps)

## Key Observation

The "0 mined" across ALL games means our conveyor chains from harvester to core are NOT successfully delivering resources. This could mean:
1. Chain direction is wrong (conveyors not aligned properly)
2. Chains don't connect all the way to core
3. Harvesters aren't on ore tiles that produce
4. The game tracks "mined" differently than expected

The economy fix reduced wasteful building, but the core problem -- getting resources from harvesters to core -- remains unsolved on all maps.
