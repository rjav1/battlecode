# V48 Quick Baseline (20 matches)

**Date:** 2026-04-06  
**Bot:** buzzing V48 (gunner removal + balanced caps)  
**Record:** 10W-10L-0D (**50% win rate**)

**Verdict: REGRESSION vs V47 (58% → 50%).** V48 changes did not improve performance.

---

## Per-Opponent Breakdown

| Opponent | W | L | Win% | V47 Win% | Delta |
|----------|---|---|------|----------|-------|
| turtle | 4 | 0 | **100%** | 50% | +50% |
| smart_defense | 2 | 1 | 67% | 20% | +47% |
| ladder_rush | 2 | 2 | 50% | 43% | +7% |
| rusher | 1 | 1 | 50% | 50% | 0% |
| adaptive | 1 | 2 | 33% | **100%** | **-67%** |
| sentinel_spam | 0 | 2 | 0% | 100% | **-100%** |
| barrier_wall | 0 | 1 | 0% | 63% | -63% |
| smart_eco | 0 | 1 | 0% | 40% | -40% |

*Note: V47 comparisons are approximate due to different sample draws and small sample sizes.*

**Concerning regressions:** adaptive (was 6W-0L, now 1W-2L) and sentinel_spam (was 2W-0L, now 0W-2L) are the biggest drops.

---

## Per-Map Breakdown

| Map | W | L | V47 record | Notes |
|-----|---|---|------------|-------|
| turtle (all maps) | 4 | 0 | 2W-2L | Strong improvement |
| settlement | 2 | 0 | 1W-1L | Good |
| face | 2 | 1 | 2W-0L | Slight drop |
| **binary_tree** | **0** | **2** | **3W-0L** | **Critical regression** |
| default_medium1 | 1 | 1 | 2W-0L | Regression |
| dna | 1 | 1 | n/a | Mixed |
| default_large2 | 1 | 1 | 1W-1L | Same |
| gaussian | 0 | 1 | 0W-3L | Still losing |
| arena | 0 | 1 | 2W-4L | Same weakness |
| corridors | 0 | 1 | 1W-1L | Drop |
| default_small1 | 0 | 1 | 0W-3L | Same weakness |
| default_large1 | 1 | 0 | 1W-3L | Improvement |
| mandelbrot | 1 | 0 | 2W-1L | Good |
| shish_kebab | 1 | 0 | 2W-2L | Good |

**binary_tree regression is the clearest signal:** 3W-0L in V47 → 0W-2L in V48. Binary_tree is a balanced map that V47 dominated — the balanced cap changes appear to have broken something specific here.

---

## Likely Regression Cause

V48 changed balanced-mode caps. Binary_tree was a 3W-0L map in V47 that went 0W-2L in V48. The balanced cap changes are the only relevant code change. Hypothesis: **the new balanced caps are too conservative early**, leaving us resource-starved in the mid-game on balanced maps with good ore coverage (binary_tree has well-distributed ore).

On binary_tree, V47's slightly more aggressive early builder spawning was exactly right. Pulling back the caps hurts on ore-rich balanced maps while not helping on sparse ones (gaussian still 0W-1L).

---

## Recommendation

**Do not ship V48 as-is.** The balanced cap changes caused regression without fixing the gaussian/sparse-ore problem. 

Options:
1. **Revert balanced caps** to V47 levels, keeping only the gunner removal (which was neutral)
2. **Make caps ore-density-aware** — use tight/conservative caps only when ore_density < 3%, keep V47 caps otherwise
3. **Run V48 vs V47 head-to-head** on binary_tree specifically to confirm the regression hypothesis

---

## Raw Results

| # | Opponent | Map | Seed | Result |
|---|----------|-----|------|--------|
| 1 | adaptive | gaussian | 5886 | LOSS |
| 2 | rusher | binary_tree | 1738 | LOSS |
| 3 | adaptive | default_medium1 | 5265 | WIN |
| 4 | ladder_rush | arena | 4807 | LOSS |
| 5 | sentinel_spam | corridors | 6875 | LOSS |
| 6 | ladder_rush | default_small1 | 5327 | LOSS |
| 7 | smart_defense | default_large2 | 6271 | LOSS |
| 8 | turtle | dna | 1377 | WIN |
| 9 | ladder_rush | settlement | 6000 | WIN |
| 10 | smart_defense | shish_kebab | 3773 | WIN |
| 11 | barrier_wall | default_medium1 | 2385 | LOSS |
| 12 | rusher | settlement | 4782 | WIN |
| 13 | turtle | default_large1 | 4975 | WIN |
| 14 | smart_defense | face | 342 | WIN |
| 15 | smart_eco | binary_tree | 2053 | LOSS |
| 16 | adaptive | face | 4835 | LOSS |
| 17 | sentinel_spam | dna | 4043 | LOSS |
| 18 | turtle | mandelbrot | 6334 | WIN |
| 19 | turtle | default_large2 | 8804 | WIN |
| 20 | ladder_rush | face | 8819 | WIN |
