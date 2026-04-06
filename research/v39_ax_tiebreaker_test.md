# v39 Ax Tiebreaker Test Results

**Date:** 2026-04-06
**Version:** v39 (late-game Ax tiebreaker)
**Feature:** One builder (id%6==2) attempts to build Ax harvester + foundry at round 1800+ for TB#1 insurance.

---

## Test 1: Regression — buzzing v39 vs buzzing_prev (v37) on default_medium1

| Metric | v39 (buzzing) | v37 (buzzing_prev) |
|--------|---------------|-------------------|
| Winner | **buzzing** (Resources tiebreak) | |
| Ti mined | 4950 | 4950 |
| Ti stored | 4419 | 6542 |
| Ax mined | 0 | 0 |
| Units | 10 | 10 |
| Buildings | 343 | 179 |

**Result: No regression.** v39 wins on Ti tiebreak. Equal Ti mining, different spending patterns.

---

## Test 2: buzzing v39 vs starter on arena (Ax ore at distance 3)

| Metric | v39 (buzzing) | starter |
|--------|---------------|---------|
| Winner | **buzzing** (Resources tiebreak) | |
| Ti mined | 9880 | 0 |
| Ti stored | 13010 | 4318 |
| Ax mined | 0 | 0 |
| Units | 13 | 3 |
| Buildings | 205 | 363 |

**Result: Win, but 0 Ax mined.** The foundry was built adjacent to the Ax harvester, but could not produce refined Ax because it never received Ti input. On arena, the Ax ore is only 3 tiles from core, and the foundry ends up surrounded by core tiles, barriers, and enemy buildings with no room for a Ti feeder conveyor.

---

## Analysis

### What works
- Builder correctly identifies Ax ore and existing Ax harvesters
- Foundry is built adjacent to Ax harvester on packed maps
- No regression on economy or win rate
- Foundry-exists guard prevents multiple foundries
- Smart placement (prefers positions near existing conveyors)

### What doesn't work yet
The foundry needs BOTH Ti AND raw Ax stacks to produce refined Ax. The current implementation:
1. Places foundry adjacent to Ax harvester (gets raw Ax input)
2. Builds output conveyor toward core (step 4)
3. Does NOT solve Ti input routing

The Ti problem is fundamental:
- On arena (Ax dist=3), the foundry is right against the core's 3x3 footprint. All adjacent tiles are core, barriers, or enemy buildings. No room for Ti feeder.
- On default_medium1 (Ax dist=8), the Ax ore is further from core but separate from Ti chains. Ti conveyors don't pass through the Ax area.
- The foundry "accepts from any side" but only if a conveyor/harvester actually feeds into it from that side.

### Root cause
Conveyor chains in the current bot are strictly per-harvester: each harvester has its own chain to core. Ti and Ax chains don't merge or intersect. Placing a foundry inline on the Ax chain gives it raw Ax but no Ti. Placing it inline on a Ti chain gives it Ti but no Ax.

### What would be needed
To actually produce refined Ax, the foundry needs a Ti feeder spur:
1. Find a Ti conveyor chain passing within 2-3 tiles of the Ax harvester
2. Build a short conveyor spur from the Ti chain INTO the foundry
3. This requires empty tiles between the Ti and Ax chains

This is viable on larger/sparser maps but fails on packed maps like arena where all space near core is occupied by round 1800.

### Recommendation
The current implementation is a foundation but needs Ti routing to actually produce Ax. The code is safe (no regression, graceful fallback) but ineffective at its goal. Consider:
1. Starting earlier (round 1500?) when there's more empty space
2. Building the foundry further from core where chains have more room
3. Using bridges to route Ti to the foundry across packed terrain
4. Abandoning the inline approach and building a dedicated Ti+Ax micro-factory on fresh terrain
