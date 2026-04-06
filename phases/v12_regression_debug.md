# v12/v13 Regression Debug Report

## Summary
v13 is a net regression. Reverting to v12 (buzzing_prev).

## Galaxy Rush Reproduction

Both v12 AND v13 lose to rusher on galaxy with identical results:
- **buzzing (v13) vs rusher**: LOSS (970 Ti vs 4920 Ti) -- tiebreak loss at turn 2000
- **buzzing_prev (v12) vs rusher**: LOSS (970 Ti vs 4920 Ti) -- identical result

The galaxy rush vulnerability is NOT a v13 regression -- it exists in v12 too.
The "Core Destroyed at turn 86" from the ladder was likely against a stronger rush bot.

Against test_attacker on galaxy: v13 WINS (16,650 Ti vs 0), so it's rush-specific.

## v13 vs v12 Head-to-Head Results

### Regressed Maps (v13 LOSES all 3):
| Map | v13 Ti Mined | v12 Ti Mined | Winner | Delta |
|-----|-------------|-------------|--------|-------|
| galaxy | 9,700 | 14,660 | v12 | -34% |
| cinnamon_roll | 0 | 0 | v12 (tie) | ~tied |
| tiles | 14,740 | 28,820 | v12 | -49% |

### v13 vs Starter:
| Map | v13 Ti Mined | v12 Ti Mined | Notes |
|-----|-------------|-------------|-------|
| galaxy | 4,960 | 4,950 | Essentially identical vs starter |
| cinnamon_roll | 0 | 0 | Both lose to starter (!) |
| tiles | 14,740 | 14,740 | Identical vs starter |
| default_medium1 | 23,390 | 9,790 | v13 MUCH better here |

### v13 vs v12 on default_medium1:
v13 wins 25,800 vs 8,820. v13's delayed military helps on open maps.

## Root Cause Analysis

### What v13 Changed from v12:
1. **Gunner builder trigger: round 200 -> 400** (delayed by 200 rounds)
2. **Attacker trigger: round 500 -> 700** (delayed by 200 rounds)
3. **Attacker harvester requirement: 4 -> 5** (needs more harvesters)
4. **Skip barriers on tight maps** (new map_mode check)

### Why v13 Regresses on Tiles (-49% Ti):
The id%5==1 builder, when diverted to gunner building at round 200 (v12), STOPS
building conveyors and bridges. This is actually beneficial on maps like tiles where
continued exploration wastes Ti on infrastructure. In v13, this builder continues
exploring until round 400, spending Ti on conveyors/bridges that don't yield enough
harvesters to justify the cost.

### Why v13 Wins on default_medium1 (+193% Ti):
On open maps with abundant ore, the extra 200 rounds of harvesting by the gunner-builder
produces more harvesters, which compound into higher Ti income. The military diversion
at round 200 was too early for these maps.

### Bridge Analysis (Task 3):
- Bridge threshold: `bc + 20` on non-tight maps -- this is low but identical in v12/v13
- Bridge priority IS above roads (bridge fallback at line 239, road at line 258)
- Bridge bounds checking: uses `bt.distance_squared(pos) > 9` check, adequate
- Bridge building on galaxy: not the root cause (identical in v12/v13)

## Decision: REVERT to v12

v13 loses head-to-head on ALL 3 regressed maps. The delayed military timing was a
bad trade -- the maps where v13 wins (default_medium1) are less common on the ladder.

**Action**: Copy buzzing_prev/main.py -> buzzing/main.py

## Galaxy Rush: Separate Issue
The galaxy rush vulnerability exists in BOTH v12 and v13. This needs a separate fix
(early defense, rush detection, etc.) and should not block the revert.
