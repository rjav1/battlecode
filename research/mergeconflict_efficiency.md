# MergeConflict Efficiency Analysis

**Date:** 2026-04-08  
**Question:** How does MergeConflict mine 2394 Ti/harvester vs our 903 Ti/harvester?  
**Data sources:** replay_analysis_apr6.md, winning_replays.md

---

## The Gap in Numbers

From replay_analysis_apr6.md (MergeConflict vs buzzing bees V40, socket map, round 1702):

| Metric | MergeConflict | buzzing bees | Ratio |
|--------|---------------|--------------|-------|
| Ti collected | 16,760 | 10,840 | 1.55x |
| Harvesters | 7 | 12 | 0.58x |
| Ti/harvester | **2,394** | **903** | **2.65x** |
| Conveyors | 32 | 73 | 0.44x |
| Conveyors/harvester | 4.6 | 6.1 | 0.75x |
| Bots | 2 | 10 | 0.2x |

MergeConflict mines **2.65x more per harvester** with **1/5th the builders** and **half the conveyors**.

---

## Root Cause Analysis

### Hypothesis 1: Shorter chains (verified as partial contributor)

MergeConflict's 32 conveyors for 7 harvesters = 4.6 conveyors/harvester.
Our 73 conveyors for 12 harvesters = 6.1 conveyors/harvester.

A shorter chain means fewer opportunities for a break in the chain. Resource stacks flow through conveyors at 1 stack/conveyor/round. A harvester outputs 1 stack every 4 rounds. A chain of length N can carry at most 1 stack every 4 rounds (harvester-limited), so shorter chains aren't inherently FASTER — they're just cheaper (lower scale penalty).

**Verdict:** Shorter chains reduce scale inflation (which makes harvesters cheaper = more total harvesters possible), but don't directly increase Ti/harvester for existing harvesters.

### Hypothesis 2: No broken chains (primary contributor)

Our harvester throughput of 903 vs 2,394 suggests many of our harvesters have broken or partial chains. With only 12 harvesters and 10,840 Ti collected over 2000 rounds:
- Average per harvester: 903 Ti = 90.3 stacks of 10
- At 1 stack per 4 rounds: 90 stacks requires ~360 rounds of active delivery
- But the game runs 2000 rounds: implies harvesters only active ~18% of the time
- Likely cause: conveyor chains broken (enemy attack, wrong direction, missing connections)

MergeConflict's 7 harvesters × 2,394 Ti/each = 16,758 Ti total (matches observed)
- 2,394 Ti = 239 stacks per harvester
- At 1 stack/4 rounds: 239 stacks = ~956 rounds of active delivery
- Over 2000 rounds: ~48% active time
- Much more reliable chains

**Verdict: Our chains break frequently. MergeConflict's chains are reliable.**

### Hypothesis 3: Harvesters placed closer to core (moderate contributor)

From winning_replays.md: On socket (50x20), we mined 29,640 Ti vs MC's 14,410. We dominated on that specific map. But on balanced maps we lose.

MergeConflict likely places harvesters on ore tiles closest to their core, then bridges or short chains. Shorter physical distance = shorter chain = fewer intermediate conveyors = lower scale penalty = cheaper future harvesters.

Our explore formula on balanced maps sends builders to all 8 sectors. Some sectors have ore close to core (short chain), others far (long chain). MergeConflict likely focuses on close ore first.

### Hypothesis 4: Scale difference compounds everything

At round 1702:
- Our 10 bots (+200% scale) + 12 harvesters (+60%) + 73 conveyors (+73%) + 2 barriers (+2%) + 1 sentinel (+20%) + 1 bridge/splitter (+10%) = ~365% total scale
- MergeConflict's 2 bots (+40%) + 7 harvesters (+35%) + 32 conveyors (+32%) = ~107% total scale

At 365% scale, our harvesters cost floor(3.65 × 20 Ti) = 73 Ti each.
At 107% scale, their harvesters cost floor(2.07 × 20 Ti) = 41 Ti each.

So MergeConflict can afford 1.78x more harvesters per Ti spent. With the same starting Ti, they can deploy more harvesters faster, creating a compounding advantage: more harvesters → more Ti → more harvesters.

**This is the core feedback loop that explains the efficiency gap.**

---

## Why Their Chains Are More Efficient

### Theory: They use harvester positioning differently

On socket (50x20), our bot wins (29,640 Ti). This suggests when ore is abundant and scattered, our multi-builder exploration strategy works. But on balanced maps (equal-sized, moderate ore), MergeConflict wins.

**Key insight from winning_replays.md:** We beat MC on maps with ≥34 Ti ore tiles (2x more) and lose on maps with ≤10 Ti ore tiles. The efficiency gap is tied to ORE DENSITY:
- High ore density: our many builders each find distinct ore, all chains work → we win
- Low ore density: our many builders compete for few ore tiles, chains often point to same tiles → we waste scale, MC's 2 precise builders win

### Theory: Their 2 builders build perfectly positioned chains

With only 2 builders:
1. Builder 1 targets nearest ore to core, builds minimal chain (3-5 conveyors), harvests
2. Builder 2 targets 2nd nearest ore, builds minimal chain, harvests
3. No more builders spawned — no scale from unnecessary bots

Total: 2 bots (+40%) + 2 harvesters (+10%) + ~8 conveyors (+8%) = ~58% scale
Each subsequent harvester costs floor(1.58 × 20) = 31 Ti (very cheap)

In contrast, we spawn 8 bots immediately: 8 bots (+160%) before building a single harvester. Then 12 harvesters (+60%) + 73 conveyors (+73%) = 293% total by the time we're done.

**MergeConflict's strategy is sequential and minimal. Ours is parallel and wasteful.**

---

## What We Can Copy

### 1. Cap builders at 4 on balanced maps (currently cap=6-8)

V61 on balanced maps caps at `4 if rnd <= 100 else 6 if rnd <= 300 else 8`.
Reducing to `3 if rnd <= 100 else 4 if rnd <= 500 else 6` would:
- Reduce scale inflation from bots by 40-80%
- Force fewer, better-chosen harvesters instead of many mediocre ones
- Risk: might miss ore on maps with >8 ore tiles per side

### 2. Place harvesters in core-proximity order

Instead of exploring to all 8 sectors simultaneously, have the first 3 builders all go to the 3 NEAREST ore tiles to core first. Then explore farther.

Current: sector formula spreads builders to 8 different directions regardless of ore distance.
Target: Rank explore targets by distance to core, assign builders sequentially to nearest-first.

### 3. Count ore tiles before ramping builders

V61 already detects map_mode. Add ore density check:
- Count ore tiles visible in first 10 rounds
- If total ore tiles (estimated via density) < 16 → cap builders at 5 max
- If total ore > 32 → use current cap

This directly addresses why MC beats us on arena (10 Ti ore total) but we beat them on socket.

---

## Empirical Baseline

From winning_replays.md match data (MC vs us, c1f07eed):

| Map | Our Ti | MC Ti | Ratio | Result |
|-----|---------|-------|-------|--------|
| socket (50x20) | 29,640 | 14,410 | 2.06x us | WIN |
| arena (25x25) | 11,530 | 17,460 | 0.66x us | LOSS |
| default_small1 (20x20) | 19,160 | 20,670 | 0.93x us | LOSS |
| thread_of_connection (20x20) | 28,680* | 32,990* | close | WIN |

*Model estimates

**Conclusion:** On low-ore-density tight maps, MC's efficiency advantage is decisive. On high-ore-density maps, our volume strategy dominates. The fix is ore-count-aware builder caps.

---

## Recommended Fix (High Priority)

Add to `_core()` builder spawning logic:

```python
# Estimate ore density from visible tiles early
if rnd <= 10 and not hasattr(self, '_ore_est'):
    ore_near = sum(1 for t in c.get_nearby_tiles() 
                   if c.get_tile_env(t) in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE))
    self._ore_est = ore_near  # tiles within core vision r²=36
    
# Adjust builder cap based on ore estimate
low_ore = getattr(self, '_ore_est', 99) < 8  # fewer than 8 ore tiles near core
if low_ore:
    cap = min(cap, 5)  # reduce to MC-style lean operation
```

This single change might close the gap on arena and default_small1 while preserving our advantage on ore-rich maps.
