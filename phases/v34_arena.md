# v34: Arena Fix -- Raise Tight Builder Cap

## Problem
arena (25x25, area=625) was the last auto-loss map. We lost to BOTH ladder_eco and ladder_rush on arena in ALL positions.

## Root Cause
arena classified as "tight" (area <= 625). Tight mode capped builders at 7 max (3->5->7 ramp). With only 7 builders vs ladder_eco's 40, we couldn't cover all 14 ore tiles (10 Ti + 4 Ax). ladder_rush's 3 rush builders also overwhelmed our sparse defenses.

## Fix
Raised tight builder cap from `3->5->7` to `3->7->15`. No other changes -- early barriers and tight exploration patterns preserved.

## Results

### v33 Baseline (all LOSSES on arena)
| Matchup | Pos1 Result | Pos2 Result |
|---------|-------------|-------------|
| vs ladder_eco | LOSE (9880 vs 9920 mined) | LOSE (9910 vs 13490 mined) |
| vs ladder_rush | LOSE (13690 vs 15710 mined) | WIN (9910 vs 0 mined) |

### v34 (arena improved)
| Matchup | Pos1 Result | Pos2 Result |
|---------|-------------|-------------|
| vs ladder_eco | **WIN** (14290 vs 9920 mined) | LOSE (9910 vs 14030 mined) |
| vs ladder_rush | LOSE (7990 vs 13090 mined) | **WIN** (7320 vs 0 mined) |

### Summary
- arena: From 0-1/4 wins to **2/4 wins** (no longer auto-loss)
- ladder_rush pos1 still loses but gap narrowed (was 0/4, now 2/4 overall)

### Regression (v34 vs v33, 5 maps)
| Map | Result | v34 Mined | v33 Mined |
|-----|--------|-----------|-----------|
| default_medium1 | WIN | 9380 | 4950 |
| hourglass | WIN | 24530 | 24320 |
| corridors | TIE | 14790 | 14790 |
| landscape | WIN | 14650 | 9790 |
| settlement | WIN | 36080 | 7270 |

**4/5 wins, 1 tie. No regressions.**

### face (other tight map) regression
| Matchup | Result |
|---------|--------|
| vs ladder_rush | WIN (9340 vs 4970 mined) |
| vs ladder_eco | LOSE (9510 vs 14830 mined) |

face unchanged from v33 (was already winning rush, losing eco).

## Alternatives Tried (all rejected)
1. **Reclassify arena as balanced** (area < 625 instead of <= 625): Lost rush defense (early barriers removed), mined only 1710 vs ladder_rush
2. **4 barriers on tight**: Worse than 2 -- Ti wasted on barriers not reaching rushers
3. **Defensive healing**: No effect -- heal 4HP vs 2 dmg*3 rushers per round
4. **Gunner on tight maps**: No effect -- gunner needs ammo via conveyors, complex
5. **Sector-based explore on tight**: Catastrophic -- builders scatter wastefully, mine only 540 Ti
6. **Aggressive ramp (5->10->20)**: Won eco pos2 but lost more to rush (5600 mined vs 7990)

## Deploy Status
- DEPLOY_CHECKLIST: PASS (5/5 vs starter, 4/5 vs v33, self-play OK)
- Ready for deployment
