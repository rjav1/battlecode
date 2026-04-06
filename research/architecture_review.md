# Architecture Review: buzzing v44 Feature Cost/Benefit Analysis

**Date:** 2026-04-06
**Reviewer:** architecture-reviewer agent
**Bot:** bots/buzzing/main.py (~1364 lines, v44)

## Executive Summary

Our bot has 8 distinct features beyond core mining. **Most are net-negative for Ti production.** Simple bots with 3-4 builders and zero features outmine us 2-4x. The root cause: every feature costs scale (+1% per conveyor, +20% per builder, +10% per gunner, etc.) and diverts builder-turns from harvester placement. Features must produce MORE Ti than they cost in scale inflation and opportunity cost.

---

## Feature-by-Feature Analysis

### 1. Armed Sentinel (lines 377-787)

**Cost:** +21% scale minimum (splitter 1% + branch conveyor 1% + sentinel 20%), 62 Ti materials, ~10-20 rounds of builder time walking/building, PLUS destroys an existing conveyor (temporarily breaking a chain).

**Benefit:** Area denial IF it fires. Requires ammo delivery via splitter chain.

**Evidence:**
- Sentinel timing at round 500 with 5+ harvesters requirement
- From battlecode_learnings: "Sentinels without ammo are 30 Ti + 20% scale WASTED"
- The splitter-splice approach DESTROYS a working conveyor to insert a splitter -- this breaks resource flow during construction
- In replay analysis, our 1 sentinel did nothing while Polska Gurom's 6 sentinels defended their core
- The armed sentinel code is 125 lines (662-787) of complex multi-step stateful logic that frequently fails (multiple `_sentinel_step = 5` bailout paths)

**Verdict: REMOVE.** 125 lines of complexity for a feature that costs 21%+ scale, breaks an existing chain, and rarely fires. The builder spends 10-20 rounds on this instead of placing harvesters. If we want defense, simple unarmed gunners (10 Ti, +10% scale) placed opportunistically are cheaper and proven more effective (gunners beat sentinels 3-0 in BFS testing per learnings).

---

### 2. Attacker Raider (lines 357-364, 1067-1163)

**Cost:** 1 builder permanently diverted from mining (20% of builder workforce if 5 builders). Roads built for movement (+0.5% each). ~100 lines of code.

**Benefit:** Destroy enemy infrastructure (harvesters, conveyors, foundries).

**Evidence:**
- Triggers at round 500 with 4+ harvesters, assigned to id%6==5 (1 in 6 builders)
- From elo_collapse_analysis: "We have zero ability to threaten opponent cores. Every single game win we have is via resource tiebreaker at round 2000."
- From battlecode_learnings: "97% of games end by resource tiebreaker -- we have NEVER destroyed an enemy core"
- The attacker uses `_nav_attacker` which builds roads (not conveyors) -- these roads cost Ti and scale but produce zero resource flow
- On small maps the attacker might reach enemy infra; on large maps it wanders for hundreds of rounds
- The attacker's 2 damage per attack (costs 2 Ti + action cooldown) vs a 20 HP conveyor = 10 attacks = 20 Ti + 10 rounds to destroy ONE conveyor. Not economical.

**Verdict: REMOVE.** The attacker never produces positive ROI. It diverts a builder from mining for 1500 rounds, builds wasteful roads, and does negligible damage. The 2-damage builder attack is too weak to matter. If we ever want offense, a launcher-based approach would be far more effective, but offense is not our bottleneck -- economy is.

---

### 3. Bridge Shortcuts (lines 292-344)

**Cost:** 20 Ti per bridge + 10% scale each. Code complexity: ~50 lines.

**Benefit:** Skip conveyor chains for distant harvesters by bridging directly to existing chain or core.

**Evidence:**
- Triggers after harvester placement (`_bridge_target` set at line 420)
- Only attempts bridge if ore is >3 tiles from core (dist_sq > 9)
- From battlecode_learnings: "Bridge expansion: SELECTIVE. +70% Ti on settlement (wall-heavy) but -33% on open maps. 2-3 bridges max, not 33"
- Polska Gurom uses 29-33 bridges effectively -- but their entire economy is bridge-based, not a bolt-on
- Our bridge attempts often fail (multiple try/except blocks, fallback paths)
- The chain-join logic (find nearest allied conveyor closer to core) is sound in theory but unreliable in practice

**Verdict: MODIFY (simplify).** Keep the concept but simplify drastically. Current implementation tries chain-join first, then core-tile bridge, with complex iteration. Reduce to: if harvester is >5 tiles from core AND a bridge can reach any core tile, build it. Remove chain-join logic (too unreliable). Cap at 3 bridges total. ~15 lines instead of 50.

---

### 4. Chain-Fix Mode (lines 404-407, 1166-1218)

**Cost:** Builder walks backward along recorded path fixing conveyor directions. ~50 lines. Diverts builder from mining for potentially many rounds.

**Benefit:** Fix winding conveyor chains that have direction changes (zigzags don't deliver resources).

**Evidence:**
- Only triggers for first 2 harvesters if path has 3+ direction changes
- From battlecode_learnings: "v15: Chain-fix for winding paths (cold 5K->23K Ti)" -- this was a significant improvement historically
- But also: "diagonal gaps are tolerable (speed > connectivity, proven v32)"
- The fix_path recording (line 529-530) adds overhead to every nav step
- Chain-fix walks the builder BACKWARD, away from new ore, consuming rounds

**Verdict: MODIFY (keep but limit).** The chain-fix had proven value on cold. But limit it: only fix chains for the FIRST harvester (not first 2), and cap fix-walk at 8 steps max. The builder should get back to mining quickly. Remove the fix_path recording after harvester 1 to save overhead.

---

### 5. Ax Tiebreaker (lines 387-395, 789-1007)

**Cost:** 1 builder diverted at round 1800+. Harvester (+5%), foundry (+100%!!), output conveyor (+1%) = +106% scale. 60+ Ti in materials. ~220 lines of complex multi-step code.

**Benefit:** Mine refined axionite for tiebreaker #1 (refined Ax delivered > Ti delivered).

**Evidence:**
- From battlecode_learnings: "Axionite-first: RULED OUT. Ax never mined, foundry +100% scale is a trap. Top teams are right to skip it"
- "0 Ax mined in all tests"
- "Nobody uses axionite, foundries, gunners, or breaches at top level"
- The Ax builder has a known oscillation bug (stuck bouncing between 2 tiles for 200 rounds, documented in local_bot_losses_debug.md)
- Foundry costs +100% scale -- at round 1800, this inflates ALL building costs for the final 200 rounds
- Even if it works perfectly, 200 rounds of foundry output = ~50 stacks = maybe 50 refined Ax. TB#1 only matters if Ti is tied.

**Verdict: REMOVE.** 220 lines of buggy code for a feature that never works, costs +106% scale, and addresses a tiebreaker that almost never matters (Ti collected is virtually never exactly tied). The foundry's +100% scale alone makes this net negative even if it functioned perfectly.

---

### 6. Barriers (lines 246-288 early barriers, 397-402 + 1009-1064 mid-game barriers)

**Cost:** 3 Ti per barrier, +1% scale each. Dynamic cap 6-15 barriers = 6-15% scale, 18-45 Ti. ~80 lines total.

**Benefit:** Block enemy builder/attacker access to core area.

**Evidence:**
- Early barriers (round <=30): 2 barriers near core toward enemy, costs 6 Ti + 2% scale
- Mid-game barriers (round 80+): up to 6-15 barriers based on Ti bank
- From battlecode_learnings: "Barriers: 30 HP for 3 Ti (best HP/Ti ratio). NOT walkable -- leave gaps"
- From elo_collapse_analysis: 15 core destruction losses, maps like face/galaxy/shish_kebab
- barrier_wall bot (which beats us) uses 10-15 barriers as its ONLY defense
- BUT: our barriers are placed opportunistically when builder happens to be near core, not strategically
- The placement code (candidates at dist 2-3 from core, perpendicular spread) is reasonable

**Verdict: KEEP (minor simplify).** Barriers are cheap (3 Ti, 1% scale) and provide real defensive value. The early barrier code is fine. Simplify mid-game barriers: remove the dynamic cap (fixed cap of 8), remove the Ti>50 gate (always place if affordable), and reduce placement code. Net: ~40 lines instead of 80.

---

### 7. Spend-Down Gunners (lines 347-354)

**Cost:** 10 Ti + 10% scale per gunner. Diverts builder from mining temporarily.

**Benefit:** Convert hoarded Ti into defense when bank is high (Ti>300, round>300).

**Evidence:**
- From battlecode_learnings: "V45 Breakthrough: Spend-down defense: builders near core build gunners when Ti>300, round>300, harvesters>=3"
- Gunners are the cheapest turret (10 Ti vs sentinel 30 Ti vs breach 15+10)
- Gunner damage: 10 per shot (30 with Ax ammo), fires along forward ray
- BUT: gunners need ammo (2 Ti stacks per shot). Without ammo delivery chain, they're 10 Ti + 10% scale wasted
- In practice, gunners near core DO get ammo from passing conveyor chains
- Cap of 5 gunners = up to 50% scale -- significant

**Verdict: MODIFY.** Keep spend-down gunners but reduce cap from 5 to 2-3. The first 1-2 gunners near core provide real defense for 20 Ti + 20% scale. Gunners 3-5 add diminishing returns (50% scale for marginal coverage). Also raise Ti threshold from 300 to 500 -- we need to be truly hoarding before diverting builders.

---

### 8. Gunner Builder Role (lines 365-374, id%5==1)

**Cost:** 20% of builders permanently assigned to gunner placement. Builder diverted from mining after round 30-150.

**Benefit:** Dedicated gunner placement ensures turrets get built.

**Evidence:**
- Assigns id%5==1 builders to gunner duty (1 in 5 builders)
- With spend-down gunners (feature 7) already covering gunner placement opportunistically, this dedicated role is redundant
- A dedicated gunner builder walks toward core, places gunner, then... does what? Goes back to mining? The code just keeps trying `_place_gunner` every round.
- Combined with spend-down gunners, this means 2 different code paths trying to build the same thing

**Verdict: REMOVE.** Redundant with spend-down gunners. Remove the dedicated gunner builder role entirely. Spend-down gunners (feature 7, modified to cap 2-3) handle gunner placement when Ti is available. This frees 20% of builders to mine full-time.

---

## Summary Table

| # | Feature | Lines | Scale Cost | Ti Cost | Verdict | Expected Impact |
|---|---------|-------|------------|---------|---------|-----------------|
| 1 | Armed Sentinel | 125 | +21%+ | 62 Ti | **REMOVE** | +5-10% Ti (builder freed) |
| 2 | Attacker Raider | 100 | +roads | builder-turns | **REMOVE** | +5% Ti (builder freed) |
| 3 | Bridge Shortcuts | 50 | +10% each | 20 Ti each | **MODIFY** | Neutral (simpler code) |
| 4 | Chain-Fix | 50 | 0 | builder-turns | **MODIFY** | +2% Ti (faster return to mining) |
| 5 | Ax Tiebreaker | 220 | +106% | 60+ Ti | **REMOVE** | +3-5% Ti (builder freed, scale saved) |
| 6 | Barriers | 80 | +6-15% | 18-45 Ti | **KEEP** | Neutral (defensive value) |
| 7 | Spend-Down Gunners | 8 | +10-50% | 10-50 Ti | **MODIFY** | +2% (fewer wasted gunners) |
| 8 | Gunner Builder Role | 10 | 0 direct | builder-turns | **REMOVE** | +5% Ti (builder freed to mine) |

**Total lines removed:** ~455 lines (from ~1364 to ~910)
**Total scale saved:** ~30-50% per game (sentinel, attacker roads, Ax foundry, excess gunners)
**Builders freed:** 2-3 builders return to full-time mining

---

## Recommended Simplified Architecture

```
Core:
  - Spawn builders (map-adaptive cap: tight 3/5/8, balanced 3/4/6/8, expand 3/5/8/12)
  - Convert refined Ax (if any arrives)

Builder Bot:
  1. Early barriers (round <=30, 2 barriers toward enemy) -- KEEP
  2. Spend-down gunners (Ti>500, round>300, cap 2) -- SIMPLIFIED
  3. Mid-game barriers (round 80+, cap 8) -- SIMPLIFIED  
  4. Build harvester on adjacent ore -- CORE FUNCTION
  5. Simple bridge shortcut (harvester >5 tiles from core, bridge to core) -- SIMPLIFIED
  6. Chain-fix (first harvester only, max 8 steps) -- SIMPLIFIED
  7. Pick ore target (wall-density-adaptive scoring) -- KEEP
  8. Navigate with d.opposite() conveyors -- KEEP
  9. Explore (sector-based) -- KEEP

Gunner:
  - Fire at target -- KEEP

REMOVED:
  - Armed sentinel (all 125 lines)
  - Attacker raider (all 100 lines)  
  - Ax tiebreaker (all 220 lines)
  - Gunner builder role (id%5==1 check)
```

---

## Expected Elo Impact

**Conservative estimate: +30-50 Elo**

Reasoning:
- Freeing 2-3 builders from non-mining roles should increase Ti mined by 15-25%
- Removing 30-50% scale inflation makes every harvester and conveyor cheaper
- From elo_collapse_analysis: "3-2 matches: 21W-27L -- small economy improvements flip many of these"
- Each flipped 3-2 loss to 3-2 win = ~6 Elo points
- Flipping 5-8 of those close matches = +30-50 Elo
- This would move us from ~1438 to ~1470-1490 range (Silver tier)

**Risk:** Removing sentinel/gunner defense could increase core destruction losses on rush maps. Mitigated by keeping barriers + 2 spend-down gunners.
