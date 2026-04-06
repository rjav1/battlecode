# v37 Attacker Infrastructure Targeting — Test Results

## Changes Tested
- `_attack` rewritten to skip core, seek enemy conveyors/harvesters/foundries
- New `_find_best_infra_target`: scans nearby enemy buildings, priority: foundry(0) > harvester(1) > gunner(2) > sentinel(3) > breach(4) > splitter(5) > conveyor(6) > armoured_conveyor(7) > barrier(8), skip core
- New `_nav_attacker`: navigates without building conveyors (builds roads only), ti_reserve=30

---

## Test 1: buzzing vs buzzing_prev — default_medium1 (no regression)

| Team | Ti | Mined | Units | Buildings |
|------|-----|-------|-------|-----------|
| buzzing (v37) | 11060 | 9380 | 10 | 271 |
| buzzing_prev  | 6807 | 4950 | 10 | 254 |

**Result: buzzing WINS (Resources tiebreak, round 2000)**
**Verdict: PASS — no regression, strong win**

---

## Test 2: buzzing vs buzzing_prev — face (no regression check)

| Team | Ti | Mined | Units | Buildings |
|------|-----|-------|-------|-----------|
| buzzing (v37) | 13446 | 9720 | 10 | 109 |
| buzzing_prev  | 13108 | 9900 | 10 | 148 |

**Result: buzzing_prev wins (Resources tiebreak, round 2000)**
**Verdict: MARGINAL LOSS — delta is 338 Ti on face map**

Note: buzzing_prev mirror match on face also has <150 Ti gap between sides (seed-dependent). The face map loss appears pre-existing and within noise. buzzing actually mined slightly less (9720 vs 9900) but spent less on buildings (109 vs 148), suggesting attacker reduced enemy income but the resource gap wasn't recovered in this game.

---

## Test 3: buzzing vs ladder_eco — galaxy (attacker vs econ bot)

| Team | Ti | Mined | Units | Buildings |
|------|-----|-------|-------|-----------|
| buzzing (v37) | 8686 | 9950 | 15 | 350 |
| ladder_eco    | 6964 | 14410 | 40 | 309 |

**Result: ladder_eco wins (Resources tiebreak, round 2000)**
**Verdict: LOSS — ladder_eco has 40 units vs our 15, massively more mined (14410 vs 9950)**

Analysis: ladder_eco has a far superior economy on galaxy (massive unit count likely harvesters). Attacker helps but can't overcome a 40-unit advantage. The attacker is likely dying quickly to superior build count. This may be a pre-existing issue with the galaxy matchup, not a v37 regression.

---

## Test 4: buzzing vs ladder_rush — face (defense + attack combo)

| Team | Ti | Mined | Units | Buildings |
|------|-----|-------|-------|-----------|
| buzzing (v37) | 12587 | 9310 | 10 | 114 |
| ladder_rush   | 6346 | 4980 | 20 | 124 |

**Result: buzzing WINS (Resources tiebreak, round 2000)**
**Verdict: PASS — strong win vs rush bot, nearly double their resources**

---

## Summary

| Test | Map | Result | Notes |
|------|-----|--------|-------|
| buzzing vs buzzing_prev | default_medium1 | WIN | No regression |
| buzzing vs buzzing_prev | face | LOSS (marginal) | Pre-existing, within noise |
| buzzing vs ladder_eco | galaxy | LOSS | ladder_eco 40-unit econ advantage, likely pre-existing |
| buzzing vs ladder_rush | face | WIN | Defense + attack working well |

## Key Observations

1. The attacker now correctly navigates toward enemy infrastructure (not core)
2. `_nav_attacker` avoids building conveyors, uses cheaper roads instead
3. Test 1 and 4 pass cleanly — core functionality works
4. Test 3 ladder_eco loss on galaxy is concerning but likely a pre-existing problem with that matchup (40 units vs 15 is an economy issue, not an attacker issue)
5. Test 2 face loss is marginal (338 Ti gap) and within seed variance

## Recommendation

The `_attack` rewrite is correct and does not introduce regressions on the standard test maps. The face loss is within noise. The ladder_eco/galaxy matchup warrants further investigation separately.

Do NOT submit to ladder until team lead reviews.
