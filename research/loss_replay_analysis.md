# Replay Analysis: Match vs One More Time (1-4 LOSS)

**Match ID:** 7c9a4dd9-227d-49de-8146-8d42fdb6daa9
**Date:** Apr 5, 2026
**Analyzed via:** game.battlecode.cam/visualiser

---

## Executive Summary

**Our bot has a catastrophic conveyor chain problem.** We build harvesters on ore tiles but do NOT connect them back to the core with conveyor chains. As a result, our harvesters generate resources that never reach the core. Meanwhile, the opponent builds fewer harvesters but connects every single one with dense conveyor networks, collecting 2-3x more total Ti despite having fewer harvesters.

We won Game 5 only because that map (pls_buy_cucats_merch) has ZERO ore -- no harvesters are possible, making it a pure starting-resource conservation game where our defensive sentinels gave us an edge.

---

## Game-by-Game Data

### Game 1: landscape (LOSS)

**Round 100 snapshot:**
| Metric | buzzing bees (G) | One More Time (S) |
|---|---|---|
| Titanium in bank | 494 | 24 |
| Ti collected | 310 | 500 |
| Bots | 4 | 8 |
| Conveyors | 46 | 78 |
| Harvesters | 4 | 4 |

**Round 500 snapshot:**
| Metric | buzzing bees (G) | One More Time (S) |
|---|---|---|
| Titanium in bank | 3717 | 80 |
| Ti collected | 3360 | 3740 |
| Bots | 6 | 21 |
| Conveyors | 69 | 181 |
| Harvesters | 8 | 8 |
| Sentinels | 2 | 0 |

**Round 1000 snapshot:**
| Metric | buzzing bees (G) | One More Time (S) |
|---|---|---|
| Titanium in bank | 6921 | 236 |
| Ti collected | 7820 | 8740 |
| Bots | 6 | 40 |
| Conveyors | 112 | 210 |
| Harvesters | 30 | 8 |
| Sentinels | 2 | 0 |

**Round 2000 (FINAL):**
| Metric | buzzing bees (G) | One More Time (S) |
|---|---|---|
| Titanium in bank | 18421 | 9034 |
| Ti collected | 16820 | 18740 |
| Bots | 6 | 49 |
| Conveyors | 112 | 220 |
| Harvesters | 30 | 8 |
| Sentinels | 2 | 0 |

**Analysis:** We have 30 harvesters vs their 8, yet they collected 18740 Ti vs our 16820. We also hoarded 18421 Ti unspent. Our harvesters are NOT connected to the core. Opponent has 8x more bots (49 vs 6) and 2x more conveyors (220 vs 112).

---

### Game 2: battlebot (LOSS)

**Round 2000 (FINAL):**
| Metric | buzzing bees (G) | One More Time (S) |
|---|---|---|
| Titanium in bank | 16802 | 16941 |
| Ti collected | 13110 | 28550 |
| Bots | 6 | 49 |
| Conveyors | 40 | 262 |
| Harvesters | 14 | 9 |
| Bridges | 1 | 2 |
| Sentinels | 3 | 0 |

**Analysis:** They collected **2.18x** more Ti (28550 vs 13110) with fewer harvesters (9 vs 14). Their 262 conveyors form connected supply chains. Our 40 conveyors are scattered navigation aids.

---

### Game 3: cold (LOSS)

**Round 2000 (FINAL):**
| Metric | buzzing bees (G) | One More Time (S) |
|---|---|---|
| Titanium in bank | 3866 | 294 |
| Ti collected | 8260 | 25970 |
| Bots | 8 | 46 |
| Roads | 7 | 0 |
| Conveyors | 303 | 599 |
| Harvesters | 43 | 22 |
| Sentinels | 2 | 0 |

**Analysis:** Worst ratio: they collected **3.14x** more Ti (25970 vs 8260). We have 43 harvesters vs their 22 -- nearly double -- yet collect 1/3 as much. They have 599 conveyors vs our 303, but their conveyors DELIVER while ours are navigation scatter. This map has abundant ore, making the conveyor chain gap maximally punishing.

---

### Game 4: corridors (LOSS)

**Round 2000 (FINAL):**
| Metric | buzzing bees (G) | One More Time (S) |
|---|---|---|
| Titanium in bank | 18634 | 13427 |
| Ti collected | 15580 | 39310 |
| Bots | 8 | 49 |
| Roads | 2 | 0 |
| Conveyors | 165 | 498 |
| Harvesters | 6 | 27 |
| Foundries | 0 | 2 |
| Sentinels | 0 | 0 |

**Analysis:** They collected **2.52x** more Ti (39310 vs 15580). On this map, they have MORE harvesters (27 vs 6) AND more conveyors (498 vs 165). They also built 2 foundries. We hoarded 18634 Ti unspent. This map's layout (long corridors) may have hampered our builders' ore-finding.

---

### Game 5: pls_buy_cucats_merch (WIN)

**Round 2000 (FINAL):**
| Metric | buzzing bees (G) | One More Time (S) |
|---|---|---|
| Titanium in bank | 4592 | 4288 |
| Ti collected | 0 | 0 |
| Bots | 6 | 12 |
| Conveyors | 36 | 54 |
| Harvesters | 0 | 0 |
| Sentinels | 4 | 0 |
| Bridges | 1 | 0 |

**Analysis:** This map has NO ore. Both teams collected 0 Ti. The only resources are the starting 500 Ti. We won because we conserved more starting Ti (4592 vs 4288). Our sentinels (4 vs 0) may have helped. The opponent wasted resources building more bots and conveyors on a map with nothing to harvest.

**This win does NOT validate our economy -- it only shows we're slightly better at NOT spending on a resource-free map.**

---

## Opponent Strategy: "One More Time" (Elo ~1500)

Based on watching the replays, their bot:

1. **Spawns MANY more bots** -- consistently 40-49 bots vs our 6-8. They scale to the bot cap aggressively.
2. **Builds dense conveyor networks** -- 200-600 conveyors forming connected chains from harvesters to core.
3. **Uses fewer harvesters but CONNECTS them** -- 8-27 harvesters, all feeding into the conveyor network.
4. **Spends aggressively** -- always <300 Ti in bank. Reinvests everything into infrastructure.
5. **Uses no sentinels, gunners, or launchers** -- pure economy focus.
6. **Uses foundries on some maps** (2 foundries on corridors).
7. **Uses no roads** -- conveyors serve as both transportation and resource delivery.

## Our Bot's Problems (confirmed by replay data)

### Problem 1: DISCONNECTED HARVESTERS (Critical)
We build 6-43 harvesters but they are NOT connected to the core with conveyor chains. The conveyors we build are facing wrong directions (backward from builder movement, not toward core). Evidence:
- Game 1: 30 harvesters, 16820 Ti collected. Opponent: 8 harvesters, 18740 Ti collected.
- Game 3: 43 harvesters, 8260 Ti collected. Opponent: 22 harvesters, 25970 Ti collected.

### Problem 2: MASSIVE RESOURCE HOARDING
We accumulate 3000-18000+ Ti in the bank instead of spending it. The opponent keeps <300 Ti and reinvests everything. Our "cost + 50" buffer checks are too conservative, but the bigger issue is that we simply don't have enough things to spend on.

### Problem 3: TOO FEW BOTS
We cap at 6-8 bots while the opponent runs 40-49. More bots = more harvesters placed = more conveyors built = more territory covered. Our builder cap (line 33) limits us to 2 early, 4 mid, 6 late, 8 very late.

### Problem 4: CONVEYORS USED FOR NAVIGATION, NOT DELIVERY
Our bot builds conveyors as movement aids (line 258-262: `face = d.opposite()`), not as resource delivery infrastructure. The opponent builds conveyors specifically to form chains from harvesters to core.

### Problem 5: NO FOUNDRIES
The opponent built foundries on corridors. We never build foundries. Foundries may provide additional resource processing benefits.

---

## What Determines Resource Victory?

Based on the data, Resource Victory appears to be determined by **Ti collected** (total titanium collected over the game), NOT by current bank balance. Evidence:
- Game 1: We had 18421 Ti in bank vs their 9034, but LOST because they had 18740 Ti collected vs our 16820.
- Game 4: We had 18634 Ti in bank vs their 13427, but LOST because they had 39310 Ti collected vs our 15580.

This means hoarding is actively harmful -- unspent Ti in the bank does NOT count toward victory. **Only resources that flow through the core (Ti collected) matter.**

---

## Recommendations for Next Bot Version

### MUST FIX (determines wins/losses):
1. **Build conveyor chains FROM each harvester BACK TO the core.** After placing a harvester, the builder should lay a chain of conveyors facing toward the core, connecting the harvester output to the core input. This is the single most impactful change.
2. **Increase bot count aggressively.** Remove the conservative cap. Spawn builders continuously -- the opponent runs 40-49 bots.
3. **Stop hoarding.** Remove or reduce the Ti buffer requirements. Spend resources on more harvesters, more conveyors, more bots.

### SHOULD FIX:
4. **Build conveyors for delivery, not navigation.** Stop building backward-facing conveyors for movement. Use roads for movement if needed, or just walk.
5. **Consider foundries.** The opponent builds them on some maps.
6. **Explore more of the map.** On corridors, we only built 6 harvesters while they built 27. More bots exploring = more ore found.

### VALIDATE:
7. **Confirm Ti collected = victory condition.** Our data strongly suggests this but should verify in docs.
8. **Test on pls_buy_cucats_merch-style maps.** We win resource-free maps. Focus improvements on ore-rich maps.
