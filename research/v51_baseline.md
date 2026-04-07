# V51 Baseline (20 matches)

**Date:** 2026-04-06  
**Bot:** buzzing V51  
**Record:** 11W-9L-0D (**55% win rate**)

**Verdict: REGRESSION from V49 (65% → 55%). Do not ship over V49.**

Progression: v47=58% → v49=65% → v50=40% → **v51=55%**

V51 does not restore V49's 65% baseline. Something in V51's changes is hurting performance relative to V49.

---

## Per-Opponent Breakdown

| Opponent | W | L | Win% | V49 Win% | Delta |
|----------|---|---|------|----------|-------|
| balanced | 2 | 0 | **100%** | 75% | +25% |
| sentinel_spam | 1 | 0 | 100% | — | — |
| turtle | 1 | 0 | 100% | — | — |
| adaptive | 1 | 0 | 100% | — | — |
| rusher | 2 | 1 | 67% | — | — |
| ladder_eco | 1 | 1 | 50% | 60% | -10% |
| smart_eco | 1 | 1 | 50% | 100% | **-50%** |
| **fast_expand** | **1** | **3** | **25%** | — | **New weakness** |
| smart_defense | 1 | 3 | 25% | 25% | 0% |

**New weakness: fast_expand (1W-3L, 25%).** This opponent did not feature prominently in V49 testing. Three losses in one run suggests a systemic issue vs fast_expand's strategy. smart_defense remains at 25% — unchanged from V49.

---

## Per-Map-Type Breakdown

| Type | W | L | Win% | V49 Win% | Delta |
|------|---|---|------|----------|-------|
| Expand | 4 | 2 | 67% | **83%** | -16% |
| Balanced | 5 | 3 | 63% | 33% | +30% |
| Tight | 2 | 4 | **33%** | 40% | -7% |

Expand map dominance dropped from 83% (V49) to 67%. Tight maps remain weak. Balanced maps improved slightly.

### Notable map results
- **hourglass**: 0W-2L (both vs fast_expand) — consistent failure on this map
- **face**: 0W-2L — confirmed persistent weakness (smart_defense + fast_expand)
- **gaussian**: 0W-1L — still losing, sparse-ore issue unresolved
- **wasteland**: 1W-1L — was 4W-1L in V47, regression on this map

### Fast_expand on hourglass (2 losses, seeds 2947 and 2073)
Two separate seeds, same map, same opponent — both losses. hourglass is a balanced map with an hourglass shape that likely creates bottlenecks. fast_expand may exploit the narrow center corridor to claim both sides' ore before we can expand past the chokepoint.

---

## Comparison to V49

V49 strengths that appear degraded in V51:
- Expand maps: 83% → 67% (-16pp) — the biggest drop
- smart_eco: 100% → 50% (-50pp) — was a clean sweep, now mixed
- fast_expand: new 25% weakness (not tested in V49 sample)

V51 improvements over V49:
- Balanced maps: 33% → 63% (+30pp) — significant gain
- balanced opponent: 75% → 100%

The expand map regression is concerning — V49's 83% expand performance was its standout strength. V51 loses 2 expand games (default_large1 vs ladder_eco, wasteland vs smart_defense) that V49 likely won.

---

## Recommendation

**Revert to V49 or identify what changed.** The expand map regression from 83% → 67% is the clearest signal. V51's changes appear to have disrupted expand-mode behavior. Key questions:
1. What did V51 change vs V49? (The diff will explain the regression)
2. Why is fast_expand suddenly 1W-3L? fast_expand builds infrastructure fast — if V51 slows our early economy, fast_expand capitalizes.
3. Why is hourglass 0W-2L? V49 won hourglass 2W-0L.

Until these are understood, V49 remains the best stable version at 65%.

---

## Raw Results

| # | Opponent | Map | Type | Seed | Result |
|---|----------|-----|------|------|--------|
| 1 | smart_defense | shish_kebab | tight | 8801 | WIN |
| 2 | ladder_eco | corridors | balanced | 4333 | WIN |
| 3 | smart_eco | cold | balanced | 1422 | WIN |
| 4 | rusher | settlement | expand | 5615 | WIN |
| 5 | smart_eco | gaussian | balanced | 5017 | LOSS |
| 6 | smart_defense | face | tight | 4903 | LOSS |
| 7 | ladder_eco | default_large1 | expand | 6490 | LOSS |
| 8 | rusher | default_small2 | tight | 8583 | LOSS |
| 9 | balanced | butterfly | balanced | 2621 | WIN |
| 10 | sentinel_spam | wasteland | expand | 7242 | WIN |
| 11 | balanced | default_large2 | expand | 8405 | WIN |
| 12 | fast_expand | hourglass | balanced | 2947 | LOSS |
| 13 | smart_defense | arena | tight | 6332 | LOSS |
| 14 | turtle | arena | tight | 5384 | WIN |
| 15 | fast_expand | hourglass | balanced | 2073 | LOSS |
| 16 | fast_expand | binary_tree | balanced | 4667 | WIN |
| 17 | smart_defense | wasteland | expand | 7444 | LOSS |
| 18 | adaptive | pixel_forest | expand | 5466 | WIN |
| 19 | rusher | dna | balanced | 3554 | WIN |
| 20 | fast_expand | face | tight | 5412 | LOSS |
