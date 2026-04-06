# vs Balanced Bot — Deep Test Analysis
Date: 2026-04-06

## Test Results (seed 1, all maps)

| Map | Winner | Buzzing Ti mined | Balanced Ti mined | Buzzing Bldgs | Balanced Bldgs |
|-----|--------|-----------------|-------------------|---------------|----------------|
| arena | **balanced** | 4,970 | 19,770 | 206 | 145 |
| gaussian | **balanced** | 13,540 | 29,740 | 248 | 112 |
| binary_tree | **balanced** | 4,960 | 18,330 | 431 | 171 |
| default_medium1 | **buzzing** | 16,670 | 29,780 | 229 | 143 |
| galaxy | **balanced** | 3,730 | 9,920 | 362 | 271 |
| settlement | **buzzing** | 10,310 | 9,630 | 559 | 251 |

**Score: buzzing 2-4 balanced**

## Economy Gap

Balanced consistently mines ~2x more Ti than buzzing despite having fewer buildings and fewer units (always exactly 5 units). This is the core problem.

| Map | Balanced/Buzzing mining ratio |
|-----|-------------------------------|
| arena | 3.98x |
| gaussian | 2.20x |
| binary_tree | 3.70x |
| default_medium1 | 1.79x (buzzing wins but still lags!) |
| galaxy | 2.66x |
| settlement | 0.93x (buzzing wins here) |

## What Balanced Does That We Don't

### 1. Hard Cap of 4-5 Builders — The Key Difference
Balanced spawns **max 4 builders** until round 400, then 5. It never spawns more.
Buzzing spawns many more (16-19 units observed). 

**This is the root cause.** Every extra builder costs 30+ Ti and +20% scale. Balanced uses that Ti to afford more harvesters earlier.

Balanced builder cost math (4 builders):
- Builder 1: 30 Ti, scale 1.2
- Builder 2: 36 Ti, scale 1.44
- Builder 3: 52 Ti, scale 1.73
- Builder 4: 62 Ti, scale 2.07
- Total: ~180 Ti on builders

Buzzing with 16 builders: scale has ballooned enormously, harvesters cost 3-4x more.

### 2. Simpler Conveyor Strategy — d.opposite() Only
Balanced always places conveyors facing `d.opposite()` (back toward where it came from = facing the resource source). This creates clean chains that actually flow. Buzzing's BFS nav + conveyor placement may create broken chains or waste Ti on conveyors that don't connect.

### 3. No Wasted Resources on Complex Features
Balanced doesn't have:
- Sentinel placement logic
- Bridge shortcuts
- Chain-fix mode
- Axionite tiebreaker logic (until very late)
- Armed sentinels

All these features cost Ti and builder action turns that balanced spends on harvesters.

### 4. Defender Role — Barriers Precisely Placed
Balanced dedicates 1 builder (id%4==0) to building 4 barriers at distance 3-4 from core in enemy direction. This is cheap (1 Ti each after multiplier) and provides defense without wasting builder turns on complex logic.

### 5. Attacker After Round 400
Balanced sends an attacker toward enemy core after round 400. Buzzing waits until round 500 with stricter conditions. Minor difference but attacker disruption can matter.

## Why Buzzing Loses on Specific Maps

### arena (worst loss: 4x mining deficit)
- Arena is a tight map (small) — buzzing spawns up to ~cap 18 builders
- Scale gets destroyed from over-building
- Balanced's 4-builder limit keeps scale low = cheap harvesters
- Also: arena likely has limited ore close to core — buzzing's many builders and conveyors waste Ti

### binary_tree (3.7x deficit)
- Complex maze map — buzzing's BFS nav probably builds many conveyors trying to navigate walls
- Lots of buildings (431 vs 171!) — buzzing is drowning in conveyor roads
- Balanced's simple opposite-conveyor + explore logic may work better in mazes

### galaxy (2.7x deficit)
- Large open map — buzzing goes expand mode with aggressive builder spawning
- Despite more builders, much less ore mined (3,730 vs 9,920)
- Galaxy may have ore clusters far from core where balanced's simpler pathfinding still works

### settlement, default_medium1 (buzzing wins)
- These appear to be maps where buzzing's BFS nav pays off despite scale cost
- Or maps where ore is positioned such that chain connectivity matters
- Settlement: buzzing mines slightly more despite far more buildings (559 vs 251!)

## Root Causes — Priority Order

1. **Builder count too high** — scale destruction from spawning 10-19 builders makes harvesters cost 3-5x more, collapsing economy. Balanced's 4-builder cap is the secret.

2. **Ti spent on conveyors/roads** — buzzing builds 2-3x more buildings than balanced but mines less. The conveyor chains may not be flowing properly or are overly long.

3. **No wasted turns on complex features** — balanced's simplicity means every action-turn goes toward mining. Buzzing's sentinel, bridge, chain-fix logic consumes builder time.

4. **Axionite bot never finds Ax tiles** — the `[AX] ax_tiles=[]` log spam shows the Ax tiebreaker builder oscillates back and forth finding no Ax ore. This wastes a builder's late-game turns.

## Actionable Fixes

### High Priority
1. **Reduce max builders to 4-5 total** on balanced/tight maps — match balanced's discipline. The econ_cap formula needs a hard cap override: never exceed 5 builders on <1000 tile maps.
2. **Audit conveyor chain connectivity** — are conveyors actually flowing to core or building dead-end chains?
3. **Fix Ax tiebreaker builder** — if no Ax ore visible after 10 rounds of searching, abandon and mine Ti instead.

### Medium Priority  
4. **Profile balanced vs tight maps separately** — balanced wins on arena (tight) with only 4 builders; our tight cap of 18 is way too high.
5. **Consider simpler conveyor strategy** — d.opposite() facing may outperform BFS chain-building in terms of actual resource flow.

## Key Insight

Balanced wins not because it's smarter — it wins because it's disciplined. 4 builders, simple conveyors, harvesters close to core. Economy scales linearly instead of collapsing under scale multiplier pressure. Our complex features (sentinels, bridges, chain-fix) are luxuries that hurt us by:
- Increasing builder count (scale)
- Consuming builder action-turns
- Spending Ti that should go to harvesters
