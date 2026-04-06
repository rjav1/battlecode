# The Defect 0-5 Replay Analysis

## Match Summary

| Match | Date/Time | Score | Our Version | Maps |
|-------|-----------|-------|-------------|------|
| WIN | Apr 6, 12:12 PM | buzzing bees 4-1 The Defect | V43 | hooks, shish_kebab, default_large1, cold, corridors |
| LOSS | Apr 6, 03:12 PM | The Defect 5-0 buzzing bees | V45 | landscape, wasteland, hooks, starry_night, chemistry_class |

**Key difference #1: We changed bot versions (V43 -> V45) between matches.**
**Key difference #2: Completely different map pools (only "hooks" shared).**

## 0-5 Loss: Per-Game Breakdown

All 5 games ended as **Resource Victory at round 2000** -- no core kills.

### Game 1: landscape

| Metric | The Defect | buzzing bees | Ratio |
|--------|-----------|-------------|-------|
| Ti collected (r500) | 3500 | 2290 | 1.5x |
| Ti collected (r1000) | 7300 | 4790 | 1.5x |
| Ti collected (r2000) | 14960 | 9790 | 1.5x |
| Harvesters (r500) | 29 | 8 | 3.6x |
| Roads | 178 | 12 | -- |
| Conveyors | 71 | 293 | -- |
| Bots | 6 | 10 | -- |
| Turrets | 0 | 0 | -- |

**Analysis:** Consistent 1.5x Ti collection gap driven by 3.6x harvester advantage. The Defect uses roads for builder movement (178 roads, cheap at 1 Ti each) while we use conveyors (293 conveyors at 3 Ti each). Our conveyor-heavy approach wastes Ti on infrastructure instead of harvesters.

### Game 2: wasteland

| Metric | The Defect | buzzing bees | Ratio |
|--------|-----------|-------------|-------|
| Ti collected (r500) | 2720 | **0** | INF |
| Ti collected (r2000) | 12140 | **0** | INF |
| Harvesters (r500) | 19 | 1 | 19x |
| Harvesters (r2000) | 28 | 2 | 14x |
| Bots (r2000) | 6 | 15 | -- |
| Conveyors (r2000) | 264 | 248 | -- |

**Analysis:** CATASTROPHIC FAILURE. We collected ZERO titanium the entire 2000-round game. We had 248 conveyors and 15 bots but only 2 harvesters, and those 2 harvesters were not connected to the core. We spent all our starting 500 Ti on bots and conveyors that accomplished nothing. The Defect collected 12140 Ti. This map has sparse, scattered ore that our bot clearly cannot handle.

### Game 3: hooks

| Metric | The Defect | buzzing bees | Ratio |
|--------|-----------|-------------|-------|
| Ti collected (r500) | 3520 | 2780 | 1.3x |
| Ti collected (r2000) | 20400 | 12160 | 1.7x |
| Harvesters (r500) | 7 | 2 | 3.5x |
| Roads (r2000) | 315 | 0 | -- |
| Conveyors (r2000) | 62 | 336 | -- |

**Analysis:** Closest game early (1.3x gap at r500) but The Defect's harvester advantage compounds over time (1.7x at end). We build 0 roads but 336 conveyors. Note: we WON hooks in the 4-1 match (with V43) but LOST it here (with V45), suggesting V45 regression on this map.

### Game 4: starry_night

| Metric | The Defect | buzzing bees | Ratio |
|--------|-----------|-------------|-------|
| Ti collected (r500) | 5750 | 1000 | 5.75x |
| Ti collected (r2000) | 33390 | 4830 | 6.9x |
| Harvesters (r500) | 40 | 6 | 6.7x |
| Roads (r2000) | 336 | 1 | -- |
| Conveyors (r2000) | 225 | 440 | -- |

**Analysis:** Worst blowout. The Defect built 40 harvesters by round 500 vs our 6. Nearly 7x Ti collection advantage. The map has swirl patterns -- ore is accessible but spread out, and The Defect is vastly better at reaching and harvesting distant ore patches.

### Game 5: chemistry_class

| Metric | The Defect | buzzing bees | Ratio |
|--------|-----------|-------------|-------|
| Ti collected (r500) | 7430 | 4630 | 1.6x |
| Ti collected (r2000) | 32740 | 19590 | 1.7x |
| Harvesters (r500) | 19 | 10 | 1.9x |
| Roads (r2000) | 341 | 0 | -- |
| Conveyors (r2000) | 169 | 454 | -- |

**Analysis:** Closest game in raw numbers (19590 Ti collected) but still a clear loss. Again, The Defect builds nearly 2x more harvesters.

## The Defect's Strategy (observed across all 5 games)

1. **Road-based builder movement**: Uses roads (1 Ti each, +0.5% scale) instead of conveyors (3 Ti each, +1% scale) for builder paths. This is 3x cheaper per tile and adds half the cost scaling.
2. **Massive harvester counts**: Consistently builds 19-40 harvesters per game vs our 2-10. They prioritize harvester density above all else.
3. **Lean bot count**: Always exactly 6 bots (core + 5 builders). They don't waste units on extra bots.
4. **No turrets, no axionite**: Pure Ti economy play. No foundries, no gunners, no military. Win by economic dominance.
5. **Conveyor-light**: Uses fewer conveyors (62-264) because roads handle movement; conveyors are only for resource transport chains.

## Our Weaknesses Exposed

1. **Conveyor-heavy infrastructure**: We build 200-450 conveyors at 3 Ti each (600-1350 Ti on conveyors alone). Much of this is for builder movement, not resource transport. We should use roads instead.
2. **Too few harvesters**: We consistently build only 2-10 harvesters. On maps with distant ore (wasteland, starry_night), we sometimes fail to build ANY working harvester chains.
3. **Too many bots**: We spawn 10-15 bots vs their 6. Extra bots cost 30+ Ti each (with scaling) and don't produce economic value if they can't reach ore.
4. **Broken on sparse-ore maps**: On wasteland, we collected 0 Ti in 2000 rounds. Our pathfinding/expansion doesn't handle maps where ore is far from the core.
5. **Bridge usage**: We use bridges (0-8) while they use 0. Bridges cost 20 Ti + 10% scaling each -- expensive and may not provide proportional value.

## V43 vs V45 Regression

- The 4-1 WIN used V43; the 0-5 LOSS used V45
- On the shared map "hooks": V43 won, V45 lost
- This strongly suggests V45 introduced a regression in economy/harvester placement
- V44/V45 changes should be reviewed for unintended harvester or expansion regressions

## Recommendations

1. **Use roads for builder movement, not conveyors** -- 3x cheaper, half the scaling
2. **Prioritize harvester count** -- aim for 15-30+ harvesters, not 5-10
3. **Reduce bot count** -- 6 bots (5 builders) is enough if they are efficient
4. **Fix sparse-ore map pathfinding** -- ensure bots can navigate to distant ore and build connected chains
5. **Review V44/V45 changes** -- identify and revert any harvester/expansion regressions
6. **Skip bridges early game** -- too expensive (20 Ti + 10% scaling) when roads work fine
7. **No military spending** -- at our current Elo, pure economy beats mixed strategies
