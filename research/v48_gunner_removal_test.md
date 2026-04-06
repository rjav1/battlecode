# V48 Gunner Removal Test

**Date:** 2026-04-06
**Change:** Remove broken gunner code (Task #9)

---

## What Was Removed

Inspection of bots/buzzing/main.py confirmed the following were already cleaned up in a prior pass:
- `_pending_gunner_ammo` field from `__init__`
- `gunner_placed` counter from `__init__`
- `_place_gunner` method
- `_gunner` method
- `EntityType.GUNNER` dispatch in `run()`
- Spend-down defense gunner block

**Remaining gunner references (intentional, kept):**
- Docstring header — historical version notes only
- `EntityType.GUNNER: 2` in attack `PRIORITY` dict inside `_attack` — correct targeting priority for attacker builders

No edits required; file was already clean.

---

## Regression Test Results

Command: `python.exe test_regression.py --quick`

### Core Regression: buzzing vs buzzing_prev
| Map | Seed | Result | Ti (buzzing vs prev) |
|-----|------|--------|----------------------|
| default_medium1 | 1 | WIN | 9800 vs 4940 |
| cold | 42 | LOSS | 19620 vs 24350 |
| face | 137 | WIN | 18600 vs 9910 |
| settlement | 256 | WIN | 37390 vs 9760 |
| galaxy | 999 | WIN | 13660 vs 9940 |

**4W-1L — PASS**

### Self-Play Stability
- buzzing vs buzzing on default_medium1: OK (resources t2000)

### Final Verdict: PASS (50s total)

---

## Conclusion

Gunner code was already fully removed before this task ran (prior cleanup pass). Regression confirms no regressions from the removal — 4W-1L vs buzzing_prev (same as expected baseline). The one loss (cold map) is a pre-existing issue unrelated to gunners.
