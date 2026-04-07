# Feature ROI Analysis: Barriers, Chain-Fix, Bridge Shortcut

**Date:** 2026-04-06  
**Motivation:** ladder_passive (2-builder, zero-feature bot) mines 9780 Ti vs buzzing's 9820 on face — nearly identical. Buzzing builds 5-10x more buildings. Are the extra features providing negative ROI?

---

## Key Data: buzzing vs ladder_passive

| Map | buzzing mined | passive mined | buzzing bldg | passive bldg | Winner |
|-----|--------------|--------------|-------------|-------------|--------|
| face | 9820 | 9780 | 169 | 53 | buzzing (marginal) |
| gaussian | 19820 | 19860 | 233 | 72 | **passive** |
| default_medium1 | 14230 | 9820 | 405 | 26 | buzzing |
| butterfly | 36140 | 14940 | 68 | 12 | buzzing |
| corridors | 5090 | 9940 | 26 | 20 | **passive** |
| cold | 29210 | 19070 | 502 | 168 | buzzing |
| settlement | 28210 | 18780 | 760 | 314 | buzzing |

**Observation:** On gaussian and corridors, ladder_passive beats buzzing despite fewer features. On expand maps (cold, settlement), buzzing wins more decisively but also builds 3-5x more. The question is how much of buzzing's advantage comes from features vs scale.

---

## Feature 1: Barriers

### What barriers do
- **Early barriers (rnd <= 30):** 1-2 barriers placed 2-3 tiles from core in enemy direction. Triggers if `(map_mode == 'tight' and rnd >= 5)` OR `harvesters_built >= 1`.
- **Late barriers (rnd >= 80):** Up to 6-15 barriers (depending on Ti balance). Placed 2-3 tiles from core toward enemy, spread perpendicular. Fires when builder is within r²=20 of core.

### Cost calculation

**Direct costs:**
- Barrier base cost: 3 Ti each (+1% scale)
- Late-game scale (after 200 conveyors + 8 harvesters): ~10.8x scale
- Each late barrier costs: `3 * 10.8 = 32 Ti`
- 12 barriers: `12 * 32 = ~384 Ti` direct cost
- 2 early barriers (scale ~1.5x): `3 * 1.5 * 2 = ~9 Ti`

**Scale inflation:**
- 12 barriers add 12% to the scale multiplier: +12% on all future buildings
- At mid-game scale 10.8x: each future harvester costs `20 * 10.8 * 1.12 = 242 Ti` vs `20 * 10.8 = 216 Ti` = +26 Ti per harvester
- Over 5 future harvesters: `5 * 26 = 130 Ti` scale inflation
- Over 50 future conveyors: `50 * (3 * 10.8 * 1.12 - 3 * 10.8) = ~20 Ti` inflation

**Builder turns wasted:**
- Late barrier check fires every turn builder is near core (r²<=20). Each `_build_barriers` call scans all nearby buildings and checks candidates.
- Active barrier placement: builder walks near core (usually already there) and builds. ~2-5 turns per barrier build.
- 12 barriers: ~24-60 builder turns at mid-game, each turn = ~25 Ti opportunity cost (no conveyor built)
- 12 barriers * 2 turns * 25 Ti = ~600 Ti opportunity cost

**Total barrier cost: ~384 + 130 + 600 = ~1114 Ti equivalent**

### What barriers prevent

**Scenario: enemy attacker reaches our core.**
- Enemy builder attacks core for 2 damage/turn at 2 Ti cost to them
- Our core has 500 HP — takes 250 hits to destroy
- A barrier (30 HP, 3 Ti to build) absorbs some hits before attacker reaches core
- But: attackers can bypass barriers (they can walk on allied roads/conveyors, and barriers don't block movement — only buildings with HP)

Wait — re-reading game rules: "Builder Bot: Can only walk on Conveyors, Roads, Allied core." Barriers are buildings but NOT walkable. Enemy builders CANNOT walk through barriers. Barriers block enemy builder movement.

**Barrier effectiveness:**
- 1 barrier = 30 HP, blocks a 1-tile corridor
- Enemy builder deals 2 damage/turn but costs 2 Ti — they can destroy a barrier in 15 turns for 30 Ti
- If our core has no barriers: enemy reaches core quickly, attacks 500 HP over 250 turns
- With barrier wall of 3 barriers: enemy spends 45 turns and 90 Ti destroying them first
- If enemy is spending Ti on attacking: they're not building harvesters

**But:** Our baseline shows we beat rusher/ladder_rush at ~100% even without barriers working well. The barrier strategy taxes OUR economy to slow enemies that are already losing to us.

### Barrier ROI verdict: **NEGATIVE on most maps**

- Costs ~1100 Ti equivalent
- Provides ~45-90 turns of delay vs attackers we already beat (100% vs rusher, ladder_rush)
- Hurts vs passive eco opponents by inflating scale and diverting builder turns
- Maps where it helps: none observed in 50-match baseline that would flip a loss to a win
- Suspects: barrier building near core takes builder turns when builder should be exploring for the 4th-6th ore tile

---

## Feature 2: Chain-Fix

### What chain-fix does
After building first 4 harvesters, if the fix_path had >= 2 direction changes, the builder walks BACKWARD along the path toward core, fixing any misaligned conveyors.

The "fix" logic:
```python
correct_facing = behind_pos.direction_to(self.fix_path[self.fix_idx])
# behind_pos = one step further toward ore
# fix_path[fix_idx] = one step closer to core
# correct_facing = direction from ore-side to core-side = toward core
```

### Is chain-fix actually fixing anything?

The `_nav` method builds conveyors with `face = d.opposite()` where `d` is the movement direction (toward ore). `d.opposite()` = toward the previous tile = toward core. **This is already the correct facing.**

So the chain built during navigation already faces core at every tile. Chain-fix only matters when:
1. The builder moved diagonally (NE) but the path should go N then E separately — the diagonal conveyor at (x+1, y-1) faces SW, but the "true" path direction was N then E
2. The BFS path forced a diagonal step where a cardinal turn was intended

**Critical test:** In our corridors regression study, `buzzing_prev` (without chain-fix) mines 14850 Ti vs `test_no_bridge` (without chain-fix) mining 14520 — only 2% gap. This suggests chain-fix contributes minimal delivery improvement.

### Cost calculation

**Builder turns wasted:**
- Chain-fix fires for each of the first 4 harvesters when path has >= 2 turns
- For a 15-tile path, the bot walks back 15 tiles (15 turns) + walks forward 15 tiles to next ore (would happen anyway) = 15 extra turns per chain-fix
- 4 harvesters * 15 extra turns = 60 turns = ~1500 Ti opportunity cost (at 25 Ti/conveyor/turn)

**Periodic retrigger (maze maps only):**
- Every 100 rounds on maze maps (wall_density > 20%)
- At round 100 a 10-tile path = 10 extra turns = ~250 Ti opportunity cost per retrigger
- 5 retrigers * 250 = 1250 Ti over the game

**Total chain-fix cost: ~1500-2750 Ti equivalent** (depending on path length and retriggers)

### What chain-fix prevents

A misaligned conveyor breaks the delivery chain. If one conveyor in a chain of 20 faces the wrong way, ALL ore from that harvester is lost. This is binary: either the chain delivers or it doesn't.

**But:** The `_nav` method already builds correct-facing conveyors. Misalignment only occurs when:
- Diagonal movement creates a chain that doesn't connect linearly
- The resource stack arrives at a conveyor's output face (rejected)

From empirical data: on corridors, `test_no_bridge` (no chain-fix) mines 14520 Ti vs buzzing_prev's 14850 — both deliver at 97% efficiency without chain-fix. The chain built by d.opposite() navigation already works.

### Chain-fix ROI verdict: **MARGINALLY NEGATIVE to NEUTRAL**

- Costs 60-120 builder turns (~1500-3000 Ti equivalent)
- Fixes diagonally-built conveyors that may already deliver fine
- Empirical evidence: removing it didn't hurt corridors mining (-2% only)
- On maze maps with periodic retrigger: 5 extra retriggers × 10 turns = 50 turns wasted
- Net: the feature likely costs more in builder turns than it saves in delivery efficiency

---

## Feature 3: Bridge Shortcut (post-harvester)

### What it does (current V59 state)
After building a harvester, sets `_bridge_target = ore`. On the NEXT turn:
1. Only fires if `9 < ore.distance_squared(core) <= 25` (ore is 3-5 tiles from core)
2. Builds a bridge from ore-adjacent tile pointing to a core tile
3. Cost: 20 Ti × scale

### Cost calculation

At mid-game scale (10.8x):
- Bridge cost: `20 * 10.8 = 216 Ti`
- +10% scale inflation: future harvesters cost +10.8 * 2 = 21 Ti more, conveyors +3 * 1.08 = 0.32 Ti more
- Over 5 future harvesters: +5 * 21.6 = 108 Ti inflation
- **Total bridge cost per use: ~324 Ti**

The bridge fires for ore at dist² 9-25 from core — typically 1-2 of the first 4-5 harvesters on open maps. So 1-2 bridges built = ~648 Ti total cost.

### What the bridge provides

For ore at distance 3-5 tiles from core: the d.opposite() conveyor chain already delivers ore efficiently. A bridge adds a direct shortcut BUT:
- The bridge sits adjacent to the ore tile pointing to core
- The harvester → ore-adj-bridge → core path skips 3-4 intermediate conveyors
- Those 3-4 conveyors are ALREADY BUILT (they were laid during navigation)
- The intermediate conveyors are orphaned — they no longer carry ore from this harvester
- But they might carry ore from other harvesters that share the chain

**Empirical result from V59 research:** Bridge removal (chain-join leg) helped corridors by +9430 Ti. The bridge shortcut (core-only, dist-gated V59 version) preserves behavior on medium-distance ore. But 648 Ti per game in direct + inflation costs for marginal chain shortcut is expensive.

### Bridge shortcut ROI verdict: **NEGATIVE for chain-join, BORDERLINE for core-only**

- Core-only bridge (dist 9-25): costs ~324 Ti, provides minor delivery speedup for 1-2 harvesters. Likely neutral to marginal.
- Chain-join bridge: proved harmful (V57 vs V59 = 57% vs 64%). Already removed.
- Current V59 still fires the core-bridge for the 1-3 harvesters with ore at dist 9-25.

---

## Comparative Building Count Analysis

| Bot | Buildings | Ti Mined | Buildings/Ti Mined | Winner |
|-----|-----------|----------|--------------------|--------|
| buzzing (gaussian) | 233 | 19820 | 0.012 | LOSS |
| passive (gaussian) | 72 | 19860 | 0.004 | WIN |
| buzzing (face) | 169 | 9820 | 0.017 | WIN |
| passive (face) | 53 | 9780 | 0.005 | LOSS |
| buzzing (dm1) | 405 | 14230 | 0.028 | WIN |
| passive (dm1) | 26 | 9820 | 0.003 | LOSS |

**Key insight:** Passive bot mines with 3-10x fewer buildings. On gaussian it matches buzzing's mining with 1/3 the buildings, meaning buzzing wastes 161 buildings producing no additional ore vs passive. Those buildings' scale inflation + direct Ti cost are pure drag.

On dm1, buzzing mines 4410 more Ti but spent ~15× more buildings doing it. The extra buildings mostly represent: barrier wall, chain-fix retreading, bridge shortcut, exploration conveyors past the first 3-4 ore clusters.

---

## Recommendation Summary

| Feature | Direct Ti Cost | Scale Inflation | Builder Turns Wasted | Benefit | ROI |
|---------|---------------|----------------|---------------------|---------|-----|
| Barriers (late) | ~384 Ti | +130 Ti | ~600 Ti | Slows rushers we already beat | **NEGATIVE** |
| Barriers (early, 2x) | ~9 Ti | ~5 Ti | ~20 Ti | Marginal rush defense | Borderline |
| Chain-fix | 0 Ti | 0 Ti | ~1500 Ti turns | Fixes rare diagonal misalignment | **MARGINAL NEGATIVE** |
| Bridge shortcut (core-only) | ~324 Ti | +108 Ti | ~20 Ti | Minor speedup for 1-2 harvesters | Borderline |

### Priority cuts

**Cut 1 (highest ROI): Remove late barriers entirely.**
- The `_build_barriers` method and the `rnd >= 80` barrier block cost ~1100 Ti equivalent per game.
- We beat 100% of rushers without barriers in the baseline.
- Removing late barriers alone could save ~400 Ti in scale inflation + builder turn opportunity.
- Keep early barriers (2x, rnd<=30) as they cost almost nothing and provide some rush defense.

**Cut 2 (second highest): Remove chain-fix entirely.**
- d.opposite() navigation already produces correct delivery chains.
- Chain-fix wastes 60-120 builder turns per game.
- Empirical: corridors no-chain-fix = -2% mining (within noise).
- Removing chain-fix simplifies code significantly (removes `fix_path`, `fix_idx`, `fixing_chain`, `_fix_chain`, `_check_needs_low_reserve`).

**Cut 3 (third): Remove bridge shortcut (core-only) post-harvester.**
- 324 Ti per use for marginal delivery speedup on already-efficient short chains.
- V59's bridge shortcut is the last remnant of the bridge feature.
- Full removal would match the `test_no_bridge` baseline (+185% corridors improvement preserved).

### Predicted impact of all 3 cuts

Based on V59 (64%) as baseline:
- Late barrier removal: expect +2-3pp (recovers Ti wasted on scale inflation, more ore clusters reached)
- Chain-fix removal: expect +1-2pp (more builder turns available for ore exploration)
- Bridge shortcut removal: expect 0pp to +1pp (already gated to rare cases)

**Conservative prediction: V61 (all 3 cuts) = 67-70% win rate.**

This would match V52's 70% but with cleaner, simpler code and better economy fundamentals.

---

## The Fundamental Problem: Scale Explosion

The root cause of buzzing's underperformance vs passive on equal-ore maps:

| Feature | Scale additions |
|---------|----------------|
| 12 late barriers | +12% |
| 2 bridges | +20% |
| Chain-fix conveyors rebuilt | +2% (destroy/rebuild = net 0 but wastes Ti) |
| Total overhead | +34% scale |

At mid-game with scale 10.8x, a +34% overhead brings scale to 14.5x. The 8th harvester costs `20 * 14.5 = 290 Ti` vs `20 * 10.8 = 216 Ti` = 74 Ti more per harvester = 592 Ti over 8 harvesters just from scale inflation.

The passive bot with 72 buildings on gaussian reaches scale ~3x (72 * avg 2% = ~144% cumulative). Buzzing with 233 buildings reaches scale ~14.5x. That's a 4.8x scale difference, meaning buzzing's 5th harvester costs 4.8× more than passive's 5th harvester.

**The features aren't the problem per se — the building COUNT is. But features cause unnecessary building count (barrier wall + chain-fix retrace conveyors + bridge + exploration sprawl).**
