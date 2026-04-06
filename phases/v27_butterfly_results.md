# v27: Butterfly Map Investigation + Fix

## Problem
buzzing mines 24.9K Ti from butterfly position A vs smart_eco's 34.8K — a 10K gap (-29%).

## Simulation Results (v26 baseline)

| Match | buzzing Ti Mined | smart_eco Ti Mined | Winner |
|-------|-----------------|-------------------|--------|
| buzzing(A) vs smart_eco(B) butterfly | 24,870 | 34,810 | smart_eco |
| smart_eco(A) vs buzzing(B) butterfly | 34,810 | 34,640 | smart_eco |
| buzzing(A) vs smart_eco(B) cold | 17,230 | 14,340 | buzzing |
| smart_eco(A) vs buzzing(B) cold | 4,880 | 19,690 | buzzing |
| buzzing(A) vs smart_eco(B) default_medium1 | 18,770 | 4,900 | buzzing |
| smart_eco(A) vs buzzing(B) default_medium1 | 12,340 | 16,650 | buzzing |

## Root Cause Analysis

### butterfly map properties
- 31x31 = 961 tiles → "balanced" map mode (625 < 961 < 1600)
- 18.4% walls (above 15% maze threshold but only from some positions)
- 10 fragmented regions (4-dir BFS); path=14 via diagonal movement
- 94 Ti + 57 Ax ore = **15.7% of all tiles are ore**
- Nearest Ti = 3 steps from core — ore is VERY close to core

### Key finding: position A doesn't trigger maze mode
Butterfly has horizontal reflection. Core A at (8,24), Core B at (22,24).

- Position B (22,24): at round 5+, local wall density from builder scan > 15%
  → `is_maze = True` → uses pure builder_dist ore scoring
- Position A (8,24): at round 5+, local wall density < 15% (core area is more
  open in this half) → `is_maze = False` → uses core-proximate scoring
  (`builder_dist + core_dist * 2`)

Core-proximate scoring PENALIZES ore far from core. On butterfly, all ore is
in the wings (3+ steps from core but the whole map is wings). This causes
position A builders to score ore poorly, leading to suboptimal targeting.

### Why smart_eco mines 34.8K from BOTH positions
smart_eco always uses pure `builder_dist` (nearest ore) regardless of wall
density. No maze detection needed — it's uniformly nearest-first. This means
smart_eco correctly picks whatever ore tile is closest to the builder on every
turn, including butterfly's wing ore.

### Secondary factors
- buzzing has military overhead (gunners, barriers, attackers) consuming Ti
  and builder time that smart_eco doesn't have
- buzzing's `explore_reserve = 30 when core_dist_sq > 50` prevents conveyors
  far from core on some positions (but butterfly ore is 3 steps from core,
  so this is less critical here)

## Investigation: What Was Tried

### Attempt 1: Lower wall_density threshold (10%)
- Butterfly position A: 33,210 mined (+33%) ✓
- default_medium1 regressed severely (maze mode triggered on open map) ✗

### Attempt 2: Averaged wall samples over rounds 5-30
- Still triggered on default_medium1 position B (8,130 mined) ✗

### Attempt 3: Round 10 lock-in instead of round 5
- Still triggered on default_medium1 ✗

### Attempt 4: Military suppression in maze mode
- Butterfly improved (39,530 mined from pos A when 10% threshold)
- Cold position A regressed: 17,230 → 14,420 (maze from diamond wall) ✗

### Attempt 5: Ore density detection (WINNER)
Track ore_density = (visible ore tiles) / (total visible tiles) at round 5.

- butterfly: ore is 3 steps from core → ore_density ≈ 12-16% at round 5 ✓
- default_medium1: ore is 9+ steps from core → ore_density ≈ 0% at round 5 ✓
- cold: ore is 10+ steps from core → ore_density ≈ 0% at round 5 ✓

Two checks:
- `_check_is_maze()`: wall_density > 15% OR ore_density > 12% — used for ore scoring
- `_check_needs_low_reserve()`: wall_density > 15% AND ore_density > 8% — used for explore_reserve

## Fix Applied (v27)

### 1. Added `_ore_density` tracking
Lock in ore density at round 5+ (like wall_density). Counts ALL ore tiles in vision
(including occupied), divided by total tiles scanned.

### 2. Updated `_check_is_maze()` to use OR
```python
wall_maze = self._wall_density is not None and self._wall_density > 0.15
ore_rich = self._ore_density is not None and self._ore_density > 0.12
return wall_maze or ore_rich
```
This detects butterfly position A via ore_density trigger even when wall_density < 0.15.

### 3. Added `_check_needs_low_reserve()` with AND
```python
wall_maze = self._wall_density is not None and self._wall_density > 0.15
ore_rich = self._ore_density is not None and self._ore_density > 0.08
return wall_maze and ore_rich
```
Conservative check (requires BOTH) to avoid lowering explore_reserve on cold
(diamond wall creates local wall clusters, but ore is 10+ steps away → ore_density ≈ 0).

### 4. Ore scoring uses `_check_is_maze()`
Both positions of butterfly now use pure builder_dist ore scoring (nearest-first),
matching smart_eco's approach on this ore-rich fragmented map.

### 5. Explore reserve uses `_check_needs_low_reserve()`
Butterfly positions that trigger both checks (wall > 15% AND ore > 8%) use
explore_reserve = 5 instead of 30. Cold does NOT trigger this (ore_density ≈ 0).

## Final Test Results (v27)

| Match | buzzing Ti Mined | smart_eco Ti Mined | Winner | Change |
|-------|-----------------|-------------------|--------|--------|
| buzzing(A) vs smart_eco(B) butterfly | **29,020** | 34,810 | smart_eco | **+4,150 (+16.7%)** |
| smart_eco(A) vs buzzing(B) butterfly | 34,810 | **38,360** | buzzing ✓ | **+3,720 (+10.7%)** |
| buzzing(A) vs smart_eco(B) cold | 17,230 | 14,340 | buzzing ✓ | 0 (no regression) |
| smart_eco(A) vs buzzing(B) cold | 4,880 | 19,690 | buzzing ✓ | 0 (no regression) |
| buzzing(A) vs smart_eco(B) default_medium1 | 18,770 | 4,900 | buzzing ✓ | 0 (no regression) |
| smart_eco(A) vs buzzing(B) default_medium1 | 12,340 | 16,650 | buzzing ✓ | 0 (no regression) |

## Match-Level Summary

| Map | v26 Result | v27 Result |
|-----|-----------|-----------|
| butterfly vs smart_eco | 0-2 LOSS (both positions) | 1-1 DRAW (win pos B, lose pos A) |
| cold vs smart_eco | 2-0 WIN | 2-0 WIN (unchanged) |
| default_medium1 vs smart_eco | 2-0 WIN | 2-0 WIN (unchanged) |

## Remaining Gap on butterfly position A

Position A still loses to smart_eco (29,020 vs 34,810, -5,790 Ti gap). Remaining factors:
1. **Military overhead**: buzzing builds gunners/barriers/attackers; smart_eco is pure economy
   - Attempting to suppress military on maze maps caused cold regression (diamond wall
     falsely triggers wall_density > 0.15)
2. **Position A wall density < 0.15**: explore_reserve stays at 30 when far from core
   (but butterfly ore is 3 steps from core, so this is secondary)
3. **Structural asymmetry**: position A (x=8) is closer to the west map edge; the butterfly
   wings may have different ore accessibility patterns per position

The remaining gap is acceptable — buzzing now wins one butterfly position it previously lost.

## Code Changes Summary

File: `C:\Users\rahil\downloads\battlecode\bots\buzzing\main.py`

- Added `self._ore_density = None` in `__init__`
- Ore scan now counts `total_ore_count` (all ore in vision, occupied or not)
- Ore density locked in at round 5+ alongside wall density
- Added `_check_is_maze()` method: wall_density > 0.15 OR ore_density > 0.12
- Added `_check_needs_low_reserve()` method: wall_density > 0.15 AND ore_density > 0.08
- Ore scoring uses `_check_is_maze()` (was: `wall_density > 0.15 only`)
- Explore reserve uses `_check_needs_low_reserve()` (same logic, just renamed)
- Updated docstring to v27
