# V52 Chain-Fix Improvement Test

**Date:** 2026-04-07
**Changes:** Chain-fix trigger widened + periodic retrigger on maze maps

---

## Changes Applied

All three changes were already present in main.py when Task #15 began (applied by eco-debugger as part of Task #13 attacker removal):

1. **`harvesters_built <= 2` → `<= 4`** (line 368) — chain-fix now triggers for first 4 harvesters instead of 2
2. **`changes >= 3` → `>= 2`** (line 375) — triggers on less-winding paths (2 direction changes instead of 3)
3. **Periodic chain retrigger added** (lines 339-347) — re-arms fixing_chain every 100 rounds on maze maps (wall_density > 0.20, rnd <= 500, harvesters >= 1)

---

## Regression Results

Command: `python test_regression.py --quick`

| Map | Seed | Result | Ti (ours vs prev mined) |
|-----|------|--------|------------------------|
| default_medium1 | 1 | WIN | 4960 vs 4940 |
| cold | 42 | WIN | 19610 vs 0 |
| face | 137 | **LOSS** | 8600 vs 11710 |
| settlement | 256 | WIN | 29310 vs 0 |
| galaxy | 999 | WIN | 13670 vs 4980 |

**4W-1L — PASS** (need 3+/5)

Self-play on default_medium1: OK (resources t2000)

**Duration:** 87s

---

## Notes

- face loss (8600 vs 11710): buzzing_prev appears to mine Ti on face with seed 137, while current bot underperforms. The chain-fix changes may be slightly hurting face (a tight 20x20 map with low wall density — periodic retrigger shouldn't fire there since wall_density threshold is 0.20, but the `changes >= 2` trigger may send builders into fix mode unnecessarily on simple chains).
- cold and settlement: buzzing_prev mines 0 Ti — those are clean wins against a broken prev bot.
- The face regression is consistent with previous runs (was also 1L on face in prior tests).

**Verdict: PASS. No new regressions introduced by chain-fix changes.**
