# Tight Map Ore Proximity Research

**Date:** 2026-04-06
**Question:** On tight maps (arena, face), how far is ore from our core? How fast do we get harvesters?

---

## Map Specs

| Map | Size | Core center (team 1) | Core center (team 2) |
|-----|------|----------------------|----------------------|
| arena | 25x25 | (8, 10) | (16, 14) |
| face | 20x20 | (5, 7) | (14, 7) |

Both are classified as "tight" by buzzing (area ≤ 625 tiles).

---

## arena (25x25) — Team 1 ore distances

### Ti ore (sorted by distance from core center)
| Position | Euclidean dist | Chebyshev (travel rounds) |
|----------|---------------|---------------------------|
| (4, 8) | 4.5 | **3** |
| (5, 15) | 5.8 | **4** |
| (7, 4) | 6.1 | **5** |
| (12, 3) | 8.1 | 6 |
| (7, 19) | 9.1 | 8 |
| (17, 5) | 10.3 | 8 |
| (19, 9) | 11.0 | 10 |
| (12, 21) | 11.7 | 10 |
| (20, 16) | 13.4 | 11 |
| (17, 20) | 13.5 | 9 |

### Ax ore (sorted by distance from core center)
| Position | Euclidean dist | Chebyshev (travel rounds) |
|----------|---------------|---------------------------|
| **(8, 13)** | **3.0** | **2** — closest ore on map |
| (12, 7) | 5.0 | **3** |
| (12, 17) | 8.1 | 6 |
| (16, 11) | 8.1 | 7 |

**Key finding:** The closest ore to arena team 1 core is Ax ore at (8,13), only 2 travel rounds away. Nearest Ti is 3 rounds away.

---

## face (20x20) — Team 1 ore distances

### Ti ore (sorted by distance)
| Position | Euclidean dist | Chebyshev (travel rounds) |
|----------|---------------|---------------------------|
| **(1, 8)** | **4.1** | **3** — closest ore on map |
| (7, 13) | 6.3 | 5 |
| (7, 0) | 7.3 | 6 |
| (12, 0) | 9.9 | 6 |
| (12, 13) | 9.2 | 6 |
| (1, 16) | 9.8 | 8 |
| (18, 8) | 13.0 | 12 |
| (18, 16) | 15.8 | 12 |

### Ax ore (sorted by distance)
| Position | Euclidean dist | Chebyshev (travel rounds) |
|----------|---------------|---------------------------|
| (1, 1) | 7.2 | 5 |
| (5, 18) | 11.0 | 10 |
| (14, 18) | 14.2 | 10 |
| (18, 1) | 14.3 | 12 |

**Key finding:** Nearest ore on face is Ti at (1,8), 3 travel rounds from core. No close Ax ore — nearest is 5 rounds away.

---

## Observed Harvester Timing (probe_buzzing vs starter)

### arena, seed 1
| Event | Round | Ore type | Position |
|-------|-------|----------|----------|
| **1st harvester** | **3** | Ax | (8, 13) — 2 travel rounds |
| 2nd harvester | 9 | Ti | (4, 8) — 3 travel rounds |
| 3rd harvester | 14 | Ti | (7, 4) |
| 4th harvester | 18 | Ti | (5, 15) |
| 5th harvester | 36 | Ax | (12, 7) |
| (late Ax run) | 156 | Ax | (12, 17) |
| (late Ti) | 171 | Ti | (12, 21) |

**Harvester count at milestones:**
- Round 10: **2** harvesters
- Round 20: **4** harvesters
- Round 50: **5** harvesters
- Round 100: **5** harvesters

### face, seed 1
| Event | Round | Ore type | Position |
|-------|-------|----------|----------|
| **1st harvester** | **6** | Ti | (1, 8) — 3 travel rounds |
| 2nd harvester | 18 | Ax | (1, 1) |
| 3rd harvester | 83 | Ti | (12, 0) |
| 4th harvester | 109 | Ax | (18, 1) |

**Harvester count at milestones:**
- Round 10: **1** harvester
- Round 20: **2** harvesters
- Round 50: **2** harvesters
- Round 100: **3** harvesters

---

## Analysis

### arena vs face comparison

arena is dramatically faster to ramp than face:
- **arena**: 4 harvesters by round 20, thanks to ore within 2-3 travel rounds on ALL sides
- **face**: only 2 harvesters by round 20; the cluster of Ti ore at (1,8) is the only fast target

### Why arena is faster

1. Ax ore at (8,13) is only 2 rounds from core — first harvester builds on round 3
2. Three more ore tiles within 3-5 rounds, all reachable by separate builders in parallel
3. By round 18 buzzing already has 4 harvesters running

### Why face is slower

1. Nearest Ti at (1,8) takes 3 rounds minimum — first harvester round 6
2. Only ONE ore tile within 5 rounds of travel (Ti at (1,8)) — other tiles are 6-12 rounds away
3. 3rd and 4th harvesters don't land until rounds 83 and 109 — very late ramp
4. face's Ti ore is distributed symmetrically and far from center; most tiles are enemy-side or mid-map

### Implication for first builder routing

The first builder spawns on round 1 on a core tile. With 1-move-per-round and no road infrastructure:
- **arena**: builder can reach nearest ore (2 rounds) by round 3, build harvester, already producing
- **face**: builder needs 3+ rounds to reach (1,8), plus conveyor build-back — first output around round 8-10

The current bot correctly finds the nearest ore via `_best_adj_ore`, but it explores randomly before reaching ore. A direct first-builder path toward the nearest ore tile would shave 2-4 rounds off the first harvester.

### Ore type distribution

| Map | Nearest ore | Type | Action |
|-----|-------------|------|--------|
| arena | (8,13) dist=2 | **Ax** | Ax harvester first — needs foundry to be useful, but starts Ti stack flow |
| face | (1,8) dist=3 | **Ti** | Ti harvester first — ideal |

Note: On arena, the closest ore is Axionite. Raw Ax delivered to core is **destroyed** (docs). Arena's fast ramp comes from Ti ore at (4,8) in round 9, not the Ax ore at round 3. The Ax harvester output is wasted unless a foundry is built (expensive: +100% scale).

---

## Recommendations

1. **arena**: First builder should beeline to Ti at (4,8) (3 rounds) rather than Ax at (8,13) (2 rounds) — Ti is immediately useful, Ax is wasted without a foundry.

2. **face**: Very limited early ore — only (1,8) is fast. Second builder should immediately target (7,13) or (7,0). The 83-round gap before 3rd harvester is a major economy bottleneck.

3. **General tight map pattern**: With 3-6 ore tiles within reasonable reach, the first 2-3 builders should each beeline to a distinct ore tile in parallel rather than sequentially. The current claiming system (markers) helps, but the slow 83-round 3rd harvester on face suggests the 2nd and 3rd builders are both wandering.

4. **Road investment**: Roads cost 1 Ti (+0.5% scale) and enable builder movement. For a 3-5 tile path to ore, laying a road first then returning costs ~5 Ti and 10 rounds — likely not worth it vs. just walking on conveyors built on the return trip. Skip roads for tight maps.
