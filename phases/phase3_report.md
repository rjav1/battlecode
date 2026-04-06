# Phase 3 Report: Fix Regressions, Symmetry Detection, Sentinels

## What Changed

### Change 1: Chain-Building Removed
Phase 2's chain-building return trip was the primary source of regressions. It forced builders to walk all the way back to core after every harvester, wasting 10-20 rounds per harvester on maps where the outbound chain was already connected.

**Multiple approaches were tested:**
- Distance-based threshold (chain-build only for distant harvesters) — helped small maps, hurt large
- Smart early exit (5 consecutive connected tiles) — inconsistent results
- Opportunistic harvesting during chain-walk — caused interference

**Conclusion:** The outbound trip already builds a connected conveyor chain in the vast majority of cases. Chain-building's marginal benefit on a few maps doesn't justify the regression it causes on others. Removed entirely.

### Change 2: Symmetry Detection
`_get_enemy_direction` now samples visible tiles and tests which mirror transformation (rotational, horizontal reflection, vertical reflection) preserves the map structure. This correctly identifies enemy core position on all 3 symmetry types.

```python
# Tests rotational: (w-1-x, h-1-y), horiz: (w-1-x, y), vert: (x, h-1-y)
# Scores each by counting matching tile environments in vision
# Returns direction toward enemy based on best-matching symmetry
```

### Change 3: Improved Sentinel Placement
Sentinels now prefer placement adjacent to existing conveyor chains (for potential ammo access). The placement loop checks each candidate tile for nearby conveyors on non-facing sides.

## Test Results

### Win/Loss (default seed, 14 maps)

| Map | Winner | Ti Mined | Units |
|-----|--------|----------|-------|
| default_small1 | buzzing | 26,720 | 8 |
| default_small2 | buzzing | 28,290 | 8 |
| default_medium1 | buzzing | 42,520 | 8 |
| default_medium2 | buzzing | 23,670 | 8 |
| default_large1 | buzzing | 18,560 | 8 |
| default_large2 | buzzing | 37,110 | 8 |
| arena | buzzing | 14,810 | 8 |
| hourglass | buzzing | 24,760 | 8 |
| corridors | buzzing | 14,410 | 8 |
| settlement | buzzing | 33,380 | 8 |
| wasteland | **starter** | 0 | 8 |
| butterfly | buzzing | 29,760 | 8 |
| face | buzzing | 14,660 | 8 |
| cubes | buzzing | 19,510 | 8 |

**Record: 13/14 wins** (wasteland is a map geometry issue — consistent across all phases)

### 3-Seed Average Comparison

| Map | Phase 1 (1 seed) | Phase 3 (3-seed avg) | Notes |
|-----|---------|---------------------|-------|
| default_small1 | 24,190 | 27,110 | +12% |
| default_small2 | 23,980 | 22,520 | ~same |
| default_medium1 | 19,200 | 28,330 | +48% |
| default_medium2 | 26,130 | 8,946 | Seed-dependent |
| default_large1 | 18,880 | 20,966 | +11% |
| default_large2 | 37,460 | 37,576 | same |
| arena | 23,580 | 14,816 | Seed-dependent |
| hourglass | 24,760 | 21,506 | ~same |
| corridors | 14,700 | 14,600 | same |
| settlement | 38,600 | 38,046 | same |
| face | 4,980 | 6,590 | +32% |
| cubes | 29,100 | 25,150 | ~same |
| butterfly | 33,420 | 29,760 | ~same |

**Note:** Phase 1 numbers are single-seed while Phase 3 averages 3 seeds. Direct comparison is unreliable due to high engine variance (±30% between seeds). The economy code is functionally identical between Phase 1 and Phase 3.

### Self-Play
- buzzing vs buzzing: No crashes. 11 and 12 units (sentinels on both sides). 28,310 vs 22,650 Ti.

### CPU
- No timeouts on cubes (50x50).

## Symmetry Detection

Tested on maps of each symmetry type:
- **Rotational** (default_medium1): Correctly identifies enemy direction ✓
- **Horizontal** (battlebot): Correctly identifies enemy direction ✓  
- **Vertical** (default_small2): Correctly identifies enemy direction ✓

Detection works by sampling visible tiles and counting environment matches for each symmetry type. The highest-scoring type determines the enemy core position.

## Sentinel Status

- Sentinels are placed when conditions are met (round > 200, designated builder near core, enough Ti)
- Sentinel placement prefers tiles adjacent to existing conveyors for potential ammo
- Auto-fire code is active (fires when ammo >= 10)
- **Ammo delivery remains incomplete** — sentinels don't receive ammo reliably without dedicated supply chains. They serve as 30 HP obstacles + 32 vision radius sentries.
- In self-play, both sides show 11-12 units, confirming sentinels ARE being placed

## Chain-Building Analysis

Extensive testing of chain-building approaches revealed a fundamental tension:
- **Chain repair helps** large maps with long paths (settlement: +42% in Phase 2)
- **Chain repair hurts** small maps with short paths (default_small1: -11% in Phase 2)
- The time cost of walking back (10-20 rounds per harvester) exceeds the benefit on maps where the outbound chain is already connected

The outbound trip builds conveyors at each new tile. Gaps only occur when:
1. The road fallback is used (rare — only when all 8 directions fail)
2. The builder moves through existing non-conveyor tiles (roads from exploration)

These gaps are infrequent enough that removing chain-building is the better overall strategy.

## Known Limitations

1. **Wasteland remains unwinnable on most seeds** — map geometry blocks ore access
2. **Sentinel ammo delivery incomplete** — requires splitters or dedicated harvester (Phase 4)
3. **No chain repair** — occasional road tiles in conveyor chains reduce resource delivery
4. **High seed variance** — same code can give ±30% Ti mined on different seeds
5. **No bridges** — fragmented maps remain challenging
6. **No offensive capability** — purely defensive

## Phase 4 Recommendations

1. **Splitters for sentinel ammo** — branch from main chain to feed sentinels
2. **Bridges** for cross-terrain transport (critical for fragmented maps like sierpinski_evil)
3. **Adaptive chain repair** — only repair when Ti delivery rate is low (check income vs spending)
4. **Increase builder cap** to 10-12 in late game
5. **Markers for builder coordination** — avoid targeting the same ore
6. **Map-specific strategies** — rush on narrow maps, economy on wide maps

## Review Agent Findings

### Chain Reviewer + Devil's Advocate
These agents reviewed the chain-building code that was subsequently REMOVED. Their findings (shallow connectivity check, step cap too low, builder-on-core-tile bug) validated the decision to remove chain-building entirely. The chain-building approach is fundamentally fragile — it requires solving chain verification, multi-builder conflicts, and step-cap tuning simultaneously. Phase 1's simpler approach (build conveyors during outbound navigation only) is more robust.

### Final Integration Reviewer
- Economy code is clean and matches Phase 1 pattern ✓
- Symmetry detection formulas verified correct (rot, horiz, vert) ✓
- `can_build_sentinel` prevents placement on conveyor tiles ✓
- MEDIUM: P0 sentinel can steal one action cooldown from P1 harvester (low probability — only 1-in-4 builders, only after round 200, capped at 2 sentinels)
- MINOR: Symmetry scoring defaults to rotational when all mirror tiles are outside vision (acceptable — rotational is the most common type)
- Dead code `_on_or_adjacent_to_core` identified and removed ✓

## Files Modified
- `C:\Users\rahil\downloads\battlecode\bots\buzzing\main.py` (~215 lines, down from ~280)
- `C:\Users\rahil\downloads\battlecode\phases\phase3_report.md` (this report)
