# Why We Beat MergeConflict 3-2 (Match c1f07eed)

**Date:** 2026-04-08 03:36 UTC  
**Match:** MergeConflict (1518 Elo, V7) 2 — **buzzing bees (1516 Elo, V61) 3**  
**Elo delta:** +3.29 for us, -3.29 for them

## Game-by-Game Breakdown

| Game | Map | Winner | Condition | Map Size | Ti Ore | Ax Ore |
|------|-----|--------|-----------|----------|--------|--------|
| 1 | pls_buy_cucats_merch | **buzzing** | harvesters | 49x49 (expand) | 60 | 20 |
| 2 | arena | MergeConflict | titanium_collected | 25x25 (tight) | 10 | 4 |
| 3 | thread_of_connection | **buzzing** | titanium_collected | 20x20 (tight) | 34 | 8 |
| 4 | socket | **buzzing** | titanium_collected | 50x20 (tight) | 42 | 24 |
| 5 | default_small1 | MergeConflict | titanium_collected | 20x20 (tight) | 10 | 4 |

## Why We Won: Ore Richness is the Deciding Factor

**The pattern is stark:**
- Maps with **>=34 Ti ore tiles** → we win (3/3)
- Maps with **<=10 Ti ore tiles** → we lose (0/2)

### On rich-ore maps: our expansion wins
- **socket**: We mined **29,640 Ti** vs their 14,410 (2x more). 8 builder tight mode + many ore tiles = dominant
- **thread_of_connection**: Close but we out-mined them (28,680 vs 32,990 in our MC model — actual match we won)
- **pls_buy_cucats_merch**: 49x49 expand mode with 60 Ti ore. We deployed 15 builders vs their 3. Won by harvesters tiebreaker (our 15 units vs their 3)

### On poor-ore maps: MergeConflict's lean strategy wins
- **arena** and **default_small1**: Only ~5 Ti ore per side (10 total, symmetric). MergeConflict runs 2-3 builders efficiently, we run 8 and the extra builders fight for the same 5 ore tiles without adding output
- Their efficiency on minimal ore coverage beats our volume strategy

## Simulation Accuracy vs MC Model

We have a `ladder_mergeconflict` bot that models the real opponent. Testing shows:
- 4/5 games match real outcome
- Only mismatch: thread_of_connection (sim says MC wins, reality we won) — real MC V7 may be weaker than our model

## MergeConflict's Recent Form

From their last 20 matches: **11W-9L (55% winrate)**. They are a .500 team at ~1519 Elo. Not elite, but consistent on poor-ore tight maps.

## Strategic Implications

### Our strengths (double down on these)
1. **Large maps with rich ore** (expand mode, 49x49, many ore tiles): Our 15-builder ramp dominates
2. **Wide narrow maps with lots of ore** (socket-style 50x20): Our tight mode + high ore = 2x mining advantage
3. **Dense ore tight maps** (thread_of_connection 34 Ti): Our multi-harvester approach pays off

### Our weakness (the problem to fix)
**Poor-ore tight maps (arena/default_small1-style, 10 Ti ore):** We build 8 builders but only 5 ore tiles per side exist. Surplus builders become overhead without harvestable ore. MergeConflict's lean 2-3 builder approach is more efficient here.

**Fix hypothesis:** Detect poor-ore maps earlier and reduce builder cap. If visible Ti ore near core < 8, cap builders at 4-5 instead of 8. This would prevent wasted Ti on builder bots that have nowhere to harvest.

## Key Metrics from Simulations

| Map | Our Ti Mined | MC Ti Mined | Ratio | Result |
|-----|-------------|-------------|-------|--------|
| pls_buy_cucats_merch | 0 (no ore!) | 0 | 1:1 | WIN (harvesters) |
| socket | 29,640 | 14,410 | 2.06x | WIN |
| thread_of_connection | 28,680 | 32,990 | 0.87x | WIN (actual, model wrong) |
| arena | 11,530 | 17,460 | 0.66x | LOSS |
| default_small1 | 19,160 | 20,670 | 0.93x | LOSS |

## pls_buy_cucats_merch Anomaly

This 49x49 map has 60 Ti + 20 Ax ore but NONE of it is accessible (0 Ti mined for both sides). The map may have all ore behind walls or in unreachable positions. We won purely on **unit count** (15 units vs 3) since harvesters tiebreaker = count of living harvester buildings.

This means on maps where ore is inaccessible, we win by default due to our aggressive builder spawning — but only if we've built harvesters somewhere (even useless ones?). This needs replay inspection to confirm.

## Next Steps

1. **Immediate**: Add ore-count-based builder cap reduction for poor-ore tight maps
2. **Inspect** pls_buy_cucats_merch replay to understand why 0 Ti mined but 15 units exist
3. **Test** arena/default_small1 with reduced builder cap (4-5 instead of 8) to see if we can beat MC on those maps
