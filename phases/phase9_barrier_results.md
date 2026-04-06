# Phase 9: Barrier Walls - Test Results
## Date: April 4, 2026

### Implementation Summary

Added `_build_barriers` method to v7 bot. Builders passing near core (dist_sq <= 20) after round 80 with Ti >= 50 place barriers on the enemy-facing side, 2-3 tiles out. Gaps are left at odd perpendicular offsets for builder passage. Capped at 6 barriers per builder's visible area.

### Changes
- `bots/buzzing/main.py`: Added `_build_barriers()` method + call in `_builder` between sentinel infra and harvester building

### Test Results

| Map | Opponent | Result | Ti Mined | Ti Final | Buildings |
|-----|----------|--------|----------|----------|-----------|
| default_medium1 | starter | WIN (tiebreak) | 14,670 | 5,006 | 192 |
| corridors | starter | WIN (tiebreak) | 9,930 | 15,038 | 23 |
| face | starter | WIN (tiebreak) | 4,970 | 7,118 | 119 |
| settlement | starter | WIN (tiebreak) | 19,660 | 20,928 | 363 |
| default_medium1 | self-play | WIN (tiebreak) | 21,370 vs 16,790 | 25,690 vs 20,981 | 83 vs 120 |

### Verification Checklist
- [x] No crashes on any map
- [x] Economy not harmed (Ti mined healthy on all maps)
- [x] Barriers visible in self-play (both sides building barriers)
- [x] Wins against starter on all 4 maps
- [x] Self-play completes without errors

### Design Notes
- Barriers placed at perpendicular offsets 0, -2, +2 from enemy-facing center line
- Offsets -1 and +1 skipped to leave gaps for builder passage
- Tried dist 3 first, then dist 2 from core center
- Ti reserve of 40 above barrier cost prevents economy starvation
- Round 80 trigger aligns with barrier research recommendation (80-120 range)
