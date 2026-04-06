# Buzzing Bees - Ladder Status v3 Monitoring

**Report Date:** 2026-04-05, 10:55 PM (live monitoring)
**Current Elo:** 1464 (dropping fast -- was 1490)
**Current Rank:** #137 of 573
**Total Matches:** 5

---

## IMPORTANT: v3 Not Yet Active on Ladder

Both new matches were played with **v2**, not v3. The submission page shows v2 was used. V3 may still be processing or waiting to be picked up by the matchmaking system. Will continue monitoring for v3 matches.

---

## Match History (All 3 Matches)

### Match 1: vs One More Time (v1)
| Field | Value |
|---|---|
| Match ID | 7c9a4dd9-227d-49de-8146-8d42fdb6daa9 |
| Date | Apr 5, 10:12 PM |
| Our Version | v1 |
| Opponent | One More Time (Elo 1493, Silver) |
| Result | **1-4 LOSS** |
| Elo Change | -9.9 (1500 -> 1490) |

| Game | Map | Winner | Turns |
|---|---|---|---|
| 1 | landscape | One More Time | 2000 |
| 2 | battlebot | One More Time | 2000 |
| 3 | cold | One More Time | 2000 |
| 4 | corridors | One More Time | 2000 |
| 5 | pls_buy_cucats_merch | **buzzing bees** | 2000 |

---

### Match 2: vs Chameleon (v2) -- NEW
| Field | Value |
|---|---|
| Match ID | 0800eb31-71bb-4b24-8521-db959ddcfaef |
| Date | Apr 5, 10:22 PM |
| Our Version | **v2** |
| Opponent | Chameleon (Elo 1492, novice, Silver) |
| Result | **2-3 LOSS** |
| Elo Change | -3.1 (1490 -> ~1487) |
| Duration | 1m 46s |

| Game | Map | Winner | Turns |
|---|---|---|---|
| 1 | default_medium1 | **buzzing bees** | 2000 |
| 2 | tiles | **buzzing bees** | 2000 |
| 3 | shish_kebab | Chameleon | 2000 |
| 4 | default_medium2 | Chameleon | 2000 |
| 5 | galaxy | Chameleon | 2000 |

**Analysis:** Significant improvement from v1! We won 2 games (up from 1/5 with v1). Lost 3 games on shish_kebab, default_medium2, and galaxy. Still losing the overall match but much closer (2-3 vs 1-4 previously).

---

### Match 3: vs SPAARK (v2) -- NEW -- FIRST WIN!
| Field | Value |
|---|---|
| Match ID | f22af3ca-a9b1-4d89-8d1c-de3a236a70f6 |
| Date | Apr 5, 10:32 PM |
| Our Version | **v2** |
| Opponent | SPAARK (Elo 1495, main, Silver) |
| Result | **3-2 WIN** |
| Elo Change | +3.6 (~1487 -> 1490) |
| Duration | 2m 4s |

| Game | Map | Winner | Turns |
|---|---|---|---|
| 1 | bar_chart | SPAARK | 2000 |
| 2 | settlement | **buzzing bees** | 2000 |
| 3 | git_branches | **buzzing bees** | 2000 |
| 4 | face | SPAARK | 2000 |
| 5 | sierpinski_evil | **buzzing bees** | 2000 |

**Analysis:** OUR FIRST LADDER WIN! v2 beat SPAARK (Elo 1495, rank #132) 3-2. We won on settlement, git_branches, and sierpinski_evil. Lost on bar_chart and face.

---

## Summary: v2 Performance

| Match | Opponent | Opp Elo | Result | Games Won | Version |
|---|---|---|---|---|---|
| 1 | One More Time | 1493 | 1-4 LOSS | 1 | v1 |
| 2 | Chameleon | 1492 | 2-3 LOSS | 2 | v2 |
| 3 | SPAARK | 1495 | **3-2 WIN** | 3 | v2 |

**v2 win rate: 1W-1L (50% match win rate), 5-5 game record (50% game win rate)**
**v1 win rate: 0W-1L, 1-4 game record (20% game win rate)**

v2 is a massive improvement over v1. Game win rate jumped from 20% to 50%.

---

## Maps Performance (all versions)

| Map | Result | Version |
|---|---|---|
| pls_buy_cucats_merch | WIN | v1 |
| default_medium1 | WIN | v2 |
| tiles | WIN | v2 |
| settlement | WIN | v2 |
| git_branches | WIN | v2 |
| sierpinski_evil | WIN | v2 |
| landscape | LOSS | v1 |
| battlebot | LOSS | v1 |
| cold | LOSS | v1 |
| corridors | LOSS | v1 |
| shish_kebab | LOSS | v2 |
| default_medium2 | LOSS | v2 |
| galaxy | LOSS | v2 |
| bar_chart | LOSS | v2 |
| face | LOSS | v2 |

**Total: 6 wins, 9 losses across all games (40% game win rate overall)**

---

## Waiting for v3

V3 was SKIPPED -- the ladder went straight from v2 to v4.

---

## NEW: Match 4 -- v4 REGRESSION (0-5 LOSS)

### Match 4: vs KCPC-B (v4) -- REGRESSION ALERT
| Field | Value |
|---|---|
| Match ID | 02bfa75f-6da4-478a-b933-bcf1d4491b90 |
| Date | Apr 5, 10:42 PM |
| Our Version | **v4** (first v4 match!) |
| Opponent | KCPC-B (Elo 1495, main, Unranked, 11 matches) |
| Result | **0-5 LOSS** |
| Elo Change | **-15.8** (1490 -> 1474) |
| Duration | 4m 25s |

| Game | Map | Winner | Turns |
|---|---|---|---|
| 1 | default_medium1 | KCPC-B | 2000 |
| 2 | hourglass | KCPC-B | 2000 |
| 3 | galaxy | KCPC-B | 2000 |
| 4 | arena | KCPC-B | 2000 |
| 5 | minimaze | KCPC-B | 2000 |

**REGRESSION:** v2 won default_medium1 against Chameleon. v4 lost it against KCPC-B. v2 went 3-2 against SPAARK (Elo 1495). v4 went 0-5 against KCPC-B (Elo 1495). Same Elo opponents, dramatically worse results.

**Possible causes:**
- Aggressive builder scaling may be spending too much Ti on bots, leaving not enough for harvesters/conveyors
- The builder cap increase may cause resource starvation in early game
- Too many bots competing for the same ore tiles
- Need to watch replays to diagnose

---

## Version Comparison

| Version | Matches | Record | Game W-L | Win Rate | Avg Elo Change |
|---|---|---|---|---|---|
| v1 | 1 | 0-1 | 1-4 | 20% | -9.9 |
| v2 | 2 | 1-1 | 5-5 | 50% | +0.25 |
| v4 | 2 | 0-2 | 1-9 | 10% | -13.0 |

**v4 is a confirmed regression from v2. v5 has NOT appeared yet.**

---

## NEW: Match 5 -- v4 still active, another loss

### Match 5: vs :3 (v4) -- STILL V4, NOT V5
| Field | Value |
|---|---|
| Match ID | 83b196cf-bae2-463a-9f11-9ced8473d74c |
| Date | Apr 5, 10:52 PM |
| Our Version | **v4** (v5 not deployed yet!) |
| Opponent | :3 (Elo 1461, main) |
| Result | **1-4 LOSS** |
| Elo Change | -10.2 (1474 -> 1464) |
| Duration | 2m 57s |

| Game | Map | Winner | Turns |
|---|---|---|---|
| 1 | wasteland | **buzzing bees** | 2000 |
| 2 | cubes | :3 | 2000 |
| 3 | battlebot | :3 | 2000 |
| 4 | default_medium1 | :3 | 2000 |
| 5 | cold | :3 | 2000 |

**v4 lost to a LOWER Elo opponent (1461 vs our 1474).** We won wasteland but lost everything else. v5 hotfix has NOT reached the ladder yet.

---

## Elo Trajectory

```
Match 1 (v1): 1500 -> 1490 (-10)
Match 2 (v2): 1490 -> 1487 (-3)
Match 3 (v2): 1487 -> 1490 (+3)
Match 4 (v4): 1490 -> 1474 (-16)  <-- v4 regression
Match 5 (v4): 1474 -> 1464 (-10)  <-- v4 continues to lose
```

**Total: 1500 -> 1464 (-36 Elo). v2 was stabilizing at 1490. v4 is in freefall.**

---

## Current Ladder Position

| Rank | Elo | Team | Matches |
|---|---|---|---|
| #135 | 1483 | DODO | 805 |
| #136 | 1468 | N | 2157 |
| **#137** | **1464** | **buzzing bees** | **5** |
