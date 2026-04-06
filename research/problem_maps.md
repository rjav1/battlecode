# Problem Maps Analysis

**Date:** 2026-04-05
**Maps analyzed:** cold (0-3), shish_kebab (0-2), galaxy (0-2)
**Total lost games on these maps:** 7
**Impact:** Fixing these = potential +14 Elo (7 games * ~2 Elo swing each)

---

## 1. COLD (0-3 across all versions) -- HIGHEST PRIORITY

### Map Properties
- **Size:** 37x37 (area=1369, "medium-large")
- **Symmetry:** Horizontal reflection
- **Ore:** 115 Ti, 18 Ax -- **extremely Ti-rich** (3rd richest map)
- **Core distance:** path=12 (8-dir), path=28 (4-dir) -- relatively close cores
- **Regions:** 1 (not fragmented)
- **Type:** Econ map -- should be our strength

### Ladder Replay Data
**v1 loss (vs One More Time, round 2000):**
- Us: Ti collected=8260, Harvesters=43, Conveyors=303
- Them: Ti collected=25970, Harvesters=22, Conveyors=599
- Gap: 3.14x (they collected 3x more with half the harvesters)

**v9 loss (vs 5goats, round 2000):**
- Us: Ti collected=6730, Harvesters=14, Conveyors=62, Barriers=1
- Them: Ti collected=12500, Harvesters=5, Roads=16, Conveyors=36
- Gap: 1.86x (they collected 2x more with 1/3 the harvesters)

### Local Test Data
- **buzzing vs starter on cold: 8,130 Ti mined**
- **eco_opponent baseline on cold: 23,230 Ti mined**
- **Gap: 2.86x** -- eco_opponent mines nearly 3x more on this map

### Root Cause Analysis
Cold is a 37x37 economy map with 115 Ti ore -- it should be our best map. But we consistently collect 2-3x less Ti than opponents despite having MORE harvesters. This means:

1. **Conveyor chains don't connect on this map layout.** Cold has tight vertical corridors and a "diamond enclosure" pattern. Our conveyor chain BFS may fail to find paths through the constrained geometry.
2. **We build too many disconnected harvesters.** v1 built 43 harvesters but collected only 8260 Ti. If all 43 were connected at ~10 Ti/round, we'd collect 86,000 Ti. We collected 10% of theoretical max.
3. **The map has close cores (path=12).** This is both a rush and economy map. Our defensive spending (barriers, sentinels) may waste resources better spent on economy.

### Fix Priority: CRITICAL
This is an economy powerhouse map. Fixing conveyor chain pathfinding on cold alone could flip 3 game results.

---

## 2. SHISH_KEBAB (0-2 across v2 and v8)

### Map Properties
- **Size:** 20x20 (area=400, "small")
- **Symmetry:** Rotational
- **Ore:** 10 Ti, 4 Ax -- **extremely scarce**
- **Core distance:** path=19 (8-dir), path=36 (4-dir)
- **Regions:** 5 (highly fragmented!)
- **Type:** Fragment + Scarce

### Ladder Replay Data
**v8 loss (vs Solo Gambling, round 2000):**
- Us: Ti collected=7360, Harvesters=2, Conveyors=70, Barriers=6, Bridges=0
- Them: Ti collected=17150, Harvesters=6, Roads=32, Conveyors=40, Bridges=0
- Gap: 2.33x

### Root Cause Analysis
1. **Map fragmentation traps our builders.** 5 regions means ore is scattered across disconnected islands. Our builders stay in the starting region and only reach 2 of 10 Ti ore deposits.
2. **Zero bridges built.** Neither team uses bridges, but the opponent reaches 6 harvesters through natural road connectivity. Our starting position may have worse connectivity.
3. **Wasted 6 barriers on a 20x20 map.** On a scarce map with only 10 Ti ore, spending resources on 6 barriers is wasteful. Every Ti should go to economy.
4. **Scarce resources amplify the gap.** With only 10 Ti ore, missing even 2-3 deposits puts us at a massive disadvantage.

### Fix Priority: MEDIUM
- Need bridges to cross between fragmented regions
- Reduce barrier spending on small/scarce maps (area <= 625)
- Map adaptation should detect fragment count and adjust strategy

---

## 3. GALAXY (0-2 across v2 and v4)

### Map Properties
- **Size:** 40x40 (area=1600, "large")
- **Symmetry:** Rotational
- **Ore:** 16 Ti, 8 Ax -- **low resources**
- **Core distance:** path=34 (8-dir), path=68 (4-dir) -- very far apart
- **Regions:** 1
- **Type:** Mixed (low resources + large map + far cores)

### What Makes Galaxy Hard
1. **Very few ore deposits (16 Ti) on a large map (40x40).** Builders must travel far to find ore.
2. **Cores are far apart (path=68 4-dir).** This means long conveyor chains needed, high infrastructure cost.
3. **Low resource count** means every harvester placement matters. Missing even 1-2 deposits is decisive.
4. **Large map with low density = exploration is critical.** Builders need to cover a lot of ground efficiently.

### Fix Priority: MEDIUM
- Need better exploration on large, sparse maps
- Conveyor chain cost may be prohibitive on long-distance paths (68 steps = 68 conveyors)
- Consider targeted exploration patterns for sparse maps

---

## Summary Table

| Map | Size | Ore | Regions | Root Cause | Fix |
|---|---|---|---|---|---|
| cold | 37x37 | 115 Ti | 1 | Conveyor chains fail in tight corridors | Fix chain pathfinding for constrained layouts |
| shish_kebab | 20x20 | 10 Ti | 5 | Builders trapped in starting region | Add bridges for fragmented maps |
| galaxy | 40x40 | 16 Ti | 1 | Sparse ore on large map, long paths | Better exploration for sparse/large maps |

## Cross-Cutting Issues

1. **Conveyor chain pathfinding is the common thread.** On cold (tight corridors), shish_kebab (fragments), and galaxy (long distances), our chain builder fails to connect harvesters to core reliably.

2. **We over-invest in defense on losing maps.** 6 barriers on shish_kebab, 1-2 sentinels on cold. On maps where we're losing the resource race, every Ti should go to economy.

3. **We don't use bridges.** 0 bridges on all problem maps. Bridges could help on shish_kebab (cross fragments) and cold (bypass tight corridors).

4. **Eco_opponent mines 23,230 Ti on cold vs our 8,130 (local test).** A 2.86x gap on our worst map. If we close even half this gap, cold flips from loss to win.

## Recommended Priority

1. **Fix cold first** (0-3, economy map, highest impact -- 115 Ti ore, should be winnable)
2. **Fix shish_kebab second** (0-2, fragmented map, needs bridges)
3. **Fix galaxy third** (0-2, sparse large map, exploration improvement)
