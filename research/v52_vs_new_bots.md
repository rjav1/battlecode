# V52 vs New Test Bots

**Date:** 2026-04-06
**Bot:** buzzing (V52)
**Seed:** 1

## Results

| # | Command | Map | Winner | Buzzing Ti mined | Opponent Ti mined | Buzzing Bldg | Opp Bldg |
|---|---------|-----|--------|-----------------|-------------------|--------------|----------|
| 1 | vs ladder_road | cold | ladder_road | 15750 | 20020 | 373 | 325 |
| 2 | vs ladder_road | default_medium1 | ladder_road | 80 | 9800 | 178 | 251 |
| 3 | vs ladder_sentinel | face | ladder_sentinel | 17840 | 20330 | 116 | 134 |
| 4 | vs ladder_sentinel | arena | ladder_sentinel | 16530 | 22820 | 185 | 134 |
| 5 | vs ladder_sentinel | cold | **buzzing** | 19670 | 19610 | 375 | 334 |
| 6 | vs smart_eco | gaussian | smart_eco | 19830 | 22230 | 259 | 109 |
| 7 | vs smart_eco | cold | **buzzing** | 19670 | 19610 | 385 | 297 |

**Overall: 2W-5L (29%)**

---

## Analysis by Opponent

### vs ladder_road (0-2)

**cold:** Buzzing mined 15750 vs 20020 — lost by ~4K Ti. Building count similar (373 vs 325). Both bots built many buildings on this maze-like map. ladder_road's road-first exploration reaches ore faster in constrained terrain.

**default_medium1: CATASTROPHIC — 80 Ti mined.** Buzzing built 178 buildings but mined almost nothing (80 Ti). This is a critical failure — likely buzzing's builders got blocked or spent all Ti on conveyors without reaching ore. ladder_road mined 9800. The building count disparity (178 vs 251) with near-zero Ti delivery suggests buzzing's conveyor chains are delivering 0 ore to core.

### vs ladder_sentinel (1-2)

**face:** Lost 17840 vs 20330 mined. Buzzing built fewer buildings (116 vs 134) but delivered less Ti. Sentinel defense on face (tight map) slowed buzzing's approach.

**arena:** Lost 16530 vs 22820 mined. Buzzing built MORE buildings (185 vs 134) but mined 6K less. The sentinel positions 4-5 tiles out are blocking buzzing's expansion toward enemy-side ore. Building excess = conveyor overbuilding around sentinel barriers.

**cold:** WON by 60 Ti (19670 vs 19610). Near-draw — cold is a maze map where buzzing's chain-fix and BFS nav give slight advantage over sentinel positions.

### vs smart_eco (1-2)

**gaussian:** Lost 19830 vs 22230 mined. Buzzing built 2.4x more buildings (259 vs 109) — classic conveyor overbuilding pattern from the vs_smart_eco_v47 analysis. smart_eco's simpler nav builds fewer, more efficient conveyor chains.

**cold:** WON by 60 Ti (19670 vs 19610). Same spawn-side advantage as ladder_sentinel cold.

---

## Key Issues Identified

### 1. default_medium1 vs ladder_road — CRITICAL (80 Ti mined)
Buzzing nearly mined zero Ti. This suggests a complete economy failure on this specific matchup/map. Needs investigation: are builders getting stuck early, or is the conveyor chain delivering 0 ore to core?

### 2. Conveyor overbuilding persists
- gaussian: 259 vs 109 buildings (2.4x more)
- arena: 185 vs 134 buildings
- Building count negatively correlates with Ti mined — same pattern seen in v47 analysis

### 3. Sentinel walls block buzzing's expansion
On arena and face, ladder_sentinel's sentinels (placed 4-5 tiles from core in enemy direction) appear to block buzzing builders from reaching ore on the enemy half of the map. Buzzing mines significantly less than ladder_sentinel despite similar round timing.

### 4. Cold wins are spawn-side advantages
Both cold wins (vs ladder_sentinel and vs smart_eco) show identical Ti mined: 19670 vs ~19610. These are spawn-side tiebreaks, not skill wins.

---

## Verdict

V52 performs poorly against the upgraded test suite: **2W-5L (29%)**. The two wins are both narrow spawn-side advantages on cold. The real concern is:

1. **default_medium1 vs ladder_road** — near-zero economy is catastrophic
2. **Consistent losses to sentinel defense** — buzzing can't break through sentinel walls
3. **Losing to smart_eco on gaussian** — conveyor overbuilding still unsolved

Priority investigations:
- Debug default_medium1 vs ladder_road crash (why 80 Ti mined?)
- Fix conveyor overbuilding (gaussian: 259 vs 109 buildings)
- Determine if buzzing should add sentinel defense to stop ladder_sentinel
