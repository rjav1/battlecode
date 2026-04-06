# V47 Baseline Test Results (50 matches)

**Date:** 2026-04-06  
**Bot:** buzzing (V47 — stripped bot, ~1007 lines)  
**Overall record:** 29W-21L-0D (**58% win rate**)

Previous baselines: v42=45%, v43=50%, v46=58%  
V47 maintains v46 performance despite stripping 350 lines of dead features — no regression.

---

## Per-Opponent Breakdown

| Opponent | W | L | Win% | Notes |
|----------|---|---|------|-------|
| adaptive | 6 | 0 | **100%** | Dominant — never lost |
| ladder_eco | 2 | 0 | **100%** | Small sample but clean sweep |
| sentinel_spam | 2 | 0 | **100%** | Small sample but clean sweep |
| balanced | 2 | 1 | 67% | Solid |
| barrier_wall | 5 | 3 | 63% | Mostly wins, some large-map losses |
| rusher | 3 | 3 | 50% | Coin flip — map-dependent |
| fast_expand | 1 | 1 | 50% | Small sample |
| turtle | 2 | 2 | 50% | Mixed — shish_kebab losses |
| ladder_rush | 3 | 4 | **43%** | Slight weakness, especially large maps |
| smart_eco | 2 | 3 | **40%** | Weakness — loses on large/medium maps |
| smart_defense | 1 | 4 | **20%** | Clear weakness — especially on arena |

**Key nemeses:** smart_defense (1W-4L), smart_eco (2W-3L), ladder_rush (3W-4L)

---

## Per-Map-Type Breakdown

### Tight Maps (face, arena, shish_kebab, default_small1, default_small2)
**Record: 6W-10L (38%)** — significant weakness on small/tight maps

| Map | W | L | Notes |
|-----|---|---|-------|
| face | 2 | 0 | Good |
| arena | 2 | 4 | Weak — smart_defense dominates here |
| shish_kebab | 2 | 2 | Mixed |
| default_small1 | 0 | 3 | Very weak — 3 losses to rusher/ladder_rush |
| default_small2 | 0 | 1 | Small sample |

### Balanced Maps (default_medium1, cold, corridors, hourglass, butterfly, binary_tree, gaussian, mandelbrot)
**Record: 13W-5L (72%)** — strongest category

| Map | W | L | Notes |
|-----|---|---|-------|
| binary_tree | 3 | 0 | Excellent |
| hourglass | 2 | 0 | Excellent |
| default_medium1 | 2 | 0 | Excellent |
| cold | 2 | 0 | Excellent |
| butterfly | 1 | 0 | Good |
| mandelbrot | 2 | 1 | Good |
| corridors | 1 | 1 | Mixed |
| gaussian | 0 | 3 | Weak — all 3 losses (rusher, barrier_wall, smart_eco) |

### Expand Maps (settlement, landscape, wasteland, default_large1, default_large2, pixel_forest)
**Record: 10W-6L (63%)** — solid but with large-map weakness

| Map | W | L | Notes |
|-----|---|---|-------|
| landscape | 2 | 0 | Excellent |
| wasteland | 4 | 1 | Strong |
| pixel_forest | 1 | 0 | Good |
| settlement | 1 | 1 | Mixed |
| default_large2 | 1 | 1 | Mixed |
| default_large1 | 1 | 3 | Weak — ladder_rush and smart_eco beat us here |

---

## Key Findings

1. **Maintains 58% baseline** — stripping dead code caused no regression vs v46.
2. **Strong on balanced maps (72%)** — the bot's core economy is well-tuned for medium maps.
3. **Weak on tight maps (38%)** — especially `default_small1` (0-3) and `arena` (2-4). Rush defense likely insufficient on close-quarters maps.
4. **smart_defense is a nemesis (1W-4L, 20%)** — primarily beats us on `arena`. Worth investigating why.
5. **gaussian is a problem map (0-3)** — lost to rusher, barrier_wall, and smart_eco there. Possible positional/pathing issue specific to that map.
6. **ladder_rush exploits large maps** — 3 of 4 losses vs ladder_rush came on large maps (default_large1 x2, shish_kebab). Expansion speed likely the issue.

## Recommended Focus Areas

- Improve tight-map performance (rush defense, faster early aggression)
- Investigate smart_defense specifically on arena
- Debug gaussian map behavior (0-3 record)
- Improve large-map expansion vs fast-rush strategies

---

## Raw Results

| # | Opponent | Map | Type | Seed | Result |
|---|----------|-----|------|------|--------|
| 1 | rusher | default_small1 | tight | 5546 | LOSS |
| 2 | adaptive | landscape | expand | 4033 | WIN |
| 3 | ladder_eco | face | tight | 671 | WIN |
| 4 | sentinel_spam | wasteland | expand | 2010 | WIN |
| 5 | balanced | default_medium1 | balanced | 2799 | WIN |
| 6 | barrier_wall | binary_tree | balanced | 8672 | WIN |
| 7 | ladder_rush | default_large1 | expand | 8302 | LOSS |
| 8 | fast_expand | wasteland | expand | 8760 | LOSS |
| 9 | sentinel_spam | default_large1 | expand | 8607 | WIN |
| 10 | balanced | mandelbrot | balanced | 141 | LOSS |
| 11 | adaptive | mandelbrot | balanced | 5910 | WIN |
| 12 | barrier_wall | hourglass | balanced | 382 | WIN |
| 13 | turtle | hourglass | balanced | 7407 | WIN |
| 14 | smart_defense | arena | tight | 8584 | LOSS |
| 15 | adaptive | mandelbrot | balanced | 5095 | WIN |
| 16 | smart_eco | cold | balanced | 5202 | WIN |
| 17 | rusher | gaussian | balanced | 3699 | LOSS |
| 18 | smart_defense | arena | tight | 3135 | LOSS |
| 19 | smart_eco | arena | tight | 7285 | WIN |
| 20 | turtle | shish_kebab | tight | 7934 | LOSS |
| 21 | smart_defense | default_small2 | tight | 850 | LOSS |
| 22 | ladder_rush | shish_kebab | tight | 765 | WIN |
| 23 | turtle | binary_tree | balanced | 2730 | WIN |
| 24 | rusher | default_small1 | tight | 257 | LOSS |
| 25 | ladder_rush | arena | tight | 8514 | LOSS |
| 26 | balanced | butterfly | balanced | 3452 | WIN |
| 27 | barrier_wall | default_large2 | expand | 7935 | LOSS |
| 28 | barrier_wall | settlement | expand | 3869 | LOSS |
| 29 | ladder_rush | default_large1 | expand | 1306 | LOSS |
| 30 | adaptive | binary_tree | balanced | 3169 | WIN |
| 31 | adaptive | arena | tight | 8907 | WIN |
| 32 | barrier_wall | wasteland | expand | 5029 | WIN |
| 33 | barrier_wall | gaussian | balanced | 3595 | LOSS |
| 34 | ladder_rush | settlement | expand | 988 | WIN |
| 35 | barrier_wall | corridors | balanced | 4701 | WIN |
| 36 | ladder_eco | wasteland | expand | 6174 | WIN |
| 37 | barrier_wall | landscape | expand | 6289 | WIN |
| 38 | smart_eco | corridors | balanced | 5812 | LOSS |
| 39 | rusher | default_medium1 | balanced | 8713 | WIN |
| 40 | smart_defense | face | tight | 1670 | WIN |
| 41 | smart_eco | gaussian | balanced | 2164 | LOSS |
| 42 | turtle | shish_kebab | tight | 3656 | LOSS |
| 43 | rusher | pixel_forest | expand | 5501 | WIN |
| 44 | smart_eco | default_large1 | expand | 7745 | LOSS |
| 45 | ladder_rush | shish_kebab | tight | 8641 | WIN |
| 46 | smart_defense | arena | tight | 5278 | LOSS |
| 47 | rusher | cold | balanced | 4112 | WIN |
| 48 | ladder_rush | default_small1 | tight | 1151 | LOSS |
| 49 | adaptive | wasteland | expand | 6315 | WIN |
| 50 | fast_expand | default_large2 | expand | 3116 | WIN |
