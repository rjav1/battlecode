# Bridge Expansion Research — Aggressive Bridge Usage

**Date:** 2026-04-06
**Analyst:** Research agent
**Context:** Blue Dragon (#1 team, 2791 Elo) uses 33 bridges. We currently use bridges in only 2 narrow scenarios. This document investigates where more bridge usage would help.

---

## Current Bridge Usage in buzzing

### 1. Post-harvester shortcut (lines 293–331)

After building a harvester, the builder sets `self._bridge_target = ore` and on the **next round** tries to build a bridge from a tile adjacent to the ore toward the core.

**Gate:** `9 < ore.distance_squared(core) <= 25` — only for harvesters 3–5 tiles from core.

**What it does:** Replaces the first conveyor(s) in the chain with a single bridge directly to a core tile. No bridging attempted for harvesters closer than dist²=9 or further than dist²=25.

### 2. Nav fallback (lines 499–517)

When the builder cannot move OR build a conveyor in the current direction, it tries to build a bridge 2–3 tiles ahead toward the target.

**Purpose:** Unsticking the builder when walls or occupied tiles block movement.

**Problem:** The bridge target is a random forward tile (toward the ore), not toward core. This rarely helps resource delivery — it only helps the builder bot cross obstacles.

---

## Test Results: buzzing vs buzzing_prev

| Map | Winner | buzzing Ti mined | prev Ti mined | Notes |
|-----|--------|-----------------|---------------|-------|
| cold | **prev** | 19670 | 19700 | Cold has diamonds/walls; minimal difference |
| corridors | **buzzing** | 14850 | 14790 | Corridors favor wall-crossing; buzzing slightly better |
| butterfly | **prev** | 24840 | 39480 | buzzing loses badly — 37% less mining |
| settlement | **buzzing** | 35470 | 13400 | buzzing mines 2.6x more |
| galaxy | **buzzing** | 13670 | 9940 | buzzing mines 37% more |
| arena | **buzzing** | 13070 | 11660 | buzzing mines 12% more |
| default_medium1 | **buzzing** | 9380 | 4950 | buzzing mines 90% more |

**Note:** buzzing_prev is v37 (same as buzzing), which ALSO lacks `_build_ax_tiebreaker`. The buzzing bot has this method but buzzing_prev raises AttributeError at round 1800. The butterfly loss is likely a strategy issue, not a bridge issue (buzzing_prev wins despite the same bug).

**Key finding:** The butterfly loss (24840 vs 39480 — a 59% gap) is the most concerning result. This is a fragmented ore map. The buzzing bot's ore density detection (`_ore_density > 0.12`) should activate maze-mode, but something is failing.

---

## Bridge Opportunity Analysis

### A. Chain-to-Chain Bridges

**Concept:** When two separate conveyor chains exist within distance²≤9 of each other, a single bridge can join them, enabling resource flow without laying more conveyors.

**When this matters:** On maps like butterfly where ore is in fragmented clusters. Builder A builds a chain from cluster 1 to core. Builder B builds chain from cluster 2, which passes near chain 1. A bridge from chain 2 into chain 1 saves N conveyors.

**Cost vs benefit:**
- Bridge: 20 Ti + 10% scale
- Conveyors saved: each saved conveyor = 3 Ti + 1% scale
- Break-even: 7 conveyors saved (Ti) or 10 conveyors saved (scale)

**Verdict:** Only worthwhile when chains would otherwise need 7+ conveyors to merge. On tight maps where chains are only 1-3 tiles apart, use a conveyor. On large maps where chains diverge significantly, a bridge merger is cost-effective.

**Detection code pattern:**
```python
# After building a harvester, scan nearby for allied conveyors/splitters
# that are NOT connected to this chain
for eid in c.get_nearby_buildings():
    etype = c.get_entity_type(eid)
    if etype in (EntityType.CONVEYOR, EntityType.SPLITTER):
        epos = c.get_position(eid)
        # If another chain tile is within bridge range (dist² ≤ 9)
        # AND a bridge between our last-placed tile and that tile would work
        if ore.distance_squared(epos) <= 9:
            if c.can_build_bridge(ore_adj, epos):
                c.build_bridge(ore_adj, epos)
```

**Risk:** Bridges connect to existing tiles. If that existing tile is on a dead-end chain or not flowing to core, the bridge achieves nothing. Need to verify chain is connected.

### B. Wall-Crossing Bridges

**Concept:** Proactively detect when the BFS path to ore crosses many walls and build a bridge over the wall cluster rather than routing conveyors around it.

**Mechanic advantage:** Bridges bypass walls entirely — they are the ONLY mechanism to deliver resources across impassable terrain. Conveyors cannot be placed on walls.

**When this matters:** Maps like cold (diamond walls), corridors (wall mazes), settlement (wall clusters). These maps have ore on the far side of walls where conveyor routing requires going around (doubling or tripling the chain length).

**Detection:** Compare straight-line distance (pos.distance_squared(target)) vs BFS path length. If BFS path is ≥ 2x longer than straight-line distance, a wall cluster is blocking. A bridge that crosses the wall could cut the path significantly.

**Implementation idea:**
```python
def _should_bridge_wall(self, pos, target, passable):
    """Returns True if a bridge would significantly shorten the path."""
    straight_dist = pos.distance_squared(target)
    bfs_steps = self._bfs_path_length(pos, target, passable)
    # Wall-crossing is beneficial if BFS path is 2x longer than straight line
    return bfs_steps is not None and bfs_steps ** 2 > straight_dist * 4
```

**Then in _nav:** When `_should_bridge_wall` is True, scan for a bridge position that reaches past the wall cluster toward the target.

**Practical challenge:** Finding the optimal bridge target (tile just past the wall, but within dist²≤9) requires knowing the wall geometry. The bot would need to scan for empty tiles on the far side of the wall cluster.

**Risk:** Building a bridge toward a tile that's not connected to core wastes 20 Ti. Need to ensure the bridge target leads toward the correct path.

### C. Harvester-to-Core Bridges for All Distances

**Current gate:** `9 < dist² <= 25` — only for harvesters ~3–5 tiles from core.

**Proposal:** Extend to `9 < dist² <= 50` with an intermediate strategy:
- For `dist² <= 25`: direct bridge to core tile (existing logic, correct)
- For `25 < dist² <= 50`: bridge to a midpoint conveyor, then conveyors from there

**Why 50?** A harvester at dist²=50 is ~7 tiles from core. A 7-conveyor chain costs 21 Ti + 7% scale. A bridge (20 Ti + 10% scale) is cheaper on Ti but worse on scale. At dist²=50, the Ti savings are marginal but the bridge eliminates chain-routing complexity and potential mis-facing bugs.

**Better idea for large distances:** At dist²>25, instead of bridging directly to core, bridge to the NEAREST allied conveyor/splitter that's already flowing toward core. This is a "bridge to existing chain" approach.

```python
# After building harvester, find nearest allied chain tile
nearest_chain = None
min_chain_dist = 10**9
for eid in c.get_nearby_buildings():
    if c.get_entity_type(eid) in (EntityType.CONVEYOR, EntityType.SPLITTER):
        if c.get_team(eid) == c.get_team():
            epos = c.get_position(eid)
            d = ore.distance_squared(epos)
            if d < min_chain_dist:
                min_chain_dist = d
                nearest_chain = epos

if nearest_chain and min_chain_dist <= 9:
    # Bridge directly to nearest chain tile
    for bd in DIRS:
        bp = ore.add(bd)
        if c.can_build_bridge(bp, nearest_chain):
            c.build_bridge(bp, nearest_chain)
            break
```

**Expected benefit:** Reduces chain length for all harvesters. Any harvester within bridge range of an existing chain can join it with 1 bridge instead of N conveyors.

### D. Bridge Cascades (Bridge → Conveyor → Bridge)

**Concept:** A single bridge reaches distance²≤9 (~3 tiles). Two bridges with a conveyor between them can reach ~6 tiles. Three bridges ~9 tiles. This allows crossing very large distances.

**Example:** Ore is 12 tiles from core behind a wall. Normal path: 15-20 conveyors around the wall. Bridge cascade: Bridge1 (crosses wall, 3 tiles), Conveyor (1 tile), Bridge2 (3 more tiles), Conveyor (1 tile), Bridge3 to core = 3 bridges + 2 conveyors = 60 Ti + 32% scale vs 15 conveyors = 45 Ti + 15% scale.

**Verdict:** Cascades are rarely better than long conveyor chains on cost. The break-even for cascades vs conveyors requires crossing walls that would otherwise force 20+ conveyors of routing.

**Where it's actually useful:** Cold-style maps where walls create forced routing of 20+ tiles. The diamond walls on cold create situations where direct-path conveyor is impossible and routing requires doubling back significantly.

**Implementation complexity:** High. Builder needs to plan 3-step bridge cascade, execute them sequentially, and ensure each bridge target is correctly positioned. Not worth implementing before simpler improvements.

---

## Root Cause: Butterfly Loss Analysis

The butterfly map has fragmented ore clusters. buzzing_prev mines 39480 Ti vs buzzing's 24840 Ti. Both are v37, so what's different?

Looking at the code: buzzing has `_build_ax_tiebreaker` and a late-game `_sentinel_step` system. buzzing_prev doesn't have `_build_ax_tiebreaker` (causes AttributeError after round 1800 — but that's minor).

The real difference: buzzing's version may have subtle changes to ore targeting or builder behavior that hurt on butterfly's fragmented terrain. The `_check_needs_low_reserve` requiring BOTH high walls AND ore richness may be failing on butterfly.

**Butterfly specific:** butterfly has very high ore density (fragmented clusters everywhere) but potentially lower wall density near core. If `_ore_density > 0.12` triggers maze mode but `_check_needs_low_reserve` doesn't trigger (because wall density near core is lower), builders use high explore_reserve (30 Ti) and avoid building conveyors far from core — starving the fragmented ore clusters.

---

## Priority Recommendations

### High Priority (implement now)

**1. Extend post-harvester bridge to dist²≤50 with chain-join**

Current code only bridges when `9 < dist² <= 25`. Extending to `dist² <= 50` and including a "bridge to nearest existing chain" fallback would dramatically improve connectivity on large maps.

**Code change in `_builder` bridge section (lines 293-331):**
```python
if self._bridge_target and self.core_pos and c.get_action_cooldown() == 0:
    ore = self._bridge_target
    ore_to_core = ore.distance_squared(self.core_pos)
    ti = c.get_global_resources()[0]
    bc = c.get_bridge_cost()[0]
    
    if ti >= bc + 5:
        # Strategy A: Bridge directly to core (if within range)
        if 9 < ore_to_core <= 25:
            # existing logic — try bridge to core tile
            ...
        
        # Strategy B: Bridge to nearest allied chain tile (any distance)
        elif ore_to_core > 25:
            nearest_chain = None
            min_d = 10
            for eid in c.get_nearby_buildings():
                try:
                    et = c.get_entity_type(eid)
                    if et in (EntityType.CONVEYOR, EntityType.SPLITTER, EntityType.BRIDGE):
                        if c.get_team(eid) == c.get_team():
                            epos = c.get_position(eid)
                            d = ore.distance_squared(epos)
                            if d < min_d:
                                min_d = d
                                nearest_chain = epos
                except Exception:
                    pass
            if nearest_chain:
                for bd in DIRS:
                    bp = ore.add(bd)
                    try:
                        if c.can_build_bridge(bp, nearest_chain):
                            c.build_bridge(bp, nearest_chain)
                            self._bridge_target = None
                            return
                    except Exception:
                        pass
    
    self._bridge_target = None
```

**Expected impact:** +10–30 Ti/round on large fragmented maps where harvesters are 6–10 tiles from existing chains.

**2. Wall-crossing bridge in nav fallback**

Current nav fallback (lines 499-517) bridges to a random forward tile. Make it smarter: when the BFS path is significantly longer than straight-line distance, bridge TOWARD CORE (not toward ore) from the current position.

**The insight:** When stuck behind a wall heading TO ore, you can't bridge the wall easily (you're not on the other side). But when you HAVE built a harvester and need to run the conveyor chain BACK to core, the wall crossing bridge becomes valuable.

So: add a wall-crossing bridge step in `_fix_chain` mode — when walking back toward core and a wall blocks the path, build a bridge over the wall to the nearest accessible core-side tile.

### Medium Priority (investigate further)

**3. Detect isolated chains and bridge-join them**

After building a second+ harvester, scan if the new chain is near an existing chain. If within bridge range, join them with a bridge instead of running two parallel chains to core.

**Trigger:** When `self.harvesters_built >= 2` and BFS path to new ore passes near an existing chain.

**4. Proactive wall-scan before exploration**

On maps with wall_density > 0.15, before navigating to distant ore, check if a bridge from near core would reach past the wall to the ore's side. If yes, build the bridge first, then explore through it.

### Low Priority (not worth it yet)

**5. Bridge cascades:** Too complex, rarely better than long conveyor routing on cost analysis.

**6. Bridging for all harvesters blindly:** The Blue Dragon approach (33 bridges = bridge everything) inflates scale +330% and is only viable if you're also destroying enemy infrastructure rapidly to reset scale. Not viable for our current strategy.

---

## Specific Code Changes Required

### Fix 1: Extend bridge gate from dist²≤25 to include chain-joining

**File:** `bots/buzzing/main.py`  
**Location:** Lines 293-331 (`_bridge_target` logic)

Current logic:
```python
if 9 < ore.distance_squared(self.core_pos) <= 25:
    # try bridge to core
```

Proposed change:
```python
ore_core_dist = ore.distance_squared(self.core_pos)
if ore_core_dist > 9:  # not trivially close to core
    ti = c.get_global_resources()[0]
    bc = c.get_bridge_cost()[0]
    if ti >= bc + 5:
        # Direct-to-core bridge if within range
        if ore_core_dist <= 25:
            # ... existing bridge-to-core logic ...
        # Chain-join bridge if existing chain is within bridge range
        else:
            self._try_bridge_to_chain(c, ore)
```

### Fix 2: Smarter nav fallback bridge target

**File:** `bots/buzzing/main.py`  
**Location:** Lines 499-517

Current: bridges toward the ore target.  
Fix: when in chain-fix mode or navigating back toward core, bridges TOWARD core instead.

```python
# In nav fallback bridge section:
# Determine bridge target based on context
if self.fixing_chain and self.core_pos:
    bridge_aim = self.core_pos  # Bridge toward core when returning
else:
    bridge_aim = target  # Bridge toward ore when exploring
```

### Fix 3: Remove distance cap entirely from post-harvester bridge

The `else: self._bridge_target = None` at line 331 discards the bridge opportunity when dist²>25. Instead, we should try the chain-join approach for those cases rather than just clearing the target.

---

## Expected Elo Impact by Scenario

| Scenario | Map Types | Expected Gain |
|----------|-----------|---------------|
| Extended post-harvester bridge (chain-join) | Large, fragmented maps | +20–40 Elo |
| Wall-crossing bridge in chain-fix mode | Cold, settlement, corridors | +10–25 Elo |
| Chain-to-chain bridge detection | Butterfly, fragmented clusters | +15–30 Elo |
| All together on hard maps | Cold, settlement, butterfly | +40–80 Elo |
| Regression risk on open maps | Arena, default maps | -5–15 Elo |

**Net expected:** +30–60 Elo if implemented carefully with distance guards.

---

## What Blue Dragon Actually Does

With 33 bridges per game, Blue Dragon is likely doing:
1. **Bridge every harvester regardless of distance** — simpler logic, no chain-routing bugs
2. **Bridge to existing chain tiles** — each new harvester bridges to the nearest flowing chain
3. **No conveyor chain-fix needed** — bridges eliminate the mis-facing problem entirely
4. **Accept scale inflation** — at Grandmaster level, they're likely also destroying enemy infrastructure quickly enough to keep scale manageable

The key insight: Blue Dragon probably uses a BRIDGE-FIRST architecture where the primary connectivity mechanism is bridges (not conveyors), and conveyors only handle short 1-2 tile connections. This is a fundamentally different architecture than buzzing.

**For buzzing:** Rather than switching architectures entirely, the targeted improvements (chain-join bridges, wall-crossing bridges) should capture most of the benefit without the open-map regression risk.

---

## Conclusion

The 3 highest-value bridge improvements are:

1. **Post-harvester chain-join bridge** — after building a harvester at any distance, scan for nearby allied chains and bridge to them if within dist²≤9. Costs 20 Ti, saves N conveyors and potentially 2+ rounds of chain-walking.

2. **Wall-crossing bridge awareness in nav** — when BFS path length >> straight-line distance, actively seek a bridge position that crosses the wall cluster rather than routing around it.

3. **Extended direct-to-core bridge gate** — currently `dist²≤25` only. Should try at `dist²≤36` (6-tile Chebyshev radius from harvester to core), since diagonal placement can reach further.

None of these require architectural changes to the bot. They are additive improvements to existing bridge logic.
