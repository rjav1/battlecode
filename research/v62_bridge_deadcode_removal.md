# V62: Bridge Shortcut + Dead Code Removal

**Date:** 2026-04-06  
**Bot:** buzzing V62  
**Record:** 28W-22L-0D (**56% win rate**)  
**Threshold:** >= 66% (FAIL — -10pp below threshold)  
**Previous baseline:** V61 = 68%  
**Delta:** -12pp regression

---

## Changes Made

### 1. Removed bridge shortcut block entirely (~55 lines)
The full chain-join bridge block (`_bridge_target` logic in `_builder`):
- Removed `self._bridge_target = None` from `__init__`
- Removed the 55-line bridge shortcut block (chain-join + core-fallback)
- Removed `self._bridge_target = ore` from harvester build

### 2. Removed dead code functions (~40 lines)
- `_perp_left(d)` / `_perp_right(d)` — 2 module-level helpers, never called post-V61
- `_walk_to(self, c, pos, target)` — 22 lines, never called post-V61
- `_get_enemy_core_pos(self, c)` — 22 lines, dead since early refactor

**Total lines removed: ~95 lines**

---

## Results

**28W-22L = 56%** — 12pp below V61's 68%. FAIL.

### Per-Opponent Analysis

| Opponent | W | L | Win% | V61 Win% | Delta |
|----------|---|---|------|----------|-------|
| balanced | 4 | 0 | **100%** | 75% | +25% |
| ladder_fast_rush | 3 | 0 | **100%** | 100% | 0% |
| smart_defense | 6 | 1 | **85%** | 66% | +19% |
| barrier_wall | 3 | 1 | 75% | 60% | +15% |
| ladder_mergeconflict | 4 | 2 | 66% | 50% | +16% |
| adaptive | 1 | 1 | 50% | 100% | -50% |
| ladder_hybrid_defense | 1 | 1 | 50% | 75% | -25% |
| ladder_rush | 1 | 1 | 50% | 100% | -50% |
| turtle | 1 | 1 | 50% | 83% | -33% |
| fast_expand | 1 | 0 | 100% | 50% | +50% |
| rusher | 2 | 4 | **33%** | 33% | 0% |
| ladder_eco | 0 | 2 | **0%** | 75% | -75% |
| sentinel_spam | 0 | 1 | **0%** | 60% | -60% |
| smart_eco | 1 | 7 | **12%** | 50% | -38% |

**Critical regressions:**
- smart_eco: 50% → 12% (1W-7L) — worst single opponent collapse
- ladder_eco: 75% → 0% (0W-2L) — complete collapse
- sentinel_spam: 60% → 0% (0W-1L, small sample)
- adaptive: 100% → 50%
- turtle: 83% → 50%
- ladder_rush: 100% → 50%

### Per-Map-Type Breakdown

| Type | W | L | Win% | V61 Win% | Delta |
|------|---|---|------|----------|-------|
| Expand | 15 | 8 | **65%** | ~70% | -5% |
| Tight | 8 | 10 | **44%** | ~65% | -21% |
| Balanced | 5 | 4 | **55%** | ~70% | -15% |

**Tight map collapse to 44%** is the smoking gun. smart_eco and rusher are both strong on tight maps; without bridges, we cannot efficiently deliver ore from tight-corridor configurations.

---

## Root Cause Analysis

### Why bridge removal hurts this time (unlike V57 context)

In V57, bridge removal hurt expand maps specifically (84% → 50% on expand). This was because bridges were used for long-range ore delivery across open terrain.

In V62 (post-V61, no late barriers, no chain-fix), bridge removal hurts tight maps most severely:
- **Tight maps**: short conveyor chains where a single bridge can cut 2-4 conveyor hops → scales matter more at high scale inflation
- **smart_eco pattern**: this opponent builds efficient economy; any delivery delay means they overtake us on tight maps
- Bridge cost (20 Ti) + scale (+10%) trades poorly only when the bridge BREAKS chains (corridors issue), but on most maps bridges save Ti by reducing conveyor count

### The corridors research vs reality gap

The `corridors_chain_regression.md` research showed that removing bridge shortcut recovered corridors Ti from 5090 to 14520 (+185%). This improvement is real. However:
1. Corridors represents only ~2 matches in 50 (4%)
2. The bridge shortcut provides value across all other map types by enabling faster ore delivery
3. Net: +4pp on corridors type, -12pp overall = not worth it

### Why the chain-join bridge provides value

Despite the chain-join being "broken" on corridors (bridges to mid-chain conveyor which can disrupt flow), on most maps:
- Mid-chain conveyor is NOT mid-path — it's an already-extended chain
- Bridging to it means skipping 1-3 unnecessary conveyor tiles
- Scale savings: 2 conveyors @ +1% each saved = meaningful at scale 12x
- Delivery speed: bridge creates shortcut that feeds chain without breaking it

The corridors regression was a special case: tight winding corridors where the "nearest allied conveyor closer to core" happened to be mid-path through a narrow lane.

---

## Verdict

**REVERT V62. Bridge shortcut provides net +12pp value. Dead code removal alone is safe but not worth the risk.**

---

## Recommendation

**Restore V61 immediately.** The bridge shortcut chain-join is net positive.

### If we still want to fix corridors:
Option A: Add distance guard `ore_core_dist > 9` (matches buzzing_prev v37) — only attempt bridge if ore is more than 3 tiles from core. This preserves the chain-join on medium/far ore while not triggering on corridors close-range ore.

Option B: Accept corridors 0% and keep bridge shortcut for its 12pp overall value.

Option C: Detect maze maps and skip bridge shortcut — already have `_check_is_maze()` which detects corridors (wall_density > 15%). Add `if not self._check_is_maze():` guard.

**Option C is simplest and most targeted**: it already works for corridors detection, costs ~2 lines, and should recover corridors to ~14k Ti while preserving bridge value on all other maps.

---

## Raw Results

| # | Opponent | Map | Seed | Result |
|---|----------|-----|------|--------|
| 1 | smart_eco | galaxy | 1528 | LOSS |
| 2 | turtle | settlement | 884 | WIN |
| 3 | smart_defense | binary_tree | 5574 | LOSS |
| 4 | smart_eco | butterfly | 7870 | LOSS |
| 5 | balanced | arena | 3788 | WIN |
| 6 | smart_eco | arena | 7158 | LOSS |
| 7 | rusher | landscape | 1965 | WIN |
| 8 | smart_eco | default_small2 | 2686 | LOSS |
| 9 | ladder_rush | default_large1 | 7560 | WIN |
| 10 | barrier_wall | default_large2 | 2579 | LOSS |
| 11 | barrier_wall | settlement | 5591 | WIN |
| 12 | smart_defense | gaussian | 7865 | WIN |
| 13 | ladder_mergeconflict | dna | 436 | WIN |
| 14 | rusher | default_small1 | 6304 | LOSS |
| 15 | rusher | binary_tree | 3071 | LOSS |
| 16 | barrier_wall | settlement | 1291 | WIN |
| 17 | rusher | butterfly | 8741 | LOSS |
| 18 | smart_defense | dna | 4560 | WIN |
| 19 | smart_defense | corridors | 1370 | WIN |
| 20 | barrier_wall | face | 1089 | WIN |
| 21 | ladder_fast_rush | butterfly | 1152 | WIN |
| 22 | sentinel_spam | corridors | 6370 | LOSS |
| 23 | smart_eco | wasteland | 7373 | WIN |
| 24 | ladder_mergeconflict | hourglass | 8102 | WIN |
| 25 | ladder_mergeconflict | arena | 9978 | LOSS |
| 26 | balanced | pixel_forest | 6372 | WIN |
| 27 | ladder_hybrid_defense | galaxy | 5143 | LOSS |
| 28 | balanced | settlement | 6383 | WIN |
| 29 | turtle | shish_kebab | 6567 | LOSS |
| 30 | ladder_fast_rush | settlement | 6244 | WIN |
| 31 | ladder_fast_rush | cold | 5022 | WIN |
| 32 | rusher | settlement | 7310 | LOSS |
| 33 | ladder_mergeconflict | binary_tree | 956 | LOSS |
| 34 | ladder_mergeconflict | pixel_forest | 8365 | WIN |
| 35 | ladder_hybrid_defense | tree_of_life | 5067 | WIN |
| 36 | fast_expand | default_medium1 | 5888 | WIN |
| 37 | balanced | landscape | 5843 | WIN |
| 38 | smart_eco | default_small1 | 3106 | LOSS |
| 39 | smart_eco | default_small2 | 5613 | LOSS |
| 40 | rusher | pixel_forest | 1390 | WIN |
| 41 | smart_defense | dna | 4415 | WIN |
| 42 | smart_eco | shish_kebab | 6683 | LOSS |
| 43 | ladder_rush | galaxy | 3906 | LOSS |
| 44 | ladder_eco | hourglass | 5248 | LOSS |
| 45 | adaptive | default_medium1 | 6465 | WIN |
| 46 | adaptive | binary_tree | 3434 | LOSS |
| 47 | ladder_mergeconflict | cold | 621 | WIN |
| 48 | smart_defense | settlement | 4874 | WIN |
| 49 | smart_defense | face | 8935 | WIN |
| 50 | ladder_eco | default_large1 | 4687 | LOSS |
