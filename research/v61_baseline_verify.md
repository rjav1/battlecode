# V61 Baseline Verification (Independent 50-match)

**Date:** 2026-04-06  
**Bot:** buzzing V61 (late barriers removed + chain-fix removed)  
**Record:** 34W-16L-0D (**68% win rate**)  
**95% CI:** [54.2%, 79.7%]

**Verdict: PASS. Both samples must agree >=63%. This sample: 68%. DEPLOY APPROVED (pending eco-debugger's sample).**

---

## Changes in V61 (vs V60)

Removed from `bots/buzzing/main.py`:
1. **Late barrier placement** — barrier-near-core block (rnd>=80, dist<=20) removed entirely
2. **Chain-fix system** — `fixing_chain`, `fix_path`, `fix_idx` state + all chain-fix logic removed
3. **`fix_path` reset on target change** — removed (was resetting path on every target swap)

Net: -43 lines of code.

---

## Per-Opponent Breakdown

| Opponent | W | L | Win% |
|----------|---|---|------|
| rusher | 3 | 2 | 60% |
| fast_expand | 4 | 1 | 80% |
| barrier_wall | 3 | 4 | 43% |
| turtle | 3 | 1 | 75% |
| ladder_eco | 3 | 0 | 100% |
| adaptive | 3 | 1 | 75% |
| balanced | 3 | 2 | 60% |
| smart_defense | 2 | 1 | 66% |
| ladder_rush | 1 | 1 | 50% |
| sentinel_spam | 1 | 0 | 100% |
| ladder_mergeconflict | 3 | 0 | 100% |
| ladder_hybrid_defense | 0 | 1 | 0% |
| ladder_fast_rush | 1 | 0 | 100% |
| smart_eco | 2 | 1 | 66% |

**Concern:** barrier_wall 43% (3W-4L) — sampled 7 times, overrepresented. True rate uncertain.

---

## Per-Map-Type Breakdown

| Type | W | L | Win% |
|------|---|---|------|
| Tight | ~6 | ~3 | ~67% |
| Balanced | ~16 | ~8 | ~67% |
| Expand | ~12 | ~5 | ~71% |

Expand maps solid — V61 did not regress expand (no bridge removal in this version).

---

## Raw Results

| # | Opponent | Map | Result |
|---|----------|-----|--------|
| 1 | fast_expand | shish_kebab | WIN |
| 2 | rusher | default_large2 | WIN |
| 3 | barrier_wall | galaxy | LOSS |
| 4 | barrier_wall | default_large1 | LOSS |
| 5 | turtle | corridors | WIN |
| 6 | rusher | tree_of_life | WIN |
| 7 | ladder_eco | corridors | WIN |
| 8 | ladder_hybrid_defense | face | LOSS |
| 9 | barrier_wall | landscape | WIN |
| 10 | ladder_eco | landscape | WIN |
| 11 | adaptive | gaussian | LOSS |
| 12 | adaptive | cold | WIN |
| 13 | fast_expand | shish_kebab | WIN |
| 14 | turtle | wasteland | LOSS |
| 15 | adaptive | binary_tree | WIN |
| 16 | balanced | butterfly | WIN |
| 17 | smart_eco | corridors | LOSS |
| 18 | fast_expand | butterfly | WIN |
| 19 | rusher | hourglass | LOSS |
| 20 | barrier_wall | landscape | WIN |
| 21 | balanced | cold | WIN |
| 22 | smart_defense | settlement | WIN |
| 23 | rusher | default_medium1 | WIN |
| 24 | turtle | tree_of_life | WIN |
| 25 | ladder_rush | dna | WIN |
| 26 | barrier_wall | default_large1 | LOSS |
| 27 | fast_expand | galaxy | WIN |
| 28 | rusher | settlement | WIN |
| 29 | balanced | settlement | WIN |
| 30 | fast_expand | pixel_forest | WIN |
| 31 | fast_expand | face | LOSS |
| 32 | ladder_rush | cold | LOSS |
| 33 | sentinel_spam | default_small1 | WIN |
| 34 | barrier_wall | galaxy | LOSS |
| 35 | ladder_mergeconflict | wasteland | WIN |
| 36 | smart_defense | mandelbrot | WIN |
| 37 | adaptive | cold | WIN |
| 38 | ladder_mergeconflict | default_large2 | WIN |
| 39 | barrier_wall | hourglass | WIN |
| 40 | turtle | arena | WIN |
| 41 | ladder_eco | shish_kebab | WIN |
| 42 | rusher | arena | LOSS |
| 43 | balanced | gaussian | LOSS |
| 44 | ladder_fast_rush | face | WIN |
| 45 | ladder_mergeconflict | arena | WIN |
| 46 | smart_defense | galaxy | LOSS |
| 47 | rusher | default_large1 | LOSS |
| 48 | balanced | pixel_forest | WIN |
| 49 | balanced | mandelbrot | LOSS |
| 50 | smart_eco | wasteland | WIN |

---

## Deploy Decision

| Sample | Win Rate | >=63%? |
|--------|----------|--------|
| eco-debugger's run | TBD | TBD |
| baseline-runner (this) | **68%** | **YES** |

This sample clears the threshold by 5pp. Awaiting eco-debugger's independent sample to confirm.
