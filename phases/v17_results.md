# v17 Results: Raise econ_cap on balanced/expand maps

## Change
Raised `econ_cap` multiplier in `bots/buzzing/main.py` line 80:
```python
# OLD: econ_cap = vis_harv * 2 + 3
# NEW: econ_cap = vis_harv * 3 + 4
```
This allows the core to spawn more builders when more harvesters are visible — i.e., when we can afford scale cost. The hard caps (balanced: 10, expand: 12) remain unchanged; the `econ_cap` throttle is now less restrictive.

## Swing Map Tests vs smart_eco

| Map            | Winner  | buzzing Ti mined | smart_eco Ti mined | Gap closed? |
|----------------|---------|------------------|--------------------|-------------|
| default_medium1| buzzing | 17,470           | 14,380             | +3,090 lead |
| settlement     | smart_eco | 19,660          | 27,230             | Still behind |
| landscape      | buzzing | 17,140           | 4,900              | Dominant    |

Settlement: smart_eco still dominates (27K vs 20K). Gap narrowed from prior baseline but not eliminated. Need further investigation.

## Regression Tests vs buzzing_prev

| Map            | Winner  | buzzing Ti mined | buzzing_prev Ti mined | Delta    |
|----------------|---------|------------------|-----------------------|----------|
| default_medium1| buzzing | 23,810           | 4,910                 | +18,900  |
| hourglass      | buzzing | 23,560           | 19,460                | +4,100   |
| settlement     | buzzing | 19,660           | 18,420                | +1,240   |
| corridors      | buzzing | 14,650           | 9,940                 | +4,710   |
| face           | buzzing | 23,770           | 9,880                 | +13,890  |

Result: **5/5 wins** — regression requirement of 3/5 exceeded. Economy improvement is significant across all maps.

## Verdict: PASS — deploy

All regression tests won. Ti mined increased substantially vs buzzing_prev on all maps. Economy gap vs smart_eco narrowed on most maps (exception: settlement, where smart_eco still leads; further work needed there in future versions).
