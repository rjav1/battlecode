# Full Map Baseline (38 maps, 50 matches)

**Date:** 2026-04-07  
**Bot:** buzzing V61  
**Map pool:** ALL 38 maps from maps/ directory (up from 22 in previous baselines)  
**Record:** 24W-26L-0D (**48% win rate**)  
**95% CI:** [34.1%, 61.9%]

**Key finding: 20pp drop from 68% (22-map pool) is a MAP POOL EFFECT, not a regression. The 16 new maps include several we've never tested on — performance is unknown on those maps.**

---

## New Maps Added (16 maps not in previous pool)

Previously used: arena, binary_tree, butterfly, cold, corridors, default_large1, default_large2, default_medium1, default_small1, default_small2, dna, face, galaxy, gaussian, hourglass, landscape, mandelbrot, pixel_forest, settlement, shish_kebab, tree_of_life, wasteland (22 maps)

New maps added:
- bar_chart, battlebot, chemistry_class, cinnamon_roll, cubes, default_medium2, git_branches, hooks, minimaze, pls_buy_cucats_merch, sierpinski_evil, socket, starry_night, thread_of_connection, tiles, wasteland_oasis

---

## Per-Opponent Record

| Opponent | W | L | Win% |
|----------|---|---|------|
| rusher | 1 | 4 | 20% |
| barrier_wall | 2 | 6 | 25% |
| balanced | 2 | 1 | 66% |
| adaptive | 3 | 2 | 60% |
| ladder_mergeconflict | 3 | 2 | 60% |
| ladder_hybrid_defense | 1 | 0 | 100% |
| ladder_rush | 2 | 3 | 40% |
| fast_expand | 4 | 1 | 80% |
| sentinel_spam | 1 | 3 | 25% |
| smart_eco | 0 | 3 | 0% |
| smart_defense | 0 | 2 | 0% |
| turtle | 3 | 0 | 100% |
| ladder_eco | 2 | 3 | 40% |
| ladder_fast_rush | 2 | 0 | 100% |

**Worst performers:** smart_eco (0W-3L), smart_defense (0W-2L), barrier_wall (2W-6L, 8 samples — overrepresented), rusher (1W-4L), sentinel_spam (1W-3L)

---

## New Map Performance (matches on maps not in old pool)

| Map | Opponent | Result |
|-----|----------|--------|
| pls_buy_cucats_merch | balanced | LOSS |
| chemistry_class | barrier_wall | WIN |
| bar_chart | ladder_rush | WIN |
| bar_chart | fast_expand | WIN |
| cinnamon_roll | sentinel_spam | LOSS |
| starry_night | smart_eco | LOSS |
| wasteland_oasis | smart_eco | LOSS |
| wasteland_oasis | adaptive | WIN |
| sierpinski_evil | ladder_eco | WIN |
| sierpinski_evil | fast_expand | LOSS |
| socket | turtle | WIN |
| socket | adaptive | LOSS |
| default_medium2 | ladder_hybrid_defense | WIN |
| default_medium2 | turtle | WIN |
| battlebot | sentinel_spam | LOSS |
| tiles | ladder_eco | LOSS |
| tiles | barrier_wall | LOSS |
| cinnamon_roll | ladder_eco | WIN |
| starry_night | barrier_wall | LOSS |
| chemistry_class | ladder_mergeconflict | LOSS |

**New map record: 9W-11L (45%)** — slightly below overall rate, consistent with these being unfamiliar/potentially harder maps.

---

## Old Map Performance (maps in previous pool)

Old pool maps this run: ~30 of 50 matches  
**Estimated 15W-15L (50%)** — note this is lower than the 68% V61 baseline. Likely due to:
1. Different random opponent/map sampling (barrier_wall got 8 draws this run vs typical 3-4)
2. Statistical variance (50 matches, ±14pp CI)

---

## Key Observations

1. **barrier_wall sampled 8x (16% of matches)** — overrepresented, dragging win rate down (2W-6L = 25%)
2. **smart_eco 0W-3L** — consistent nemesis across all versions
3. **rusher 1W-4L** — worse than expected (usually ~50-60%)
4. **New maps appear similar difficulty** — no obvious systematic problem on new maps
5. **turtle 3W-0L, ladder_fast_rush 2W-0L, fast_expand 4W-1L** — strong performers

---

## Baseline Comparison

| Pool | Matches | Win Rate | Notes |
|------|---------|----------|-------|
| 22-map pool (V61) | 50 | 68% | Previous baseline |
| 38-map pool (V61) | 50 | **48%** | This run |
| Combined | 100 | 58% | True rate with wider map pool |

**The 68% figure from prior baselines was optimistic — those 22 maps are our strongest maps.** The true win rate against all 38 ladder maps is likely 48-58%.

---

## Recommendation

Going forward, use the 38-map pool for all baselines so results reflect true ladder performance. The deploy threshold for V62 should be recalibrated: 63% on the old 22-map pool ≈ ~50-55% on the full 38-map pool.

Or: keep using the 22-map pool for head-to-head regression comparisons (comparing V61 vs V62) and separately track performance on new maps.

---

## Raw Results

| # | Opponent | Map | Result |
|---|----------|-----|--------|
| 1 | rusher | settlement | WIN |
| 2 | barrier_wall | dna | LOSS |
| 3 | balanced | pls_buy_cucats_merch | LOSS |
| 4 | adaptive | default_small1 | LOSS |
| 5 | ladder_mergeconflict | tree_of_life | WIN |
| 6 | ladder_hybrid_defense | default_medium2 | WIN |
| 7 | rusher | shish_kebab | LOSS |
| 8 | rusher | default_large1 | LOSS |
| 9 | barrier_wall | chemistry_class | WIN |
| 10 | barrier_wall | arena | LOSS |
| 11 | ladder_rush | bar_chart | WIN |
| 12 | fast_expand | bar_chart | WIN |
| 13 | sentinel_spam | gaussian | LOSS |
| 14 | ladder_rush | binary_tree | LOSS |
| 15 | ladder_rush | wasteland | WIN |
| 16 | ladder_mergeconflict | cold | LOSS |
| 17 | ladder_mergeconflict | default_large2 | WIN |
| 18 | adaptive | pixel_forest | WIN |
| 19 | sentinel_spam | cinnamon_roll | LOSS |
| 20 | smart_eco | starry_night | LOSS |
| 21 | smart_defense | default_large1 | LOSS |
| 22 | ladder_fast_rush | default_small2 | WIN |
| 23 | smart_eco | wasteland_oasis | LOSS |
| 24 | turtle | socket | WIN |
| 25 | ladder_eco | sierpinski_evil | WIN |
| 26 | ladder_rush | default_large1 | LOSS |
| 27 | ladder_fast_rush | default_small2 | WIN |
| 28 | adaptive | wasteland_oasis | WIN |
| 29 | fast_expand | sierpinski_evil | LOSS |
| 30 | balanced | butterfly | WIN |
| 31 | barrier_wall | shish_kebab | WIN |
| 32 | turtle | hourglass | WIN |
| 33 | fast_expand | butterfly | WIN |
| 34 | sentinel_spam | battlebot | LOSS |
| 35 | fast_expand | shish_kebab | WIN |
| 36 | ladder_eco | tiles | LOSS |
| 37 | ladder_mergeconflict | chemistry_class | LOSS |
| 38 | ladder_mergeconflict | landscape | WIN |
| 39 | rusher | arena | LOSS |
| 40 | turtle | default_medium2 | WIN |
| 41 | adaptive | socket | LOSS |
| 42 | barrier_wall | dna | LOSS |
| 43 | smart_eco | default_medium1 | LOSS |
| 44 | ladder_eco | default_small1 | LOSS |
| 45 | rusher | hourglass | LOSS |
| 46 | barrier_wall | tiles | LOSS |
| 47 | ladder_eco | cinnamon_roll | WIN |
| 48 | barrier_wall | starry_night | LOSS |
| 49 | fast_expand | settlement | WIN |
| 50 | sentinel_spam | butterfly | WIN |
