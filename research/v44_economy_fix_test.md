# v44 Economy Fix Test Results

## Changes Made
1. **Lower builder caps (lines ~98-103):**
   - tight: `3 if rnd<=30 else (4 if rnd<=200 else 6)` (was: 3/7/15)
   - expand: `3 if rnd<=30 else (4 if rnd<=200 else (6 if rnd<=500 else 8))` (was: 3/6/12/16)
   - balanced: `3 if rnd<=30 else (4 if rnd<=200 else 6)` (was: 3/5/8/10)

2. **Delayed gunner timing (line ~367):**
   - balanced: round 300 (was 120)
   - expand: round 400 (was 150)
   - tight: round 30 (unchanged)

3. **Delayed attacker to round 800 (was 500)**

## Test Results

### buzzing vs balanced, arena, seed 1
- Winner: **balanced** (Resources tiebreak, round 2000)
- buzzing: 17476 Ti (14600 mined), 6 units, 171 buildings
- balanced: 24064 Ti (19780 mined), 5 units, 122 buildings
- Gap: -5180 Ti mined. Still losing but units/buildings much better (6 vs 13 builders before, 171 vs 206 buildings)

### buzzing vs balanced, default_medium1, seed 1
- Winner: **buzzing** (Resources tiebreak, round 2000)
- buzzing: 22567 Ti (20420 mined), 9 units, 125 buildings
- balanced: 21545 Ti (18620 mined), 5 units, 212 buildings
- Gap: +1800 Ti mined. WIN vs balanced on this map.

### buzzing vs barrier_wall, dna, seed 1
- Winner: **barrier_wall** (Resources tiebreak, round 2000)
- buzzing: 13195 Ti (12940 mined), 7 units, **364 buildings**
- barrier_wall: 30716 Ti (27220 mined), 3 units, 179 buildings
- Gap: -14280 Ti mined. CRITICAL LOSS. Still building 2x as many buildings on this map.

### buzzing vs buzzing_prev, cold, seed 1
- Winner: **buzzing_prev** (Resources tiebreak, round 2000)
- buzzing: 14713 Ti (15200 mined), 7 units, 269 buildings
- buzzing_prev: 24753 Ti (28310 mined), 11 units, 496 buildings
- Note: buzzing_prev has MORE units/buildings and mines more on cold — suggests cold needs more builders

### buzzing vs buzzing_prev, settlement, seed 1
- Winner: **buzzing** (Resources tiebreak, round 2000)
- buzzing: 24560 Ti (36760 mined), 19 units, 528 buildings
- buzzing_prev: 8695 Ti (13830 mined), 20 units, 365 buildings
- WIN vs old self on settlement. +22930 Ti mined advantage.

### buzzing vs ladder_rush, face, seed 1
- Winner: **buzzing** (Resources tiebreak, round 2000)
- buzzing: 16953 Ti (13350 mined), 10 units, 86 buildings
- ladder_rush: 6218 Ti (4970 mined), 20 units, 142 buildings
- WIN vs ladder_rush.

## Summary

| Match | Result | buzzing mined | opponent mined | gap |
|-------|--------|--------------|----------------|-----|
| vs balanced, arena | LOSS | 14600 | 19780 | -5180 |
| vs balanced, default_medium1 | WIN | 20420 | 18620 | +1800 |
| vs barrier_wall, dna | LOSS | 12940 | 27220 | -14280 |
| vs buzzing_prev, cold | LOSS | 15200 | 28310 | -13110 |
| vs buzzing_prev, settlement | WIN | 36760 | 13830 | +22930 |
| vs ladder_rush, face | WIN | 13350 | 4970 | +8380 |

## Analysis

- **Good:** Builder count reduced from 13 to 6-10 on most maps. Building count down from 200+ to 86-269.
- **Concerning:** dna map: still 364 buildings with only 7 units — the conveyor chain waste is extreme on this map.
- **cold regression:** losing to buzzing_prev (old self) on cold badly. Need investigation.
- **dna regression:** barrier_wall mines 2x more with far fewer buildings. Root cause unclear — may be map-specific pathfinding building too many conveyors.
- **Net win rate:** 3-3 split. Builder cap reduction didn't uniformly help. Some maps benefit, others hurt.

## Key Issues to Investigate

1. **dna map**: 364 buildings is absurd for 7 units. Something is causing conveyor spam.
2. **cold map**: losing to own prev version — cap reduction may be too aggressive for cold (many ore tiles needing multiple builders).
3. **arena vs balanced**: still 5000 Ti behind — economy fix not sufficient on this map.
