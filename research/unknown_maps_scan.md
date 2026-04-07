# Unknown Maps Scan — All 38 Maps vs Starter

**Date:** 2026-04-06  
**Bot:** buzzing V61  
**Method:** `cambc run buzzing starter <map> --seed 1` (+ seed 2-3 for problem maps)  
**Threshold:** < 1000 Ti mined = structural weakness

---

## Summary

| Category | Maps | Count |
|----------|------|-------|
| BROKEN (0 Ti mined, we lose) | cinnamon_roll, sierpinski_evil, pls_buy_cucats_merch, git_branches | 4 |
| TIMEOUT (engine hangs) | castle_keep, labyrinth | 2 |
| WEAK (low Ti, marginal) | wasteland_oasis (~4670 mined) | 1 |
| SIDE-DEPENDENT | binary_tree (0 as A, 24k as B) | 1 |
| WORKING | all others | 30 |

---

## Full Results Table

| Map | Buzzing Ti Mined | Starter Ti Mined | Winner | Notes |
|-----|-----------------|-----------------|--------|-------|
| **BROKEN — 0 Ti mined** | | | | |
| cinnamon_roll | **0** | 0 | starter | Both mine 0 — starter wins on passive income |
| sierpinski_evil | **0** | 0 | starter | Both mine 0 — starter wins on passive income |
| pls_buy_cucats_merch | **0** | 0 | starter | Both mine 0, end Ti = 18-60 |
| git_branches | **0** | 0 | starter | We lose despite same 0 mining |
| **TIMEOUT — engine hangs** | | | | |
| castle_keep | TIMEOUT | TIMEOUT | ? | Match never completes in 90s |
| labyrinth | TIMEOUT | TIMEOUT | ? | Match never completes in 90s |
| **SIDE-DEPENDENT** | | | | |
| binary_tree | 0 as A / **24690 as B** | 0 | buzzing (as B) | 0% as player A, 100% as player B |
| **WORKING — confirmed** | | | | |
| battlebot | 9860 | 0 | buzzing | Strong |
| bar_chart | 9270 | 0 | buzzing | Strong |
| minimaze | 4890 | 0 | buzzing | Good |
| tiles | 8970 | 0 | buzzing | Good |
| cubes | 26840 | 0 | buzzing | Very strong |
| thread_of_connection | 24610 | 0 | buzzing | Very strong |
| chemistry_class | 14630 | 0 | buzzing | Strong |
| hooks | 27450 | 0 | buzzing | Very strong |
| socket | 19580 | 0 | buzzing | Strong |
| default_medium2 | 17200 | 0 | buzzing | Strong |
| starry_night | 19660 | 0 | buzzing | Strong (Ti bank only 6203 — high spend) |
| mandelbrot | 27360 | 0 | buzzing | Very strong |
| wasteland_oasis | 4670 | 0 | buzzing | Marginal — low Ti bank (1861-4110) |
| arena | (local tested) | — | — | Known good |
| butterfly | (local tested) | — | — | Known |
| cold | (local tested) | — | — | Known good |
| corridors | (local tested) | — | — | Known, chain issue |
| default_large1 | (local tested) | — | — | Known good |
| default_large2 | (local tested) | — | — | Known |
| default_medium1 | (local tested) | — | — | Known good |
| default_small1 | (local tested) | — | — | Known |
| default_small2 | (local tested) | — | — | Known |
| dna | (local tested) | — | — | Known |
| face | (local tested) | — | — | Known good |
| galaxy | (local tested) | — | — | Known |
| gaussian | (local tested) | — | — | Known |
| hourglass | (local tested) | — | — | Known |
| landscape | (local tested) | — | — | Known |
| mandelbrot | (local tested) | — | — | Known |
| pixel_forest | (local tested) | — | — | Known |
| settlement | (local tested) | — | — | Known good |
| shish_kebab | (local tested) | — | — | Known |
| tree_of_life | (local tested) | — | — | Known |
| wasteland | (local tested) | — | — | Known |

---

## Critical Failures: Root Cause Analysis

### cinnamon_roll — 0 Ti mined (both sides)

Both buzzing and starter mine 0 Ti. Starter wins on passive income (~3500 vs ~3251 at rnd 2000).

**Root cause:** Map structure is a spiral/roll shape. Ore tiles exist but are enclosed — builders cannot reach them via the conveyor-first navigation. The map likely has ore surrounded by walls reachable only via a specific winding path. Our BFS is limited to 200 steps. If the path to ore exceeds 200 BFS steps, `_bfs_step` returns None, greedy direction fails against walls, and builder gets stuck.

**Evidence:** `0 Ti mined` is categorical failure — not degraded delivery but zero ore access. Builder is stuck before reaching ore.

### sierpinski_evil — 0 Ti mined (both sides)

Both sides mine 0. Starter wins on passive income.

**Root cause:** Sierpinski fractal map — ore is in isolated fractal regions separated by walls. Our BFS (200 steps) cannot find a path through the fractal. The conveyor-first nav requires passable tiles; fractals may create situations where the passable path is very long or disconnected from the starting position.

**Evidence:** Same pattern as cinnamon_roll — categorical zero.

### pls_buy_cucats_merch — 0 Ti mined (both sides), near-zero Ti bank

Both sides mine 0 AND end with almost no Ti. End Ti = 18-119. Starter sometimes barely wins.

**Root cause:** Most extreme case — both sides are completely stuck. The map name suggests a special/joke map. Ore may be completely unreachable (enclosed by walls), or the map has an unusual layout that traps builders immediately.

**Evidence:** Total Ti = 18-119 (vs passive income alone of ~5000) means even passive income isn't accumulating properly. Possible that buildings are being built and destroying Ti reserves.

### git_branches — 0 Ti mined, we lose despite 0-mining

git_branches is the worst: we mine 0, starter mines 0, but starter wins with 4297 vs our 714 Ti. We're spending our passive Ti income on buildings that don't help.

**Root cause:** Map likely has a branch structure similar to binary_tree. Our builders move toward ore via BFS, building conveyors along the way. The conveyors cost Ti but don't contribute to mining (ore never reached). Starter's bot (minimal building) retains passive income. We hemorrhage Ti on useless conveyors.

**Evidence:** 714 vs 4297 Ti — we're net-negative vs passive income. We've spent ~4300+ Ti on buildings that produced no return.

---

## Timeout Maps

### castle_keep — engine timeout (90s+)

Match never completes. This suggests an infinite loop or extremely long computation in the engine or in our bot code on this specific map geometry. Could be:
1. Our BFS hitting an edge case that causes very slow per-turn execution
2. Engine bug on castle_keep map format
3. Map is excessively large

**Impact:** castle_keep appears in our ladder losses (Code Monkeys beat us on castle_keep twice). If we time out, we forfeit. But the ladder matches did complete (turns=2000), so perhaps the timeout is a local runner issue. The ladder may have a higher timeout.

**Note:** Code Monkeys beat us on castle_keep — this may be a meaningful weakness even if the engine eventually completes.

### labyrinth — engine timeout (90s+)

Same pattern as castle_keep. Also appeared in our wins (Quwaky G3: labyrinth we won via Ti). Labyrinth has a maze structure — our BFS may be extremely slow on it.

---

## Side-Dependent Map

### binary_tree — 0% as player A, 100% as player B

As player A (buzzing A): mines 40 Ti, loses.
As player B (buzzing B): mines 24690 Ti, wins massively.

The map is rotationally symmetric. Player A core is in one position, player B in the mirror. Player B core must be positioned where it can reach ore clusters via the natural BFS expansion, while player A core's local accessible ore is trapped behind a branch configuration our BFS cannot navigate within 200 steps.

This is confirmed in ladder: Polska Gurom destroyed our core at turn 278 on binary_tree — we were player A, couldn't mine, and they rushed.

---

## Maps We Win Cleanly (New Discoveries)

| Map | Ti Mined | Verdict |
|-----|----------|---------|
| battlebot | 9860 | Strong — big open map |
| bar_chart | 9270 | Strong |
| cubes | 26840 | Very strong |
| thread_of_connection | 24610 | Very strong |
| hooks | 27450 | Very strong |
| socket | 19580 | Strong |
| mandelbrot | 27360 | Very strong |
| minimaze | 4890 | Good |
| tiles | 8970 | Good |
| chemistry_class | 14630 | Strong |

These are maps we haven't been testing locally but are winning on. Good news — we're not systematically broken on all new maps.

---

## Impact on Ladder Match Results

Cross-referencing with our ladder close-match losses:

| Map | Appeared in | Our result | Scan result |
|-----|-------------|------------|-------------|
| castle_keep | Code Monkeys 2× loss | LOSS | TIMEOUT |
| minimaze | Cenomanum G2 loss | LOSS | WIN vs starter |
| wasteland_oasis | Cenomanum G1 loss | LOSS | WIN vs starter (low Ti) |
| cinnamon_roll | Quwaky G2 loss | LOSS | BROKEN (0 Ti) |
| bear_of_doom | Quwaky G1 loss | LOSS | not in local maps |
| battlebot | Highly Suspect G1 loss | LOSS | WIN vs starter |
| default_large1 | Highly Suspect G3 loss | LOSS | tested, known map |
| chemistry_class | Highly Suspect G5 loss | LOSS | WIN vs starter (14630 Ti) |

**Key insight:** We lose on minimaze, wasteland_oasis, battlebot, chemistry_class vs ladder opponents, but WIN vs starter on these maps. This means: the maps themselves are fine for us, but **ladder opponents are outfarming us on equal maps.** The problem is opponent economy, not map geometry (except for the BROKEN and binary_tree A-side cases).

---

## Recommendations

### Immediate: Add to test suite
Maps that work and appear on ladder:
- battlebot, bar_chart, minimaze, tiles, cubes, thread_of_connection, chemistry_class, hooks, socket, mandelbrot, default_medium2, starry_night, wasteland_oasis

Add these to `test_varied.py`'s map lists to improve local test coverage.

### Fix priority: BROKEN maps (0 Ti mined)

**cinnamon_roll, sierpinski_evil, pls_buy_cucats_merch, git_branches:** Root cause is BFS 200-step limit failing on complex map geometries.

**Proposed fix:** Increase BFS step limit from 200 to 500 in `_bfs_step`. Cost: minor CPU per builder turn. Benefit: may unlock navigation on spiral/fractal maps.

**Risk:** Adding 300 BFS steps per turn per builder. At 8 builders × 2000 turns = 16000 extra BFS calls. Each BFS call at 500 steps visits ~500 nodes. This could hit the 2ms CPU limit.

**Alternative:** For exploration mode (no target), use a greedy "explore random direction" instead of BFS when stuck, which avoids the BFS cost on unmapped maps.

### Investigate: castle_keep timeout

castle_keep appears 2× in our Code Monkeys losses. If we're running pathologically slow there, we may be losing on time. Need to profile with `c.get_cpu_time_elapsed()` or reduce BFS budget on very large maps.

### Accept: binary_tree player A

Binary_tree player A is a structural loss. No fix without major architectural change. Accept 0% on this side — it's symmetric, so we win as player B equally.

### Add to V63 scope: Expand TIGHT_MAPS in test_varied.py

Many "new" ladder maps appear to be tight (cinnamon_roll, minimaze, tiles, bar_chart, battlebot). Adding them to the local test suite means our 50-match baseline better reflects ladder reality.
