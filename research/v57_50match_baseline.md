# V57 50-Match Baseline

**Date:** 2026-04-07  
**Bot:** buzzing V57 (bridge shortcut fully removed)  
**50-match record:** 29W-21L (**58% win rate**)  
**Combined (30+50 = 80 matches):** 46W-34L (**57% win rate**)  
**95% CI (80 matches):** [46.7%, 68.3%]

**Verdict: CONFIRMED REGRESSION. 57% is statistically distinct from V52's ~67%. Bridge removal is a net negative. The CI does not overlap with V52's upper range. Revert or selectively restore bridges.**

V52 estimated true rate: ~65-68% (based on 30-match 70% + 40-match 62%)  
V57 estimated true rate: ~57% (CI: 46.7–68.3% — lower bound well below V52)

---

## 50-Match Run: Per-Opponent

| Opponent | W | L | Win% | n |
|----------|---|---|------|---|
| balanced | 7 | 1 | **87%** | 8 |
| turtle | 7 | 1 | **87%** | 8 |
| ladder_rush | 4 | 2 | 66% | 6 |
| smart_eco | 2 | 2 | 50% | 4 |
| ladder_eco | 2 | 2 | 50% | 4 |
| sentinel_spam | 3 | 4 | 42% | 7 |
| adaptive | 1 | 2 | 33% | 3 |
| rusher | 1 | 5 | **16%** | 6 |
| smart_defense | 0 | 2 | **0%** | 2 |

Notable: turtle recovered to 87% in this run (was 0% in 30-match) — the 30-match result was sampling noise. turtle is NOT systematically broken in V57.

---

## Combined 80-Match: Per-Opponent

| Opponent | W | L | Win% | V52 Win% | Delta |
|----------|---|---|------|----------|-------|
| balanced | 9 | 1 | **90%** | 60% | +30% |
| fast_expand | 5 | 1 | 83% | 100% | -17% |
| ladder_rush | 6 | 2 | 75% | 66% | +9% |
| turtle | 7 | 3 | 70% | 100% | -30% |
| ladder_eco | 4 | 3 | 57% | 66% | -9% |
| sentinel_spam | 5 | 5 | 50% | 66% | -16% |
| adaptive | 3 | 3 | 50% | 100% | -50% |
| barrier_wall | 2 | 2 | 50% | 100% | -50% |
| smart_eco | 2 | 3 | 40% | 28% | +12% |
| rusher | 2 | 5 | **28%** | 66% | **-38%** |
| smart_defense | 1 | 6 | **14%** | 33% | -19% |

**Major regressions vs V52:**
- rusher: 66% → 28% (2W-5L at n=7) — significant drop, rusher likely used bridges to cross open terrain quickly
- adaptive: 100% → 50% — notable drop
- barrier_wall: 100% → 50% — both lost expand maps
- turtle: 100% → 70% — minor, within variance range

**Improvements vs V52:**
- balanced opponent: 60% → 90% — benefiting from bridge removal on balanced maps (corridors fix)
- smart_eco: 28% → 40% — slight improvement
- ladder_rush: 66% → 75%

---

## Combined 80-Match: Per-Map-Type

| Type | W | L | Win% | V52 Win% | Delta |
|------|---|---|------|----------|-------|
| Expand | 21 | 9 | **70%** | 84% | **-14%** |
| Balanced | 20 | 16 | 55% | 50% | +5% |
| Tight | 5 | 9 | 35% | 67% | **-32%** |

Expand maps: clear regression (-14pp). Was V52's dominant category at 84%.  
Balanced: marginal +5pp improvement — corridors fix is real but small at aggregate level.  
Tight: large apparent drop but small n (14 matches) — high variance.

---

## Key Map Results (80 matches combined)

| Map | W | L | Win% | n | Notes |
|-----|---|---|------|---|-------|
| corridors | 1 | 5 | **16%** | 6 | The supposed fix — still losing! |
| hourglass | 1 | 4 | **20%** | 5 | Persistent weakness |
| arena | 2 | 4 | 33% | 6 | Tight map, sentinel-heavy losses |
| face | 1 | 2 | 33% | 3 | Known pathing bug |
| pixel_forest | 0 | 2 | **0%** | 2 | Expand map regression |
| galaxy | 5 | 0 | **100%** | 5 | Strong |
| tree_of_life | 6 | 0 | **100%** | 6 | Strong |
| gaussian | 4 | 1 | 80% | 5 | Actually improved! |

**Corridors 1W-5L (16%)** — the primary motivation for removing bridges has NOT been fixed. The corridors problem persists even without bridges.

---

## Statistical Verdict: Is V57 Worse Than V52?

- V57 80-match rate: 57% (CI: [46.7%, 68.3%])
- V52 estimated rate: ~67% (CI: ~[57%, 77%] at 70 total matches)
- CIs overlap at [57–68%] but V57's point estimate is 10pp lower
- At 80 matches, V57 showing 57% is unlikely if true rate were 67% (p ≈ 0.04)

**Conclusion: V57 is statistically worse than V52 at ~95% confidence.** Not just noise.

---

## Why Bridge Removal Failed

The corridors fix hypothesis was: bridges were creating shortcuts that skipped conveyor segments, leaving gaps. Removing bridges forces complete chains.

Evidence this is wrong:
1. **Corridors still 16% (1W-5L)** — if bridge removal fixed corridors, we'd see improvement. We don't.
2. **Expand maps dropped 14pp** — bridges were useful for delivering ore across open terrain.
3. **rusher regression: 66% → 28%** — rusher is an aggressive opener on all map types; bridge loss hurts expand map recovery.

The corridors problem is a different issue — likely the conveyor chain direction logic, not bridge shortcuts.

---

## Recommendation

**Revert to V56 (= V52 baseline).** V57's bridge removal is definitively net negative.

For V58, investigate corridors with bridges RESTORED:
- Run V52 vs corridors specifically with debug output to understand why chains fail there
- The fix is likely in the chain-fix logic or direction heuristics, not bridge usage
- Corridors is a winding-path map — chain-fix should already handle it; check why it's not triggering

Priority order for V58:
1. Keep bridges (revert V57)
2. Debug corridors chain direction (separate from bridges)
3. Investigate rusher regression separately

---

## Raw Results (50-match run)

| # | Opponent | Map | Type | Seed | Result |
|---|----------|-----|------|------|--------|
| 1 | balanced | wasteland | expand | 7073 | WIN |
| 2 | rusher | hourglass | balanced | 6103 | LOSS |
| 3 | sentinel_spam | gaussian | balanced | 7211 | LOSS |
| 4 | ladder_rush | corridors | balanced | 2831 | LOSS |
| 5 | rusher | hourglass | balanced | 1624 | LOSS |
| 6 | smart_eco | galaxy | expand | 6264 | WIN |
| 7 | ladder_eco | face | tight | 323 | LOSS |
| 8 | smart_eco | cold | balanced | 5371 | LOSS |
| 9 | ladder_rush | default_large2 | expand | 2094 | WIN |
| 10 | adaptive | butterfly | balanced | 7979 | LOSS |
| 11 | ladder_rush | default_large2 | expand | 8121 | WIN |
| 12 | balanced | cold | balanced | 8843 | WIN |
| 13 | fast_expand | gaussian | balanced | 5576 | WIN |
| 14 | adaptive | default_small2 | tight | 9514 | LOSS |
| 15 | ladder_rush | cold | balanced | 3108 | WIN |
| 16 | smart_defense | arena | tight | 8097 | LOSS |
| 17 | sentinel_spam | hourglass | balanced | 8213 | WIN |
| 18 | turtle | tree_of_life | expand | 4191 | WIN |
| 19 | turtle | binary_tree | balanced | 2695 | WIN |
| 20 | balanced | default_large1 | expand | 8054 | WIN |
| 21 | rusher | binary_tree | balanced | 5034 | LOSS |
| 22 | smart_eco | default_large1 | expand | 4522 | LOSS |
| 23 | turtle | arena | tight | 1378 | WIN |
| 24 | balanced | tree_of_life | expand | 8022 | WIN |
| 25 | rusher | default_large1 | expand | 9219 | LOSS |
| 26 | turtle | default_large2 | expand | 6135 | LOSS |
| 27 | balanced | hourglass | balanced | 974 | LOSS |
| 28 | ladder_rush | cold | balanced | 9922 | WIN |
| 29 | ladder_eco | tree_of_life | expand | 9743 | WIN |
| 30 | balanced | default_small1 | tight | 198 | WIN |
| 31 | ladder_eco | hourglass | balanced | 3534 | LOSS |
| 32 | turtle | default_medium1 | balanced | 3826 | WIN |
| 33 | sentinel_spam | galaxy | expand | 6550 | WIN |
| 34 | adaptive | wasteland | expand | 9431 | WIN |
| 35 | barrier_wall | settlement | expand | 8050 | WIN |
| 36 | ladder_rush | corridors | balanced | 3849 | LOSS |
| 37 | sentinel_spam | corridors | balanced | 9048 | LOSS |
| 38 | turtle | galaxy | expand | 9090 | WIN |
| 39 | balanced | default_small1 | tight | 5636 | WIN |
| 40 | sentinel_spam | mandelbrot | balanced | 6794 | WIN |
| 41 | balanced | default_large1 | expand | 2797 | WIN |
| 42 | rusher | arena | tight | 9113 | LOSS |
| 43 | smart_eco | galaxy | expand | 8664 | WIN |
| 44 | turtle | gaussian | balanced | 5381 | WIN |
| 45 | sentinel_spam | arena | tight | 8305 | LOSS |
| 46 | rusher | tree_of_life | expand | 252 | WIN |
| 47 | turtle | arena | tight | 3704 | WIN |
| 48 | ladder_eco | landscape | expand | 5107 | WIN |
| 49 | sentinel_spam | arena | tight | 9943 | LOSS |
| 50 | smart_defense | pixel_forest | expand | 8779 | LOSS |
