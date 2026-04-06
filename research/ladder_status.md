# Buzzing Bees - Ladder Status Report

**Report Date:** 2026-04-05 (data captured live from game.battlecode.cam)

## Team Overview

| Field | Value |
|---|---|
| Team Name | buzzing bees |
| Team ID | d26cf1d1-efc6-45d2-ac75-bfba4ce4aadc |
| Category | main |
| Region | international |
| Current Elo | 1490 |
| Current Rank | #131 of 572 |
| Peak Rank | N/A (not yet established) |
| Peak Rating | N/A (not yet established) |
| Total Matches | 1 |
| Members | 1/4 (craig, owner) |
| Submission | v1 |

## Current Standing Summary

We are **unranked** with only 1 ladder match played. Our Elo dropped from the starting 1500 to 1490 after a loss. We sit at rank #131 out of 572 teams, but this is largely a default placement -- many teams below us also have few or zero matches.

## Match History (Complete)

### Match 1 (LOSS) -- Our Only Match

| Field | Value |
|---|---|
| Match ID | 7c9a4dd9-227d-49de-8146-8d42fdb6daa9 |
| Date/Time | Apr 5, 10:12:27 PM |
| Opponent | One More Time |
| Opponent Elo | 1493 (Silver) |
| Opponent Rank | #124 of 572 |
| Opponent Matches | 2560 |
| Result | **1-4 LOSS** |
| Elo Change | -9.9 (1500 -> 1490) |
| Match Duration | 2m 53s |
| Match Type | ladder (rated) |

#### Game-by-Game Breakdown

| Game # | Map | Winner | Condition | Turns |
|---|---|---|---|---|
| 1 | landscape | One More Time | Resource Victory | 2000 |
| 2 | battlebot | One More Time | Resource Victory | 2000 |
| 3 | cold | One More Time | Resource Victory | 2000 |
| 4 | corridors | One More Time | Resource Victory | 2000 |
| 5 | pls_buy_cucats_merch | **buzzing bees** | Resource Victory | 2000 |

## Loss Analysis

### Match vs One More Time (1-4 LOSS)

**Opponent Profile:**
- "One More Time" has played 2560 matches -- they are highly experienced
- Their Elo is 1503 (Gold tier), rank #124
- They have a peak rank of #76 and peak rating of 1579
- 3 members on the team (MathCosine, Luca, KURATUS)
- They win roughly 50% of their matches against similar-Elo opponents based on their recent history

**Key Observations:**
1. **All 5 games went to turn 2000** -- no early eliminations. Every game was decided by Resource Victory at the maximum turn count. This means our bot survives to endgame but loses the resource accumulation race.
2. **We lost on 4 of 5 maps**: landscape, battlebot, cold, corridors
3. **We won on 1 map**: pls_buy_cucats_merch
4. **The loss condition is consistently Resource Victory** -- we are being out-resourced, not out-fought. Our bot likely lacks an efficient resource gathering strategy or is not contesting resources effectively.

### Maps We Lost On
- **landscape** -- Resource Victory at turn 2000
- **battlebot** -- Resource Victory at turn 2000
- **cold** -- Resource Victory at turn 2000
- **corridors** -- Resource Victory at turn 2000

### Map We Won On
- **pls_buy_cucats_merch** -- Resource Victory at turn 2000

## Elo Range Context

Based on the ladder data, our current Elo (1490) puts us in the following neighborhood:

| Rank | Elo | Team | Matches |
|---|---|---|---|
| #127 | 1498 | MergeConflict | 1365 |
| #128 | 1496 | Highly Suspect | 2560 |
| #129 | 1492 | Vibecoders | 2559 |
| #130 | 1492 | Chameleon | 2362 |
| **#131** | **1490** | **buzzing bees** | **1** |
| #132 | 1486 | SPAARK | 2561 |
| #133 | 1483 | DODO | 803 |
| #134 | 1482 | Quwaky | 1474 |
| #135 | 1481 | The Defect | 2560 |

Most teams around us have played 1000-2500+ matches. We have played 1. Our Elo will be highly volatile as we play more matches.

## Tier Breakdown (from ladder)

| Tier | Elo Range | Example Teams |
|---|---|---|
| Grandmaster | 2500+ | Blue Dragon (2778), something else (2562) |
| Master | 2200-2500 | Kessoku Band (2714), meowl fan club (2203) |
| Candidate Master | 2000-2200 | WindRunners (2190), PPP (2116) |
| Diamond | 1900-2000 | JDK: More like IDK (1997), nus duck robots (1945) |
| Gold | 1500-1600 | muteki (1575), X_101 (1558) |
| Silver | 1400-1500 | MWLP (1434), arnon (1432) |
| Bronze | <1400 | Room 40z (1269), TheWarriors (1234) |

We are at the **bottom edge of Gold / top of Silver** territory.

## Win Rate

- **Overall: 0-1 (0% win rate)**
- **Game-level: 1-4 (20% game win rate)**

With only 1 match this is not statistically meaningful, but the pattern is clear: we lose the resource game on most maps.

## Patterns and Priorities

### What the data tells us:
1. **Resource collection is our primary weakness.** Every single game ended at turn 2000 with a Resource Victory. We are not dying early -- we survive but get out-resourced.
2. **We may have a map-specific advantage on pls_buy_cucats_merch** -- worth investigating what's different about that map layout.
3. **Our opponent was not particularly strong** (Elo 1493, similar to ours). Teams at this Elo range are beatable. We should be able to compete here with improvements to resource gathering.
4. **We need more matches** to establish a meaningful Elo and identify map-specific patterns.

### Code-Level Root Cause Analysis (bots/buzzing/main.py)

Reviewing our v1 bot against the match data, several structural weaknesses explain the consistent Resource Victory losses:

1. **No conveyor chains to core.** Our builders build conveyors only as movement obstacles (line 258-262: `face = d.opposite()`). They face backward from movement direction, not toward the core. This means harvesters are likely NOT connected to the core, so harvested resources may not be flowing back efficiently. Top teams build deliberate conveyor chains from harvesters to core.

2. **Builder cap is too conservative early.** Core spawns max 2 builders until round 40, then 4 until round 200 (line 33). With only 2 builders in the critical early game, we're slow to reach ore deposits and build harvesters. The roadmap targets first harvester by round 10-15; our builder cap may delay this.

3. **Harvester placement is greedy, not strategic.** `_best_adj_ore` (line 305-313) picks the closest ore to core, but doesn't consider whether a conveyor chain exists or can be built. Isolated harvesters generate resources that may never reach the core.

4. **Resource hoarding buffer.** We require `ti >= cost + 50` to spawn builders (line 38) and `ti >= harvester_cost + 15` to build harvesters (line 116). At Silver/Gold Elo, opponents are likely spending resources more aggressively. Our 50-Ti buffer for builders is cautious.

5. **Attacker role drains economy.** After round 400, 25% of builders (my_id % 4 == 2) switch to attacking (line 106). This permanently removes a builder from economic production to walk across the map. Against a ~1500 Elo opponent who likely turtles, this wastes a unit.

6. **Sentinel placement too late and too few.** Sentinels only place after round 200, only by builder id%4==1, capped at 2 visible sentinels (lines 100, 147, 161). This means minimal defense and no ammo supply chain.

7. **No foundry or axionite harvesting.** The bot only harvests titanium ore (line 96: `ORE_TITANIUM`). Axionite ore is completely ignored. If the tiebreaker counts total resources or if axionite harvesters provide additional income, we're leaving resources on the table.

### Recommended Priorities (from match data + code analysis):

1. **FIX: Conveyor chains from harvesters to core** -- This is the #1 issue. Without connected supply chains, harvesters may generate resources that never reach our core, directly explaining why we lose Resource Victory tiebreakers.
2. **FIX: Increase early builder count** -- Spawn 3 builders by round 15 to accelerate harvester placement.
3. **INVESTIGATE: What resources count for Resource Victory** -- Do we need axionite too? Is it total Ti in core, or total harvested?
4. **REDUCE: Attacker allocation** -- 25% of builders attacking is too aggressive at this Elo. Consider 1 attacker only after 6+ harvesters.
5. **IMPROVE: Sentinel ammo supply** -- Sentinels without ammo are useless obstacles. Need splitter-based delivery.
6. **TEST: Watch replays** -- Use the visualiser to confirm whether conveyor chains are the bottleneck.

### Recommended investigation:
- Watch replays of the 4 losses (landscape, battlebot, cold, corridors) via the visualiser to understand where we fall behind on resources
- Watch the replay of our win on pls_buy_cucats_merch to understand what works
- Focus bot improvements on resource accumulation efficiency
- Consider requesting test matches against lower-rated opponents to establish baseline performance

## Raw Data

### Ladder Position (nearby teams, ranks 123-140)

```
#123  1503  Pray and Deploy      main  Int'l  2561 matches
#124  1503  One More Time        main  Int'l  2560 matches
#125  1503  natto warriors       main  UK     2560 matches
#126  1501  KCPC-B               main  UK     8 matches
#127  1498  MergeConflict        novice Int'l 1365 matches
#128  1496  Highly Suspect       main  Int'l  2560 matches
#129  1492  Vibecoders           main  Int'l  2559 matches
#130  1492  Chameleon            novice UK    2362 matches
#131  1490  buzzing bees         main  Int'l  1 match
#132  1486  SPAARK               main  Int'l  2561 matches
#133  1483  DODO                 main  UK     803 matches
#134  1482  Quwaky               main  Int'l  1474 matches
#135  1481  The Defect           main  Int'l  2560 matches
#136  1476  Cenomanum            novice UK    2560 matches
#137  1473  Solo Gambling        novice Int'l 284 matches
#138  1470  Some People          main  UK     2561 matches
#139  1468  strong vibe          main  Int'l  2560 matches
#140  1467  O_O                  main  Int'l  2560 matches
```

### Match Result Detail

```
Match: 7c9a4dd9-227d-49de-8146-8d42fdb6daa9
Date: Apr 5, 2026, 10:12:27 PM
Type: Rated Ladder Match

buzzing bees (1500, v1) vs One More Time (1493)
Result: 1-4 LOSS
Elo change: -9.9

Game 1: landscape       -> One More Time wins (Resource Victory, 2000 turns)
Game 2: battlebot       -> One More Time wins (Resource Victory, 2000 turns)
Game 3: cold            -> One More Time wins (Resource Victory, 2000 turns)
Game 4: corridors       -> One More Time wins (Resource Victory, 2000 turns)
Game 5: pls_buy_cucats_merch -> buzzing bees wins (Resource Victory, 2000 turns)
```
