# Butterfly Map Regression Investigation

## Summary

**No regression exists.** The apparent regression was a measurement artifact caused by butterfly map asymmetry.

## Test Results

### Initial observation (false regression)
```
cambc run buzzing buzzing_prev butterfly
Winner: buzzing_prev  (Resources tiebreak, round 2000)
buzzing: 24840 Ti mined | buzzing_prev: 44400 Ti mined
```

### Key finding: v37 vs v37 gives identical split
```
cambc run buzzing_prev buzzing_prev butterfly
Winner: buzzing_prev (player 2)
Player 1: 24840 Ti mined | Player 2: 44400 Ti mined
```

The 24840 vs 44400 split appears regardless of which bot version plays. It is a property of the butterfly map itself — player 1 (left/first team) has significantly worse ore access than player 2 on this map.

### Side-swap confirms buzzing is fine
```
cambc run buzzing_prev buzzing butterfly
Winner: buzzing  (Resources tiebreak, round 2000)
buzzing_prev: 24840 Ti mined | buzzing (v39): 51530 Ti mined
```

When buzzing (v39) plays as player 2, it mines MORE than buzzing_prev (v37) ever did as player 2 (~51530 vs ~44400).

### default_medium1 regression check
```
cambc run buzzing buzzing_prev default_medium1
Winner: buzzing
buzzing: 9610 Ti mined | buzzing_prev: 4950 Ti mined
```
No regression on balanced maps.

## Root Cause

Butterfly map has asymmetric ore placement that strongly favors player 2. Any test of `A vs B` where `A` always plays player 1 will show A performing worse, regardless of bot quality.

## What Changed in v38/v39

The only code changes from v37 to v39:
1. **Bridge distance guard**: `<= 25` changed to `<= 36` for ore-to-core bridge shortcut
2. **Chain-join bridge**: Added fallback that bridges ore tile to nearest allied conveyor tile
3. **Ax tiebreaker**: Late-game (round 1800+) one builder builds Ax harvester + foundry

None of these affect butterfly performance since the bridge code only fires immediately after building a harvester, and on butterfly player 1 side the ore layout doesn't trigger these code paths differently.

## Investigation of Bridge Changes

Tested with bridge guard reverted to `<= 25` — identical results (24840 mined), confirming the bridge code path is not exercised on butterfly player 1 side.

## Recommendation

No fix needed. The butterfly "regression" was a false alarm due to:
- Always testing `buzzing` as player 1 on an asymmetric map
- Not swapping sides to compare fairly

For future map-specific testing, always run both `A vs B` and `B vs A` and average the results.
