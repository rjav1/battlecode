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
Match 6 (v8): 1464 -> 1468 (+4)   <-- v8 RECOVERY! First win since v2
```

**v8 stops the bleeding! Elo recovering.**

---

## NEW: Match 6 -- v8 FIRST WIN! Recovery begins

### Match 6: vs Solo Gambling (v8) -- V8 DEBUT WIN
| Field | Value |
|---|---|
| Match ID | daccc3bf-fb35-43ee-b5b7-4cbb85cbc694 |
| Date | Apr 5, 11:02 PM |
| Our Version | **v8** (skipped v5/v6/v7!) |
| Opponent | Solo Gambling (Elo 1479, novice, 289 matches) |
| Result | **3-2 WIN** |
| Elo Change | +3.9 (1464 -> 1468) |
| Duration | **54s** (fastest match yet!) |

| Game | Map | Winner | Turns |
|---|---|---|---|
| 1 | landscape | **buzzing bees** | 2000 |
| 2 | shish_kebab | Solo Gambling | 2000 |
| 3 | git_branches | **buzzing bees** | 2000 |
| 4 | tiles | **buzzing bees** | 2000 |
| 5 | default_small1 | Solo Gambling | 2000 |

**Key observations:**
- Won landscape! (v1 lost this map to One More Time)
- Won git_branches and tiles (consistent with v2 wins)
- Lost shish_kebab (also lost in v2 vs Chameleon)
- Match duration 54s vs 2-4min for previous matches -- v8 is dramatically more efficient
- Beat a higher-Elo opponent (1479 vs our 1464)

---

## Updated Version Comparison

| Version | Matches | Record | Game W-L | Win Rate | Avg Elo Change |
|---|---|---|---|---|---|
| v1 | 1 | 0-1 | 1-4 | 20% | -9.9 |
| v2 | 2 | 1-1 | 5-5 | 50% | +0.25 |
| v4 | 2 | 0-2 | 1-9 | 10% | -13.0 |
| v8 | 1 | 1-0 | 3-2 | 60% | +3.9 |
| **v9** | **1** | **1-0** | **3-2** | **60%** | **+3.4** |

**v8+v9 on a 2-match win streak! Both at 60% game win rate. Elo recovering.**

---

## NEW: Match 7 -- v9 DEBUT WIN! Two in a row!

### Match 7: vs 5goatswalkintoabarbut1dies (v9) -- BACK-TO-BACK WINS
| Field | Value |
|---|---|
| Match ID | 7fb532f0-f1bf-4d0a-b4a7-49dd6b1ef7d8 |
| Date | Apr 5, 11:12 PM |
| Our Version | **v9** (first v9 match!) |
| Opponent | 5goatswalkintoabarbut1dies (Elo 1472, main, 2212 matches) |
| Result | **3-2 WIN** |
| Elo Change | +3.4 (1468 -> 1471) |
| Duration | **50s** (fastest yet!) |

| Game | Map | Winner | Turns |
|---|---|---|---|
| 1 | tree_of_life | **buzzing bees** | 2000 |
| 2 | starry_night | 5goats | 2000 |
| 3 | pls_buy_cucats_merch | **buzzing bees** | 2000 |
| 4 | git_branches | **buzzing bees** | 2000 |
| 5 | cold | 5goats | 2000 |

**Key observations:**
- 2-match win streak (v8 + v9)!
- Won tree_of_life (new map), pls_buy_cucats_merch (consistent win), git_branches (consistent win)
- Lost starry_night and cold
- cold is a consistent loss across versions (lost in v1 and now v9)
- Beat a higher-Elo, experienced opponent (1472 Elo, 2212 matches)
- 50s match duration -- v9 is our fastest

---

## Elo Trajectory (Updated)

```
Match 1 (v1): 1500 -> 1490 (-10)
Match 2 (v2): 1490 -> 1487 (-3)
Match 3 (v2): 1487 -> 1490 (+3)
Match 4 (v4): 1490 -> 1474 (-16)  <-- v4 regression
Match 5 (v4): 1474 -> 1464 (-10)  <-- v4 continues to lose
Match 6 (v8): 1464 -> 1468 (+4)   <-- recovery begins
Match 7 (v9): 1468 -> 1471 (+3)   <-- v9 continuing recovery
```

**Elo trend reversed! Two consecutive wins recovering from v4 crash.**

---

## Map Win/Loss Tracker (all versions)

| Map | Wins | Losses | Notes |
|---|---|---|---|
| git_branches | 3 | 0 | Consistent win (v2, v8, v9) |
| pls_buy_cucats_merch | 2 | 0 | Consistent win (v1, v9) |
| tiles | 2 | 0 | Consistent win (v2, v8) |
| landscape | 1 | 1 | Won v8, lost v1 |
| tree_of_life | 1 | 0 | Won v9 |
| settlement | 1 | 0 | Won v2 |
| sierpinski_evil | 1 | 0 | Won v2 |
| wasteland | 1 | 0 | Won v4 |
| default_medium1 | 1 | 2 | Won v2, lost v4 twice |
| cold | 0 | 3 | Consistent loss (v1, v4, v9) |
| shish_kebab | 0 | 2 | Consistent loss (v2, v8) |
| battlebot | 0 | 2 | Lost v1, v4 |
| galaxy | 0 | 2 | Lost v2, v4 |
| starry_night | 0 | 1 | Lost v9 |
| default_small1 | 0 | 1 | Lost v8 |

**Strongest maps:** git_branches (3-0), pls_buy_cucats_merch (2-0), tiles (2-0)
**Weakest maps:** cold (0-3), shish_kebab (0-2), battlebot (0-2), galaxy (0-2)

---

## Current Ladder Position

| Rank | Elo | Team | Matches |
|---|---|---|---|
| **#136** | **1471** | **buzzing bees** | **7** |
