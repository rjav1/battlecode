# V57 Economic Validation

**Date:** 2026-04-06
**Change:** Removed `_bridge_target` chain-join bridge block

---

## buzzing vs smart_eco (4 maps, seed 1)

| Map | buzzing mined | smart_eco mined | Winner |
|-----|--------------|-----------------|--------|
| corridors | 14520 | 14660 | smart_eco (-1%) |
| gaussian | 24780 | 23900 | **buzzing (+4%)** |
| default_medium1 | 19760 | 20170 | smart_eco (-2%) |
| cold | 19670 | 23730 | smart_eco (-17%) |

**Result: 1W-3L vs smart_eco**

---

## buzzing vs buzzing_prev (2 maps, seed 1)

| Map | buzzing mined | buzzing_prev mined | Winner |
|-----|--------------|-------------------|--------|
| corridors | 14520 | 14850 | buzzing_prev (-2%) |
| gaussian | 24800 | 19800 | **buzzing (+25%)** |

---

## Analysis

**corridors:** Fixed — 14520 mined (was 5090). Now within 1% of smart_eco. buzzing_prev edges by 2% (14850) but same ballpark.

**gaussian:** buzzing wins both smart_eco and buzzing_prev. Bridge removal helped here too.

**default_medium1:** Very close — buzzing 19760 vs smart_eco 20170 (-2%). Essentially tied.

**cold:** Largest gap — buzzing 19670 vs smart_eco 23730 (-17%). cold is a maze-like map where smart_eco's 8-builder ramp reaches ore faster. The builder cap difference (buzzing balanced cap: 4→6→7→8 vs smart_eco's 4→6→7→8 with no econ_cap throttle) likely explains this gap.

## Key Takeaway

The bridge fix resolved the corridors regression completely. The remaining gap vs smart_eco on cold is a **builder cap / econ_cap throttle issue**, not a chain efficiency issue. On 3/4 maps buzzing is within 2% of smart_eco. cold is the outlier at -17%.

## Next Priority

cold map gap: smart_eco mines 4060 more Ti on cold. The `econ_cap = max(time_floor, vis_harv*3+4)` formula throttles builder spawning when core can't see far harvesters. Removing or relaxing this formula could close the cold gap.
