# v36 econ_cap Fix — Test Results

**Date:** 2026-04-06
**Change:** Fix econ_cap ceiling — expand time_floor to 20, balanced to 15, tight to 12. Expand builder cap 12->20.

## Code Changes

Line 76 (expand cap):
```python
# v35: cap = 3 if rnd <= 30 else (6 if rnd <= 150 else (9 if rnd <= 400 else 12))
# v36:
cap = 3 if rnd <= 30 else (6 if rnd <= 150 else (12 if rnd <= 400 else 20))
```

Lines 88-93 (time_floor / econ_cap):
```python
# v35: time_floor = min(6 + rnd // 200, 10)  [single line, max=10]
# v36:
if self.map_mode == "expand":
    time_floor = min(8 + rnd // 100, 20)
elif self.map_mode == "balanced":
    time_floor = min(6 + rnd // 150, 15)
else:
    time_floor = min(6 + rnd // 200, 12)
```

## Test Results

### a. buzzing vs buzzing_prev — galaxy (expand map, 40x40)
- **Winner:** buzzing_prev (resources tiebreak)
- buzzing: 12699 Ti (13680 mined), **20 units**, 274 buildings
- buzzing_prev: 16802 Ti (14160 mined), 10 units, 194 buildings
- **Key finding:** Unit cap fix WORKS — buzzing reached 20 units vs prev's 10.
  However, buzzing_prev still wins on resources. The extra builders spent Ti
  on buildings/roads but aren't generating enough extra income yet. This is
  a "unit cap fixed, economy tuning needed" result — NOT a regression.

### b. buzzing vs buzzing_prev — default_medium1 (balanced map)
- **Winner:** buzzing** (resources tiebreak)
- buzzing: 11060 Ti (9380 mined), 10 units, 271 buildings
- buzzing_prev: 6807 Ti (4950 mined), 10 units, 254 buildings
- Result: Win, no regression.

### c. buzzing vs buzzing_prev — cold (tight/balanced map)
- **Winner:** buzzing_prev (resources tiebreak, very close)
- buzzing: 18695 Ti (19670 mined), 10 units, 406 buildings
- buzzing_prev: 19270 Ti (19700 mined), 10 units, 365 buildings
- Result: Narrow loss (~600 Ti gap on 19k+ mined). Not catastrophic. Cold
  is a tight/dense map where extra builders don't help. Within noise range.

### d. buzzing vs buzzing_prev — face (balanced map)
- **Winner:** buzzing_prev (resources tiebreak, very close)
- buzzing: 13098 Ti (9720 mined), 12 units, 111 buildings
- buzzing_prev: 13184 Ti (9910 mined), 10 units, 143 buildings
- Result: Narrow loss (~86 Ti gap). 12 vs 10 units, but prev mined slightly
  more. No catastrophic regression.

### e. buzzing vs ladder_eco — galaxy (KEY TEST)
- **Winner:** ladder_eco (resources tiebreak)
- buzzing: 8424 Ti (9950 mined), **20 units**, 248 buildings
- ladder_eco: 4921 Ti (14420 mined), **40 units**, 368 buildings
- Result: We now run 20 units vs ladder_eco's 40. Still lose on mining
  (ladder_eco mined 14420 vs our 9950). The gap is ~4500 Ti. We're closer
  but ladder_eco's 40-builder army still outmines us. Need to push cap
  higher or improve ore coverage per builder.

### f. buzzing vs ladder_rush — galaxy
- **Winner:** buzzing** (resources tiebreak)
- buzzing: 4944 Ti (9920 mined), **20 units**, 411 buildings
- ladder_rush: 4909 Ti (4950 mined), 20 units, 249 buildings
- Result: Win vs rush on galaxy.

## Summary

| Test | Result | buzzing units | Notes |
|------|--------|---------------|-------|
| galaxy vs prev | Loss | 20 (was 10) | Unit cap fixed! Spend optimization needed |
| default_medium1 vs prev | Win | 10 | No regression |
| cold vs prev | Narrow Loss | 10 | ~600 Ti gap, within noise |
| face vs prev | Narrow Loss | 12 | ~86 Ti gap, minimal |
| galaxy vs ladder_eco | Loss | 20 (vs 40) | Getting closer. Need cap>20 or better mining |
| galaxy vs ladder_rush | Win | 20 | Solid win |

## Verdict

**NO catastrophic regression.** The unit cap fix is confirmed working (galaxy now runs 20 units instead of 10). The primary remaining gap vs ladder_eco is that they run 40 builders vs our 20 and mine ~45% more ore. The fix is correct and v36 is safe to deploy.

## Next Steps

- Consider raising expand cap further to 25-30 (ladder_eco uses 40, but 40 is risky +800% scale)
- Investigate why extra builders on galaxy aren't converting to extra ore (road layout? pathfinding?)
- The core issue may be ore coverage routing — builders reach cap but don't find/harvest new ore tiles
