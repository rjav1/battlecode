# V55 Baseline (30 matches)

**Date:** 2026-04-07  
**Bot:** buzzing V55 (explore reach fix)  
**Record:** 14W-16L-0D (**47% win rate**)

**Verdict: REGRESSION. Down from V52's 70% to 47% — 23pp drop. DO NOT ship. Revert or investigate immediately.**

Progression: v42=45% → v43=50% → v46=58% → v47=58% → v49=65% → v50=40% → v51=55% → v52=70% → **v55=47%**

---

## Per-Opponent Breakdown

| Opponent | W | L | Win% | V52 Win% | Delta |
|----------|---|---|------|----------|-------|
| fast_expand | 2 | 0 | **100%** | 100% | 0% |
| adaptive | 2 | 0 | **100%** | 100% | 0% |
| ladder_eco | 4 | 1 | 80% | 66% | +14% |
| ladder_rush | 2 | 1 | 66% | 66% | 0% |
| sentinel_spam | 1 | 1 | 50% | 66% | -16% |
| barrier_wall | 1 | 1 | 50% | 100% | -50% |
| smart_defense | 1 | 1 | 50% | 33% | +17% |
| rusher | 1 | 2 | 33% | 66% | -33% |
| smart_eco | 0 | 4 | **0%** | 28% | -28% |
| turtle | 0 | 2 | **0%** | 100% | **-100%** |
| balanced | 0 | 3 | **0%** | 60% | **-60%** |

**Critical regressions:**
- turtle: 0W-2L (was 100% in V52) — 2 matches, butterfly and default_small1
- balanced: 0W-3L (was 60% in V52) — face, binary_tree, shish_kebab
- smart_eco: 0W-4L (was 28% — already bad, now worse)
- barrier_wall: 1W-1L (was 100%)
- rusher: 1W-2L (was 66%)

---

## Per-Map-Type Breakdown

| Type | W | L | Win% | V52 Win% | Delta |
|------|---|---|------|----------|-------|
| Expand | 7 | 4 | **63%** | 84% | -21% |
| Balanced | 4 | 5 | 44% | 57% | -13% |
| Tight | 3 | 7 | **30%** | 33% | -3% |

Expand maps dropped from 84% → 63%. Previously our dominant category. The explore reach fix was supposed to improve expand maps, but they got worse. This is highly suspicious — the regression is likely in expand maps specifically (ladder_rush/default_large1 LOSS, smart_eco/default_large2 LOSS, barrier_wall/default_large2 LOSS, smart_eco/pixel_forest LOSS).

Tight maps 30% vs V52's 33% — roughly unchanged (both poor). This is not where the regression is coming from.

---

## Root Cause Hypothesis

The explore reach fix changed how builders navigate. The significant regressions are:
1. **turtle: 0W-2L** — turtle is a passive/economic opponent. V52 beat it 100%. A regression here suggests our economy is broken, not our combat.
2. **Expand maps: 63% vs 84%** — the fix was supposed to help expand maps. Getting worse on expand = the explore fix broke something in expand map navigation.
3. **smart_eco: 0W-4L** — previously 28% (already weak), now completely shut out. On shish_kebab, arena, default_large2, pixel_forest. Two are expand maps.

**Most likely cause:** The explore reach fix is causing builders to walk too far from core before building harvesters, or is breaking the conveyor chain routing. If builders explore further before settling, they'll build longer chains which costs more Ti and takes more time — net negative.

**Alternative:** The fix introduced a bug in pathfinding that causes builders to get stuck or deadlock on certain map types.

---

## Specific Concerning Losses

| # | Opponent | Map | Type | Notes |
|---|----------|-----|------|-------|
| 4 | ladder_rush | default_large1 | expand | V52: would have won this |
| 6 | turtle | butterfly | balanced | V52: 100% vs turtle — regression |
| 16 | smart_eco | default_large2 | expand | Expand map loss |
| 17 | turtle | default_small1 | tight | V52: 100% vs turtle |
| 25 | barrier_wall | default_large2 | expand | V52: 100% vs barrier_wall |
| 30 | smart_eco | pixel_forest | expand | Expand map loss |

4 of 11 losses are on expand maps vs opponents we dominated before. This is the regression signal.

---

## Recommendation

**DO NOT SHIP V55.** 47% is catastrophic — back at V50 regression territory (40%).

Immediate actions:
1. **Revert to V52** as the active bot — V52 at 70% is still our best known bot
2. **Diagnose the explore reach fix** — run V55 vs V52 in regression tests (face, default_large1, pixel_forest, butterfly) to isolate exactly what broke
3. **Run regression suite** to confirm V52 is intact before any ladder activity

The explore reach fix likely needs to be scoped more carefully. The git_branches improvement (0→25350 Ti) may have been at the cost of general map performance — either builders are exploring too far, or the fix interferes with the chain-building logic on standard maps.

---

## Raw Results

| # | Opponent | Map | Type | Seed | Result |
|---|----------|-----|------|------|--------|
| 1 | rusher | arena | tight | 6592 | LOSS |
| 2 | smart_eco | shish_kebab | tight | 1082 | LOSS |
| 3 | sentinel_spam | shish_kebab | tight | 4441 | WIN |
| 4 | ladder_rush | default_large1 | expand | 7660 | LOSS |
| 5 | rusher | default_small1 | tight | 4982 | LOSS |
| 6 | turtle | butterfly | balanced | 5637 | LOSS |
| 7 | barrier_wall | mandelbrot | balanced | 5743 | WIN |
| 8 | ladder_eco | corridors | balanced | 3849 | LOSS |
| 9 | fast_expand | settlement | expand | 7442 | WIN |
| 10 | sentinel_spam | cold | balanced | 2518 | LOSS |
| 11 | ladder_eco | default_small2 | tight | 6097 | WIN |
| 12 | ladder_rush | pixel_forest | expand | 2109 | WIN |
| 13 | fast_expand | tree_of_life | expand | 7219 | WIN |
| 14 | smart_eco | arena | tight | 4094 | LOSS |
| 15 | smart_defense | dna | balanced | 1471 | LOSS |
| 16 | smart_eco | default_large2 | expand | 2861 | LOSS |
| 17 | turtle | default_small1 | tight | 9211 | LOSS |
| 18 | adaptive | shish_kebab | tight | 922 | WIN |
| 19 | smart_defense | tree_of_life | expand | 5805 | WIN |
| 20 | ladder_eco | default_medium1 | balanced | 9186 | WIN |
| 21 | rusher | landscape | expand | 660 | WIN |
| 22 | ladder_eco | wasteland | expand | 2355 | WIN |
| 23 | balanced | face | tight | 1067 | LOSS |
| 24 | adaptive | mandelbrot | balanced | 613 | WIN |
| 25 | barrier_wall | default_large2 | expand | 51 | LOSS |
| 26 | ladder_eco | default_large1 | expand | 1234 | WIN |
| 27 | balanced | binary_tree | balanced | 604 | LOSS |
| 28 | ladder_rush | gaussian | balanced | 2017 | WIN |
| 29 | balanced | shish_kebab | tight | 4064 | LOSS |
| 30 | smart_eco | pixel_forest | expand | 3883 | LOSS |
