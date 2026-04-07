# V57 Baseline (30 matches)

**Date:** 2026-04-07  
**Bot:** buzzing V57 (bridge shortcut fully removed)  
**Record:** 17W-13L-0D (**57% win rate**)

**Verdict: REGRESSION. Down from V52's 70% to 57% — 13pp drop. Bridge removal hurt more than corridors improved. DO NOT ship V57 as-is.**

Progression: v52=70% → v55=47% (reverted) → v56=65% → **v57=57%**

---

## Per-Opponent Breakdown

| Opponent | W | L | Win% | V52 Win% | Delta |
|----------|---|---|------|----------|-------|
| ladder_rush | 2 | 0 | **100%** | 66% | +34% |
| rusher | 1 | 0 | **100%** | 66% | +34% |
| balanced | 2 | 0 | **100%** | 60% | +40% |
| fast_expand | 4 | 1 | 80% | 100% | -20% |
| sentinel_spam | 2 | 1 | 66% | 66% | 0% |
| ladder_eco | 2 | 1 | 66% | 66% | 0% |
| adaptive | 2 | 1 | 66% | 100% | -34% |
| barrier_wall | 1 | 2 | 33% | 100% | **-67%** |
| smart_defense | 1 | 4 | **20%** | 33% | -13% |
| turtle | 0 | 2 | **0%** | 100% | **-100%** |
| smart_eco | 0 | 1 | 0% | 28% | -28% |

**Critical regressions:**
- turtle: 100% → 0% (0W-2L) — passive eco opponent collapse, same signal as V55
- barrier_wall: 100% → 33% (1W-2L) — was a clean sweep in V52
- adaptive: 100% → 66% (2W-1L) — minor but notable
- smart_defense: 33% → 20% (1W-4L) — 5 matches, genuinely worse

---

## Per-Map-Type Breakdown

| Type | W | L | Win% | V52 Win% | Delta |
|------|---|---|------|----------|-------|
| Balanced | 11 | 5 | **68%** | 50% | **+18%** |
| Expand | 5 | 5 | 50% | 84% | **-34%** |
| Tight | 1 | 3 | 25% | 67% | -42% |

This is the smoking gun: **expand maps collapsed from 84% → 50%**. Bridge removal specifically hurt expand maps — bridges were used to deliver ore across open terrain on large maps. Without them, conveyor chains on expand maps are less efficient.

Balanced maps improved (+18%) — corridors fix is real (corridors went 1W-2L here, was 0W-3L in V52 comprehensive). But this gain is outweighed by the expand map loss.

---

## Corridors Analysis

corridors: 1W-2L (33%) in V57 vs 0W-3L (0%) in V52 comprehensive.

Marginal improvement on corridors. The +185% Ti improvement seen in isolated testing (5090→14520 Ti) is not translating to match wins — opponents may also benefit from the absence of bridges, or the test was against a specific weaker opponent.

---

## Root Cause

Bridge shortcuts were providing value on **expand maps** specifically — large open maps where ore is far from core. Without bridges, builders must build long unbroken conveyor chains across open terrain, which is slower and costs more Ti.

The corridors improvement is real but small. The expand map regression is large and systematic:
- smart_defense/default_large2: LOSS (expand)
- smart_defense/pixel_forest: LOSS (expand)
- turtle/settlement: LOSS (expand)
- smart_eco/default_large2: LOSS (expand)
- fast_expand/default_large1: LOSS (expand)

5 of 10 expand losses. In V52, expand was 84% (11W-2L). V57 is 50% (5W-5L) — a collapse.

---

## Recommendation

**Revert bridge removal. V57 is a net negative (-13pp).**

The corridors improvement (+18% balanced) does not compensate for the expand regression (-34% expand). 

Options for V58:
1. **Restore bridges on expand maps only** — gate bridge usage by `map_mode == 'expand'`
2. **Partial bridge removal** — keep bridges for ore delivery (long-range), remove only the "shortcut" navigation use
3. **Revert fully to V56** — accept that corridors stays at 0% while keeping expand at 84%

Option 1 or 2 is likely the right path: bridges help on expand maps and should be kept there, while the corridors issue is a separate pathfinding problem unrelated to bridges.

---

## Raw Results

| # | Opponent | Map | Type | Seed | Result |
|---|----------|-----|------|------|--------|
| 1 | sentinel_spam | corridors | balanced | 1711 | LOSS |
| 2 | ladder_rush | cold | balanced | 6869 | WIN |
| 3 | ladder_eco | binary_tree | balanced | 6089 | WIN |
| 4 | adaptive | cold | balanced | 4860 | WIN |
| 5 | ladder_rush | dna | balanced | 3424 | WIN |
| 6 | smart_defense | face | tight | 413 | LOSS |
| 7 | smart_defense | default_large2 | expand | 1653 | LOSS |
| 8 | sentinel_spam | face | tight | 1381 | WIN |
| 9 | ladder_eco | landscape | expand | 4631 | WIN |
| 10 | smart_defense | gaussian | balanced | 8736 | WIN |
| 11 | smart_defense | pixel_forest | expand | 3376 | LOSS |
| 12 | turtle | shish_kebab | tight | 7863 | LOSS |
| 13 | fast_expand | gaussian | balanced | 9125 | WIN |
| 14 | rusher | corridors | balanced | 7650 | WIN |
| 15 | adaptive | butterfly | balanced | 146 | LOSS |
| 16 | balanced | dna | balanced | 1544 | WIN |
| 17 | sentinel_spam | tree_of_life | expand | 1449 | WIN |
| 18 | ladder_eco | corridors | balanced | 3161 | LOSS |
| 19 | adaptive | settlement | expand | 3948 | WIN |
| 20 | fast_expand | butterfly | balanced | 4838 | WIN |
| 21 | balanced | tree_of_life | expand | 7172 | WIN |
| 22 | turtle | settlement | expand | 8194 | LOSS |
| 23 | smart_eco | default_large2 | expand | 9609 | LOSS |
| 24 | barrier_wall | default_small1 | tight | 6742 | LOSS |
| 25 | fast_expand | mandelbrot | balanced | 3388 | WIN |
| 26 | barrier_wall | galaxy | expand | 783 | WIN |
| 27 | barrier_wall | cold | balanced | 2011 | LOSS |
| 28 | smart_defense | default_medium1 | balanced | 7995 | LOSS |
| 29 | fast_expand | butterfly | balanced | 8073 | WIN |
| 30 | fast_expand | default_large1 | expand | 7661 | LOSS |
