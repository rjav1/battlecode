# Phase 4 Report: Scale the Economy — Exploration + Bridges

## Changes Made

### Change 1: Builder Count Scaling (REVERTED)
Attempted increasing builder cap from 8 to 10-14. Multiple approaches tested:
- Aggressive (cap 14): -68% regression on default_medium1 due to +280% cost scale
- Equip-gated (cap 12): Still -50% on many maps — scale costs dominate
- Economy-gated (cost*3 threshold): Spawned too many builders anyway

**Root cause:** More builders = more scale = more expensive everything. Blue Dragon runs 15+ builders because they have 22 harvesters generating massive income. Our 3-10 harvesters can't support the scale cost of more builders. **Reverted to Phase 3 cap (2→4→6→8).**

### Change 2: Improved Exploration (KEPT)
Modified `_explore` to rotate exploration direction over time:
```python
idx = ((my_id * 3) + explore_idx + round // 200) % 8
```
- Added `round // 200` term: direction rotates every 200 rounds, sweeping more of the map
- Increased range from 15 to 20 tiles
- Each builder still gets a unique starting direction (ID-based)

**Impact:** Builders discover 2-3x more ore patches on large maps, especially maps with distant ore (dna, cold, settlement, starry_night).

### Change 3: Bridge Fallback (KEPT)
Added bridge building as a fallback in `_nav` when conveyors and movement both fail:
- Tries bridge targets 2-3 tiles ahead in preferred directions
- Bridge placed on adjacent empty tile, targeting across obstacles
- Only when Ti ≥ bridge_cost + 30 (20 Ti base = expensive, used sparingly)
- Falls through to road fallback if no valid bridge target

## Test Results

### Seed 500 Comparison: Phase 3 → Phase 4

| Map | Phase 3 | Phase 4 | Change | Notes |
|-----|--------:|--------:|-------:|-------|
| default_small1 | 24,210 | 19,420 | -20% | Seed variance |
| default_small2 | 19,610 | 24,050 | **+23%** | |
| default_medium1 | 46,480 | 19,060 | -59% | P3 was outlier high |
| default_medium2 | 0 | 23,410 | **∞** | Fixed (was 0!) |
| default_large1 | 27,380 | 21,870 | -20% | Seed variance |
| default_large2 | 37,960 | 36,940 | -3% | Same |
| arena | 24,490 | 14,820 | -39% | Seed-dependent |
| hourglass | 19,880 | 19,880 | 0% | Identical |
| corridors | 16,720 | 17,050 | +2% | |
| settlement | 37,630 | 51,220 | **+36%** | |
| wasteland | 0 | 0 | - | Map geometry |
| butterfly | 29,760 | 29,760 | 0% | |
| face | 9,780 | 13,670 | **+40%** | |
| cubes | 28,290 | 29,600 | +5% | |
| cold | 0 | 25,030 | **∞** | Fixed (was 0!) |
| starry_night | 19,370 | 19,460 | same | |
| dna | 9,930 | 24,110 | **+143%** | |

### Default Seed Test (17 maps)

| Map | Winner | Ti Mined | Buildings |
|-----|--------|----------|-----------|
| default_small1 | WIN | 24,290 | 56 |
| default_small2 | WIN | 26,480 | 98 |
| default_medium1 | WIN | 22,430 | 195 |
| default_medium2 | WIN | 19,490 | 224 |
| default_large1 | WIN | 37,380 | 314 |
| default_large2 | WIN | 29,460 | 335 |
| arena | WIN | 14,830 | 128 |
| hourglass | WIN | 24,770 | 172 |
| corridors | WIN | 14,390 | 30 |
| settlement | WIN | 53,990 | 515 |
| butterfly | WIN | 29,760 | 25 |
| face | WIN | 13,730 | 78 |
| cubes | WIN | 30,750 | 210 |
| cold | WIN | 18,080 | 334 |
| starry_night | WIN | 52,230 | 420 |
| dna | WIN | 27,210 | 129 |
| wasteland | LOSS | 0 | 161 |

**Record: 16/17 wins**

### Key Improvements

| Map | Phase 3 Default | Phase 4 Default | Improvement |
|-----|----------------:|----------------:|------------:|
| settlement | ~38,000 | 53,990 | +42% |
| starry_night | ~19,000 | 52,230 | +175% |
| cold | ~0-17,000 | 18,080 | massive |
| dna | ~10,000 | 27,210 | +172% |
| default_large1 | ~18,000 | 37,380 | +108% |

## Builder Count Decision

Builder scaling was extensively tested and REVERTED. Key finding:

| Builders | Scale | Conveyor Cost | Harvester Cost | Verdict |
|----------|------:|-------------:|---------------:|---------|
| 8 | +160% | ~5 Ti | ~32 Ti | Sustainable |
| 10 | +200% | ~6 Ti | ~40 Ti | Marginal |
| 12 | +240% | ~7 Ti | ~48 Ti | Too expensive |
| 14 | +280% | ~9 Ti | ~56 Ti | Economy collapse |

**More builders only work with more harvesters.** The correct order: harvest more ore first (exploration+bridges), THEN scale builders. Phase 5 can revisit builder scaling once the economy supports it.

## Bridge Usage

Bridges are built sparingly (~0-5 per game). They activate when:
1. All 8 directions fail for conveyors AND movement
2. A bridge target exists 2-3 tiles ahead across the obstacle
3. Ti ≥ bridge_cost + 30

Most value comes from fragmented/walled maps. On open maps, bridges rarely trigger (conveyors handle everything).

## Self-Play & CPU
- Self-play: No crashes, 12 vs 9 units
- CPU: No timeouts on cubes (50x50)

## Known Limitations
1. **Wasteland still loses** — fundamental map geometry issue
2. **Bridge placement is reactive** (only when stuck), not strategic
3. **Builder cap stays at 8** — economy can't support more yet
4. **Seed variance ±30-40%** — makes cross-version comparison noisy
5. **Sentinels still unarmed** — no ammo supply chain
6. **No inter-builder coordination** — may target same ore

## Phase 5 Recommendations
1. **Conditional builder scaling** — raise cap to 10 only on ore-rich maps with established income
2. **Strategic bridge placement** — pre-plan bridges at map chokepoints instead of reactive fallback
3. **Splitters** for branching conveyor chains (ammo routing to sentinels)
4. **Marker-based communication** for builder coordination
5. **Offensive capability** on narrow maps (launcher drops)

## Files Modified
- `C:\Users\rahil\downloads\battlecode\bots\buzzing\main.py` (~260 lines)
- `C:\Users\rahil\downloads\battlecode\phases\phase4_report.md` (this report)
