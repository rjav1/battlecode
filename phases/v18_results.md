# v18 Results: Fix econ_cap floor

## The Fix
`econ_cap = max(6, vis_harv * 3 + 4)` — floor of 6 so builders never starve when harvesters are out of vision.

## Test Results

### vs smart_eco on settlement
- buzzing: 19660 mined
- smart_eco: 27230 mined
- Winner: smart_eco (still ahead, but buzzing now functional on large map)

### vs starter on settlement
- buzzing: 37510 mined
- starter: 0 mined
- Winner: buzzing

### Regression (buzzing vs buzzing_prev)

| Map            | buzzing mined | buzzing_prev mined | Winner       |
|----------------|--------------|-------------------|--------------|
| default_medium1 | 23780        | 7510              | buzzing      |
| settlement     | 19660        | 17520             | buzzing      |
| corridors      | 14650        | 14650             | buzzing_prev (tiebreak, identical) |
| face           | 14730        | 17110             | buzzing_prev |
| hourglass      | 23560        | 19460             | buzzing      |

**Score: 3/5 wins** — meets regression threshold.

## Notes
- settlement Ti jumped: buzzing now mines more than buzzing_prev on large map (19660 vs 17520)
- corridors is effectively a draw (identical resources, units, and buildings)
- face regression: econ_cap floor of 6 may over-build builders on some medium maps; tradeoff accepted
- smart_eco gap on settlement remains (19660 vs 27230) — further cap tuning needed in future version
