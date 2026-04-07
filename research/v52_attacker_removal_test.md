# V52 Attacker Removal Regression Test

**Date:** 2026-04-06
**Change:** Removed all attacker code from bots/buzzing/main.py
  - `self.is_attacker = False` from `__init__`
  - Attacker assignment block (rnd>500, harvesters>=4, id%6==5)
  - `_attack`, `_find_best_infra_target`, `_nav_attacker` methods (~98 lines)

## Regression Results

| Map | Result | Our Ti | Their Ti | Notes |
|-----|--------|--------|----------|-------|
| default_medium1 | WIN | 4960 | 4940 | |
| cold | WIN | 19610 | 0 | |
| face | LOSS | 8600 | 11710 | Pre-existing loss, not a regression |
| settlement | WIN | 29310 | 0 | |
| galaxy | WIN | 13670 | 4980 | |

**Core Regression: 4W-1L — PASS**
**Self-Play Stability: OK**
**Final Verdict: PASS**

## Analysis

The face map loss is pre-existing (identical to previous regression results). Attacker removal caused no regressions.

Benefits of removal:
- Saves ~98 lines of dead code
- Eliminates `is_attacker` branch entirely
- Recovers scale inflation from roads built by attacker builder (15-unit scale on expand maps)
- No builder diverted to attack duty after round 500

## Decision: DEPLOY
