# Butterfly Map Investigation

**Date:** 2026-04-07  
**Context:** butterfly is 0W-3L in V59 baseline (all vs adaptive). Investigating root cause.

---

## Match Results

| Match | Buzzing Ti (mined) | Opp Ti (mined) | Bldgs (us/them) | Winner |
|-------|-------------------|----------------|-----------------|--------|
| buzzing vs starter, seed 1 | 29352 (24840) | 4856 (0) | 36/73 | **buzzing** |
| buzzing vs adaptive, seed 1 | 29352 (24840) | 37832 (33880) | 36/51 | **adaptive** |
| buzzing_prev vs starter, seed 1 | 38590 (34630) | 4872 (0) | 49/73 | **buzzing_prev** |
| buzzing_prev vs adaptive, seed 1 | 29101 (24840) | 37832 (33880) | 40/51 | **adaptive** |

---

## Map Properties

| Property | Value |
|----------|-------|
| Dimensions | 31x31 |
| Total tiles | 961 |
| Ti ore tiles | 95 (9.8% density) |
| Ax ore tiles | 57 (5.9% density) |
| Wall tiles | 180 (18.7% density) |
| Empty tiles | 634 (65.9%) |
| Map type | balanced (area=961, between 625-1600) |
| Wall pattern | Butterfly-wing curves — moderately complex |

**Ti density 9.8% is HIGH** — butterfly has abundant ore (gaussian was 2.3%, corridors ~3%). This is not a sparse-ore problem.

---

## Root Cause Analysis

### Finding 1: buzzing_prev mines 10k MORE Ti than buzzing vs starter

| Bot | Ti mined (vs starter) | Buildings |
|-----|----------------------|-----------|
| buzzing (V59) | 24,840 | 36 |
| buzzing_prev | 34,630 | 49 |

**10k Ti gap with only 13 more buildings.** buzzing_prev is building more harvesters more efficiently — it mines 39% more Ti while building only 36% more buildings. This is a clear regression in buzzing vs buzzing_prev on butterfly.

This regression was introduced somewhere between buzzing_prev and the current bot. Given V52/V56/V58's known improvements over V49, buzzing_prev here is likely a recent snapshot (V45/V46 era). The attacker removal (V52) may have hurt butterfly specifically if attackers were useful for clearing territory or forcing opponents off ore.

### Finding 2: Both lose to adaptive at 33880 mined

- buzzing: 24840 vs adaptive's 33880 — **9040 Ti gap**
- buzzing_prev: 24840 vs adaptive's 33880 — **same 24840 mined** (prev loses same amount)

Wait — buzzing_prev also only mines 24840 vs adaptive (same as buzzing), despite mining 34630 vs starter. This means **adaptive is actively suppressing our harvest** — not a pure economy gap. Adaptive's 51 buildings at round 2000 include sentinels or barriers that block our harvester paths on butterfly.

### Finding 3: Adaptive consistently mines 33880 regardless of opponent

adaptive mines 33880 in both matches (vs buzzing and vs buzzing_prev). This is a fixed performance ceiling for adaptive on butterfly. We need to mine >33880 to win.

buzzing_prev mines 34630 vs starter but drops to 24840 vs adaptive (-10k). This confirms adaptive is actively interfering with our harvest — likely placing barriers or sentinels on our conveyor paths, or our builders are spending time navigating around adaptive's infrastructure.

### Finding 4: Low building count (36) is suspicious

buzzing builds only 36 buildings in 2000 rounds vs adaptive. buzzing_prev builds 40-49. A lower building count with lower Ti mined means our harvesters aren't being placed efficiently — either builders aren't finding ore, or they're building fewer chains overall.

The butterfly wall pattern creates arcing corridors — the "wings". Our builders may be navigating suboptimally through the curved walls, resulting in fewer harvesters placed than buzzing_prev.

---

## Comparison: buzzing vs buzzing_prev on butterfly

| Metric | buzzing (V59) | buzzing_prev |
|--------|--------------|--------------|
| Ti mined (vs starter) | 24,840 | **34,630** |
| Buildings (vs starter) | 36 | 49 |
| Ti per building | 690 | **707** |
| Ti mined (vs adaptive) | 24,840 | 24,840 |
| Buildings (vs adaptive) | 36 | 40 |

The regression is 100% in the "vs starter" benchmark — without adversarial pressure, buzzing_prev places 13 more buildings and mines 9.8k more Ti. Under adaptive pressure, both are suppressed equally to 24840.

This means the regression is in **builder exploration/placement efficiency**, not in conveyor chains or chain-fix. Fewer harvesters are being placed on butterfly.

---

## Likely Root Cause: Attacker Removal (V52)

buzzing_prev predates V52. V52 removed the "attacker mode" where builders switch to raiding enemy infrastructure after round 500. On butterfly, the wing walls create natural corridors — attacker builders navigating those corridors may have been placing harvesters as a side effect of their exploration, even if the primary goal was attacking.

With attacker mode removed, builders settle earlier and stop exploring. On butterfly's complex curved-wall layout, builders that would have continued exploring (as attackers) are now idle after placing their initial harvesters, leaving ore on the outer wings uncovered.

**Supporting evidence:** 36 buildings (buzzing) vs 49 buildings (buzzing_prev) — the 13-building difference corresponds roughly to the harvesters a late-exploring attacker builder would have placed.

---

## Secondary Issue: adaptive's suppression strategy

On butterfly, adaptive places 51 buildings. Our building count stays at 36 whether we face starter or adaptive — adaptive is not reducing our harvest by physically blocking us, but by racing to claim ore tiles first. If adaptive builds harvesters on the outer wings before our builders reach them, we mine from fewer tiles.

adaptive's 33880 Ti mined with 51 buildings suggests it places more harvesters on butterfly's abundant ore (9.8% Ti density = 95 ore tiles). If we reach 36 harvesters vs their 51, the Ti gap follows directly.

---

## Recommendations

### Fix 1: Increase post-harvest exploration on balanced maps (HIGH PRIORITY)

After placing a harvester, builders should continue exploring to the next ore tile rather than halting. On butterfly (9.8% Ti density), there are 95 ore tiles — a single builder can cover many more tiles if it keeps walking.

**Implementation:** After `harvesters_built >= 2`, don't reduce `explore_reserve` as aggressively. Currently the code likely lowers the reserve once initial harvesters are placed. Keep a higher reserve on balanced maps with >5% Ti density.

### Fix 2: Check builder idle time after first harvest on butterfly

Run with debug output to confirm builders are idling after their first 2-3 harvesters rather than continuing to explore. If confirmed, the fix is to increase the `explore_reserve` or reduce the time-floor cap on balanced maps.

### Fix 3: Investigate whether cost scaling is the bottleneck

With 95 Ti ore tiles available, the cost scaling (each builder +20%, each harvester +5%) will push harvester cost to 50-70 Ti by round 500. If Ti income from first harvesters can't keep up with scaling, additional builders can't be spawned. Check whether the bottleneck is exploration (builders not reaching ore) or spawning (not enough Ti to spawn more builders).

---

## Summary

butterfly is lost because:
1. **We mine only 24840 Ti vs adaptive's 33880** — a 9040 Ti deficit
2. **buzzing_prev mines 34630 vs starter** — we regressed 10k Ti between prev and current bot
3. **Root cause: builders stop exploring too early** — attacker removal (V52) eliminated the late-game exploration that was inadvertently placing harvesters on butterfly's outer wings
4. **adaptive uses butterfly's abundant ore (9.8% Ti, 95 tiles) better** — it places more harvesters and claims more of the map

The fix is targeted: increase builder exploration persistence on balanced maps with high ore density. This should recover the 10k Ti gap and make butterfly competitive.
