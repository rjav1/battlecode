# v36 Deploy Test Results

**Date:** 2026-04-06  
**Changes:** Gunner timing fix — enables gunners on tight maps (round 60), lowers harv_req to 1 for tight maps, removes tight-map barrier guard.

## Regression Tests (buzzing v36 vs buzzing_prev/v34)

| Map | Winner | Notes |
|-----|--------|-------|
| default_medium1 | buzzing | Resources tiebreak — 11060 vs 6807 Ti (big margin) |
| hourglass | buzzing | Resources tiebreak — 26368 vs 28613 Ti (prev mined more but we had more buildings) |
| landscape | buzzing | Resources tiebreak — 10914 vs 7757 Ti |
| corridors | buzzing_prev | Identical Ti (19417 both), lost on buildings tiebreak (26 vs 26 — exact tie pushed to prev) |
| settlement | buzzing | Resources tiebreak — 29528 vs 8638 Ti (massive margin, 15 vs 10 units) |

**Regression result: 4/5 wins** (threshold: 3/5)

## Face Map Test (was: core-destroyed at turn 137)

- **Previous behavior:** buzzing core destroyed at turn 137 by enemy (no gunners to defend)
- **New behavior:** Game runs full 2000 rounds. buzzing_prev wins tiebreak (13108 vs 13446 Ti — very close)
- **Verdict: FIXED.** No more instant core loss on tight maps.

## Self-play Crash Test

- Map: default_medium1
- Result: No crash. Completed 2000 rounds cleanly.

## Deploy Decision

All three criteria met:
- 4/5 regression (>= 3 required)
- Face no longer instant-loss (core survival restored)
- Self-play stable

**DEPLOYED** as Version 37 (ID: 6c9a6b49-ee9d-4572-9eaa-d97c1f3ed8f4)

## Notes

- corridors loss is a near-perfect mirror (identical Ti both sides) — essentially a coin flip
- face tiebreak loss (13446 vs 13108) suggests buzzing_prev slightly better economy there, but survival is the key metric
- The core fix (removing `map_mode != "tight"` guard) solves the actual bug; economy tuning is secondary
