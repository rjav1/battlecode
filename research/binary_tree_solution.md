# Binary Tree Map — Research & Solution

**Date:** 2026-04-08  
**Question:** How do 1600+ Elo bots mine on binary_tree? We get 40-5600 Ti as side A vs their 16000+.

---

## Map Properties

- **Size:** 41x30 (area=1230) → classified as **"balanced"** by V61
- **Wall structure:** Binary tree of walls creating branching corridors
- **Ti ore:** 30 tiles in 5 clusters. **Asymmetric** distances from each core.
- **Ax ore:** 24 tiles in 4 clusters. Equidistant from both cores (~8 BFS steps each).
- **Total ore density:** 4.4%

### ASCII layout (. empty, # wall, T Ti-ore, A Ax-ore)

```
 0: ...................TTT...................   <- top-center Ti (17+ steps from A)
 1: ...................TTT...................
 2: .................##...##.................   <- binary tree trunk begins
...
 8: ..........AAA...............AAA..........   <- Ax ore (8 steps from each core!)
 9: ..........AAA...............AAA..........
...
17: .TTT............TTT...TTT............TTT.   <- Ti ore at left (15 steps from A), right (35 steps from A)
18: .TTT............TTT...TTT............TTT.
...
26: ..........AAA...###...###...AAA..........   <- Ax ore (8 steps from B)
27: ..........AAA...#.......#...AAA..........
...
29: ........##....##.........##....##........
```

**Core A (NW)** spawns at approximately (2,2). **Core B (SE)** spawns at approximately (38,27).

---

## Ore Distance Asymmetry — the Core Problem

| Ore Cluster | BFS steps from A | BFS steps from B |
|-------------|-----------------|-----------------|
| Left Ti (1-3, 17-18) | **15** | 37 |
| Center-left Ti (16-18, 17-18) | **15** | 26 |
| Top-center Ti (19-21, 0-1) | 17 | 42 |
| Right Ti (37-39, 17-18) | 35 | **9** |
| Left Ax (10-12, 8-9) | 8 | 29 |
| Right Ax (28-30, 26-27) | 29 | **8** |

**Core B's nearest Ti is only 9 steps away. Core A's nearest Ti is 15 steps.**

**Key:** Within 10 BFS steps, Core B has 6 Ti ore tiles. Core A has **0 Ti** (only Ax).

Within 20 steps: Core A has 20 Ti (equal or more than B), but the first 15 rounds matter most — Core B gets its first harvester active 6 rounds earlier.

### The South Path is Clear (and V61 doesn't use it well)

Columns 1-2 are **wall-free** all the way from Core A (2,2) down to Ti ore at (1-3, 17-18). A builder can walk straight south and reach Ti in 15 steps — no maze navigation needed. Yet V61 only mines ~4,950-5,600 Ti from side A (vs 16,010 from side B). This is approximately 1 harvester's full output for 2000 rounds — V61 finds exactly ONE ore cluster.

---

## How 1600+ Elo Bots Actually Win binary_tree

**They don't mine more. They kill the enemy core.**

| Team | Rating | binary_tree games | Win method |
|------|--------|-------------------|------------|
| Blue Dragon | 2798 | 7/7 wins | 5x core_destroyed, 2x Ti tiebreaker |
| Kessoku Band | 2647 | 4/5 wins | 3x core_destroyed, 1x Ti, 1x loss |
| something else | 2646 | 3/4 wins | 3x core_destroyed |

**Blue Dragon wins from BOTH sides:**
- Side A (NW) vs MFF1: core_destroyed at turns **297** and **424**
- Side B (SE): core_destroyed at turns 875, 1525, 1782

The binary tree corridor structure gives a **36 BFS step path** between cores — identical for both sides. Top bots build aggressive offense (gunners/launchers firing down corridors) that kills the enemy core before mining advantage matters.

Core B's 6-round head start on Ti ore likely helps fund the first offensive structure, but the core-kill strategy applies from both sides.

---

## Why V61 Is Broken as Side A

### Current behavior
- V61 classifies binary_tree as **"balanced"** (area 625-1600)
- Balanced explore: `sector = (id * 7 + explore_idx * 3 + rnd // 50) % 8`
- With 8 builder IDs distributed across 8 directions from Core A (2,2):
  - WEST → target (0,2): hits map edge immediately, zero ore
  - NORTH → target (2,0): only reaches top-center Ti at 17+ steps
  - NORTHEAST → target (40,0): runs into walls, far from all ore
  - EAST → target (40,2): far from all accessible ore
  - **SOUTH** → target (2,29): hits Ti ore at (1-3, 17-18) at step 15 ✓
  - **SOUTHWEST** → target (0,29): also hits Ti ore at (1-3, 17-18) ✓

Only **2 of 8 explore directions** are productive from Core A. The other 6 builders spend Ti building roads and conveyors toward dead ends, then rotate to better sectors later — but the early Ti is wasted.

### The hard cap
V61 consistently mines ~4,950-5,600 Ti from side A regardless of opponent or seed. This corresponds to roughly 1 harvester running for the full game — it finds the left Ti cluster at (1-3, 17-18) but not the center-left cluster at (16-18, 17-18) which is also 15 BFS steps away.

### V61 as side B mines 3x more
From Core B (38,27), the nearest Ti at (37-39, 17-18) is only 9 steps. Multiple builders all converge there quickly, and the right-side Ax (28-30, 26-27) is also 8 steps away. More clusters are hit early, more harvesters placed, more Ti mined.

---

## Proposed Solutions

### Solution 1: Offense (recommended — matches what 1600+ Elo bots do)

Build a gunner early and orient it to fire down the corridor toward the enemy core. The binary tree has a clear 36-step path between cores. A gunner placed near Core A and oriented toward Core B can fire along this corridor, dealing 10 damage per shot.

**Mechanics:**
- Gunner placed within action r²=13 of the corridor entrance
- Fires at any enemy building in its forward ray
- With ammo delivery (2 Ti stacks per shot), 50 shots = 500 damage = core kill
- At 1 reload/round: 50 rounds of firing after setup → setup by round ~200 for kill by round ~250

This mirrors what Blue Dragon does (core_destroyed turn 297 from side A).

### Solution 2: South-first exploration fix

For binary_tree (and similar maps), detect that ore is in the south and prioritize SOUTH/SOUTHWEST explore sectors. 

**Detection signal:** If Core A is in the NW quadrant (pos.x < w/4 and pos.y < h/4) AND the nearest Ti ore is > 10 BFS steps away AND Ax ore is very close (< 10 steps), we're likely in the "binary tree" configuration where ore is south.

**Fix:** On balanced maps, if `harvesters_built == 0` at round 50+, force `explore_idx` to rotate faster (every 20 rounds instead of 50) until a harvester is placed. This self-corrects from dead-end sectors faster.

**Simpler fix:** Cap the road-building Ti reserve to 0 when no harvesters exist — don't spend Ti on infrastructure before placing a harvester. This limits dead-end exploration damage.

### Solution 3: Classify binary_tree as "tight" (area=1230, short_dim=30 > 22, so not triggered)

Tight maps use a different explore formula that's less sector-based. Not applicable without lowering the tight threshold, which risks regressions on other maps.

---

## Impact Assessment

On the ladder, binary_tree appears in roughly 1 in 38 map slots. Fixing side A performance from ~5600 to ~16000 Ti mined would:
- Convert losses vs any bot that mines > 5600 from side B → wins
- Still lose vs Blue Dragon/Kessoku-level rushers (they kill cores)

**To compete with top bots on binary_tree:** Must implement offensive core-rush capability. The ore mining fix alone only helps vs mid-tier opponents.

**Minimum viable fix:** Force faster sector rotation (every 20 rounds) when no harvesters built. Low regression risk. Estimated: +3-6 Ti ore mines per builder → might push side A to ~8000-10000 Ti.

**Maximum fix:** Gunner-based rush down the central corridor. Matches how 2400+ Elo bots win. High implementation cost but applies broadly (not just binary_tree).
