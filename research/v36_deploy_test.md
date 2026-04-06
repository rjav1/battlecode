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

## v36b: Econ_cap Tuned Down (Version 38)

**Reason:** chemistry_class regressed 27% with v37 econ_cap values (26840→19560 Ti mined by prev).  
**Fix:** Tuned-down time_floor ramps applied by team-lead before retest.

| Parameter | v37 value | v38 value |
|-----------|-----------|-----------|
| Expand time_floor | min(8+rnd//100, 20) | min(8+rnd//200, 15) |
| Balanced time_floor | 15 | min(6+rnd//150, 12) |
| Tight time_floor | 12 | min(6+rnd//200, 10) |
| Expand cap | 20 | 16 |

### Re-test Results (buzzing v38 vs buzzing_prev/v34)

| Map | Winner | Notes |
|-----|--------|-------|
| default_medium1 | buzzing | 11060 vs 6807 Ti |
| hourglass | buzzing | 26211 vs 28613 Ti (we had more buildings) |
| landscape | buzzing | 10580 vs 7757 Ti |
| corridors | buzzing_prev | Identical Ti (19417 both), coin flip tiebreak |
| settlement | buzzing | 28751 vs 8921 Ti (massive margin, 16 vs 10 units) |
| chemistry_class | buzzing | 17015 vs 10270 Ti (buzzing wins even though prev mined more) |

**Regression result: 4/5 wins** (threshold: 3/5)  
**Face:** Full 2000 rounds, no core destruction. buzzing_prev tiebreak 13108 vs 13446 (core fix intact).  
**Self-play:** No crash.

**DEPLOYED** as Version 38 (ID: aa4a2032-415c-4edf-8317-b959472d3b62)

## Notes

- corridors loss is a near-perfect mirror (identical Ti both sides) — essentially a coin flip
- face tiebreak loss (13446 vs 13108) suggests buzzing_prev slightly better economy there, but survival is the key metric
- The core fix (removing `map_mode != "tight"` guard) solves the actual bug; economy tuning is secondary
- chemistry_class: buzzing wins on stored Ti despite mining less — more efficient spending on infrastructure
