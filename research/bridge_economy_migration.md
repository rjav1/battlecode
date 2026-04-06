# Bridge Economy Migration Plan: ladder_bridge -> buzzing

## Executive Summary

ladder_bridge beats buzzing on economy maps despite being a pure-economy bot with zero military. On `cold`, it mines **22700 Ti with 236 buildings** vs buzzing's **19670 Ti with 489 buildings**. That's 15% more resources with **half the buildings** -- meaning dramatically better cost scaling and resource efficiency.

---

## TOP 5 Differences (Ranked by Impact)

### 1. Bridge-First Resource Delivery (HIGHEST IMPACT)

**ladder_bridge:** After EVERY harvester, immediately builds a bridge from the harvester back to the nearest allied conveyor/core tile. Uses `_find_bridge_sink()` to find the closest existing infrastructure, then builds a bridge directly. Only falls back to conveyors if bridge can't reach.

**buzzing:** Builds long conveyor chains from core to ore, then optionally tries a bridge shortcut NEXT round via `_bridge_target` (lines 296-361). The bridge is a "nice to have" afterthought with restrictive conditions:
- Only attempts if `9 < ore.distance_squared(core) <= 36` (line 299)
- Tries core tiles first, then chain-join as fallback
- If bridge fails, the conveyor chain already exists

**Why ladder_bridge wins:** A single bridge (cost 20 Ti, +10% scale) replaces 3-8 conveyors (cost 3 Ti each = 9-24 Ti, but each adds +1% scale = +3-8% cumulative). The scale savings compound -- fewer buildings means everything else stays cheaper.

**Migration difficulty:** MEDIUM. The core change is making bridge the PRIMARY delivery method, not a fallback.

### 2. Aggressive Builder Spawning (HIGH IMPACT)

**ladder_bridge core spawn caps:**
- Round 1-20: cap 5
- Round 21-60: cap 10
- Round 61-150: cap 15
- Round 151+: cap 20

Simple, aggressive, no econ_cap throttle. Reserve is just `cost + 2`.

**buzzing core spawn caps (expand mode):**
- Round 1-30: cap 3
- Round 31-150: cap 6
- Round 151-400: cap 12
- Round 401+: cap 16

Plus econ_cap = `max(time_floor, vis_harv * 3 + 4)` throttles further. Reserve is `cost + 2` but the caps themselves are conservative.

**Why ladder_bridge wins:** More builders = more harvesters placed earlier. The early economy snowball effect means 5 builders at round 20 can have 3-4 harvesters running by round 30, while buzzing's 3 builders might only have 1-2.

**Migration difficulty:** LOW. Raise caps, especially early game. But need to keep econ_cap logic to prevent over-spawning when economy stalls.

### 3. Minimal Building Footprint (HIGH IMPACT)

**ladder_bridge:** 236 buildings for 22700 Ti = ~96 Ti per building. Every building is productive (harvester, bridge, or navigation conveyor).

**buzzing:** 489 buildings for 19670 Ti = ~40 Ti per building. Includes barriers, roads, gunners, sentinels, extra conveyors from chain-fix, and speculative exploration conveyors.

**Key overhead in buzzing:**
- Early barriers (lines 248-293): 2+ barriers = 2-4% scale for minimal defensive value in eco games
- Gunners (lines 372-380): 10% scale each, 3 max = 30% scale
- Sentinels (lines 384-392): 20% scale each
- Barrier walls (lines 418-424): up to 15 barriers = 15% scale
- Chain-fix conveyors (lines 427-429): replaces conveyors, adding more buildings
- Exploration conveyors: nav builds conveyors even when exploring (wasting Ti far from core)

**Migration difficulty:** MEDIUM. Delay military buildings, increase Ti reserve thresholds.

### 4. Simpler Navigation with Road Fallback (MEDIUM IMPACT)

**ladder_bridge _nav:** Tries conveyor first (d.opposite() facing), then road fallback. BFS limited to 200 steps. No chain-fix, no complex path tracking.

**buzzing _nav:** Same conveyor-first but with:
- fix_path recording (line 548-549)
- Road fallback with ti_reserve=5 (line 574-584)
- Bridge fallback before road (lines 553-571) -- but only when stuck, not proactive
- Exploration with variable ti_reserve (lines 630-634)

**Why ladder_bridge wins:** It builds fewer but more strategic conveyors. The BFS cap at 200 steps prevents expensive pathfinding. Roads are cheap (1 Ti, 0.5% scale) for exploration paths.

**Migration difficulty:** LOW. Cap BFS, use roads more for exploration.

### 5. No Ore Claiming Overhead (LOW-MEDIUM IMPACT)

**ladder_bridge:** Random shuffle of visible ore, picks nearest from top 8. No markers, no claiming, no coordination. Simple and fast.

**buzzing:** Complex marker-based claiming system (lines 502-509): place marker on target ore, penalize claimed tiles. This adds CPU overhead and occasionally causes issues (markers blocking harvesters, marker placement consuming action turns).

**Why ladder_bridge wins:** With more builders, statistical coverage replaces coordination. The marker system adds complexity for marginal benefit.

**Migration difficulty:** LOW. Can keep markers but reduce their weight in scoring.

---

## Specific Migration Plan (Priority Order)

### Phase 1: Bridge-First Harvester Delivery (Expected: +30-50 Elo)

**What to change in `bots/buzzing/main.py`:**

1. **After harvester build (line 438-458):** Instead of setting `_bridge_target` for next round, immediately try to build a bridge from the harvester to the nearest existing infrastructure.

   Replace lines 442-458:
   ```python
   self._bridge_target = ore  # attempt bridge shortcut next round
   # Chain-fix for first 2 harvesters...
   ```
   With immediate bridge attempt:
   ```python
   # Try bridge directly -- replaces conveyor chain with single building
   self._try_bridge_from_harvester(c, ore)
   self.fix_path = []
   ```

2. **Add new method `_try_bridge_from_harvester()`:** Mirrors ladder_bridge's approach -- find nearest allied conveyor/core tile, build bridge adjacent to harvester pointing at it.

3. **Remove distance restriction (line 299):** Currently `9 < dist <= 36`. Bridges work at distance_sq <= 9, so the restriction should be on bridge placement, not harvester distance.

4. **Remove the entire `_bridge_target` deferred logic (lines 296-361):** Replace with immediate bridge attempt.

### Phase 2: Raise Builder Caps (Expected: +15-25 Elo)

**Lines 94-99 (core spawn caps):**

Current expand mode: `3 -> 6 -> 12 -> 16`
Change to: `5 -> 10 -> 15 -> 20` (match ladder_bridge)

Current balanced mode: `3 -> 5 -> 8 -> 10`
Change to: `5 -> 8 -> 12 -> 15`

Current tight mode: `5 -> 10 -> 18` (already aggressive, keep as-is)

**Lines 109-124 (econ_cap):**
Raise time_floor formula:
- Expand: `min(10 + rnd // 150, 20)`
- Balanced: `min(8 + rnd // 100, 15)`

### Phase 3: Delay Military (Expected: +10-15 Elo)

**Lines 372-380 (gunner):** Change `gunner_round` from 60/120/150 to 200/300/400. Require 4+ harvesters for all modes.

**Lines 384-392 (sentinel):** Change from round 1000 to round 1500. Require 8+ harvesters.

**Lines 248-293 (early barriers):** Remove entirely on expand/balanced maps. Keep only for tight maps.

**Lines 418-424 (barrier walls):** Change from round 80 to round 400. Reduce max_barriers to 4/6/10.

### Phase 4: Reduce Exploration Waste (Expected: +5-10 Elo)

**Lines 630-634 (explore Ti reserve):**
Always use `explore_reserve = 30` when far from core (>50 dist_sq), regardless of maze detection. Explorers should use roads, not conveyors.

**Lines 1194-1213 (BFS):**
Cap BFS at 200 steps (add `steps` counter like ladder_bridge line 305).

### Phase 5: Simplify Ore Selection (Expected: +0-5 Elo)

**Lines 461-491 (ore scoring):**
Add randomization like ladder_bridge (shuffle + pick from top 8). This prevents all builders converging on same ore cluster.

---

## What to KEEP from Buzzing (Not in ladder_bridge)

1. **Gunner/Sentinel defense** -- critical for PvP, just delay timing
2. **Attacker raider** -- unique advantage, keep but raise harvester threshold
3. **Barriers** -- useful on tight maps for rush defense, keep but reduce count
4. **Symmetry detection** -- needed for attacker/gunner targeting
5. **Map mode detection** -- adapt strategy per map size
6. **Marker claiming** -- keep but lower penalty weight
7. **Ax tiebreaker foundry** -- critical for TB1, keep as-is
8. **Chain-fix** -- can remove; bridge-first makes long chains rare

---

## Expected Combined Impact

| Phase | Elo Gain | Cumulative |
|-------|----------|------------|
| 1. Bridge-first delivery | +30-50 | +30-50 |
| 2. Raise builder caps | +15-25 | +45-75 |
| 3. Delay military | +10-15 | +55-90 |
| 4. Reduce explore waste | +5-10 | +60-100 |
| 5. Simplify ore selection | +0-5 | +60-105 |

**Conservative estimate: +60 Elo. Optimistic: +100 Elo.**

---

## Risk Assessment

- **Rush vulnerability:** Delaying military means we lose to early rush bots. Mitigate by keeping tight-map barriers and adding emergency gunner spawn if enemy units spotted near core.
- **Bridge placement failures:** Not all harvesters can bridge directly. Need conveyor fallback (keep existing nav logic).
- **Over-spawning builders:** More builders with no ore = wasted Ti. Keep econ_cap but raise it.
- **Testing required:** Must benchmark against both eco bots AND military bots to ensure we don't regress on PvP maps.
