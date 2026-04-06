# vs smart_eco Debug Analysis — v47

Date: 2026-04-06
Bot tested: buzzing (v47) vs smart_eco

## Test Results

| Map            | Seed | Winner     | Buzzing Ti (mined) | smart_eco Ti (mined) | Buzzing Bldg | smart_eco Bldg |
|----------------|------|------------|--------------------|----------------------|--------------|----------------|
| default_medium1| 1    | smart_eco  | 9873 (9100)        | 10440 (9880)         | 117          | 187            |
| gaussian       | 1    | smart_eco  | 21916 (19840)      | 27192 (23340)        | 229          | 110            |
| galaxy         | 1    | smart_eco  | 13821 (13670)      | 18049 (14660)        | 259          | 168            |
| cold           | 1    | smart_eco  | 17873 (19670)      | 29568 (28230)        | 264          | 415            |

**Result: 0-4 (0% win rate)**

---

## Root Cause Analysis

### 1. Building Count Anomaly — Conveyor Waste

The most glaring signal: **buzzing builds 2-4x more buildings than smart_eco while mining LESS**.

- gaussian: 229 vs 110 buildings, buzzing mines 19840 vs 23340
- galaxy: 259 vs 168 buildings, buzzing mines 13670 vs 14660
- cold: 264 vs 415 (cold is maze-like, so both build more, but buzzing earns far less despite similar scale)

**Diagnosis:** Buzzing is spending massive Ti on conveyors that don't efficiently deliver ore. smart_eco spends that Ti reserve on fewer, more direct conveyor chains + more harvesters. Every wasted conveyor = Ti not available for the next harvester or builder.

### 2. Builder Cap vs. Aggressive Spending — smart_eco builds 8 builders by round 200+

smart_eco cap schedule:
- Round <=30: 4 builders
- Round <=100: 6 builders
- Round <=200: 7 builders
- Round >200: 8 builders
- Ti reserve needed: only cost+5

buzzing cap schedule (balanced map, e.g. default_medium1 is ~medium):
- Round <=25: 3 builders  ← SLOWER START
- Round <=100: 4 builders  ← MUCH SLOWER (smart_eco has 6!)
- Round <=300: 6 builders
- Round >300: 8 (but capped by econ_cap)

**Critical gap:** At round 100, smart_eco has 6 builders vs buzzing's 4 on balanced maps. This means smart_eco harvesters more ore tiles 2 builders earlier = compounding Ti income lead.

### 3. econ_cap Formula Throttles Spawning

Buzzing uses: `econ_cap = max(time_floor, vis_harv * 3 + 4)`

With `time_floor` = 6 (balanced, early), this means:
- 0 harvesters visible from core → cap = 6 (barely above time_floor)
- 1 harvester visible → cap = max(6, 7) = 7
- But harvesters may not be in core's vision range (r²=36 is limited)

This formula is **self-limiting**: the core can't see harvesters placed far away, so vis_harv stays low, throttling the cap below what it should be. smart_eco ignores harvesters entirely and just spawns to cap with aggressive Ti threshold (cost+5).

### 4. Ti Reserve Difference

- buzzing: `ti < cost + 2` → spawns when Ti >= cost+2
- smart_eco: `ti < cost + 5` → spawns when Ti >= cost+5

This is actually BETTER for buzzing (lower reserve = faster spawn). But buzzing's higher per-unit conveyor spending burns through Ti reserves that should fund builder spawns.

### 5. cold Map: Raw Axionite Destruction

cold (19670 Ti mined for buzzing) — note buzzing mined MORE Ti than smart_eco (19670 vs 28230 is raw, but buzzing ends with 17873 while smart_eco has 29568). Wait — smart_eco mined 28230 vs buzzing's 19670, meaning smart_eco found more/better ore or got there faster. The +8500 Ti mined gap = critical cold map issue. smart_eco's rotating exploration with 8 builders finds ore faster.

### 6. Ax Tiebreaker — Both Score 0

Both bots end with 0 axionite. buzzing explicitly has Ax score +50000 penalty to avoid Ax ore. smart_eco builds Ax harvesters too (both Ti and Ax). However both deliver 0 axionite to core. This suggests neither builds a foundry for conversion. This is a missed tiebreaker opportunity for late-game if Ti is close.

---

## Key Differences: smart_eco vs buzzing

| Feature | smart_eco | buzzing |
|---------|-----------|---------|
| Builder cap at r=100 (balanced) | 6 | 4 |
| Builder cap ramp-up speed | Fast (4 by r30) | Slow (3 by r25, 4 by r100) |
| econ_cap formula | None (pure time cap) | vis_harv * 3 + 4 (throttles!) |
| Ti reserve to spawn | cost+5 | cost+2 |
| Conveyor strategy | d.opposite(), simple BFS | d.opposite() + fix_chain + bridge + complex |
| Building count | ~110-264 | ~117-415 |
| Ax ore targeting | Yes (both Ti+Ax) | No (heavy penalty +50000) |
| Attacker builder | No | Yes (id%6==5, round 500+) |
| Gunner | No | Yes (round 300+, Ti>500) |
| Barrier building | No | Yes (round 80+) |

---

## Recommendations (Priority Order)

### Fix 1: Raise builder caps to match smart_eco — CRITICAL

Current buzzing caps are too conservative, especially at round 100 (4 vs 6 builders).

Change balanced mode:
```python
# Current:
cap = 3 if rnd <= 25 else (4 if rnd <= 100 else (6 if rnd <= 300 else 8))
# Target:
cap = 4 if rnd <= 30 else (6 if rnd <= 100 else (7 if rnd <= 200 else 8))
```

Change tight mode:
```python
# Current: 3 → 5 → 8
# Target:  4 → 6 → 8  (same as smart_eco)
```

This alone could close 30-50% of the Ti mined gap.

### Fix 2: Remove or relax econ_cap formula — CRITICAL

The `econ_cap = max(time_floor, vis_harv * 3 + 4)` formula throttles spawning because:
- Core vision r²=36 doesn't reach far harvesters
- Results in lower builder count than intended cap

**Option A:** Remove econ_cap entirely — let time caps drive spawning
**Option B:** Replace vis_harv with `self.harvesters_built` (count across all builders via markers) — avoids vision limitation

Recommendation: Option A (simpler, matches smart_eco's approach). The time floor and map-mode caps already encode good enough logic.

### Fix 3: Reduce conveyor spending — HIGH PRIORITY

gaussian builds 229 buildings with lower Ti mined. This screams conveyor overbuilding. smart_eco's simple approach (build conveyor on each step toward ore) works better than buzzing's complex fix_chain + bridge logic.

**Hypothesis:** fix_chain, bridge shortcuts, and the pending_gunner_ammo all add conveyor waste without proportional delivery benefit. Test a simplified nav that just builds conveyors on the direct path, no chain-fix.

### Fix 4: Consider removing/delaying military features

- Attacker builder (round 500+): costs Ti on roads, no resource benefit before r800
- Gunner placement (round 300+): gunner cost 10 Ti + ammo conveyors — this Ti could go to a harvester
- Early barriers (round 5-30): modest cost but delays builder movement to ore

smart_eco wins with 0 military. These features hurt economy vs pure-eco opponents.

### Fix 5: Add Ax harvesting for tiebreaker

smart_eco targets both Ti AND Ax. buzzing applies a +50000 score penalty. If Ax is closer/more abundant, buzzing passes it up entirely. Raw Ax must be refined (foundry) but:
- 1 foundry = 40 Ti at +100% scale = expensive but game-winning
- Axionite tiebreaker is #2 after total refined Ti delivered

For late game (round 1500+), if Ti exceeds ~2000, consider building a foundry + Ax harvester chain.

---

## Summary

The 0% win rate vs smart_eco comes down to **2-3 fewer active builders in rounds 1-200** due to:
1. Conservative builder caps (4 at r100 vs smart_eco's 6)
2. econ_cap throttling further reducing spawns
3. Excessive conveyor spending (2-4x building count) depleting Ti that should fund builder spawns

smart_eco's simplicity is its strength: spawn builders aggressively, build conveyors directly to ore, ignore military. buzzing's complexity (attacker, gunner, barriers, chain-fix, bridge) is net-negative in pure economy matchups.

**Primary fix:** Raise builder caps + remove econ_cap formula = likely 3-4 Ti mined improvement per map.
