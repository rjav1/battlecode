# vs smart_defense Debug Analysis

## Test Results

| Map | Winner | buzzing Ti | smart_defense Ti | buzzing Buildings | SD Buildings | buzzing Mined | SD Mined |
|-----|--------|-----------|-----------------|-------------------|--------------|---------------|----------|
| default_medium1 (seed 1) | smart_defense | 3,780 | 22,147 | 241 | 148 | 4,950 | 20,740 |
| cold (seed 1) | **buzzing** | 14,360 | 16,310 | 392 | 257 | 15,580 | 13,860 |
| galaxy (seed 1) | smart_defense | 10,865 | 17,469 | 231 | 230 | 9,950 | 14,650 |
| default_medium1 (seed 42) | smart_defense | 3,780 | 22,147 | 241 | 148 | 4,950 | 20,740 |
| galaxy (seed 42) | smart_defense | 10,865 | 17,469 | 231 | 230 | 9,950 | 14,650 |

**Result: buzzing 1-4 vs smart_defense (20% win rate). On cold only, buzzing wins — cold is a maze-like map where our BFS + maze detection helps.**

---

## Root Cause Analysis

### 1. Building Count: We Waste Resources on Infrastructure

The starkest signal is **building count**:
- default_medium1: buzzing 241 buildings vs smart_defense 148 → **63% more buildings**
- galaxy: buzzing 231 buildings vs smart_defense 230 → similar, but we mined 9,950 vs SD's 14,650

On default_medium1, buzzing builds 93 more structures but mines only 4,950 Ti vs SD's 20,740. This gap is catastrophic. Each extra conveyor costs scale, and most of these are **exploration conveyors** — conveyors dropped as walkways while navigating to ore that never forms a productive chain.

### 2. smart_defense Strategy (from code analysis)

smart_defense is intentionally simple:
- **4 builders, fixed cap** — never overbuilds builders that outpace ore coverage
- **Conveyors with d.opposite() facing** — same technique as us, but FAR fewer built
- **No attacker, no sentinel, no sentinel splice** — zero expenditure on non-economy features
- **Barriers at round 80 (8 around core)** — cheap, effective defense
- **2 gunners at round 200** — minimal turret investment (10 Ti each, 2 built)
- **Gunner fires at ammo >= 2** — same as us

Their advantage: **they build fewer conveyors because they have fewer builders navigating around**. 4 builders produce far fewer exploration conveyors than our 10-16.

### 3. Our Exploration Conveyor Waste

When a buzzing builder has no ore in vision, it calls `_explore()`, which calls `_nav()`. `_nav()` drops a conveyor on every tile it steps through (`ti >= cc + ti_reserve`). With `ti_reserve=30 if core_dist_sq > 50 else 5`, it's still dropping conveyors on exploration paths.

With 10-16 builders exploring, each taking a different sector, they collectively build hundreds of exploration conveyors that:
- Raise the cost scale for all future buildings
- Don't connect to anything useful
- Consume Ti that could stay as banked resources for tiebreak

### 4. Builder Cap Too High — The Self-Defeating Economy

On galaxy (expand map), our cap reaches 16. With 16 builders each building conveyors on exploration paths:
- Scale inflates rapidly 
- Each new harvester costs more
- The 16 builders produce fewer net harvesters than 4 focused builders would
- End result: buzzing mined only 9,950 Ti while SD with 12 units mined 14,650

The formula `econ_cap = max(time_floor, vis_harv * 3 + 4)` drives overbuilding. With harvesters producing, vis_harv grows, which permits more builders, who explore more, who waste more on conveyors.

### 5. Scale Inflation Snowballs

smart_defense builds:
- Roads and conveyors for navigation (scale: +0.5-1% each)
- 8 barriers (+1% each)
- 2 gunners (+10% each)
- ~4 harvesters (+5% each)
- **Total scale additions: ~50-60% total**

buzzing builds 93+ more conveyors on default_medium1 alone → each at +1% → **+93% extra scale just from excess conveyors**. This makes harvesters cost 5% more per extra conveyor pair built, compounding throughout the game.

---

## Why cold is different

On cold (maze-like map), our BFS navigation + maze detection kicks in with `explore_reserve = 5`, so we build fewer dead-end conveyors. Also, cold has lots of Ti ore accessible near core, so builders find ore quickly without much exploration. Our higher builder count actually helps here (more harvesters built). SD's 4-builder cap becomes a ceiling.

---

## Specific Recommendations

### Fix 1: Cap builders much lower — match SD's philosophy

**Current:** expand cap = 3→6→12→16, balanced = 3→5→8→10
**Recommended:** expand cap = 3→4→6→8, balanced = 3→4→5→6

The economy multiplier from 4 focused builders > 16 scattered builders in most maps, because exploration conveyors cost more than they're worth.

### Fix 2: Suppress conveyor building during exploration entirely

When a builder is in `_explore()` mode (no target ore), set `ti_reserve` very high — high enough to prevent conveyor placement unless Ti is overflowing:

```python
explore_reserve = 200  # Don't drop exploration conveyors
```

Only build a road (cheaper, +0.5% scale) as a walkway. Or build nothing and walk on existing paths.

### Fix 3: Road-first navigation, not conveyor-first

During navigation to ore (not yet adjacent), prefer building **roads** instead of **conveyors** as walkway tiles. Once a harvester is placed and we know the chain direction, retroactively upgrade the roads to conveyors pointing correctly. This halves the scale inflation from infrastructure.

Current code in `_nav()` always tries conveyor first — roads only as final fallback. Invert this for tiles that are more than 3 steps from the ore target.

### Fix 4: Eliminate the econ_cap formula driving overbuilding

The formula `econ_cap = max(time_floor, vis_harv * 3 + 4)` is too aggressive. Replace with:

```python
econ_cap = min(vis_harv * 2 + 2, max_cap)  # 2 builders per harvester max
```

This prevents the runaway scenario where harvesters generate more builders who build more junk.

### Fix 5: Stop sentinel/attacker features until economy matches SD

The armed sentinel splice (multi-round stateful operation) is blocking builders from building harvesters. At round 500+, a builder assigned to sentinel duty spends 4-5 rounds doing nothing economically useful. With an already weak economy, this is a double loss.

Disable sentinel until `global_Ti_mined > 10000` or only allow it when we're ahead on resources.

---

## Priority Order

1. **Highest impact:** Lower builder cap drastically (Fix 1) + suppress exploration conveyors (Fix 2)
2. **High impact:** Road-first navigation (Fix 3)  
3. **Medium impact:** Fix econ_cap formula (Fix 4)
4. **Low impact:** Guard sentinel/attacker with economy condition (Fix 5)

The gap on default_medium1 (3,780 vs 22,147 Ti final) is so large that the root cause is almost entirely Fix 1 + Fix 2 — too many builders building useless exploration conveyors and raising scale for everything else.
