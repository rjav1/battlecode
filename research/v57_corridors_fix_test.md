# V57 Corridors Chain Fix Test

**Date:** 2026-04-06
**Change:** Removed entire `_bridge_target` post-harvester bridge block from `bots/buzzing/main.py`

---

## What Changed

The `_bridge_target` block (lines 275–333 pre-fix) fired after every harvester build, attempting to bridge from an ore-adjacent tile to the "nearest allied conveyor closer to core" (chain-join shortcut) or core itself.

**Root cause of corridors regression:** On maze maps (corridors), the chain-join bridge targets a mid-path conveyor. This breaks the natural d.opposite() delivery chain between harvester and core — resources teleport to a mid-chain conveyor and stall or are rejected (wrong input side). The natural chain between harvester and bridge target is left without upstream input.

**Fix applied:** Removed entire `_bridge_target` block. The natural d.opposite() conveyor chain is already the optimal delivery mechanism.

**Note on team-lead's suggested `dist > 9` guard:** Tested first — did NOT fix corridors (still 5090 mined). All corridors ore is far from core (dist >> 9), so the guard doesn't prevent chain-join bridges from firing. Full removal was necessary.

---

## Test Results

### corridors vs smart_eco (key fix target)

| | buzzing (V57) | smart_eco |
|--|--|--|
| Ti mined | 14520 | 14660 |
| Buildings | 25 | 36 |
| Winner | smart_eco (resources) | — |

corridors: 14520 mined — up from 5090 pre-fix (+185%). Near-parity with smart_eco (14660).

### Core Regression: buzzing vs buzzing_prev (5 maps)

| Map | buzzing mined | buzzing_prev mined | Result |
|-----|--------------|-------------------|--------|
| default_medium1 | 28430 | 4950 | WIN |
| cold | 19670 | 0 | WIN |
| face | 21120 | 4970 | WIN |
| settlement | 37800 | 0 | WIN |
| galaxy | 19020 | 4980 | WIN |

**5/5 WIN vs buzzing_prev** (regression PASS).

### Additional Maps

| Map | buzzing mined | buzzing_prev mined | Result |
|-----|--------------|-------------------|--------|
| corridors | 14520 | 14850 | -2% (near-parity) |
| gaussian | 24800 | 19800 | WIN |

### Self-Play Stability

- buzzing vs buzzing on default_medium1: OK (no crash, 14840 vs 9900 mined, resources tiebreak)

---

## Verdict: PASS

V57 fix is complete and regression-safe. corridors is fixed from 5090 → 14520 mined (+185%).

**Recommend deploy as V57.**
