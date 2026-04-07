# V62 Addition Candidates — Smallest Possible +2pp Features

**Date:** 2026-04-06  
**Context:** V61 = 68%, all cut attempts failed, bridge is load-bearing. Goal: push past 70%.  
**Constraint:** Any addition must pass dual 50-match at >= 66%. Risk budget is small.

---

## Diagnostic: What Beats Us and Why

### V61 known loss patterns (50-match baseline)

| Opponent | V61 W% | Primary loss cause |
|----------|--------|--------------------|
| smart_eco | 50% | Pure eco bot — matches our mining, wins on tiebreaker |
| rusher | 33% | Overwhelms tight maps before we have defenses |
| smart_defense | 66% | Occasional galaxy/binary_tree map issues |
| ladder_eco | 75% | Resource hijacking on shared ore (dna, gaussian) |
| binary_tree | 0% as A | Map geometry — ore on far branch unreachable from A side |

### V62 regression analysis (bridge removal)
Bridge removal caused smart_eco to drop from 50%→12% and tight maps to collapse to 44%. This means: **the bridge shortcut is providing ~8pp of value specifically vs high-economy opponents on tight maps**. The chain-join bridge on tight maps shortcuts 2-3 conveyor hops, accelerating delivery when ore is close to core. This is the correct behavior on non-corridor tight maps.

### Root economic gap
smart_eco (our #1 loss driver) uses identical core nav logic but:
1. No markers (saves ~0.5pp scale inflation per game)
2. Builds Ax harvesters freely (our +50000 penalty keeps us off Ax)
3. Simpler explore (no sector spread, just rotate 150 rounds)

Matching smart_eco perfectly → 50% win rate. To beat it we need an economic edge OR military pressure.

---

## Candidate 1: Ti Spend-Down (Raise Builder Cap When Bank > 800)

**Hypothesis:** When `Ti_bank > 800` and builders < 15, we're hoarding. Spawning extra builders converts idle Ti into ore coverage.

**Current behavior:** Hard cap in `_core` = 8 (balanced), 15 (expand), 8 (tight) by late game. `econ_cap = max(time_floor, vis_harv*3+4)`. With 5 harvesters: econ_cap=19, hard_cap=8 → spawns stop at 8.

**Proposed change:** When `Ti > 800`, raise effective cap by 2-3:
```python
ti = c.get_global_resources()[0]
if ti > 800:
    cap = min(cap + 3, 15)  # spend-down: extra builders when flush
```

**Why it might work:** On settle/galaxy expand maps where Ti accumulates late (19240 mined on cold, 27960 on settlement), extra builders find and harvest distant ore sooner. This specifically helps vs turtle (passive eco) and smart_eco (neck-and-neck economy) where late-game Ti advantage decides.

**Why it might not work:** Scale inflation. Each builder (+20%) + their conveyors raises future costs. At scale 3.5x, builder costs 105 Ti, conveyors cost 10.5 Ti. Extra builders may spend more in scale taxes than they produce. Also, `econ_cap` already allows this if vis_harv*3+4 > time_floor.

**Risk level: Low.** 3-line change. Can gate behind `rnd > 300` to avoid early-game scale blowup.

**Estimated gain: +1-3pp** vs turtle, smart_eco on expand maps. Likely neutral on tight maps.

---

## Candidate 2: Sentinel Ammo Delivery (Late-Game Area Denial)

**Hypothesis:** Sentinel placed near enemy approach + 10 Ti ammo stacks → denies late-game pushes and adds Elo pressure. Top-team estimate: +20-30 Elo.

**Current state:** V61 handles `EntityType.SENTINEL` (fires if ammo >= 10) but never builds sentinels. This is dead code — the feature was removed in earlier version.

**What's required:**
1. Core spawns 1 sentinel (cost: 30 Ti base, +20% scale) at round 800+ in expand/balanced mode
2. One builder routes a conveyor from Ti chain to sentinel's non-facing side
3. Sentinel faces enemy direction (from `_get_enemy_direction`)

**Why it might work:** Sentinel vision r²=32 (extremely long range). With Ti ammo, it suppresses enemy builder bots approaching our ore. Against rusher and ladder_rush (2W-3L combined in V61), a sentinel could block the approach vector.

**Why it might not work:**
- We already removed sentinel from V37 — it was net neutral then (sentinels without ammo delivery = wasted 30 Ti)
- Sentinel costs 30 Ti + 20% scale at round 800 scale is ~4x → ~120 Ti + 20% = +48 Ti scale tax. Very expensive.
- Ammo delivery requires dedicated conveyor routing toward sentinel, which takes builder turns away from ore
- We don't build sentinels NOW, so adding it risks regression on all the maps where V61 is stable

**Risk level: High.** Requires 40-60 lines of new code. Scale inflation concern. Previously removed for reason.

**Estimated gain: +0-3pp** on maps where enemy approaches. Net uncertain.

---

## Candidate 3: Raise Balanced/Tight Builder Cap (6→8 early, not just late)

**Hypothesis:** Current balanced cap: 3 until rnd 25, 4 until rnd 100, 6 until rnd 300, 8 after. Smart_eco spawns 4 by rnd 30, 6 by rnd 100. We're 2 builders behind at every milestone.

**Proposed change:**
```python
# balanced: 4 by rnd 25, 6 by rnd 100, 8 after (matches smart_eco timing)
cap = 4 if rnd <= 25 else (6 if rnd <= 100 else 8)
```

**Why it might work:** 2 extra builders in early game = 2 more harvesters by round 100. On balanced maps (55% in V62, was ~70% in V61), those harvesters produce ~1000 Ti extra by round 500. This is a direct eco parity fix vs smart_eco.

**Why it might not work:** `econ_cap = max(time_floor, vis_harv*3+4)` throttles spawns based on visible harvesters. If vis_harv=0, econ_cap=4 regardless. The throttle exists to prevent over-building before ore is found. Raising the hard cap may not help if econ_cap is the binding constraint. Also: 2 extra early builders = +40% scale before first harvester, making first harvester (and all conveyors) more expensive.

**Risk level: Low.** 2-line change.

**Estimated gain: +1-2pp** on balanced maps if econ_cap allows. Could be neutral if throttle is binding.

---

## Candidate 4: Axionite Harvester Relaxation

**Hypothesis:** We penalize Ax ore heavily (+50000 score). Smart_eco takes all ore including Ax freely. On Ax-rich maps, we skip ore tiles that smart_eco claims, leaving us with fewer harvesters.

**Current logic:**
```python
if c.get_tile_env(t) == Environment.ORE_AXIONITE:
    score += 50000  # Strongly prefer Ti — raw Ax to core is DESTROYED
```

**The problem with Ax:** Raw axionite delivered to core IS destroyed — but the HARVESTER still contributes to unit count (tiebreaker 3) and the raw Ax stays in storage (tiebreaker 4). We lose Ti tiebreaker (tiebreaker 2) but gain axionite tiebreaker (4). On maps with more Ax than Ti, claiming Ax harvesters is strictly better than leaving them unclaimed.

**Proposed change:** Reduce Ax penalty from +50000 to +5000 (still prefer Ti but take Ax when Ti is scarce):
```python
if c.get_tile_env(t) == Environment.ORE_AXIONITE:
    score += 5000  # prefer Ti but Ax is better than empty
```

**Why it might work:** On Ax-heavy maps (butterfly, settlement parts), we currently yield ore tiles to smart_eco. Taking them costs nothing extra (same conveyor infrastructure) and adds harvester count + raw Ax to tiebreakers.

**Why it might not work:** Raw Ax delivered to core IS destroyed (official rule). If an Ax conveyor chain accidentally reaches the core, all that raw Ax is gone. The penalty exists for a reason. Risk of chain confusion on maps with mixed Ti/Ax ore where chain routing might cross.

**Risk level: Low-Medium.** 1-line change but behavior change on Ax-heavy maps.

**Estimated gain: +1-2pp** on Ax-rich maps.

---

## Candidate 5: Binary_Tree Fix (Player A Geo Bug)

**Hypothesis:** 0% as player A on binary_tree — unreachable ore branch. We build conveyors into a dead-end branch and miss the main ore. A targeted fix could recover 2-3 matches per 50.

**What we know:** binary_tree has ore clusters on "branch tips". Player A core is at a position where the branch toward the nearest ore tip requires walking through a narrow corridor that may be blocked by initial conveyor placement. V61 went 0W-5L on binary_tree (from V61 and V62 data combined).

**Proposed fix:** Hard to diagnose without replays. Likely requires:
1. Don't place conveyors that block your own future movement path
2. BFS pathing already handles walls — the issue may be builder getting stuck in a dead-end branch

**Risk level: Unknown.** Need replay analysis. Could be 1-line fix (adjust BFS cost) or could require structural change.

**Estimated gain: +2-4pp** if fixed — binary_tree appears in ~10% of test matches.

---

## Recommendation: Implementation Order

### Priority 1: Candidate 1 (Ti spend-down) — implement as V63

**Rationale:** 3-line change, lowest risk, directly addresses late-game Ti accumulation which is confirmed by high mining numbers (19240-37800 Ti in wins). Gate behind `rnd > 300 and Ti > 800` to avoid early scale blowup.

```python
# In _core, after computing cap:
ti = c.get_global_resources()[0]
if ti > 800 and rnd > 300:
    cap = min(cap + 3, 15 if self.map_mode == 'expand' else 12)
```

### Priority 2: Candidate 3 (Balanced builder cap) — implement alongside V63

**Rationale:** 2-line change, matches smart_eco's proven timing. Addresses eco gap directly. Low risk — econ_cap is the safety valve.

### Priority 3: Candidate 4 (Ax relaxation) — implement as V64 if V63 passes

**Rationale:** 1-line change, addresses ore yield on Ax-heavy maps. But needs isolation testing first (butterfly, settlement replays).

### Deprioritize: Sentinel ammo delivery

**Rationale:** Previously removed for reason. 40-60 lines. Scale cost is severe (~120+ Ti at late-game scale). The net gain is uncertain and the risk of regression on currently-stable maps is high. Only revisit if Priority 1-3 stall.

---

## Expected V63 Target

If Ti spend-down + balanced cap raise both work:
- Expand maps: +3-5pp (more late builders when Ti > 800)
- Balanced maps: +2-3pp (faster builder ramp matches smart_eco)
- Tight maps: neutral (cap already hits econ_cap ceiling faster)
- Expected: V63 = 70-72%

**Threshold: must be >= 66% (V61's floor).**
