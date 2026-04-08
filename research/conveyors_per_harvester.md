# Conveyors Per Harvester / Buildings Per Builder Analysis

**Date:** 2026-04-08
**Test:** buzzing vs starter, seed 1, 4 maps
**All results:** buzzing wins every game (tiebreak on resources)

---

## Raw Match Data

| Map | Ti mined | Units | Buildings | Builder bots (units-1) | Buildings/builder |
|-----|:--------:|:-----:|:---------:|:----------------------:|:-----------------:|
| corridors | 18,620 | 8 | 143 | 7 | **20** |
| galaxy | 9,950 | 8 | 362 | 7 | **52** |
| cold | 19,670 | 8 | 554 | 7 | **79** |
| settlement | 28,140 | 15 | 651 | 14 | **47** |

Note: settlement spawns 14 builders (large map cap hits 15 units total) vs 7 on the others.

---

## The Bloat Threshold

**>50 buildings per builder = bloat problem.**

| Map | Buildings/builder | Bloat? | Baseline win rate |
|-----|:-----------------:|:------:|:-----------------:|
| corridors | 20 | No | 100% |
| settlement | 47 | Borderline | mixed |
| galaxy | 52 | Yes | 33% |
| cold | 79 | Yes | 33% |

corridors at 20 buildings/builder is the healthy baseline — walls physically constrain exploration so builders reuse existing paths. galaxy (52) and cold (79) are well above threshold.

---

## What Drives the Gap

**corridors:** High wall density channels builders into fixed paths. Once a conveyor chain exists, subsequent builders walk it for free (conveyors are passable). Result: 143 total buildings for 7 builders.

**cold:** 37x37 open map, only 18 walls. After placing a harvester, each builder calls `_explore()` in `main.py` which navigates toward a far sector target and places a conveyor on **every tile it steps on** via `_nav()`. No termination condition. On open terrain, 7 builders each lay 50-80 conveyors of pure exploration waste. Result: 554 buildings.

**settlement:** Large map (50x38) so the core spawns up to 14 builders. More builders = more exploring = more total buildings (651), but per-builder rate (47) is lower because builders are more likely to overlap paths on a filled map.

---

## Cost Scale Impact

Each conveyor/barrier adds +1% to global cost scale.

| Map | Buildings | Approx scale | Harvester actual cost | Ti cost to build 8 harvesters |
|-----|:---------:|:------------:|:---------------------:|:-----------------------------:|
| corridors | 143 | ~2.4x | ~48 Ti | ~384 Ti |
| settlement | 651 | ~7.5x | ~150 Ti | ~1,200 Ti |
| cold | 554 | ~6.5x | ~130 Ti | ~1,040 Ti |
| galaxy | 362 | ~4.6x | ~92 Ti | ~736 Ti |

At 6.5x scale on cold, building a harvester costs 130 Ti instead of 20 Ti. The whole harvester scaling strategy becomes unaffordable after the first 3-4 harvesters. This is why cold and galaxy mining throughput is low despite long game durations.

---

## Estimated Effective Harvesters

Harvester max output: 1 stack (10 Ti) per 4 rounds x 2000 rounds = 5,000 Ti per harvester.

| Map | Ti mined | Est. effective harvesters |
|-----|:--------:|:------------------------:|
| corridors | 18,620 | ~4 |
| galaxy | 9,950 | ~2 |
| cold | 19,670 | ~4 |
| settlement | 28,140 | ~6 |

Cold and corridors have the same ~4 harvesters but cold uses 554 buildings to get there vs 143 — the extra 411 buildings are pure exploration waste that price out future harvesters.

---

## Conclusion

The bloat root cause is confirmed: **`_explore()` builds conveyors on every step with no termination**. On open maps (cold=79 buildings/builder, galaxy=52) this creates runaway cost scaling that makes harvesters unaffordable past the first few.

**Fix:** Once a builder's `harvesters_built >= 2` (or global econ_cap is reached), switch `_explore()` to idle or road-only mode (roads cost 1 Ti at +0.5% scale vs conveyors at 3 Ti +1% scale). This would drop cold from 79 to ~25 buildings/builder, collapsing scale from 6.5x to ~2.5x and cutting harvester cost from 130 Ti to ~50 Ti.
