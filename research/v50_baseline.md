# V50 Baseline (20 matches)

**Date:** 2026-04-06  
**Bot:** buzzing V50 (tight cap 8→10)  
**Record:** 8W-12L-0D (**40% win rate**)

**Verdict: SEVERE REGRESSION. Do not ship. Revert immediately.**

Progression: v47=58% → v49=65% → v48=50% → **v50=40%**

The tight-cap raise from 8→10 caused the worst result in recorded history. Spawning 2 extra builder bots on tight maps is actively harmful — it increases cost scaling faster than it yields harvester output, pricing out the infrastructure we need to mine.

---

## Per-Opponent Breakdown

| Opponent | W | L | Win% | V49 Win% | Delta |
|----------|---|---|------|----------|-------|
| barrier_wall | 3 | 0 | **100%** | 100% | 0% |
| fast_expand | 1 | 0 | 100% | — | — |
| smart_defense | 1 | 0 | 100% | 25% | +75% |
| turtle | 1 | 2 | 33% | — | — |
| smart_eco | 1 | 2 | 33% | 100% | **-67%** |
| balanced | 1 | 3 | 25% | 75% | **-50%** |
| ladder_rush | 0 | 2 | 0% | 0% | 0% |
| sentinel_spam | 0 | 1 | 0% | — | — |
| adaptive | 0 | 1 | 0% | — | — |
| ladder_eco | 0 | 1 | 0% | — | — |

**Biggest collapses:** smart_eco (100%→33%), balanced (75%→25%). These were reliable wins in V49 — losing them signals a systemic regression, not bad matchup draws.

---

## Per-Map-Type Breakdown

| Type | W | L | Win% | V49 Win% | Notes |
|------|---|---|------|----------|-------|
| Expand | 3 | 1 | 75% | 83% | Slight drop — galaxy W, shish_kebab L |
| Balanced | 4 | 6 | 40% | 33% | Mixed — corridors 1W-2L, gaussian 0W-2L |
| Tight | 1 | 5 | 17% | 40% | Collapse — face L, small1 L, arena L, shish_kebab L |

Tight maps went from 40% → 17% despite the cap being raised to help tight maps. The extra builders are making things worse, not better.

**gaussian: 0W-2L** (two different opponents). Still losing.

---

## Root Cause: Cost Scaling Spiral

Raising tight cap from 8→10 means we spawn 2 extra builder bots (+20% scale each = +40% cumulative scale increase). On tight maps with limited ore:

- Each extra builder costs 30 Ti base × higher scale
- Each building they place costs more due to inflated scale  
- Harvesters at inflated scale cost 20 Ti × scale — if scale is 1.4 instead of 1.2, each harvester costs 4 Ti more
- Conveyors cost 3 Ti × scale — more conveyors needed per harvester × higher cost per conveyor
- Net effect: the extra builders consume more Ti in scaling costs than they generate in harvest throughput

This is the same dynamic that makes foundries (100% scale) so dangerous — builder bots (+20% each) are the second most expensive scale item. 2 extra builders is a substantial cost scaling hit on a tight map with limited ore to recoup it.

---

## Key Observations

1. **The tight cap was not the bottleneck.** V49's 8-unit tight cap was sufficient. The bottleneck is builder pathing and ore targeting, not builder count.
2. **gaussian still 0W-2L** — unrelated to the cap change, confirms the sparse-ore/conveyor-chain problem persists.
3. **corridors 1W-2L** — was a win in V49. corridors is balanced, not tight, suggesting the regression extends beyond just tight maps. The cost scaling from extra tight-map builders may be poisoning the global scale for all map types.

---

## Recommendation

**Revert tight cap to 8 (V49 levels) immediately.** The problem identified in the weak matchup analysis was builder *pathing*, not builder *count*. Raising the cap addresses the wrong variable.

The real fixes needed:
1. Fix first-builder routing on face (510 Ti mined was a pathing failure, not a capacity failure)
2. Early harvester floor — ensure 2 harvesters placed by round 80 regardless of map mode
3. Cost scaling awareness — refuse to spawn builders when scale > 1.5 on tight maps

---

## Raw Results

| # | Opponent | Map | Seed | Result |
|---|----------|-----|------|--------|
| 1 | smart_defense | butterfly | 7963 | WIN |
| 2 | sentinel_spam | gaussian | 2556 | LOSS |
| 3 | balanced | pixel_forest | 6301 | WIN |
| 4 | barrier_wall | corridors | 2058 | WIN |
| 5 | ladder_rush | default_small1 | 9279 | LOSS |
| 6 | fast_expand | cold | 8989 | WIN |
| 7 | balanced | corridors | 7080 | LOSS |
| 8 | smart_eco | cold | 9260 | LOSS |
| 9 | turtle | galaxy | 403 | WIN |
| 10 | barrier_wall | settlement | 7327 | WIN |
| 11 | balanced | gaussian | 1842 | LOSS |
| 12 | smart_eco | face | 6350 | LOSS |
| 13 | smart_eco | dna | 3431 | WIN |
| 14 | barrier_wall | settlement | 2331 | WIN |
| 15 | turtle | butterfly | 6758 | LOSS |
| 16 | adaptive | corridors | 3667 | LOSS |
| 17 | balanced | mandelbrot | 1573 | LOSS |
| 18 | ladder_rush | arena | 6960 | LOSS |
| 19 | ladder_eco | binary_tree | 6429 | LOSS |
| 20 | turtle | shish_kebab | 5457 | LOSS |
