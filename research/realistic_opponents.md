# Realistic Test Opponents -- Ladder Strategy Models

**Created:** 2026-04-04

---

## Overview

Two test opponents built to model real 1500 Elo ladder strategies based on nemesis analysis of One More Time, KCPC-B, Polska Gurom, and Warwick CodeSoc.

---

## ladder_eco -- "Realistic 1500 Elo Economy"

**Models:** One More Time, KCPC-B, The Defect

**Key behaviors:**
- 40 builders (near 49 unit cap) -- aggressive ramp: 5 by r20, 10 by r50, 20 by r100, 40 by r300
- d.opposite() conveyors forming connected chains to core
- Minimal reserve: cost+2 only (spends everything)
- Harvests ALL ore types (Ti and Ax)
- No military -- pure economy
- Faster exploration rotation (every 100 rounds vs 150)
- Ore-biased spawning from core

### Test Results vs buzzing

| Map | Winner | buzzing Ti (mined) | ladder_eco Ti (mined) | buzzing Units | ladder_eco Units |
|-----|--------|--------------------|-----------------------|---------------|------------------|
| default_medium1 | **ladder_eco** | 5970 (4940) | 142 (4950) | 10 | 38 |
| settlement | **buzzing** | 19104 (27200) | 88 (0) | 10 | 16 |
| cold | **ladder_eco** | 8827 (9690) | 15516 (25370) | 10 | 40 |

**Record: buzzing 1-2 ladder_eco**

**Key insights:**
- **default_medium1:** Equal mining (4940 vs 4950) but ladder_eco wins because it SPENT its Ti (142 in bank vs 5970 hoarded). Our hoarding problem exposed.
- **settlement:** buzzing wins big -- ladder_eco mined 0 Ti, suggesting its builders couldn't find ore on this map layout. Bot needs map adaptation.
- **cold:** ladder_eco dominates with 2.6x more Ti mined (25370 vs 9690). 40 bots vs 10 bots means massively more map coverage. This mirrors the One More Time replay data (3.14x more Ti on cold).

---

## ladder_rush -- "Realistic 1500 Elo Rush+Eco"

**Models:** Polska Gurom, Warwick CodeSoc

**Key behaviors:**
- 5 builders by round 15
- Role assignment: 3/5 rush, 2/5 eco (based on ID % 5)
- Rush builders: beeline to enemy core via symmetry guess, attack buildings on own tile
- Rush builders walk on enemy conveyors and build roads to advance
- Eco builders: standard harvester + conveyor economy
- Spawn direction biased toward enemy for rushers

### Test Results vs buzzing

| Map | Winner | buzzing Ti (mined) | ladder_rush Ti (mined) | buzzing Units | ladder_rush Units |
|-----|--------|--------------------|-----------------------|---------------|-------------------|
| face | **ladder_rush** | 6101 (1840) | 9967 (8700) | 7 | 20 |
| arena | **ladder_rush** | 17220 (13690) | 16873 (15710) | 7 | 20 |
| default_medium1 | **buzzing** | 169 (550) | 274 (0) | 14 | 20 |

**Record: buzzing 1-2 ladder_rush**

**Key insights:**
- **face:** ladder_rush wins via economy (8700 vs 1840 mined). No core destruction this seed, but the eco+rush hybrid outperforms. This matches our 0-5 record on face.
- **arena:** Very close (17220 vs 16873) -- ladder_rush barely wins via mining advantage (15710 vs 13690). Matches our 0-4 record on arena.
- **default_medium1:** buzzing wins but both mined almost nothing (550 vs 0). Map-dependent behavior.

---

## Combined Assessment

| Metric | buzzing vs ladder_eco | buzzing vs ladder_rush | Total |
|--------|----------------------|------------------------|-------|
| Wins | 1 | 1 | 2 |
| Losses | 2 | 2 | 4 |
| **Win Rate** | **33%** | **33%** | **33%** |

**These opponents are HARDER than our current test fleet**, confirming the gap between local testing and ladder performance. Our 33% win rate against these realistic opponents is much closer to our 44% ladder win rate than our previous 85% local win rate.

---

## Problems Exposed

1. **Resource hoarding:** On default_medium1, both bots mined equally but we lost because we hoarded 5970 Ti vs spending it all. The tiebreaker counts delivered Ti, not banked Ti.

2. **Bot count gap:** We run 7-10 bots vs 20-40 for opponents. More bots = more map coverage = more ore found = more harvesters built.

3. **Cold/face/arena weakness confirmed:** These maps reproduce our 0-win ladder record. The opponents don't need to be sophisticated -- just running more bots with aggressive spending beats us.

4. **No rush defense tested yet:** ladder_rush didn't achieve core destruction in these seeds, but the eco advantage alone was enough to win on compact maps.

---

## Recommendations

1. **Increase builder cap** from 8-10 to 30+ to match ladder opponents
2. **Reduce resource reserve** from current levels to cost+5 or less
3. **Fix face/arena** -- these are auto-losses that these opponents reproduce
4. **Test with more seeds** to check for core destruction scenarios on face

---

*Bot files: `bots/ladder_eco/main.py`, `bots/ladder_rush/main.py`*
