# Nemesis Team Analysis: Four Teams That Always Beat Us
## Cambridge Battlecode 2026 -- Sprint 4
### Compiled: 2026-04-06

---

## Overview

Four teams account for **47% of all our losses** (14 of 30) with a combined **0-14 record** against us. Understanding why they consistently beat us is critical to climbing.

| Team | Record vs Us | Map Score | Our Elo | Their Elo | Elo Gap |
|------|-------------|-----------|---------|-----------|---------|
| **The Defect** | 0-4 | 5-15 | 1488 | 1521 | +33 |
| **KCPC-B** | 0-4 | 4-16 | 1488 | 1472 | -16 (!) |
| **One More Time** | 0-3 | 4-11 | 1488 | 1523 | +35 |
| **Polska Gurom** | 0-3 | 6-9 | 1488 | 1476 | -12 (!) |

**Critical finding:** KCPC-B and Polska Gurom have LOWER Elo than us, yet we've never beaten them. This is not about them being better overall -- they specifically counter our strategy.

---

## Team 1: The Defect (0-4, 5-15 maps)

### Profile
- **Elo:** 1521 (Silver tier, rank ~100)
- **Matches:** 2,614 (fully converged)
- **Category:** Main, International
- **Members:** 3 (AdUhTkJm, HerbLi0222, boxun)
- **Student team:** Yes

### Match History vs Us

| Match | Score | Maps Won by The Defect | Maps Won by Us |
|-------|-------|------------------------|----------------|
| #16 | 2-3 L | face, cold, wasteland | sierpinski_evil, pixel_forest |
| #35 | 1-4 L | socket, default_large2, sierpinski_evil, chemistry_class | pls_buy_cucats_merch |
| #45 | 1-4 L | face, cold, galaxy, pixel_forest | corridors |
| (4th) | 2-3 L | (various) | (various) |

### Maps They Beat Us On
face, cold, wasteland, socket, sierpinski_evil, default_large2, pixel_forest, chemistry_class, galaxy -- **extremely diverse set of maps**.

### Analysis
- **This is NOT a map-specific issue.** They beat us on 9+ different maps across ALL categories (economy maps, large maps, small maps).
- They have **fundamentally better resource collection.** On every map type, they out-collect us.
- Their 2,614 matches means their bot is well-tuned and stable.
- They are ~33 Elo above us, which is a meaningful but not huge gap.
- **Key insight:** They beat us on maps we normally WIN (sierpinski_evil: we're 6-2 overall, but 0-1 vs The Defect).

### What They Do Differently
The Defect has a broadly superior economy engine. They don't rely on any single map trick -- they simply collect more Ti across all map types. This suggests they have solved the core conveyor chain problem that we still struggle with. Their bot likely:
1. Builds connected conveyor networks efficiently on all map geometries
2. Scales harvester count appropriately per map
3. Reinvests resources aggressively (low bank balance)

### Threat Level: **HIGHEST** -- They expose our fundamental economic weakness across all maps.

---

## Team 2: KCPC-B (0-4, 4-16 maps)

### Profile
- **Elo:** 1472 (Silver tier, rank ~136)
- **Matches:** 62 (VERY FEW -- Elo not converged!)
- **Category:** Main, UK
- **Members:** 4 (Zach Land, K.IND, Flame Barrier, vayunk)
- **Student team:** Yes

### Match History vs Us

| Match | Score | Maps Won by KCPC-B | Maps Won by Us |
|-------|-------|---------------------|----------------|
| #4 | 0-5 L | default_medium1, hourglass, galaxy, arena, minimaze | (none) |
| #20 | 2-3 L | tree_of_life, cold, landscape | dna, pls_buy_cucats_merch |
| #43 | 2-3 L | arena, mandelbrot, default_large2 | corridors, default_small2 |
| (4th) | 0-5 L | (all 5 maps) | (none) |

### Maps They Beat Us On
tree_of_life, cold, landscape, arena, mandelbrot, default_large2, default_medium1, hourglass, galaxy, minimaze -- **another extremely diverse set**.

### Analysis
- **Only 62 matches played.** Their Elo (1472) is NOT converged. They could be significantly stronger than 1472.
- **0-5 blowouts** in 2 of 4 matches -- they utterly dominate us.
- They beat us on maps we normally win (hourglass: we're 6-3 overall).
- UK team with 4 members -- full squad.
- **Key insight:** With only 62 matches, their true Elo could be 1550+ (their bot may still be climbing rapidly). The low match count means the matchmaker hasn't had time to place them correctly.

### What They Do Differently
KCPC-B appears to have a highly efficient economy that crushes us across all map types. The two 0-5 sweeps suggest their advantage is massive, not marginal. Their low match count means they may have submitted a strong bot recently that hasn't been properly rated yet. They could be a "smurf" team that's actually quite strong.

### Threat Level: **VERY HIGH** -- Potentially underrated, complete domination pattern.

---

## Team 3: One More Time (0-3, 4-11 maps)

### Profile
- **Elo:** 1523 (Silver tier, rank ~98)
- **Matches:** 2,614 (fully converged)
- **Category:** Main, International
- **Members:** 3 (MathCosine, Luca, KURATUS)
- **Student team:** Yes

### Match History vs Us

| Match | Score | Maps Won by OMT | Maps Won by Us |
|-------|-------|-----------------|----------------|
| #1 | 1-4 L | landscape, battlebot, cold, corridors | pls_buy_cucats_merch |
| #37 | 2-3 L | galaxy, tiles, dna | cold, landscape |
| (3rd) | 2-3 L | (various) | (various) |

### Detailed Replay Analysis (Match #1 -- our FIRST ever ladder match)

This was our v1 bot vs One More Time. Full replay analysis available:

**Their strategy (observed from replays):**
1. **40-49 bots** active vs our 6-8. They scale aggressively to the bot cap.
2. **Dense connected conveyor networks** (200-600 conveyors forming chains from harvesters to core)
3. **Fewer harvesters but ALL connected** (8-27 harvesters, each feeding into the network)
4. **Aggressive spending** (<300 Ti in bank at all times, reinvests everything)
5. **Pure economy focus** (zero sentinels, gunners, or launchers)
6. **Uses foundries** on some maps (2 observed on corridors)

**Key economic data from replays:**

| Map | Our Ti Collected | Their Ti Collected | Ratio |
|-----|-----------------|-------------------|-------|
| landscape | 16,820 | 18,740 | 0.90x |
| battlebot | 13,110 | 28,550 | 0.46x |
| cold | 8,260 | 25,970 | 0.32x |
| corridors | 15,580 | 39,310 | 0.40x |

On cold, they collected **3.14x more Ti** with HALF our harvesters (22 vs 43). The gap is conveyor connectivity.

### What They Do Differently
One More Time is a pure economy bot with no military. They don't build turrets. They don't defend. They just build the most efficient conveyor network possible and out-collect everyone. Their strength:
- Connected conveyor chains (every harvester feeds to core)
- 40+ bots for rapid map coverage and construction
- Zero waste on military buildings
- Foundry usage for additional resource processing

### Threat Level: **HIGH** -- They have the best replay data showing exactly what we need to fix.

---

## Team 4: Polska Gurom (0-3, 6-9 maps)

### Profile
- **Elo:** 1476 (Silver tier, rank ~135)
- **Matches:** 2,614 (fully converged)
- **Category:** Main, International
- **Members:** 1 (Szymon Nowak -- SOLO PLAYER)
- **Student team:** Yes

### Match History vs Us

| Match | Score | Maps Won by PG | Maps Won by Us |
|-------|-------|----------------|----------------|
| #13 | 2-3 L | face (CD 319t!), cinnamon_roll, pls_buy_cucats_merch | tree_of_life, landscape |
| #44 | 2-3 L | landscape, wasteland, default_large2 | corridors, default_small2 |
| (3rd) | 2-3 L | (various) | (various) |

### Analysis
- **Solo player** at ~1476 Elo with 2,614 matches -- this is a dedicated, focused developer.
- **Core Destroyed us on face in 319 turns!** This is the only nemesis team that has used military aggression successfully against us.
- Despite being 12 Elo BELOW us, they beat us every time.
- All 3 matches are close (2-3), meaning we take maps off them but can't close the deal.
- They beat us on economy maps (landscape, wasteland, default_large2) AND can rush us (face CD at 319t).

### What They Do Differently
Polska Gurom has **dual competency** -- they can win via economy AND military rush. This is exactly the trait that separates top teams from the pack (see contender scouting report). Key observations:
1. **Rush capability:** Core Destroyed at turn 319 on face. This means they have offensive unit production and push logic.
2. **Economy competence:** They also beat us on landscape, wasteland, and default_large2 via Resource Victory at 2000 turns.
3. **Map awareness:** They seem to know when to rush (face -- compact map) vs when to play economy (landscape -- open map).

### Threat Level: **HIGH** -- Only nemesis with a working rush strategy. They beat us at BOTH win conditions.

---

## Cross-Nemesis Analysis

### Why We Lose to ALL of Them: The Common Thread

All four nemesis teams beat us primarily through **superior resource collection**. The evidence:

| Our Problem | Evidence |
|-------------|----------|
| **Disconnected harvesters** | We build 30-43 harvesters but collect 2-3x LESS Ti than opponents with 8-22 harvesters |
| **Resource hoarding** | We stockpile 3,000-18,000 Ti unspent while opponents keep <300 in bank |
| **Too few bots** | We max at 6-8 bots while opponents run 40-49 |
| **Conveyors used for navigation, not delivery** | Our conveyors face away from core (built as movement aids), not toward it |
| **No adaptation to map type** | Same strategy on economy maps, rush maps, fragmented maps |

### Maps Where ALL Nemeses Beat Us

| Map | The Defect | KCPC-B | One More Time | Polska Gurom | Total Losses |
|-----|-----------|--------|---------------|--------------|-------------|
| cold | 2 wins | 1 win | 1 win | - | 4 |
| galaxy | 1 win | 1 win | 1 win | - | 3 |
| face | 2 wins | - | - | 1 win (CD!) | 3 |
| landscape | - | 1 win | 1 win | 1 win | 3 |
| default_large2 | 1 win | 1 win | - | 1 win | 3 |

**Cold, galaxy, face, landscape, and default_large2** are the maps where nemeses consistently beat us.

### Are They Just Better Than Everyone, Or Do They Specifically Counter Us?

| Team | Elo | Rank | Better Than Us Overall? |
|------|-----|------|------------------------|
| The Defect | 1521 | ~100 | Yes (+33 Elo) |
| One More Time | 1523 | ~98 | Yes (+35 Elo) |
| KCPC-B | 1472 | ~136 | No (-16 Elo!) |
| Polska Gurom | 1476 | ~135 | No (-12 Elo!) |

**The Defect and One More Time are genuinely better teams** -- they beat everyone around our Elo level. They're 30-35 Elo above us.

**KCPC-B and Polska Gurom are at our level or BELOW** -- yet they beat us 100% of the time. This means they have a specific strategic advantage that counters our playstyle. Their strategies exploit our weaknesses (likely better conveyor chains, and in Polska Gurom's case, rush capability).

---

## What Should We Copy?

### From One More Time (best replay data):
1. **Connected conveyor chains** -- Every harvester must feed into a chain that reaches the core
2. **40+ bot count** -- Scale to bot cap aggressively, don't cap at 6-8
3. **Aggressive spending** -- Keep bank below 300 Ti, reinvest everything
4. **Foundry usage** -- Build foundries for additional resource processing on some maps

### From Polska Gurom:
1. **Rush capability on compact maps** -- Build offensive units when cores are close (face, battlebot)
2. **Map-aware strategy selection** -- Rush on compact maps, play economy on open maps
3. **Core Destroyed as a win condition** -- We currently win 0% by Core Destroyed; adding this doubles our win paths

### From The Defect:
1. **Broad map competence** -- Their economy works on ALL map types, not just favorable ones
2. **Consistency** -- 2,614 matches, stable strategy that works everywhere

### From KCPC-B:
1. **Unknown specific strategy** (limited data with only 62 matches), but their total domination (including two 0-5 sweeps) suggests they've solved something fundamental that we haven't

---

## What Should We Counter?

### Against Pure Economy Bots (One More Time style):
- **Rush them on compact maps.** One More Time builds ZERO turrets. A rush on face or hourglass could end games in 200 turns before their economy matters.
- **Contest ore deposits aggressively.** Place harvesters on high-value ore before they do.

### Against Rush Bots (Polska Gurom style):
- **Early defense on compact maps.** Place 1-2 sentinels near core on maps where cores are close (face, battlebot, hourglass).
- **Detect rush and switch to defense mode.**

### Against Broad-Spectrum Bots (The Defect style):
- **Must improve our own economy engine.** No shortcut -- we need better conveyor chains across all map types.

---

## Priority Actions

### Immediate (fixes 47% of our losses):
1. **Fix conveyor chain connectivity** -- Harvesters MUST feed into chains that reach the core. This is the #1 issue across ALL nemesis matchups.
2. **Increase bot cap** -- Scale from 6-8 to 30-40+ bots.
3. **Reduce resource hoarding** -- Spend aggressively, keep bank <500 Ti.
4. **Fix problem maps** -- galaxy (0-8), face (0-5), arena (0-4), cold (4-5 but losing to nemeses).

### Medium-term:
5. **Add rush capability** -- Build offensive units on compact maps (face, battlebot, hourglass).
6. **Add rush defense** -- Place sentinels near core on compact maps.
7. **Map-aware strategy selection** -- Detect map properties and adjust approach.

### Long-term:
8. **Foundry usage** -- Investigate and implement.
9. **Bridge building** -- For fragmented maps (shish_kebab, etc.).
10. **Dual competency** -- Win both Resource Victory AND Core Destroyed.

---

## Key Numbers

- **Our Elo:** 1488 (rank #134/573)
- **Net nemesis Elo:** 1498 avg (range: 1472-1523)
- **Our win rate vs nemeses:** 0% (0-14)
- **Our win rate vs everyone else:** 60% (24-16)
- **Maps lost to nemeses:** 49 out of 63 played
- **If we went 50/50 vs nemeses:** We'd gain ~40-50 Elo, reaching ~1530-1540 (Gold tier, rank ~90)

---

*Analysis compiled from API data, replay analysis, and match history. Data current as of 2026-04-06.*
