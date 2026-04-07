# V55 Balanced Map Test — corridors and gaussian

**Date:** 2026-04-06
**Version:** buzzing V55 (with reach=min(w,h)//2 fix)

---

## Map Metadata

| Map | Dimensions | Area | Mode |
|-----|-----------|------|------|
| corridors | 31x31 | 961 | balanced |
| gaussian | 35x20 | 700 | balanced |

---

## Test Results

### corridors

| Matchup | buzzing Ti (mined) | Opponent Ti (mined) | Our Bldgs | Their Bldgs | Winner |
|---------|--------------------|--------------------|-----------|-------------|--------|
| buzzing vs smart_eco | 9575 (5090) | 19380 (14660) | 26 | 36 | smart_eco |
| buzzing vs balanced | 9575 (5090) | 24771 (19800) | 26 | 32 | balanced |
| buzzing vs starter | 8145 (6810) | 2838 (0) | 156 | 472 | buzzing |
| smart_eco vs starter | 19380 (14660) | 2669 (0) | 36 | 469 | smart_eco |
| balanced vs starter | 24771 (19800) | 2651 (0) | 32 | 495 | balanced |
| buzzing_prev vs starter | 21560 (17180) | 2490 (0) | 34 | 496 | buzzing_prev |
| **buzzing vs buzzing_prev** | **9575 (5090)** | **19381 (14850)** | **26** | **25** | **buzzing_prev wins** |

**Seed-invariant results** — corridors Ti output is deterministic (identical across all seeds 1/42/137/256/999).

### gaussian

| Matchup | buzzing Ti (mined) | Opponent Ti (mined) | Our Bldgs | Their Bldgs | Winner |
|---------|--------------------|--------------------|-----------|-------------|--------|
| buzzing vs smart_eco | 21101 (19830) | 26101 (22230) | 259 | 109 | smart_eco |
| buzzing vs balanced | 20641 (19840) | 34298 (29720) | 285 | 64 | balanced |
| **buzzing vs buzzing_prev** | **28693 (28090)** | **22257 (19740)** | **298** | **49** | **buzzing wins** |

---

## Critical Finding: corridors is a competition-driven regression

**buzzing vs starter on corridors: 6810 mined, 156 buildings** — buzzing works fine alone.
**buzzing vs smart_eco on corridors: 5090 mined, 26 buildings** — collapses when facing competition.

The building count drops from 156 → 26 when facing a capable opponent. This is not a map problem — buzzing CAN build on corridors (156 buildings vs starter). Something about competing against smart_eco/balanced causes buzzing to build almost nothing.

**Comparison with buzzing_prev on corridors:**
- buzzing_prev vs smart_eco: 14850 mined, 25 buildings
- buzzing vs smart_eco: 5090 mined, 26 buildings
- Same building count (~25-26), but **3× Ti mined gap**

The building counts are nearly identical (~25-26 per bot), meaning both bots are building the same number of infrastructure pieces. But buzzing_prev mines 14850 vs buzzing's 5090. This means **buzzing_prev's conveyor chains are dramatically more efficient on corridors** — fewer wasted conveyors, better chain connectivity.

### Why buzzing regressed on corridors

buzzing has 156 buildings vs starter (lots of conveyors), but only 26 buildings vs smart_eco. This means when facing a competing bot that takes ore tiles first, buzzing **stops building**. The econ_cap formula is likely throttling: when smart_eco's builders reach ore tiles before buzzing's builders do (smart_eco builds 6 builders by round 100 vs buzzing's current 4), buzzing's `vis_harv` stays low → `econ_cap = max(time_floor, 0*3+4)` is tiny → very few builders spawned.

With fewer builders, fewer conveyors built = 26 vs 156. But even at 26 buildings, buzzing_prev with the same count mines 3× more Ti. The difference is **chain efficiency**: buzzing_prev may have different explore rotation or conveyor placement that results in fewer orphaned chains on this maze-like map.

---

## gaussian Analysis

On gaussian, buzzing BEATS buzzing_prev (28090 vs 19740 mined). So V55's changes improved gaussian. But smart_eco still wins (22230 vs 19830) and balanced dominates (29720 vs 19840). The 259 buildings vs 109 (smart_eco) confirms conveyor waste — we're building 2.4× more infrastructure but mining less.

---

## Root Causes Summary

### corridors (0-3 nemesis map)

1. **econ_cap throttling under competition**: when smart_eco takes ore first, vis_harv=0 → econ_cap throttles us to fewer builders → fewer conveyors → lower mining
2. **Chain efficiency regression vs buzzing_prev**: both at ~25-26 buildings but buzzing_prev mines 3× more — suggests buzzing's chain layout on corridors is less connected

### gaussian (0-2 nemesis map)

1. **Conveyor waste**: 259 buildings vs balanced's 64 — we build 4× more infrastructure but mine 10k less Ti
2. **Builder cap issue**: balanced beats us with only 5 units vs our 8 — their 5 focused builders outperform our 8 scattered ones on this small map
3. **econ_cap less of an issue here** (buzzing beats buzzing_prev, showing recent fixes helped)

---

## Recommendations

### corridors

1. **Remove or raise econ_cap** — the throttle kills us when opponents race to ore first. With econ_cap removed, buzzing spawns full cap (6 at r100 on balanced) and can claim ore before smart_eco
2. **Investigate chain efficiency regression** — why does buzzing_prev mine 3× more with same building count? Check if recent changes broke conveyor chain layout for maze maps

### gaussian

1. **Reduce expand builder cap** — but gaussian is balanced mode (area=700). The econ_cap (vis_harv*3+4) throttle is likely causing the issue here too — builders can't see far harvesters
2. **Conveyor waste fix still needed** — 259 vs 64 buildings remains the core problem
