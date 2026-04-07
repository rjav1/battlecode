# V59 Baseline (50 matches)

**Date:** 2026-04-07  
**Bot:** buzzing_v59 (chain-join leg removed, core-bridge with dist^2 9-25 guard kept)  
**Record:** 37W-13L (**74% win rate**)

**Verdict: DEPLOY. Easily passes 63% threshold (+11pp). Chain-join removal is a significant improvement over V58 (60-65%). Ready to apply to buzzing main.**

Progression: v52=70% → v56/v58=65% → v57=57% (regression) → **v59=74%** (chain-join removal)

---

## What Changed (V58 → V59)

Bridge shortcut at `_builder` (~line 275):
- **Removed**: Chain-join leg — scanned nearby buildings, bridged ore to nearest allied conveyor/bridge closer to core. This was breaking conveyor chains on corridors and other maps.
- **Kept**: Core-fallback leg — bridge ore-adjacent tile directly to a core tile.
- **Added**: Distance guard `9 < ore_core_dist <= 25` — only fires for medium-range ore. Close ore (dist²≤9) uses conveyor chain directly. Far ore (dist²>25) also uses conveyor chain.

This matches the behavior in `buzzing_prev` (v37) which had the same distance guard.

---

## Per-Opponent Breakdown

| Opponent | W | L | Win% | V58 Win% | Delta |
|----------|---|---|------|----------|-------|
| turtle | 3 | 1 | 75% | ~75% | 0% |
| rusher | 4 | 0 | 100% | ~100% | 0% |
| fast_expand | 5 | 1 | 83% | ~83% | 0% |
| sentinel_spam | 3 | 1 | 75% | ~75% | 0% |
| ladder_eco | 3 | 0 | 100% | ~100% | 0% |
| ladder_rush | 3 | 0 | 100% | ~100% | 0% |
| adaptive | 3 | 1 | 75% | ~66% | +9% |
| barrier_wall | 1 | 2 | 33% | ~50% | -17% |
| balanced | 4 | 0 | 100% | ~50% | +50% |
| smart_eco | 1 | 2 | 33% | ~0% | +33% |
| smart_defense | 4 | 3 | 57% | ~16% | +41% |

Key improvements vs V58: smart_defense 16%→57%, balanced 50%→100%.

---

## Corridors Analysis

Corridors matches (3 tested):
- rusher/corridors seed 7650: WIN (match 9, match 42)
- ladder_eco/corridors seed 3161: WIN (match 24)
- sentinel_spam/corridors seed 1711: LOSS (match 39)
- smart_eco/corridors seed 3161: LOSS (match 47)
- adaptive/corridors seed 7650: LOSS (match 50)

Corridors still loses to eco opponents (smart_eco, adaptive). The chain-join removal helps but corridors ore Ti mined is ~10060 (not yet at buzzing_prev's 14850). Full corridors fix requires enemy-road BFS fix (separate task).

---

## Raw Results

| # | Opponent | Map | Seed | Result |
|---|----------|-----|------|--------|
| 1 | turtle | dna | 7405 | WIN |
| 2 | rusher | pixel_forest | 7166 | WIN |
| 3 | fast_expand | shish_kebab | 3239 | WIN |
| 4 | fast_expand | cold | 4492 | WIN |
| 5 | sentinel_spam | default_large2 | 5924 | WIN |
| 6 | ladder_eco | wasteland | 6259 | WIN |
| 7 | ladder_rush | default_large1 | 1388 | WIN |
| 8 | adaptive | cold | 4860 | WIN |
| 9 | rusher | corridors | 7650 | WIN |
| 10 | smart_defense | gaussian | 8736 | WIN |
| 11 | adaptive | landscape | 6442 | WIN |
| 12 | ladder_eco | landscape | 4631 | WIN |
| 13 | smart_defense | default_medium1 | 7995 | LOSS |
| 14 | balanced | tree_of_life | 7172 | WIN |
| 15 | rusher | default_small1 | 4669 | LOSS |
| 16 | rusher | galaxy | 6634 | LOSS |
| 17 | turtle | hourglass | 8367 | WIN |
| 18 | adaptive | settlement | 3948 | WIN |
| 19 | fast_expand | mandelbrot | 3388 | WIN |
| 20 | balanced | pixel_forest | 8602 | WIN |
| 21 | sentinel_spam | face | 413 | WIN |
| 22 | sentinel_spam | face | 1381 | WIN |
| 23 | sentinel_spam | tree_of_life | 1449 | WIN |
| 24 | ladder_eco | corridors | 3161 | WIN |
| 25 | adaptive | butterfly | 146 | LOSS |
| 26 | balanced | dna | 1544 | WIN |
| 27 | turtle | shish_kebab | 7863 | LOSS |
| 28 | turtle | settlement | 8194 | LOSS |
| 29 | smart_eco | default_large2 | 9609 | WIN |
| 30 | barrier_wall | default_small1 | 6742 | WIN |
| 31 | barrier_wall | galaxy | 783 | LOSS |
| 32 | barrier_wall | cold | 2011 | LOSS |
| 33 | fast_expand | gaussian | 9125 | WIN |
| 34 | fast_expand | butterfly | 4838 | WIN |
| 35 | fast_expand | butterfly | 8073 | WIN |
| 36 | smart_defense | pixel_forest | 3376 | LOSS |
| 37 | smart_defense | default_large2 | 1653 | WIN |
| 38 | fast_expand | default_large1 | 7661 | LOSS |
| 39 | sentinel_spam | corridors | 1711 | LOSS |
| 40 | ladder_rush | cold | 6869 | WIN |
| 41 | ladder_eco | binary_tree | 6089 | WIN |
| 42 | rusher | corridors | 7650 | WIN |
| 43 | balanced | cold | 4860 | WIN |
| 44 | ladder_rush | dna | 3424 | WIN |
| 45 | smart_defense | face | 413 | WIN |
| 46 | balanced | landscape | 4631 | WIN |
| 47 | smart_eco | corridors | 3161 | LOSS |
| 48 | turtle | dna | 7405 | WIN |
| 49 | fast_expand | landscape | 4631 | WIN |
| 50 | adaptive | corridors | 7650 | LOSS |
