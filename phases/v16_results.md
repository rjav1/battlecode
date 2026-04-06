# v16 Results: shish_kebab Exploration + Early Barrier Anti-Rush

## Changes

### 1. shish_kebab exploration fix (tight maps, area <= 625)
- Extended explore range from 15 to `max(w, h)` on tight maps so builders explore the full map dimension
- Skipped gunner and barrier building on tight maps (resources too scarce)
- Bridge threshold lowered to `bc + 10` on tight maps (was `bc + 10`, kept same after testing showed more aggressive values broke corridors)

### 2. Early barrier anti-rush
- After placing first harvester, builder places up to 2 barriers near core on enemy-facing side
- Only triggers within 30 rounds and when builder is near core (dist_sq <= 18)
- Cost: ~6 Ti for 2 barriers = trivial
- Prevents core destruction by early rushes (30+ rounds of delay per barrier)

## Key Decision
Early barriers must NOT trigger before the first harvester is placed. Initial testing with `harvesters_built == 0` broke corridors (0 Ti mined) because the builder wasted its first action cooldown on a barrier instead of the first conveyor. Changed to `harvesters_built >= 1`.

## Test Results

### Target maps
| Map | Opponent | Result | buzzing Ti mined | Notes |
|-----|----------|--------|-----------------|-------|
| shish_kebab | starter | WIN | 14,260 | Was ~5K in v15, target was 8K+ |
| corridors | starter | WIN | 9,940 | No regression (was 0 with bad changes) |
| galaxy | rusher | LOSS (resources) | 1,630 | Survived to turn 2000! Was core destroyed at turn 86 |
| galaxy | starter | WIN | 9,820 | Normal performance |

### Regression vs buzzing_prev (5/5 wins, needed 3/5)
| Map | Result | buzzing Ti | prev Ti |
|-----|--------|-----------|---------|
| default_medium1 | WIN | 23,790 | 4,510 |
| settlement | WIN | 19,660 | 18,420 |
| cold | WIN | 23,140 | 10,550 |
| face | WIN | 19,130 | 12,610 |
| corridors | WIN | 9,940 | 9,930 |

## Deployment
- Submitted as Version 18 (ID: 203187bf-369a-46ac-9850-02e25319f1f4)
- buzzing_prev updated to v16
