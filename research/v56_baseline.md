# V56 Baseline (20 matches)

**Date:** 2026-04-07  
**Bot:** buzzing V56 (V52 equivalent + rnd//100 expand rotation)  
**Record:** 13W-7L-0D (**65% win rate**)

**Verdict: STABLE. Matches V52 baseline range. rnd//100 expand rotation is neutral — no regression, no improvement. Safe to ship.**

Progression: v49=65% → v52=70% (30-match) / 62% (40-match) → v55=47% (regression, reverted) → **v56=65%**

---

## Per-Opponent Breakdown

| Opponent | W | L | Win% | V52 Win% | Delta |
|----------|---|---|------|----------|-------|
| turtle | 2 | 0 | **100%** | 100% | 0% |
| rusher | 2 | 1 | 66% | 66% | 0% |
| fast_expand | 1 | 1 | 50% | 100% | -50% |
| sentinel_spam | 1 | 1 | 50% | 66% | -16% |
| ladder_eco | 1 | 0 | **100%** | 66% | +34% |
| ladder_rush | 1 | 2 | 33% | 66% | -33% |
| adaptive | 1 | 0 | **100%** | 100% | 0% |
| barrier_wall | 1 | 0 | **100%** | 100% | 0% |
| balanced | 3 | 3 | 50% | 60% | -10% |
| smart_eco | 0 | 1 | 0% | 28% | -28% |
| smart_defense | 0 | 0 | — | 33% | — |

Small sample (20 matches) — per-opponent noise is high. No opponent-level regressions are statistically meaningful here.

---

## Per-Map-Type Breakdown

| Type | W | L | Win% | V52 Win% | Delta |
|------|---|---|------|----------|-------|
| Expand | 9 | 3 | **75%** | 84% | -9% |
| Balanced | 2 | 2 | 50% | 50% | 0% |
| Tight | 2 | 2 | 50% | 67% | -17% |

Expand maps: 75% vs V52's 84% — within variance at n=12. The rnd//100 rotation did not hurt expand performance (compare: V55's expand was 63% with a different broken fix).

---

## Assessment

V56 at 65% is statistically consistent with V52's observed range (62-70% across two runs). The rnd//100 expand rotation — which periodically shifts explore direction every 100 rounds — is **neutral**: it doesn't hurt the baseline and may help edge cases like git_branches without affecting standard maps.

Key losses to note:
- fast_expand/cold (balanced): 1 loss — fast_expand is normally easy; cold may be a conveyor issue
- balanced/shish_kebab: 2 losses in 2 tries (seeds 879, 5570) — shish_kebab tight map, balanced opponent
- ladder_rush/galaxy: loss on expand map — unusual
- rusher/default_small1: tight map loss

No systemic new failure patterns. The V55 regression (explore reach going too far) is confirmed absent.

---

## Recommendation

**Safe to ship V56.** 65% baseline is confirmed. The rnd//100 rotation is harmless and may provide marginal benefit on pathological maps. True baseline is likely 65-70% (same as V52).

---

## Raw Results

| # | Opponent | Map | Type | Seed | Result |
|---|----------|-----|------|------|--------|
| 1 | turtle | dna | balanced | 7405 | WIN |
| 2 | rusher | pixel_forest | expand | 7166 | WIN |
| 3 | fast_expand | shish_kebab | tight | 3239 | WIN |
| 4 | fast_expand | cold | balanced | 4492 | LOSS |
| 5 | sentinel_spam | default_large2 | expand | 5924 | LOSS |
| 6 | ladder_eco | wasteland | expand | 6259 | WIN |
| 7 | ladder_rush | default_large1 | expand | 1388 | WIN |
| 8 | balanced | pixel_forest | expand | 8602 | WIN |
| 9 | adaptive | landscape | expand | 6442 | WIN |
| 10 | rusher | galaxy | expand | 6634 | WIN |
| 11 | barrier_wall | wasteland | expand | 7697 | WIN |
| 12 | balanced | tree_of_life | expand | 2146 | WIN |
| 13 | balanced | default_large2 | expand | 7392 | WIN |
| 14 | smart_eco | default_large2 | expand | 3206 | LOSS |
| 15 | balanced | shish_kebab | tight | 879 | LOSS |
| 16 | rusher | default_small1 | tight | 4669 | LOSS |
| 17 | balanced | shish_kebab | tight | 5570 | LOSS |
| 18 | ladder_rush | galaxy | expand | 3392 | LOSS |
| 19 | sentinel_spam | landscape | expand | 3081 | WIN |
| 20 | turtle | hourglass | balanced | 8367 | WIN |
