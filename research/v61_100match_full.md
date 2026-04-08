# V61 100-Match Full Baseline — 38-Map Pool

**Date:** 2026-04-08
**Bot:** buzzing (V61)
**Opponents:** 14 test bots (random selection)
**Maps:** Full 38-map pool (random selection)
**Seeds:** Random

## Overall Win Rate

**66W-34L-0D = 66%**

---

## Per-Opponent Breakdown

| Opponent | W | L | Win% | Games |
|----------|---|---|------|-------|
| adaptive | 9 | 1 | 90% | 10 |
| ladder_rush | 9 | 1 | 90% | 10 |
| fast_expand | 8 | 1 | 88% | 9 |
| ladder_eco | 7 | 1 | 87% | 8 |
| turtle | 4 | 1 | 80% | 5 |
| ladder_fast_rush | 3 | 1 | 75% | 4 |
| smart_eco | 8 | 5 | 61% | 13 |
| balanced | 3 | 2 | 60% | 5 |
| rusher | 4 | 3 | 57% | 7 |
| smart_defense | 1 | 1 | 50% | 2 |
| ladder_mergeconflict | 3 | 3 | 50% | 6 |
| ladder_hybrid_defense | 2 | 4 | 33% | 6 |
| barrier_wall | 3 | 5 | 37% | 8 |
| sentinel_spam | 2 | 5 | 28% | 7 |

### Key Observations
- **Strong matchups (>80%):** adaptive, ladder_rush, fast_expand, ladder_eco, turtle, ladder_fast_rush
- **Weak matchups (<40%):** sentinel_spam (28%), barrier_wall (37%), ladder_hybrid_defense (33%)
- **sentinel_spam** is the biggest problem — 5 losses in 7 games
- **barrier_wall** and **ladder_hybrid_defense** are also problematic

---

## Per-Map Breakdown

| Map | W | L | Win% | Games |
|-----|---|---|------|-------|
| bar_chart | 4 | 0 | 100% | 4 |
| butterfly | 4 | 0 | 100% | 4 |
| corridors | 2 | 0 | 100% | 2 |
| cubes | 2 | 0 | 100% | 2 |
| default_medium1 | 1 | 0 | 100% | 1 |
| default_medium2 | 2 | 0 | 100% | 2 |
| landscape | 2 | 0 | 100% | 2 |
| pixel_forest | 5 | 0 | 100% | 5 |
| settlement | 3 | 0 | 100% | 3 |
| sierpinski_evil | 3 | 0 | 100% | 3 |
| socket | 1 | 0 | 100% | 1 |
| tree_of_life | 2 | 0 | 100% | 2 |
| wasteland | 1 | 0 | 100% | 1 |
| mandelbrot | 4 | 1 | 80% | 5 |
| shish_kebab | 4 | 1 | 80% | 5 |
| dna | 3 | 1 | 75% | 4 |
| default_large1 | 2 | 1 | 66% | 3 |
| battlebot | 2 | 1 | 66% | 3 |
| cinnamon_roll | 2 | 1 | 66% | 3 |
| wasteland_oasis | 2 | 1 | 66% | 3 |
| arena | 1 | 1 | 50% | 2 |
| chemistry_class | 1 | 1 | 50% | 2 |
| default_small1 | 2 | 2 | 50% | 4 |
| hooks | 2 | 2 | 50% | 4 |
| pls_buy_cucats_merch | 1 | 1 | 50% | 2 |
| starry_night | 2 | 2 | 50% | 4 |
| tiles | 1 | 1 | 50% | 2 |
| minimaze | 1 | 2 | 33% | 3 |
| git_branches | 1 | 2 | 33% | 3 |
| galaxy | 1 | 2 | 33% | 3 |
| cold | 1 | 2 | 33% | 3 |
| gaussian | 1 | 4 | 20% | 5 |
| binary_tree | 0 | 3 | 0% | 3 |
| face | 0 | 1 | 0% | 1 |
| thread_of_connection | 0 | 1 | 0% | 1 |

### Unplayed Maps (not sampled this run)
- default_large2
- default_small2
- hourglass

---

## Maps Dragging Us Down (Losing Record, 2+ Games)

| Map | W | L | Win% | Note |
|-----|---|---|------|------|
| binary_tree | 0 | 3 | 0% | CRITICAL — 3 straight losses |
| gaussian | 1 | 4 | 20% | CRITICAL — worst multi-game map |
| minimaze | 1 | 2 | 33% | Tight map trouble |
| git_branches | 1 | 2 | 33% | Bridge/maze trouble |
| galaxy | 1 | 2 | 33% | Large open map |
| cold | 1 | 2 | 33% | |

**binary_tree** (0-3) and **gaussian** (1-4) are the highest-priority map fixes.

---

## Maps Where We Mine < 5000 Ti

Note: Economy data is not directly captured in match output (only win/loss recorded by test script). The maps with losing records above are strong proxies — tight/maze maps and certain large open maps correlate with economy failure. Based on prior research (see `research/problem_maps.md` and `research/full_map_baseline.md`), binary_tree and gaussian have historically shown low throughput.

To get exact Ti mining figures per map, a separate analysis run with score-output parsing would be needed.

---

## Summary

- **V61 holds 66% win rate** across 100 games on 35 of 38 maps
- **Ceiling confirmed:** sentinel_spam and barrier_wall remain hard counters (28-37% win rate)
- **Map weaknesses:** gaussian and binary_tree need dedicated fixes
- **Economy concern:** large open maps (galaxy, git_branches) lose more — likely BFS range / harvester placement issues
- **Strong everywhere else** — pixel_forest, butterfly, bar_chart, sierpinski_evil all at 100%
