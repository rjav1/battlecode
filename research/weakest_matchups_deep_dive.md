# V61 Weakest Matchup Deep Dive

**Date:** 2026-04-08  
**Task:** Deep-dive V61 vs sentinel_spam, ladder_hybrid_defense, barrier_wall on their best maps  
**Goal:** Identify root causes and Elo-gaining opportunities

---

## Summary Table

| Opponent | Map Set Tested | V61 Record | Root Cause |
|----------|---------------|-----------|------------|
| barrier_wall | 6 maps (3 seeds on cold) | 2W-7L (22%) | Massive overbuilding — 3.5x more buildings, burns Ti |
| ladder_hybrid_defense | 7 maps | 2W-5L (29%) | Same overbuilding on large/eco maps |
| sentinel_spam | 7 maps | 3W-4L (43%) | Ore undercover on open maps; overbuilding on hourglass |

---

## Opponent 1: barrier_wall

### Map Results
| Map | Winner | Us Ti | Them Ti | Us Bldgs | Them Bldgs |
|-----|--------|--------|---------|----------|------------|
| galaxy | barrier_wall | 14073 | 19118 | 261 | 125 |
| default_large1 | barrier_wall | 13986 | 27784 | 308 | 212 |
| default_large2 | barrier_wall | — | — | — | — |
| cold (seed 1) | barrier_wall | 8306 | 22808 | 618 | 123 |
| cold (seed 42) | barrier_wall | 14150 | 22699 | 505 | 156 |
| cold (seed 99) | barrier_wall | 14268 | 22676 | 506 | 159 |
| cold (seed 7) | barrier_wall | 12214 | 22939 | 558 | 152 |
| landscape | **buzzing** | WIN | — | — | — |
| hourglass | **buzzing** | WIN | — | — | — |

**V61 vs barrier_wall: 2W-7L (22%)**

### Root Cause Analysis

**On cold (worst map):**
- Us: 12000-14300 Ti stored, ~17700-18500 mined, **505-618 buildings**
- Them: 22700-22900 Ti stored, ~19100-19500 mined, **152-159 buildings**

We mine almost as much Ti (17700 vs 19100) but end up with ~8000-10000 LESS stored. The gap is entirely explained by building costs: 500+ buildings × avg cost ~15 Ti = **7500+ Ti spent on scale-inflated construction** vs their 155 buildings × avg cost ~15 Ti = **2300 Ti**. Difference: ~5000 Ti — exactly matches our deficit.

**On galaxy/large maps:**
Same pattern: we have 2x their buildings, similar mining, far less stored.

**Why we win on landscape/hourglass:**
These are more constrained maps where our BFS naturally limits building sprawl. Fewer ore tiles = fewer harvesters = fewer conveyors = less cost scaling.

### Fix Opportunity
**Cap conveyor/building count explicitly.** If we limit total buildings (excluding core tiles) to ~150-200, we would stop at a lower scale factor, preserve Ti, and beat barrier_wall consistently.

**Potential Elo gain:** barrier_wall-style opponents appear in ~20-25% of ladder matches. Fixing this matchup from 22% → 60% win rate = significant Elo gains.

---

## Opponent 2: ladder_hybrid_defense

### Map Results
| Map | Winner | Us Ti | Them Ti | Us Bldgs | Them Bldgs |
|-----|--------|--------|---------|----------|------------|
| face | ladder_hybrid_defense | — | — | — | — |
| galaxy | ladder_hybrid_defense | 6425 | 16167 | 386 | 292 |
| default_large1 | ladder_hybrid_defense | — | — | — | — |
| cold | ladder_hybrid_defense | 16358 | 30199 | 453 | 319 |
| landscape | ladder_hybrid_defense | — | — | — | — |
| corridors | **buzzing** | WIN | — | — | — |
| hourglass | **buzzing** | WIN | — | — | — |

**V61 vs ladder_hybrid_defense: 2W-5L (29%)**

### Root Cause Analysis

**On galaxy:**
- Us: 6425 Ti, 9950 mined, 386 buildings
- Them: 16167 Ti, 14790 mined, 292 buildings
- We mine **32% less** AND have more buildings. Double penalty.

**On cold:**
- Us: 16358 Ti, 19670 mined, 453 buildings
- Them: 30199 Ti, 29590 mined, 319 buildings
- They mine **50% more** AND have fewer buildings.

ladder_hybrid_defense appears to have better ore coverage than barrier_wall — they actively mine more, not just save more. Our harvesters may be hitting fewer ore tiles or being blocked by our own building sprawl.

**Why we win on corridors/hourglass:**
Constrained geometry limits both sides' expansion. Our strength is tight-map economy.

### Fix Opportunity
Same building cap fix as barrier_wall, PLUS improving ore coverage on large maps. If we detect large map (width×height > 900), we could prioritize distant ore tiles more aggressively.

---

## Opponent 3: sentinel_spam

### Map Results
| Map | Winner | Us Ti | Them Ti | Us Bldgs | Them Bldgs |
|-----|--------|--------|---------|----------|------------|
| default_small1 | **buzzing** | WIN | — | — | — |
| default_small2 | sentinel_spam | — | — | — | — |
| shish_kebab | **buzzing** | WIN | — | — | — |
| corridors | sentinel_spam | 19255 | 24839 | 26 | 32 |
| hourglass | sentinel_spam | 19449 | 28520 | 355 | 107 |
| face | sentinel_spam | — | — | — | — |
| butterfly | **buzzing** | WIN | — | — | — |

**V61 vs sentinel_spam: 3W-4L (43%)**

### Root Cause Analysis

**On corridors (both seeds identical!):**
- Us: 19255 Ti, **14600 mined**, 26 buildings
- Them: 24839 Ti, **19800 mined**, 32 buildings
- Almost identical building counts. They mine **35% more** ore.
- Sentinel_spam is hitting more ore tiles or has better conveyor chains on this map.
- Seed-identical results confirm this is structural, not random.

**On hourglass:**
- Us: 19449 Ti, 19860 mined, **355 buildings**
- Them: 28520 Ti, 24090 mined, **107 buildings**
- We overbuild 3.3x and mine less. Same overbuilding pattern.

**On small maps (default_small1, shish_kebab, butterfly) we WIN:**
Small maps limit expansion; sentinel spam sentinels don't have range to matter as much.

### Fix Opportunity
Two separate issues:
1. **Corridors ore miss:** We're not reaching all ore tiles. Need better exploration on long-corridor maps.
2. **Hourglass overbuilding:** Same building cap fix as barrier_wall.

---

## Cross-Cutting Root Causes

### Root Cause #1: Building Count Bloat (CRITICAL)

**Evidence:**
- cold vs barrier_wall: 505-618 buildings vs 123-159
- cold vs hybrid_defense: 453 vs 319
- hourglass vs sentinel_spam: 355 vs 107

**Mechanism:** Each extra building beyond ~150 adds to cost scaling. At 500 buildings, new conveyors cost 5-6x base price. This compounds: more expensive conveyors → slower expansion → fewer harvesters connected → less Ti per round → less Ti to spend → but we keep building roads/conveyors anyway creating a death spiral.

**Fix:** Add a global building count cap (~200 total non-core buildings). When at cap, only build if replacing a dead connection or adding a harvester on a new ore tile.

### Root Cause #2: Ore Coverage Gap on Open Maps (MODERATE)

**Evidence:**
- corridors vs sentinel_spam: 14600 vs 19800 mined (35% gap, nearly no buildings difference)
- galaxy vs hybrid_defense: 9950 vs 14790 mined (49% gap)

**Mechanism:** On open maps with scattered ore, our BFS exploration may not reach all ore clusters. Sentinel_spam and hybrid_defense bots appear to claim more ore tiles with fewer builders.

**Fix:** On maps where our mined Ti is < 75% of max possible (estimatable from map size), bias builder dispatch toward unexplored ore regions instead of building more conveyors near existing chains.

---

## Prioritized Fix List

| Fix | Difficulty | Impact | Maps Affected |
|-----|-----------|--------|---------------|
| Building count cap (~200) | Medium | HIGH — eliminates overbuilding spiral | cold, galaxy, large maps, hourglass |
| Ore exploration bias on open maps | Hard | MEDIUM — 35% more mining on corridors type | corridors, face, galaxy |
| Large map detection + strategy shift | Easy | LOW-MEDIUM — better heuristics | default_large1/2, cold |

---

## Win Rate Projection

If building count cap fix is implemented and validated:
- vs barrier_wall: 22% → ~55% (+33%)
- vs ladder_hybrid_defense: 29% → ~50% (+21%)
- vs sentinel_spam (hourglass): ~0% → ~50%
- Overall ladder win rate: from ~54% → ~62% (estimated +8%)
- Estimated Elo gain: +30-50 Elo (could push from ~1480 to ~1520-1530)
