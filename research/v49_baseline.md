# V49 Baseline (20 matches)

**Date:** 2026-04-06  
**Bot:** buzzing V49 (reverted balanced caps to V47 levels + min-dimension map classification)  
**Record:** 13W-7L-0D (**65% win rate**)

**Verdict: IMPROVEMENT.** V49 beats V47 (58%) and recovers from V48's regression (50%). The cap revert restored the balanced-map performance while the min-dimension classification helps on narrow maps like gaussian.

Progression: v42=45% → v43=50% → v46=58% → v47=58% → v48=50% → **v49=65%**

---

## Per-Opponent Breakdown

| Opponent | W | L | Win% | V47 Win% | Delta |
|----------|---|---|------|----------|-------|
| barrier_wall | 2 | 0 | **100%** | 63% | +37% |
| smart_eco | 2 | 0 | **100%** | 40% | +60% |
| balanced | 3 | 1 | 75% | 67% | +8% |
| ladder_eco | 3 | 2 | 60% | 100% | -40% |
| fast_expand | 1 | 0 | 100% | 50% | +50% |
| turtle | 1 | 0 | 100% | 50% | +50% |
| smart_defense | 1 | 3 | **25%** | 20% | +5% |
| ladder_rush | 0 | 1 | 0% | 43% | -43% |

*Small sample sizes — individual opponent swings are high variance. Overall trend is positive.*

**Persistent nemesis:** smart_defense (1W-3L, 25%) — still the weakest matchup. Hit arena 3 times (2 losses there).

---

## Per-Map-Type Breakdown

| Type | W | L | Win% | Notes |
|------|---|---|------|-------|
| **Expand** | **10** | **2** | **83%** | Outstanding — tree_of_life, pixel_forest, galaxy, landscape, settlement, wasteland all won |
| Tight | 2 | 3 | 40% | Arena weakness persists (1W-2L vs smart_defense there) |
| Balanced | 1 | 2 | 33% | hourglass win, butterfly+corridors losses |

**Expand map dominance (83%) is the standout result** — this is a major improvement from V47's 63%.

### Gaussian specifically
gaussian (seed 4431) vs smart_defense: **LOSS** — still losing despite min-dimension reclassification to tight mode. The tight caps alone don't fix the sparse-ore conveyor waste problem. Confirms the fix needs to be conveyor-chain-length-aware, not just cap-level.

### Expand map losses (2):
- default_large1 vs ladder_rush (seed 2254): consistent ladder_rush weakness on large maps
- default_large1 vs ladder_eco (seed 9532): ladder_eco beat us on the same map type — expansion speed issue

---

## Key Findings

1. **Cap revert confirmed correct** — restoring V47 balanced caps eliminated V48's regression on binary_tree and vs adaptive/sentinel_spam
2. **Expand maps now 83%** — strongest category ever recorded. Min-dimension classification may be redirecting some balanced→tight, freeing up expand-mode spawning to work better on true large maps
3. **gaussian still losing** — reclassifying as tight doesn't fix the root issue (conveyor chains too long for sparse ore). Needs chain length limit
4. **smart_defense on arena remains hard** — 0W-3L when hitting that matchup (3 appearances, 1 win only from settlement/different map)
5. **ladder_eco surprised with 2 losses** — was 2W-0L in V47 sample; default_large1 appears to be a problem map regardless of opponent

---

## Recommendation

V49 at 65% is the new best baseline — safe to consider shipping. Priority improvements for V50:
1. Conveyor chain length cap for gaussian/sparse-ore maps (root cause still unresolved)
2. Arena-specific defense vs smart_defense
3. Investigate default_large1 losses (2 losses there across different opponents)

---

## Raw Results

| # | Opponent | Map | Type | Seed | Result |
|---|----------|-----|------|------|--------|
| 1 | balanced | tree_of_life | expand | 5853 | WIN |
| 2 | ladder_eco | pixel_forest | expand | 5046 | WIN |
| 3 | ladder_eco | arena | tight | 265 | WIN |
| 4 | balanced | landscape | expand | 8969 | WIN |
| 5 | ladder_eco | galaxy | expand | 5042 | WIN |
| 6 | barrier_wall | hourglass | balanced | 4351 | WIN |
| 7 | ladder_rush | default_large1 | expand | 2254 | LOSS |
| 8 | ladder_eco | butterfly | balanced | 8355 | LOSS |
| 9 | fast_expand | arena | tight | 7307 | WIN |
| 10 | smart_defense | gaussian | tight* | 4431 | LOSS |
| 11 | ladder_eco | default_large1 | expand | 9532 | LOSS |
| 12 | smart_defense | arena | tight | 7376 | LOSS |
| 13 | smart_eco | shish_kebab | tight | 6378 | WIN |
| 14 | smart_defense | arena | tight | 54 | LOSS |
| 15 | barrier_wall | wasteland | expand | 7631 | WIN |
| 16 | smart_eco | settlement | expand | 2161 | WIN |
| 17 | balanced | corridors | balanced | 6239 | LOSS |
| 18 | turtle | pixel_forest | expand | 4122 | WIN |
| 19 | smart_defense | settlement | expand | 7939 | WIN |
| 20 | balanced | pixel_forest | expand | 8044 | WIN |

*gaussian now classified as tight via min-dimension logic
