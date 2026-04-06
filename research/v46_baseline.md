# V46 Baseline Test Results

**Date:** 2026-04-06
**Bot Version:** V46 (Version 46 on ladder) — Ti ore preference critical bug fix
**Test:** 50-match varied test (test_varied.py --count 50)
**Previous baselines:** 45% (v42), 50% (v43), 66% (v43-comprehensive)

---

## Overall Result

**29W-21L-0D — 58% win rate**

This is an improvement from V43's 50% baseline. Note the 66% v43-comprehensive was likely a favorable sample.

---

## Per-Opponent Breakdown

| Opponent | W | L | Win% | Notes |
|----------|---|---|------|-------|
| smart_eco | 0 | 6 | **0%** | CRITICAL WEAKNESS — 6/6 losses |
| adaptive | 3 | 4 | 43% | Slight negative |
| rusher | 1 | 1 | 50% | Even |
| smart_defense | 3 | 3 | 50% | Even |
| turtle | 1 | 1 | 50% | Even |
| ladder_rush | 3 | 2 | 60% | Slight positive |
| ladder_eco | 4 | 2 | 67% | Positive |
| fast_expand | 6 | 2 | 75% | Strong |
| sentinel_spam | 3 | 0 | **100%** | Dominate |
| barrier_wall | 4 | 0 | **100%** | Dominate |
| balanced | 1 | 0 | 100% | Small sample |

**Key finding: smart_eco is a 0% matchup** — 6 consecutive losses. This is our primary weakness.

---

## Per-Map-Type Breakdown

| Map Type | W | L | Win% | Notes |
|----------|---|---|------|-------|
| BALANCED | 9 | 13 | **41%** | Underperforming |
| TIGHT | 6 | 2 | 75% | Strong |
| EXPAND | 14 | 6 | 70% | Strong |

**Key finding: Balanced maps are our weak point** (41% vs 70-75% on others).

Balanced maps include: default_medium1, cold, corridors, hourglass, butterfly, binary_tree, dna, gaussian, mandelbrot

The smart_eco losses overlap heavily with balanced maps — gaussian (2x loss), wasteland (3x loss), hourglass (1x loss).

---

## Comparison vs Previous Baselines

| Version | Win Rate | Notes |
|---------|----------|-------|
| V42 | 45% | Old baseline |
| V43 | 50% | Pre-Ti-ore-fix |
| V46 | **58%** | Ti ore preference fix |

+8% improvement from Ti ore preference fix — confirms the bug was significant.

---

## Identified Weaknesses

1. **smart_eco: 0W-6L** — This opponent appears to exploit our economy strategy. Needs investigation.
2. **Balanced maps: 41%** — Medium-sized maps (hourglass, gaussian, etc.) are underperforming.
3. **adaptive: 43%** — Slight but notable weakness. Adaptive opponents adapt to our strategy.
4. **Hourglass specifically:** fast_expand beat us 2/2 times on hourglass; adaptive beat us 2x on hourglass.

---

## Recommendations

1. **Investigate smart_eco matchup** — 0% is disqualifying. What does smart_eco do differently?
2. **Balanced map strategy review** — Why are medium maps harder? Possible issue with mid-game transition.
3. **Hourglass map performance** — 4 losses on hourglass suggests a specific map weakness.
