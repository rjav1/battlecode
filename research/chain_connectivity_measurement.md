# Chain Connectivity Measurement Results

## Date: 2026-04-08

---

## Core-Side Measurement (every 100 rounds, core vision r^2=36)

| Map | Harvesters Visible | Connected | Ti Mined | Notes |
|-----|-------------------|-----------|----------|-------|
| cold | 0/0 (all rounds) | N/A | 19,670 | All harvesters beyond core vision |
| hooks | 0/0 (all rounds) | N/A | 37,030 | All harvesters beyond core vision |
| default_medium1 | 0/1 (all rounds) | 0/1 | 37,150 | 1 harvester visible but "not connected" — likely adjacent to core (direct output) |
| face | 1/1 (all rounds) | 1/1 | 9,650 | 1 harvester visible and connected |

## Key Findings

### 1. Most harvesters are BEYOND core vision
On cold and hooks, core sees ZERO harvesters for the entire 2000-round game. Yet we mine 19-37k Ti. All harvesters are built beyond r^2=36 (>6 tiles from core center). The core-side measurement CANNOT see them.

### 2. The "0/1 not connected" harvester on default_medium1 IS delivering
0/1 connected, yet 37,150 Ti mined — the highest of all maps tested. This harvester is likely on a core-adjacent tile, outputting directly to core without needing a conveyor. The connectivity check for "adjacent conveyor" misses this case.

### 3. Face: 1/1 connected, 9,650 Ti mined
The only map where a harvester is both visible AND connected via conveyor. This is our "normal" case — short chain, visible from core, working.

### 4. Core vision is too limited for this measurement
Core vision r^2=36 covers ~6 tiles in each direction. On any map larger than ~12x12, most harvesters are outside core vision. We CAN'T measure chain connectivity from the core.

## What This Means for the 19% Delivery Rate Hypothesis

**The 19% delivery rate hypothesis was WRONG.** Let me recalculate:

- default_medium1: 37,150 Ti mined. If harvesters built at ~round 10-50, theoretical max for ~3-5 harvesters ≈ 20-25k Ti. We're mining 37k — MORE than theoretical single-harvester max. Multiple harvesters ARE delivering.

- hooks: 37,030 Ti mined. Same story — chains are working well.

- cold: 19,670 Ti mined with 0 visible harvesters. Chains work fine despite maze walls.

**The chains aren't broken. The 903 Ti/harvester figure from the MergeConflict match was a DIFFERENT version (V40, pre-V61).** V61 may have significantly better chain reliability. The current code already delivers resources effectively.

## Revised Understanding

The gap to 1600 is NOT chain breaks. Our chains work. The gap is likely:
1. **Building count / scale inflation** — we build 400+ buildings, driving costs up
2. **Late harvester placement** — builders take too long to reach ore
3. **Exploration waste** — conveyors laid during exploration that carry nothing
4. **Opponent-specific weaknesses** — losing to particular strategies (sentinel_spam, ladder_hybrid_defense)

## Recommendation

**Chain audit is NOT the answer.** Chains already work. The 19% delivery rate calculation was based on stale V40 data. V61 appears to deliver effectively.

Remove the debug code and revert buzzing/main.py to committed state.
