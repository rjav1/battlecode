# v26: Arena Map Fix -- Nearest-Ore Scoring on Tight Maps

## Problem
On arena (25x25, 10 Ti ore, rotational symmetry), smart_eco mined 34K Ti while buzzing mined only 9.9K -- a 3.4x economy gap.

## Root Cause Analysis

### Position Asymmetry
Arena has strong position asymmetry despite rotational symmetry. Position B (core at 16,14) has significantly better ore access:

| Match (v25 baseline) | Buzzing Ti Mined | smart_eco Ti Mined |
|----------------------|-----------------|-------------------|
| buzzing(A) vs starter(B) | 27,800 | - |
| buzzing(A) vs smart_eco(B) | 9,890 | 34,020 |
| smart_eco(A) vs buzzing(B) | 9,880 | 14,800 |
| starter(A) vs buzzing(B) | - | 14,810 |

Both bots mine ~10K from position A, but smart_eco mines 34K from position B while buzzing gets 15K. The gap isn't fully position-dependent -- smart_eco out-mines buzzing from the SAME position.

### Ore Scoring Was Suboptimal
Buzzing scored ore tiles as `builder_dist + core_dist * 2`, prioritizing ore closer to core (shorter conveyor chains). On arena:
- Core vision r^2 = 36, ore is ~6 tiles away (dist^2 = 36)
- `core_dist * 2` penalty = up to 72, which can outweigh `builder_dist` of 10-20
- Builders skip nearby ore at map edges in favor of ore closer to core
- On a scarce map (10 Ti ore), every tile is contested -- speed to claim > chain efficiency

smart_eco uses pure `builder_dist` -- grab nearest ore regardless of core distance.

### Failed Approach: More Builders
Increasing tight map cap from 7 to 9 made things WORSE (4,960 Ti from pos A). More builders = more cost scaling = less Ti per builder, especially when builders waste resources on exploration conveyors that don't find ore.

## Fix Applied
On tight maps (area <= 625), switch to pure nearest-to-builder ore scoring (same as maze maps and smart_eco). Core-proximity scoring is retained for balanced and expand maps where conveyor chain length matters more.

```python
use_nearest = is_maze or map_mode == "tight"
```

## Test Results (v26)

### Arena (the target map)
| Match | Buzzing Ti Mined | smart_eco Ti Mined | Winner |
|-------|-----------------|-------------------|--------|
| buzzing(A) vs smart_eco(B) | 12,030 (+22%) | 22,060 | smart_eco |
| smart_eco(A) vs buzzing(B) | 9,880 | 14,800 (unchanged) | buzzing |

Position A improvement: 9,890 -> 12,030 Ti (+22%). Gap narrowed from 3.4x to 1.8x.

### Regression Tests -- No Regression
| Match | Buzzing Ti | smart_eco Ti | Winner |
|-------|-----------|-------------|--------|
| buzzing(A) vs smart_eco(B) default_medium1 | 18,770 | 4,900 | buzzing |
| smart_eco(A) vs buzzing(B) default_medium1 | 12,340 | 16,650 | buzzing |
| buzzing(A) vs smart_eco(B) cold | 17,230 | 14,340 | buzzing |
| smart_eco(A) vs buzzing(B) cold | 4,880 | 19,690 | buzzing |

All 4 regression tests: buzzing wins. No degradation.

## Remaining Gap
Buzzing still loses to smart_eco on arena from position A (12K vs 22K). The remaining gap is structural:
1. smart_eco has 8 builders vs buzzing's 7 on tight maps
2. smart_eco has zero military/barrier overhead -- pure economy
3. Buzzing builds early barriers (2x ~3 Ti) and later allocates attackers
4. Position B has inherently better ore access on arena's layout

These are acceptable tradeoffs -- barriers and military are needed vs real opponents, not pure eco bots.
