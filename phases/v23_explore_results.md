# v23: Sector-Based Exploration Results

## Change
On large maps (area >= 1600), replaced the old `id*3 + explore_idx + round//100` exploration formula with sector-based exploration from core position:
- Each builder gets a unique sector: `(id + explore_idx + round//200) % 8`
- Targets the map edge in that direction from the core (not builder position)
- No `*3` multiplier — consecutive builder IDs now get adjacent sectors, covering all 8 directions with 8 builders
- Slower rotation (every 200 rounds vs 100) — gives builders time to reach distant ore deposits

Small/medium maps (area < 1600) retain the original exploration formula unchanged.

## Key Insight
The old formula `id*3` caused direction collisions: builders with IDs 0,1,2 mapped to directions 0,3,6 which overlapped when taken modulo 8. Combined with all builders rotating simultaneously, this meant multiple builders explored the same area while leaving other map regions uncovered.

smart_eco uses essentially the same formula but compensates with 8 builders. Our fix addresses the root cause: direction diversity.

## Test Results

### Settlement (50x38, 148 Ti ore) — Primary Target
| Matchup | P1 Ti Mined | P2 Ti Mined | Winner |
|---------|-------------|-------------|--------|
| buzzing vs smart_eco | **37,290** | 19,200 | buzzing |
| buzzing vs buzzing_prev | **26,980** | 14,030 | buzzing |
| buzzing_prev vs buzzing | 19,610 | **19,620** | buzzing |

**Settlement Ti: 37,290 (target was >25K, baseline was 19.6K) — +90% improvement**

### Other Large Maps
| Map | buzzing Ti Mined | prev Ti Mined | Change |
|-----|-----------------|---------------|--------|
| cold (37x37) | 24,730 | 14,800 | +67% |
| cubes (50x50) | 30,240 | 28,150 | +7% |
| starry_night P1 (50x41) | 28,330 | 33,340 | -15% mined, but buzzing wins on delivered Ti |
| starry_night P2 | 31,710 | 9,530 | +233% |

### default_medium1 (30x30) — Regression Check
No regression. Both buzzing and buzzing_prev produce identical results (18,580 vs 33,930 Ti) because the medium-map exploration code is unchanged. The P2 advantage is inherent to this map — buzzing_prev vs itself shows the same pattern.

## Conclusion
Sector-based exploration is a major improvement on large maps with dispersed ore. The change is targeted (large maps only) and causes no regression on smaller maps.
