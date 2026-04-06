# v42 Bridge-First Harvester Delivery Test Results

## Changes Made
1. **Bridge-first delivery** (priority: chain-join > core tile)
   - Removed upper distance cap (was: `ore.distance_squared(core) <= 36`)
   - Chain-join now includes `EntityType.BRIDGE` in search targets
   - Removed distance cap on chain-join (was: `best_chain_dist <= 36`)
   - Chain-join tried BEFORE core bridge (was: after)
   - Kept minimum distance guard (`> 9`) to avoid wasting bridges on close harvesters
2. **Ax tiebreaker stuck detection** - give up after 5 rounds stuck in walk-to step

## Test Results (all seed 1)

| # | Map | Opponent | Result | Buzzing Ti Mined | Opponent Ti Mined | Notes |
|---|-----|----------|--------|------------------|-------------------|-------|
| 1 | arena | balanced | LOSS | 9,890 | 24,160 | Still losing economy race |
| 2 | dna | barrier_wall | LOSS | 16,060 | 25,530 | Same as v39 baseline |
| 3 | settlement | buzzing_prev (v37) | LOSS | 0 | 13,720 | PRE-EXISTING v39 regression |
| 4 | cold | buzzing_prev (v37) | LOSS | 0 | 28,870 | PRE-EXISTING v39 regression |
| 5 | default_medium1 | ladder_bridge | WIN | 4,950 | 4,950 | Won on tiebreakers |

## Key Findings

### Pre-existing v39 Regression (NOT caused by bridge changes)
- **cold** and **settlement** show 0 Ti mined even when bridge changes are fully reverted
- The v37->v39 changes (Ax tiebreaker, other v38-v39 changes) broke resource delivery on these maps
- buzzing (v39 base) builds 275-381 buildings but mines 0 Ti on cold/settlement
- This needs separate investigation

### Bridge-first Impact
- On **arena** and **dna**: results match v39 baseline (no improvement, no regression)
- On **default_medium1**: marginal win vs ladder_bridge
- The bridge-first change is essentially neutral because:
  - Close harvesters (dist <= 9) are excluded by the distance guard
  - Far harvesters often can't find chain tiles within bridge range (dist^2 <= 9)
  - The existing conveyor trail already provides connectivity

### Remaining Economy Gap
- **balanced** bot mines 24,160 Ti vs our 9,890 on arena (2.4x gap)
- **barrier_wall** mines 25,530 Ti vs our 16,060 on dna (1.6x gap)
- The fundamental problem remains: too many conveyors, not enough resource throughput

## Recommendations
1. **URGENT**: Investigate v39 regression on cold/settlement (0 Ti mined)
2. Bridge-first is marginal benefit -- the real economy gap is elsewhere
3. Need to reduce total building count (230-387 vs opponent 100-200)
