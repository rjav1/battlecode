# Replay Analysis - April 6, 2026

## Matches Analyzed

### Match 1: Polska Gurom (1487) vs buzzing bees (1493) -- Loss 3-2
- Match ID: 03efbb2c-0e29-4a81-948d-44d75edbccce
- Our version: MAIN V40
- Elo change: -3.5

| # | Map | Winner | Condition | Turns |
|---|-----|--------|-----------|-------|
| 1 | mandelbrot | Polska Gurom | Resource Victory | 2000 |
| 2 | binary_tree | Polska Gurom | **Core Destroyed** | 1300 |
| 3 | hooks | buzzing bees | Resource Victory | 2000 |
| 4 | default_medium1 | buzzing bees | Resource Victory | 2000 |
| 5 | wasteland_oasis | Polska Gurom | Resource Victory | 2000 |

### Match 2: MergeConflict (1499, NOVICE) vs buzzing bees (1502) -- Loss 4-1
- Match ID: 4017ade0-25f1-435f-98a0-bc172ff5062b
- Our version: MAIN V40
- Elo change: -9.8

| # | Map | Winner | Condition | Turns |
|---|-----|--------|-----------|-------|
| 1 | socket | MergeConflict | Resource Victory | 2000 |
| 2 | hooks | MergeConflict | Resource Victory | 2000 |
| 3 | wasteland_oasis | MergeConflict | Resource Victory | 2000 |
| 4 | face | MergeConflict | Resource Victory | 2000 |
| 5 | hourglass | buzzing bees | Resource Victory | 2000 |

---

## Detailed Observations

### Polska Gurom - Game 2 (binary_tree, Core Destroyed at round 1300)

**Round 389 snapshot:**

| Stat | Polska Gurom (G) | buzzing bees (S) |
|------|------------------|------------------|
| Titanium | 1 | 4,050 |
| Ti collected | 1,200 | 3,530 |
| Bots | 2 | 8 |
| Roads | 31 | 0 |
| Conveyors | 4 | 30 |
| Bridges | 29 | 0 |
| Splitters | 1 | 0 |
| Harvesters | 5 | 7 |
| Sentinels | 2 | 0 |
| Gunners | 0 | 0 |

**Round 1117 snapshot (183 rounds before core death):**

| Stat | Polska Gurom (G) | buzzing bees (S) |
|------|------------------|------------------|
| Titanium | 294 | 10,408 |
| Ti collected | 6,640 | 10,780 |
| Bots | 2 | 10 |
| Roads | 25 | 0 |
| Conveyors | 9 | 101 |
| Bridges | 33 | 1 |
| Harvesters | 5 | 13 |
| Sentinels | 6 | 1 |
| Barriers | 0 | 1 |

**Key findings - Polska Gurom game:**
1. **We had massively more resources (10,408 Ti vs 294 Ti) but still lost by core destruction.** We are hoarding titanium and not spending it on defense or offense.
2. **101 conveyors vs their 9** -- we are over-building conveyors by 10x. Each conveyor costs +1% scaling. At 101 conveyors that's +101% cost scaling just from conveyors alone.
3. **Polska Gurom uses bridges (33) + roads (25) instead of conveyors.** Bridges cost more upfront but don't need chains of conveyors. Roads are only 1 Ti each (+0.5% scale).
4. **6 sentinels vs our 1** -- Polska Gurom invested heavily in defense. Their sentinels formed a line defense that destroyed our builder attackers and eventually let them push to our core.
5. **We spawned 10 bots, they only spawned 2** -- we're wasting resources on bots that aren't doing anything productive. Each builder bot costs +20% scaling.
6. **Their bridge-based economy** uses fewer entities: 5 harvesters -> bridges -> core. No long conveyor chains that are vulnerable to attack.

### MergeConflict - Game 1 (socket, Resource Victory at round 2000)

**Round 1702 snapshot:**

| Stat | MergeConflict (G) | buzzing bees (S) |
|------|-------------------|------------------|
| Titanium | 20,998 | 12,921 |
| Ti collected | 16,760 | 10,840 |
| Bots | 2 | 10 |
| Conveyors | 32 | 73 |
| Harvesters | 7 | 12 |
| Bridges | 0 | 1 |
| Splitters | 0 | 1 |
| Barriers | 0 | 2 |
| Sentinels | 0 | 1 |
| All turrets | 0 | 1 |

**Key findings - MergeConflict game:**
1. **They collected 16,760 Ti with 7 harvesters. We collected 10,840 Ti with 12 harvesters.** Their per-harvester yield is 2,394 Ti vs our 903 Ti. Almost 3x more efficient.
2. **32 conveyors vs our 73** -- again, we over-build conveyors. Their chains are shorter and more direct.
3. **Only 2 bots vs our 10** -- MergeConflict barely spawns builders. They build efficiently with minimal bots.
4. **ZERO turrets, ZERO barriers** -- Pure economy bot. They don't waste any scaling on defense.
5. **MergeConflict is a NOVICE bracket team beating us in MAIN.** This is embarrassing -- a novice team's economy is vastly superior.
6. **The Ti graph shows divergence starting around round 300-400** and widening steadily. Their collection rate is consistently higher throughout the game.

---

## Root Cause Analysis

### Problem 1: Conveyor Overbuilding (CRITICAL)
We build 73-101 conveyors per game. Each costs +1% scaling. At 100 conveyors, our cost scaling is +100% just from conveyors (everything costs double). Meanwhile opponents use 9-32 conveyors.

**Impact:** Every subsequent building costs 2x+ more. We're effectively doubling the price of every harvester, turret, and bot we build.

**Fix needed:** Build shorter conveyor chains. Consider bridge-based transport for distant ore. Stop extending chains unnecessarily.

### Problem 2: Titanium Hoarding (CRITICAL)
At round 1117 in the Polska game, we had 10,408 Ti sitting in the bank while having only 1 sentinel. We lost by core destruction with massive unspent resources.

**Impact:** Resources in the bank do nothing. They need to be converted into harvesters (for more collection) or turrets (for defense).

**Fix needed:** Spend-down logic. If Ti > 500, aggressively build sentinels, more harvesters, or other useful structures.

### Problem 3: Bot Overspawning (HIGH)
We consistently have 8-10 bots vs opponents' 2 bots. Each builder costs +20% scaling. 10 bots = +200% scaling just from bots.

**Impact:** Massive scaling inflation. Combined with 100+ conveyors, our scaling is astronomical. A harvester that should cost 20 Ti might cost 60+ Ti.

**Fix needed:** Cap bots at 3-4 maximum. 2 builders + 1 attacker is plenty.

### Problem 4: No Bridge Usage (MEDIUM)
Polska Gurom uses 29-33 bridges to transport resources efficiently. We use 0-1 bridges. Bridges can skip over walls and deliver directly, avoiding long conveyor chains.

**Impact:** Without bridges, we build long conveyor chains around walls, each adding +1% scaling.

**Fix needed:** Implement bridge-based transport for ore tiles that are far from core or behind walls.

### Problem 5: Late/Insufficient Defense (MEDIUM)
In the Polska game, they had 2 sentinels by round 389 while we had 0. By round 1117, they had 6 sentinels vs our 1. They invested steadily in defense while we invested everything in economy infrastructure.

**Impact:** Core got destroyed at round 1300. All our economic advantage was wasted.

**Fix needed:** Build 1-2 sentinels by round 300-400. Scale to 3-4 by round 800.

### Problem 6: Harvester Count vs Efficiency
We build 12-13 harvesters but collect less than opponents with 5-7 harvesters. More harvesters != more throughput if conveyor chains are bottlenecked or disconnected.

**Impact:** Each harvester costs +5% scaling. 13 harvesters = +65% scaling. If half of them are bottlenecked, we're paying for throughput we don't get.

**Fix needed:** Focus on fewer harvesters with guaranteed direct paths to core. Quality over quantity.

---

## What Opponents Do Differently

### Polska Gurom Strategy
- Bridge-heavy transport (29-33 bridges)
- Roads for bot movement (25-31 roads)
- Minimal conveyors (4-9)
- Early sentinel investment (2 by round 389, 6 by round 1117)
- Only 2 bots -- minimal spawning
- Compact, efficient base layout
- Aggressive sentinel placement to control map center

### MergeConflict Strategy
- Pure economy, zero defense
- Minimal bots (2 only)
- Short, direct conveyor chains (32 total)
- 7 harvesters with good throughput
- No wasted scaling on unnecessary buildings
- Conveyor-based (no bridges/roads) but very efficient layouts

---

## Priority Action Items

1. **CAP BOTS AT 3-4** -- biggest bang for buck. Reduce from 10 to 3-4 bots.
2. **Cap conveyors** -- never build more than 40-50 conveyors. Use bridges for distant ore.
3. **Spend-down logic** -- if Ti > 500 and round > 300, build sentinels or more harvesters.
4. **Implement bridges** -- for ore tiles > 5 tiles from core, use bridge delivery.
5. **Earlier sentinels** -- build first sentinel by round 300, scale to 3-4 by round 800.
6. **Harvester efficiency audit** -- verify every harvester has a working chain to core before building more.
