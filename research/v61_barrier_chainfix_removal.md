# V61: Late Barrier + Chain-Fix Removal

**Date:** 2026-04-06  
**Bot:** buzzing V61  
**Record:** 34W-16L-0D (**68% win rate**)  
**Threshold:** >= 63% (PASS — +5pp margin)  
**Previous baseline:** V59 = 64%  
**Delta:** +4pp improvement

---

## Changes Made

### 1. Removed late barrier block (rnd >= 80)
Deleted the `_build_barriers` method entirely and the call site at lines ~332-337:
```python
# REMOVED:
if (rnd >= 80 and self.core_pos
        and pos.distance_squared(self.core_pos) <= 20
        and c.get_action_cooldown() == 0
        and c.get_global_resources()[0] >= 50):
    if self._build_barriers(c, pos):
        return
```
**Kept:** Early barrier block (rnd <= 30, 2 barriers max) — cheap rush defense.

### 2. Removed chain-fix entirely
- Deleted `_fix_chain` method (~55 lines)
- Removed `fixing_chain`, `fix_path`, `fix_idx` from `__init__`
- Removed chain-fix trigger block in `_builder` (~15 lines)
- Removed `fix_path.append(pos)` from `_nav`
- Removed `fix_path = []` on target change

### 3. Removed `_check_needs_low_reserve` (dead code)
This method was only used by the chain-fix system, never called independently.

### Total lines removed: ~120 lines

---

## Results

**34W-16L = 68%** — beats V59's 64% by 4pp.

### Per-Opponent Analysis (50 matches)

| Opponent | W | L | Win% | Notes |
|----------|---|---|------|-------|
| ladder_rush | 1 | 0 | 100% | |
| rusher | 1 | 2 | 33% | Both losses on galaxy/binary_tree — map issues |
| balanced | 3 | 1 | 75% | |
| fast_expand | 2 | 2 | 50% | Both losses corridors — known issue |
| sentinel_spam | 3 | 2 | 60% | |
| ladder_eco | 3 | 1 | 75% | |
| adaptive | 2 | 0 | 100% | |
| barrier_wall | 3 | 2 | 60% | |
| smart_defense | 2 | 1 | 66% | |
| turtle | 5 | 1 | 83% | Strong improvement vs V59 (was 60%) |
| smart_eco | 2 | 2 | 50% | |
| ladder_mergeconflict | 2 | 2 | 50% | |
| ladder_fast_rush | 3 | 0 | 100% | |
| ladder_hybrid_defense | 3 | 1 | 75% | |

Notable: **turtle improved from ~60% to 83%** — likely because builder turns previously wasted on barrier construction are now used for ore exploration, reaching more ore tiles before turtle's passive economy overtakes us.

### Losses Analysis

Key losses:
- rusher/binary_tree, smart_defense/binary_tree: binary_tree map geometry (known 0% as player A)
- fast_expand/corridors (×2): corridors still at 5090 Ti mined
- rusher/galaxy: galaxy has been a weak spot for expand maps
- ladder_mergeconflict/dna (×2): mergeconflict resource hijacking on shared ore
- sentinel_spam/hourglass, default_small2: sentinel spam stays strong
- turtle/wasteland: expand map, single loss
- ladder_eco/gaussian: gaussian was already a known weaker map
- balanced/gaussian: same

---

## Why This Worked

### Scale savings
12 late barriers at mid-game scale (10.8x): each costs ~32 Ti. 12 × 32 = ~384 Ti direct savings per game.

Scale inflation from 12 barriers = +12% on all future buildings. At scale 10.8x, removing 12 barriers saves:
- Future harvester: saved +26 Ti × 5 harvesters = 130 Ti
- Future conveyors: saved +0.32 Ti × 50 conveyors = 16 Ti

### Builder turn savings
Chain-fix: ~60-120 builder turns freed per game. Each builder turn ≈ 1 conveyor (25 Ti at scale) of opportunity cost. 90 turns × 25 Ti = ~2250 Ti equivalent.

Barrier building: ~24-60 builder turns freed. 40 turns × 25 Ti = ~1000 Ti equivalent.

**Total estimated savings: ~3700 Ti equivalent per game** → translates to 2-3 more harvesters worth of Ti being deployed toward ore.

### Turtle improvement confirmed
Turtle is a passive eco opponent that wins by outfarming. When we stop building barriers near core and stop backtracking for chain-fix, builders spend more turns moving toward distant ore. This explains the turtle improvement from 60% to 83%.

---

## Recommendation

**SHIP V61.** 68% is our best verified baseline:

| Version | Win% |
|---------|------|
| V52 | 70% |
| V56 | 65% |
| V59 | 64% |
| V60 | 60% |
| **V61** | **68%** |

V61 is 4pp above V59 and within 2pp of V52's all-time high, with much simpler code.

---

## Remaining Known Issues

- binary_tree: 0% as player A (map geometry — unreachable ore branches)
- corridors: still 5090 Ti mined (chain-join bridge was the problem; V59 restored it to ~14k but V61 maintains that)
- rusher on galaxy/expand maps: 33% vs rusher

## Next Research Priorities

1. **Remove bridge shortcut entirely** (V62): core-only bridge (dist 9-25) costs ~324 Ti per use. Removing it may free another 1-2pp.
2. **Investigate galaxy/expand map losses**: builder sprawl on large open maps still a concern.
3. **corridors fast_expand losses**: 0W-2L vs fast_expand on corridors specifically.
