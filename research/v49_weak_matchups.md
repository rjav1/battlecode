# V49 Weak Matchup Analysis

**Date:** 2026-04-06  
**Bot:** buzzing V49  
**Focus:** Tight map losses — what patterns cause defeat?

---

## Match Results

| # | Match | Map | Seed | Winner | buzzing Ti (mined) | Opp Ti (mined) | Mining ratio | buzzing Bldgs | Opp Bldgs |
|---|-------|-----|------|--------|-------------------|----------------|--------------|---------------|-----------|
| 1 | vs smart_defense | arena | 1 | smart_defense | 20517 (18000) | 25146 (21120) | 0.85x | 147 | 120 |
| 2 | vs smart_defense | arena | 2 | smart_defense | 20517 (18000) | 25146 (21120) | 0.85x | 147 | 120 |
| 3 | vs rusher | face | 1 | rusher | 3324 (**510**) | 11123 (9930) | **0.05x** | **31** | 221 |
| 4 | vs rusher | arena | 1 | rusher | 3812 (1750) | 5931 (4970) | 0.35x | 47 | 283 |
| 5 | vs ladder_dual | face | 1 | ladder_dual | 11736 (10270) | 21341 (19310) | 0.53x | 137 | 195 |
| 6 | vs ladder_dual | arena | 1 | ladder_dual | 11736 (10270) | 21341 (19310) | 0.53x | 137 | 195 |

*Note: Matches 1 and 2 produced identical scorelines — smart_defense is fully deterministic on arena regardless of seed. Matches 5 and 6 also identical despite different maps, suggesting ladder_dual score was cached from a shared replay write.*

**6W-0L for opponents. 0 wins across all 6 matchups.**

---

## Pattern Analysis by Matchup

### smart_defense on arena (2 matches)
- **Result:** Consistent loss, 18000 vs 21120 Ti mined (85% of opponent)
- **Buildings:** 147 vs 120 — we overbuild by 27 structures
- **Units:** 8 vs 12 — opponent has 50% more units
- **Nature of loss:** Narrow resource tiebreaker, not a blowout. We're competitive but can't close.
- **Pattern:** smart_defense runs more builder bots (12 vs 8 units). More builders = more harvesters placed faster = compounding Ti advantage. Our tight-mode builder cap of 8 leaves us undermanned. smart_defense likely ignores defensive buildings and pure-rushes harvesters.

### rusher on face (catastrophic — match 3)
- **Result:** 510 Ti mined vs 9930 — **we mine 19x less**
- **Buildings:** 31 vs 221 — rusher builds 7x more infrastructure
- **Units:** 8 vs 10 — similar unit count
- **Pattern:** CRITICAL FAILURE. We only mined 510 Ti on face. This means our harvesters barely functioned — either we placed very few, placed them on wrong tiles, or our conveyor chains to core failed entirely. Rusher built 221 buildings (primarily conveyors + harvesters at speed) while we built only 31. On face specifically, ore tiles may be in positions our early builder pathing can't reach.

### rusher on arena (match 4)
- **Result:** 1750 vs 4970 Ti mined (35% of opponent)
- **Buildings:** 47 vs 283 — rusher builds 6x more
- **Same catastrophic pattern** as face but slightly better. We're failing to establish any harvest economy on tight maps vs aggressive opponents.

### ladder_dual on face and arena (matches 5-6)
- **Result:** 10270 vs 19310 Ti mined (53% of opponent)
- **Buildings:** 137 vs 195 — closer gap but opponent still overbuildS
- **Units:** 8 vs 12 — opponent again runs more units
- **Pattern:** Similar to smart_defense — more units enables more harvesters. We're limited by builder cap and aren't getting harvester chains up fast enough.

---

## Root Causes Identified

### 1. Catastrophic harvester failure vs rusher on tight maps (face)
The 510 Ti mined result is the most alarming finding. On face, our builders either:
- Cannot path to ore tiles (face has specific wall/ore layout that blocks our BFS)
- Are spending their early rounds building roads/conveyors to non-ore tiles
- Have the first builder sent in the wrong direction, missing nearby ore entirely

**face map dimensions:** Likely a small tight map (~20x20). Ore tiles may be positioned in a pattern that our first-builder-toward-ore heuristic misses with this seed.

### 2. Builder cap too conservative on tight maps vs unit-heavy opponents
smart_defense and ladder_dual both field 12 units to our 8. Our tight-mode cap maxes at 8, while opponents run 12. More builders = more harvesters placed per round = compounding Ti advantage. The cap differential (8 vs 12) explains the consistent ~15-20% Ti deficit vs smart_defense.

### 3. Opponent building count inversion on tight maps
vs rusher: they build 221-283 buildings to our 31-47. This is the reverse of our usual problem (we normally overbuild). Rusher is specifically optimized for fast infrastructure deployment on tight maps. We're getting outpaced not by being too slow to build, but by our builders going to the wrong places first.

### 4. No rush defense
vs rusher, opponent builds 221-283 buildings by round 2000. These are overwhelmingly harvesters + conveyors placed early. We have no mechanism to contest ore tiles or slow their expansion. If they claim all ore tiles first on a small map, we can never catch up.

---

## Tight Map Failure Modes Summary

| Failure mode | Matchup | Severity |
|---|---|---|
| Harvester pathing failure / ore miss | rusher face | **Critical** (19x mining deficit) |
| Builder unit cap deficit | smart_defense, ladder_dual | Moderate (12 vs 8 units) |
- No ore contesting / rush defense | rusher | High |
| Conveyor overbuild instead of harvesters | all | Moderate |

---

## Recommended Fixes

### High priority
1. **Investigate face map ore layout** — run a debug match to see which tiles our first builder visits. 510 Ti mined suggests a near-total harvester failure. Specific to face seed 1 or structural?
2. **Raise tight-mode unit cap** — from 8 to 10-12 to match opponent unit counts. smart_defense at 12 units beats our 8 consistently.

### Medium priority
3. **Ore tile claiming / contesting** — on small maps, builders should prioritize reaching ore tiles before opponents do. Current code has marker-based claiming but may not be aggressive enough on tight maps.
4. **Early harvester count floor** — ensure at minimum 2-3 harvesters by round 100 on any map type. The 510 Ti mined result suggests this floor isn't being hit.

---

## Note on ladder_dual Identical Results
Matches 5 and 6 (ladder_dual face vs ladder_dual arena with same seed) produced byte-for-byte identical final scoreboards. This is suspicious — likely a replay file collision (both write to `replay.replay26`) where the arena match overwrote the face match's replay before the second read. The underlying matches ran correctly (confirmed by different map names in headers) but one result may be duplicated. Treat as 1 effective data point for ladder_dual.
