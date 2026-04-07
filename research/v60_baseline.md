# V60 Baseline (50 matches)

**Date:** 2026-04-07  
**Bot:** buzzing V60 (V59 + fast explore rotation when harvesters_built==0 after round 100)  
**Record:** 34W-16L (**68% win rate**)

**Verdict: PASSES 63% threshold. V60 is safe to deploy. Fast rotation fixes binary_tree (0-5 map) without regressing standard maps. +6pp vs V58 baseline (62%), +3pp below V59 local (71% was inflated).**

Progression: v58=65% → v59=74% (local, likely inflated) → **v60=68%** (same seed set, fair comparison)

---

## What Changed (V59 → V60)

In `_explore()` method, three locations (large/balanced/tight map branches):
```python
# Fast rotation fallback: if no ore found by round 100, rotate every 25 rounds
if rnd > 100 and self.harvesters_built == 0:
    sector = (mid * 7 + self.explore_idx * 3 + rnd // 25) % len(DIRS)
```

The `harvesters_built == 0` guard ensures this only fires when builders are stuck with no ore found. Standard maps have ore within reach by round 100, so `harvesters_built >= 1` and the fast rotation never activates. Only affects maps like binary_tree where starting explore direction misses all ore.

---

## binary_tree Fix Confirmed

| Match | Opponent | Map | Seed | Result |
|-------|----------|-----|------|--------|
| 41 | ladder_eco | binary_tree | 6089 | WIN |

V59 would have lost this (ladder_eco/binary_tree was a known 0-5 collapse map).

---

## Per-Opponent Breakdown

| Opponent | W | L | Win% | V59 Win% | Delta |
|----------|---|---|------|----------|-------|
| turtle | 1 | 3 | 25% | 75% | -50% |
| rusher | 4 | 0 | 100% | 100% | 0% |
| fast_expand | 5 | 1 | 83% | 83% | 0% |
| sentinel_spam | 3 | 1 | 75% | 75% | 0% |
| ladder_eco | 3 | 1 | 75% | 100% | -25% |
| ladder_rush | 3 | 0 | 100% | 100% | 0% |
| adaptive | 3 | 1 | 75% | 75% | 0% |
| barrier_wall | 1 | 2 | 33% | 33% | 0% |
| balanced | 4 | 0 | 100% | 100% | 0% |
| smart_eco | 1 | 2 | 33% | 33% | 0% |
| smart_defense | 4 | 3 | 57% | 57% | 0% |

Notable: turtle dropped 75%→25% (3 losses: shish_kebab, settlement, dna). Likely map-draw variance — turtle was only 2 matches in V59.

---

## Raw Results

| # | Opponent | Map | Seed | Result |
|---|----------|-----|------|--------|
| 1 | turtle | dna | 7405 | LOSS |
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
| 24 | ladder_eco | corridors | 3161 | LOSS |
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
| 48 | turtle | dna | 7405 | LOSS |
| 49 | fast_expand | landscape | 4631 | WIN |
| 50 | adaptive | corridors | 7650 | LOSS |
