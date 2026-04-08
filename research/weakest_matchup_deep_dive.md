# Weakest Matchup Deep Dive — Economy Analysis

**Date:** 2026-04-08
**Goal:** Identify economy gaps in our 3 worst matchups (sentinel_spam 28%, ladder_hybrid_defense 33%, barrier_wall 37%)

---

## Match Results Summary

| # | Matchup | Map | Winner | Our Ti mined | Their Ti mined | Our buildings | Their buildings |
|---|---------|-----|--------|-------------|----------------|---------------|-----------------|
| 1 | vs sentinel_spam | cold | **sentinel_spam** | 18,930 | 27,520 | 133 | 203 |
| 2 | vs sentinel_spam | galaxy | **buzzing** | 9,950 | 9,900 | 272 | 194 |
| 3 | vs ladder_hybrid_defense | default_medium1 | **ladder_hybrid_defense** | 4,940 | 4,960 | 295 | 267 |
| 4 | vs barrier_wall | gaussian | **barrier_wall** | 19,830 | 29,730 | 211 | 101 |
| 5 | vs barrier_wall | cold | **barrier_wall** | 15,720 | 18,720 | 618 | 123 |

---

## Match-by-Match Analysis

### Match 1: vs sentinel_spam on cold — LOSS
- **Ti gap:** 18,930 vs 27,520 — sentinel_spam mined **8,590 more Ti (+45%)**
- **Building gap:** 133 vs 203 — they built 70 more buildings
- **Diagnosis:** Cold is a wide-open map with many ore tiles. sentinel_spam harvested far more efficiently. Our 133 buildings with less Ti suggests we're spending on conveyors/roads rather than harvesters. sentinel_spam's pure harvesting strategy beats us on open maps.

### Match 2: vs sentinel_spam on galaxy — WIN
- **Ti gap:** 9,950 vs 9,900 — nearly identical mining (we won by tiebreak)
- **Building count:** 272 vs 194 — we built MORE buildings but same Ti
- **Diagnosis:** We won but barely, despite building 78 more structures. galaxy's layout must limit sentinel_spam's turret lines. This win is map-specific, not a real strength.

### Match 3: vs ladder_hybrid_defense on default_medium1 — LOSS
- **Ti gap:** 4,940 vs 4,960 — **essentially tied** (20 Ti difference)
- **Building gap:** 295 vs 267 — we actually built MORE buildings
- **Diagnosis:** CRITICAL FINDING. We lose despite equal economy and more buildings. The loss is pure efficiency — ladder_hybrid_defense's 267 buildings deliver more Ti to core than our 295. We are building MORE but winning LESS. This is a conveyor waste / delivery efficiency problem, not a harvester problem.

### Match 4: vs barrier_wall on gaussian — LOSS
- **Ti gap:** 19,830 vs 29,730 — barrier_wall mined **9,900 more Ti (+50%)**
- **Building gap:** 211 vs 101 — they won with only 101 buildings (half ours)
- **Diagnosis:** barrier_wall mines massive Ti with only 101 buildings — extremely efficient harvesting. gaussian has many ore tiles and barrier_wall clearly has a better harvester placement strategy. We waste 211 buildings to mine 10k less Ti. Cost scaling is killing us — every extra building we build costs more.

### Match 5: vs barrier_wall on cold — LOSS
- **Ti gap:** 15,720 vs 18,720 — barrier_wall mined **3,000 more Ti (+19%)**
- **Building gap:** 618 vs 123 — **we built 5x more buildings** and still lost
- **Diagnosis:** CRITICAL FINDING. 618 buildings vs 123. We are building 5 times as many structures as barrier_wall and losing. This is the clearest evidence of extreme conveyor waste. With 618 buildings our cost scale must be enormous — every new harvester or conveyor costs multiples of base price. barrier_wall's lean 123-building approach keeps costs low and delivers more efficiently.

---

## Root Cause Analysis

### Problem 1: Massive Building Overcounting (the #1 issue)
- Match 5: 618 buildings vs opponent's 123 — we build 5x more
- Match 4: 211 buildings vs opponent's 101 — we build 2x more
- Match 3: 295 buildings vs opponent's 267 — slight excess
- Every building raises global cost scale (+0.5% to +5% each). 618 buildings = enormous scale multiplier crushing our economy.

### Problem 2: Economy Throughput Gap on Open Maps
- cold/gaussian: opponents mine 20-50% more Ti with fewer buildings
- Our harvester chains are either: (a) not reaching ore tiles, (b) routing inefficiently, or (c) being throttled by cost scaling from excess buildings

### Problem 3: Delivery Efficiency (ladder_hybrid_defense case)
- Match 3: tied economy, tied buildings, still lose
- They deliver Ti to core more efficiently — better conveyor routing or fewer wasted stacks

### Problem 4: Sentinel_spam specifically
- Cold: they outmine us by 45% with more buildings — competitive harvesting
- Galaxy: we tie on mining but build 78 more structures (waste)
- sentinel_spam may have better early-game Ti priority for turret placement

---

## What Opponents Do Differently

| Opponent | Strategy | Buildings used | Ti efficiency |
|----------|----------|----------------|---------------|
| barrier_wall | Lean: few buildings, max harvesters on best ore | 101-123 | Excellent — mines 29k+ Ti |
| sentinel_spam | Moderate: harvests + turret spam | 194-203 | Good — 27k Ti on cold |
| ladder_hybrid_defense | Efficient delivery chains | 267 | Average mining, better delivery |
| buzzing | Sprawling: many conveyors/roads | 211-618 | Poor — mines less despite more buildings |

---

## Actionable Fixes (Priority Order)

### Fix 1: Building cap / pruning (highest impact)
- **Target:** Reduce from 618 to <200 buildings on open maps
- **How:** Destroy roads/conveyors that are no longer needed after expansion. Limit conveyor chain length. Don't build roads speculatively.
- **Expected gain:** Massive cost scale reduction — harvesters/conveyors become cheaper, allowing more harvesters

### Fix 2: Harvester placement priority
- **Target:** Get harvesters on richest ore tiles first
- **How:** Score ore tiles by proximity to core + density; place harvesters there first
- **Expected gain:** Match barrier_wall's 29k Ti throughput on gaussian/cold

### Fix 3: Conveyor delivery path efficiency
- **Target:** Close the 20 Ti gap vs ladder_hybrid_defense (default_medium1)
- **How:** Shorter conveyor chains, fewer splitters/wasted direction changes
- **Expected gain:** Win close tiebreak games

---

## Conclusion

The data reveals two distinct loss patterns:

1. **vs barrier_wall/sentinel_spam:** We mine 20-50% less Ti despite building MORE. Building bloat (618 vs 123) drives cost scaling that chokes our economy. Fix: hard building cap or aggressive destroy-unused.

2. **vs ladder_hybrid_defense:** Economy is tied but delivery is less efficient. Fix: shorter conveyor chains to core.

The 618-building game against barrier_wall on cold is the most alarming data point — this is not a strategy problem, it's a runaway building loop that must be stopped.
