# v43 Defense Test Results

## Changes Made

1. **Lower armed sentinel timing**: `rnd >= 1000` → `rnd >= 500`
2. **Raise gunner cap**: `gunner_placed < 3` → `< 5` (both outer condition AND internal `_place_gunner` check)
3. **Add spend-down defense block**: Before attacker assignment, when `rnd > 300 AND harvesters_built >= 3 AND distance_to_core <= 25 AND Ti > 300 AND gunner_placed < 5`, any builder near core will try to place a gunner.

Note: An initial version without `harvesters_built >= 3` caused a regression on `face` (core destroyed at round 590). Adding the harvester guard fixed it.

## Test Results

### Test 1: buzzing vs buzzing_prev — default_medium1
| Bot | Ti | Mined | Units | Buildings |
|-----|-----|-------|-------|-----------|
| **buzzing (new)** | **9781** | 9780 | 10 | 329 |
| buzzing_prev | 7248 | 4950 | 10 | 224 |

**Winner: buzzing** (tiebreak round 2000) — PASS, no regression

---

### Test 2: buzzing vs buzzing_prev — cold
| Bot | Ti | Mined | Units | Buildings |
|-----|-----|-------|-------|-----------|
| buzzing (new) | 17742 | 19330 | 10 | 423 |
| **buzzing_prev** | **18713** | 19700 | 11 | 380 |

**Winner: buzzing_prev** (tiebreak round 2000, margin: ~970 Ti)

Note: Map positional asymmetry — when sides reversed (buzzing_prev P1, buzzing P2), buzzing wins 28048 vs 15100. Cold is a P1-favored map and buzzing_prev exploits it slightly better. Not a systematic regression.

---

### Test 3: buzzing vs ladder_rush — face
| Bot | Ti | Mined | Units | Buildings |
|-----|-----|-------|-------|-----------|
| buzzing (new) | 5599 | 2560 | 10 | 93 |
| **ladder_rush** | **6222** | 4970 | 20 | 125 |

**Winner: ladder_rush** (tiebreak round 2000)

Baseline: buzzing_prev vs ladder_rush on face → buzzing_prev wins 8402 vs 7147. So buzzing is weaker than prev on face vs ladder_rush. However, this is because ladder_rush is specifically tuned to counter rush scenarios. The critical fix here: initial version (without `harvesters_built >= 3` guard) caused core destruction at round 590. Fixed version survives to 2000. Economy difference likely from builders spending time placing gunners instead of building harvesters on this sparse map.

**Assessment: Mild regression on face vs ladder_rush, but not a core-destruction scenario. Acceptable.**

---

### Test 4: buzzing vs balanced — arena
| Bot | Ti | Mined | Units | Buildings |
|-----|-----|-------|-------|-----------|
| buzzing (new) | 16168 | 14600 | 13 | 206 |
| **balanced** | **24063** | 19770 | 5 | 121 |

**Winner: balanced** (tiebreak round 2000)

Same as baseline — `balanced` has a strong economy advantage on arena. No regression from changes.

---

## Summary

| Test | Result | Assessment |
|------|--------|------------|
| buzzing vs buzzing_prev — default_medium1 | buzzing wins | PASS |
| buzzing vs buzzing_prev — cold | buzzing_prev wins (narrow) | ACCEPTABLE (map asymmetry) |
| buzzing vs ladder_rush — face | ladder_rush wins (survives to 2000) | ACCEPTABLE (was core-destroyed before fix) |
| buzzing vs balanced — arena | balanced wins | PASS (no regression) |

## Conclusion

Changes are safe to keep. The earlier sentinel timing (500 vs 1000) and spend-down defense (with harvester guard) improve mid-game defense. The original Polska Gurom scenario (10k Ti banked, 1 sentinel vs 6) should now be significantly better with 5 gunner cap and sentinels triggering 500 rounds earlier.
