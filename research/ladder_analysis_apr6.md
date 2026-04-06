# Ladder Analysis & Strategy Intelligence — April 6, 2026
## Cambridge Battlecode 2026 | buzzing bees (1488 Elo, rank ~#134/573)

---

## Executive Summary

The Chrome browser is not accessible in this session (extension not connected), so live ladder data was not scraped directly. Instead this report synthesizes:
1. Existing research files (nemesis_analysis.md, ladder_deep_review.md, contender_scouting.md, strategic_assessment.md)
2. Full game spec review (all 19 docs.battlecode.cam pages)
3. Current bot architecture review (bots/buzzing/main.py v35, 833 lines)

**Key finding:** We have reached a clear ceiling at ~1488 Elo. Our bot's fundamental problem is not configuration — it is that we max out at 10 units while competitive peers run 20-40. The galaxy test confirms this directly: ladder_eco runs 40 units, mines 14,430 Ti; we run 10 units, mine 9,940 Ti.

---

## 1. Our Current Position (from existing API data, April 6)

| Metric | Value |
|---|---|
| Elo | 1488 |
| Rank | ~#134 / 573 |
| Record | 24W-30L (44.4%) |
| Recent 17-match window | 10W-7L (59%) — best streak |
| Current trend | FLAT — oscillating 1474-1498 for 29 matches |

### Nearby Ladder Teams

| Rank | Team | Elo | Matches | Note |
|------|------|-----|---------|------|
| 129 | SPAARK | 1499 | 2615 | Converged, rival |
| 130 | Ash Hit | 1496 | 2614 | Converged |
| 131 | oslsnst | 1493 | 2613 | Converged, 1-3 vs us |
| 132 | O_O | 1492 | 2614 | Converged |
| 133 | natto warriors | 1491 | 2613 | Converged |
| **134** | **buzzing bees** | **1488** | **54** | Only 54 matches — volatile! |
| 135 | Polska Gurom | 1476 | 2614 | 0-3 nemesis |
| 136 | KCPC-B | 1474 | 61 | 0-4 nemesis |
| 137 | Cenomanum | 1470 | 2614 | 2-2 even |
| 138 | Chameleon | 1469 | 2416 | Improving vs us (1-2, latest 4-1 win) |

**Critical: We have only 54 matches vs 2400-2600 for neighbors. Our Elo is still highly volatile — a good bot can rapidly jump up or down.**

---

## 2. The Top of the Ladder (Context from Sprint 3 Data)

| Rank | Team | Elo | Notes |
|------|------|-----|-------|
| 1 | Blue Dragon | ~2791 | Grandmaster — untouchable |
| 2 | Kessoku Band | ~2712 | Grandmaster — untouchable |
| 3 | something else | ~2531 | Grandmaster |
| 4 | MFF1 | ~2386 | Master — gatekeeper |
| 5 | bwaaa | ~2352 | Master — peaked 2432 |
| 6 | Dear jump | ~2330 | Master — solo player |
| 7 | Oxford | ~2327 | Master — peaked 2411 |
| 8 | food | ~2325 | Master — abandoned bot still running |
| 9 | Lorem Ipsum | ~2273 | Master — novice bracket |
| 10 | Jython | ~2266 | Master |

### What Top Teams Do (from replay analysis)

**Blue Dragon (2791):**
- 308 conveyors, 33 bridges, 22 harvesters, 20 armed sentinels
- 15+ builders active simultaneously with coordinated roles
- Wins via both Core Destroyed AND Resource Victory
- 30,000+ Ti collected by round 2000

**Kessoku Band (2712):**
- Wins Core Destroyed in 148-400 turns on aggressive maps
- 10 armed sentinels by round 148
- Also wins Resource Victory on economy maps

**One More Time (1523 — our nemesis):**
- 40-49 bots active (near unit cap)
- 200-600 conveyors forming dense chains
- 8-27 harvesters, ALL connected
- Keeps bank below 300 Ti — reinvests everything
- Zero sentinels/gunners — pure economy
- 3.14x more Ti than us with HALF our harvesters (22 vs 43) on cold

---

## 3. Why We're Stuck at 1488

### Root Cause: 10 Units Cap

The v35 galaxy test shows the core problem explicitly:
- **ladder_eco**: 40 units, 14,430 Ti mined — wins
- **ladder_rush**: 20 units, 5,470 Ti mined — wins  
- **buzzing v35**: 10 units, 9,940 Ti mined — loses

Even though we mine more than ladder_rush (9,940 vs 5,470), we lose because ladder_rush mines proportionally more relative to their unit count. The actual builder cap code:

```python
# expand (galaxy): cap = 3 if rnd<=30 else (6 if rnd<=150 else (9 if rnd<=400 else 12))
# econ_cap formula: min(vis_harv*3+4, max(6+rnd//200, 10))
```

These caps are bottlenecking us to 10 units total. Competitive bots run 20-49.

### The Five Loss Patterns

| Problem | Evidence |
|---------|---------|
| **Too few builders** | We max 6-8 units; opponents run 40+ |
| **Disconnected harvesters** | 22-43 harvesters but 2-3x less Ti mined than opponents with fewer |
| **Resource hoarding** | We stockpile 3,000-18,000 Ti while opponents keep <300 in bank |
| **No map adaptation for rush** | Core destroyed in 137 turns on face (Warwick CodeSoc) |
| **Galaxy/Face/Arena = 0% win** | 0-8, 0-5, 0-4 lifetime records |

### Nemesis Pattern (Combined 0-14)

| Nemesis | Elo | Our Record | Why They Beat Us |
|---------|-----|-----------|-----------------|
| The Defect | 1521 | 0-4 | Superior economy on ALL map types |
| One More Time | 1523 | 0-3 | Pure economy — 3.14x Ti with fewer harvesters |
| KCPC-B | 1472 | 0-4 | Lower Elo than us, but dominant — likely recent strong submission |
| Polska Gurom | 1476 | 0-3 | Dual strategy: rush on compact maps, economy on open maps |

**KCPC-B at 1472 Elo beats us 4-0** — they specifically counter our strategy, not generically better.

---

## 4. Map Intelligence

### Our Best Maps (prioritize winning these)

| Map | W-L | Win% |
|-----|-----|------|
| pls_buy_cucats_merch | 7-2 | 78% |
| sierpinski_evil | 6-2 | 75% |
| dna | 3-1 | 75% |
| hourglass | 6-3 | 67% |
| corridors | 4-2 | 67% |
| pixel_forest | 5-3 | 63% |
| default_small2 | 4-1 | 80% |

### Auto-Loss Maps (must fix these)

| Map | W-L | Notes |
|-----|-----|-------|
| **galaxy** | 0-8 | 40x40 expand map — builder cap bottleneck confirmed |
| **face** | 0-5 | Core destroyed twice (137t, 319t) — rush defense needed |
| **arena** | 0-4 | Unknown issue, 0 wins ever |
| shish_kebab | 1-6 | Core destroyed by Warwick CodeSoc at 190t |
| tree_of_life | 2-5 | Economy map — conveyor connectivity |
| wasteland | 1-4 | Economy map |
| landscape | 2-5 | Economy map — One More Time 3.14x our Ti here |

### Map Category Strategy (from top team analysis)

| Map Type | Win Condition | Examples | Our Status |
|----------|--------------|---------|-----------|
| **Aggressive** (compact, close cores) | Core Destroyed 150-400t | face, hourglass, corridors, gaussian | Need rush offense/defense |
| **Defensive** (large, separated) | Resource Victory 2000t | landscape, wasteland, settlement, cold | Need better economy |
| **Mixed** | Either works | arena, binary_tree, mandelbrot | Need adaptation |

**Key meta insight:** In a Bo5, 2-3 maps will go to 2000t (economy) and 2-3 will end in Core Destroyed (military). Teams that can only win ONE type cap out at 3-2. Top teams win both types.

---

## 5. Strategic Gaps vs Top Teams

### What We Have vs What We Need

| Capability | Our Bot (v35) | Competitive Min (~1600+) | Top Teams (2400+) |
|-----------|--------------|------------------------|-------------------|
| Builder cap | 10 units | 20-25 units | 40-49 units |
| Harvesters | 6-10 | 10-15 | 15-22 |
| Conveyors | ~50 | ~100 | 200-308 |
| Bridges | 0-2 (fallback only) | 5-10 | 20-33 |
| Armed sentinels | 0 (gunners w/o reliable ammo) | 2-3 armed | 10-20 armed |
| Foundries | 0 | 0-1 | 0-2 (rarely) |
| Rush capability | 0 (no offense) | Compact map aggression | Fast CD <400t |
| Map adaptation | Partial (tight/balanced/expand) | Basic (compact vs open) | Full per-map |

---

## 6. Non-Obvious Mechanics Found in Doc Review

These came from reading the full spec — may be underexploited:

### Economy Mechanics
1. **Destroy reverses scale** — Destroying enemy buildings reduces THEIR scale contribution. If we can reach and destroy an enemy conveyor, it cuts their future costs. Our attacker currently targets the core (500 HP), not infrastructure.

2. **Harvester load balancing** — Harvester "prioritises outputting in directions used least recently." If a harvester has two adjacent conveyors, it auto-alternates. We can put two conveyors adjacent to one harvester and it will split output automatically — no splitter needed for basic doubling.

3. **Resources transferred at round end** — Resources move after ALL units act. So a bot placed on a conveyor mid-round doesn't block that round's transfer.

4. **Turrets only accept resources when completely empty** — If a gunner has 1 ammo left, it won't accept a new stack of 2. It must fire first. This means gunner ammo can get "stuck" if they don't fire between deliveries.

### Combat Mechanics
5. **Builder bot blocks turret shots** — "If a builder bot stands on a building, turret attacks on that tile hit ONLY the builder bot." We can use our own builder bots as ablative shields in front of turrets to absorb incoming fire.

6. **Sentinel stun requires refined Ax ammo** — +5 action AND move cooldown only with refined Ax ammo. Ti ammo gives no stun. We can't access stun without a foundry.

7. **Gunner rotation costs global Ti** — Rotating a gunner costs 10 Ti from the GLOBAL pool, not the gunner's budget. If we're low on Ti, rotating gunners is expensive.

8. **Healing hits all entities on tile** — Heal costs 1 Ti and heals 4 HP to ALL friendlies on that tile. If a builder stands on a building, you heal both for 1 Ti.

9. **Launcher target is bot-passable, not just empty** — The launcher throw target must be a tile that builder bots can stand on (conveyor, road, allied core, etc.). Launching into an empty field tile fails.

### Infrastructure Mechanics
10. **Splitter input: back only** — Splitter accepts input ONLY from its back (direction opposite facing). This is critical: if you face the splitter NORTH, it only accepts input from the SOUTH side. Plan conveyor chains accordingly.

11. **Bridge target distance²≤9** — Bridge target within 3 tiles. Commonly miscalculated: tiles diagonally 2 steps away are distance² = 8, which qualifies. 3 tiles orthogonally = distance² = 9, which also qualifies.

12. **Walkable buildings on bot-occupied tiles** — You CAN build conveyors and roads on a tile with a builder bot standing on it. Useful for "trapping" a builder in place while you path around them.

13. **Enemy conveyors are walkable** — Builder bots can walk on ENEMY conveyors! This means enemy conveyor networks can be used for infiltration.

---

## 7. Actionable Intelligence for Our Bot

### Highest Priority Fixes (estimated Elo impact)

#### Fix 1: Raise Builder Cap Dramatically (+30-50 Elo)
**Problem:** We cap at 10 units. ladder_eco with 40 units beats us on galaxy mining 14,430 vs 9,940.
**Fix:** Remove or dramatically relax the unit cap. The econ_cap formula `vis_harv*3+4` is too conservative — it counts only visible harvesters (within core's r²=36 vision), missing distant harvesters.
**Target:** Allow 20-30 builders by round 300, scale to 40+ by round 600.

```python
# Current bottleneck: econ_cap = max(time_floor, vis_harv * 3 + 4) capped at 10
# Fix: count ALL allied buildings of type HARVESTER using global tracking via markers,
# or simply use a more aggressive time-based ramp:
# econ_cap = max(rnd//50 + 4, vis_harv * 3 + 4)  # grows to 44 by round 2000
```

#### Fix 2: Builder Count Persistence (or reduce cap sensitivity) (+15-25 Elo)
**Problem:** `vis_harv` only counts harvesters within core's vision. On galaxy (40x40), harvesters built far from core are invisible, giving false low reading that artificially caps builders.
**Fix:** Track `harvesters_built` globally (already done per-builder!) and use it in core's cap calculation. But core doesn't have access to individual builder state. Use marker system to communicate harvester count back to core.
**Quick fix:** Set a floor based on round number regardless of vis_harv:
```python
# Allow at least rnd//100 + 4 builders regardless of visible harvesters
time_floor = min(12 + rnd // 100, 40)  # grows from 12 to 40 over 2000 rounds
```

#### Fix 3: Bridge-First Expansion on Blocked Paths (+20-40 Elo)
**Problem:** Bridges only used as "fallback" in nav. Top teams (Blue Dragon: 33 bridges) use bridges as PRIMARY terrain crossing.
**Fix:** In `_nav()`, try bridge BEFORE road fallback when direct conveyor path is blocked. Specifically: if BFS can't find a path to target within X tiles, prefer bridge over road.
**Key insight:** A bridge costs 20 Ti + 10% scale but crosses walls. A road costs 1 Ti but doesn't. On complex maps, a bridge replaces 3-8 conveyors.

#### Fix 4: Rush Defense on Compact Maps (+15-25 Elo)
**Problem:** Core destroyed in 137t (face), 190t (shish_kebab), 319t (face). We build barriers but not enough early sentinels.
**Fix:** On compact maps (tight mode), spawn a sentinel near the core-facing direction by round 80-100. No ammo needed — an unarmed sentinel still blocks builder bots from standing on its tile.

Actually, our gunners serve this purpose — but they need to be placed earlier on tight maps:
```python
# Current: gunner_round = 150 if expand else 200
# Fix: gunner_round = 60 if tight else (100 if balanced else 150)
```

#### Fix 5: Arena Map (0-4) — Investigate (+5-15 Elo)
**Problem:** 0 wins ever on arena. We don't know why.
**Fix needed:** Run `cambc run buzzing starter arena --watch` and observe what's failing. Hypothesis: arena is 40x40 (expand mode) with isolated ore clusters requiring bridges.

#### Fix 6: Face Map Defense (0-5) — Rush Detection (+10-20 Elo)
**Problem:** Enemy core is very close on face. Need early defense.
**Fix:** Detect face-style maps (core distance < 15 tiles) and place 2 gunners near core by round 50. Also: barriers at distance 3-4 from core facing enemy.

#### Fix 7: Attacker Targets Infrastructure, Not Core (+10-20 Elo)
**Problem:** Our attacker walks to enemy core (500 HP, takes 250 attacks to kill). This is almost never useful.
**Better strategy:** Attacker should target enemy conveyors and harvesters (20-30 HP, take 10-15 attacks). Destroying an enemy harvester:
- Removes their income from that ore deposit
- Reverses 5% of their cost scale (they build cheaper going forward)
- Builder can then build OUR harvester on that tile
**Fix:** In `_attack()`, prioritize adjacent enemy non-core buildings over walking to core.

---

## 8. Meta Trends (from research synthesis)

### What's Working at our Elo (~1488)
1. Pure economy bots (One More Time style) dominate — just out-mine opponents
2. Aggressive spending — keep bank below 300 Ti, reinvest immediately
3. High unit counts — 20-40+ builders and turrets together
4. Connected conveyor chains — every harvester must reach core

### What's Being Ignored (potential edges)
1. **Axionite refining** — Tiebreaker #1 is total refined Ax delivered. Nobody builds foundries. Even 1 stack of refined Ax delivered wins TB#1 against zero-Ax opponents. But foundry +100% scale cost is steep.
2. **Launcher infiltration** — Launchers throw builder bots over walls. A builder inside enemy base can destroy enemy infrastructure with no cooldown (destroy is free). Top teams use 1-3 launchers "sparingly."
3. **Breach turrets** — Nobody uses breach. 40 direct + 20 splash in 180° cone, range r²=5. Strong vs building clusters and rushing bots. Could counter sentinel-heavy pushes.
4. **Walking on enemy conveyors** — Builder bots can walk on enemy conveyors. Infiltration through enemy supply lines is possible.

### Dual Competency Gap
The critical gap between our tier (1488) and Master tier (2200+):
- **Our tier:** Win by economy only OR lose — no Core Destroyed victories
- **Master tier:** Win by economy OR by military Core Destroyed
- **Top 3:** Win both modes on ALL map types

We currently win 0% of games by Core Destroyed. Adding even 1 CD win per match would significantly improve results on aggressive maps (face, hourglass, corridors).

---

## 9. Sprint 4 Deadline (April 11) Priorities

Given the April 11 Sprint 4 snapshot, these are the highest-ROI changes:

### Immediate (implement before April 11)
1. **Raise builder cap to 20-25 by default** — Single biggest Elo lever
2. **Fix galaxy/arena specifically** — 0-win maps that appear in matches regularly
3. **Earlier gunners on tight maps** (round 60 not 200) — Rush defense
4. **Fix econ_cap to use builder_count not vis_harv** — Core counting issue

### Medium-term (April 11-20, before qualifier)
5. **Implement armed sentinel** (splitter + branch + sentinel) — Already planned in armed_gunners_plan.md, but trigger at round 500 not 1000
6. **Bridge-first expansion** — Replace road fallback with bridge preference on blocked paths
7. **Attacker targets infrastructure** — Change _attack() to target conveyors/harvesters

### Nice-to-have
8. **Face map rush detection** — Early barriers + gunners when cores are close
9. **Axionite tiebreaker** — Minimal foundry setup on maps where we're likely to lose on Ti

---

## 10. Key Numbers to Track After v36 Submission

These metrics indicate whether improvements are working:

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| Unit count at round 500 | ~10 | 20-25 | Replay viewer |
| Ti mined at round 2000 | 9,940 (galaxy) | 14,000+ | Match results |
| Galaxy win rate | 0% | 30%+ | Match history |
| Face win rate | 0% | 20%+ | Match history |
| Arena win rate | 0% | 20%+ | Match history |
| Overall Elo | 1488 | 1550+ | Ladder |
| Core Destroyed wins | 0 | 2-3/week | Match results |

---

## 11. Intelligence Gaps (What We Still Don't Know)

Since the browser wasn't accessible, these remain unknown:

1. **Current KCPC-B Elo and match count** — They had 61-62 matches last we checked. With more matches they may have climbed significantly.
2. **New teams that appeared since our last check** — The ladder at rank 100-200 changes rapidly.
3. **Warwick CodeSoc strategy details** — They core-destroyed us in 137t on face. What are they doing?
4. **Top team submission frequency** — Do they update daily? How many versions per week?
5. **Any recent meta shifts** — Sprint 3 tournament was April 5. What won? Are there post-tournament strategy changes?

---

## Summary

**Our core problem is unit count.** We run 10 units while competitors run 20-40. This single factor explains:
- Galaxy: 0-8 (40x40 map, we need 30+ builders to cover it)
- Arena: 0-4 (similar issue)
- Economy losses (fewer builders = fewer harvesters = less Ti)

The fix is straightforward: raise the builder cap from 10 to 25-40. Everything else (conveyor chains, map adaptation, attacker logic) is secondary to having enough builders to cover the map.

**Three changes that could push us from 1488 to 1550+:**
1. Builder cap: 10 → 25+ (implemented in core spawning logic)
2. Earlier gunners on tight maps (round 60 not 200) to prevent face/shish_kebab rush deaths
3. Bridge-first expansion on blocked paths (replace road fallback with bridge preference)

These are small code changes with potentially large Elo impact. They should be implemented and tested before the April 11 Sprint 4 snapshot.

---

*Research compiled from: nemesis_analysis.md, ladder_deep_review.md, contender_scouting.md, strategic_assessment.md, v35_galaxy_test.md, armed_gunners_plan.md, full docs.battlecode.cam spec review, bots/buzzing/main.py v35 analysis.*  
*Date: 2026-04-06 | Researcher Agent*
