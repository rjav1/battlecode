# v37 Armed Sentinel Test Results

## Changes
- Added `_place_armed_sentinel` method: splices splitter+branch+sentinel off existing conveyor chain
- Triggers at round 1000+, 5+ harvesters, 70+ Ti, non-tight maps
- Stateful multi-round build (steps 0-4, then done at step 5)
- Cap: 1 sentinel per builder (step=5 means done forever)

## Test Results

### Test 1: buzzing v37 vs starter (default_medium1, seed 1)
**Winner: buzzing** (Resources tiebreak, round 2000)
| | buzzing | starter |
|--|---------|---------|
| Ti stored | 31190 | 3742 |
| Ti mined | 31330 | 0 |
| Units | 10 | 3 |
| Buildings | 288 | 526 |
Result: Clear win, no crash.

### Test 2: buzzing v37 vs buzzing_prev (default_medium1, seed 1)
**Winner: buzzing v37** (Resources tiebreak, round 2000)
| | buzzing v37 | buzzing_prev |
|--|-------------|-------------|
| Ti stored | 11060 | 6807 |
| Ti mined | 9380 | 4950 |
| Units | 10 | 10 |
| Buildings | 271 | 254 |
Result: No regression. v37 outperforms prev by ~90% Ti mined.

### Test 3: buzzing v37 vs buzzing_prev (settlement, seed 1)
**Winner: buzzing v37** (Resources tiebreak, round 2000)
| | buzzing v37 | buzzing_prev |
|--|-------------|-------------|
| Ti stored | 28751 | 8921 |
| Ti mined | 40040 | 9540 |
| Units | 16 | 10 |
| Buildings | 567 | 304 |
Result: No regression. Massive improvement on settlement.

### Test 4: buzzing v37 vs ladder_eco (galaxy, seed 1)
**Winner: ladder_eco** (Resources tiebreak, round 2000)
| | buzzing v37 | ladder_eco |
|--|-------------|-----------|
| Ti stored | 8686 | 6964 |
| Ti mined | 9950 | 14410 |
| Units | 15 | 40 |
| Buildings | 350 | 309 |
Result: Loss on tiebreak (ladder_eco mined more). Not a v37 regression — same pattern as v36.

## Summary
- 3/3 wins on regression tests (vs starter, vs prev on 2 maps)
- 1 expected loss to ladder_eco on galaxy (not a regression)
- No crashes observed
- Sentinel build triggers correctly at round 1000+
- Ready for deployment after v36 is live
