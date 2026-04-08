# Forward Gunner Ammo Delivery — Research

**Date:** 2026-04-08  
**Context:** Binary_tree map push. Builder reaches near-enemy-core position, places a gunner facing enemy core. How to get Ti ammo to it?

---

## Gunner Ammo Mechanics (from CLAUDE.md)

- **Ammo source:** Titanium stacks (standard Ti, not refined Ax — plain Ti works for gunner)
- **Ammo/shot:** 2 stacks per shot (each stack = 10 Ti)
- **Reload:** 1 round — fires every round when loaded
- **Accepts ammo via:** Conveyors from any of the 3 non-facing directions
- **Only accepts when completely empty** — so needs 2 stacks delivered, fires, then needs 2 more
- **At reload 1/round:** throughput needed = 2 stacks/round = 20 Ti/round through the delivery chain
- **Damage:** 10 per shot (30 with Ax ammo) — plain Ti still useful, halved damage
- **Scale cost:** Gunner +10%, each conveyor +1%

The resource distribution rule: stacks of 10 move at end of each round through conveyors. A single conveyor chain with no branching passes 1 stack/round. To deliver 2 stacks/round, you need either 2 parallel chains or a splitter.

**Critical constraint:** Resources flow from the core/harvester side toward the turret. The chain must be connected back to the main economy (harvesters → conveyors → core), not isolated. Ti flowing to core must be *diverted* to the gunner instead — or the gunner gets a separate branch from the nearest full conveyor.

---

## The Three Options Analyzed

### Option 1: Gunner placed on existing conveyor chain reaching the front

**Concept:** The builder's natural conveyor-laying march toward enemy core already creates a chain. Place the gunner on a tile where the chain passes, facing toward the enemy.

**Mechanics:**
- The conveyor chain passes Ti *through* to core — but a gunner placed *on* a conveyor tile receives stacks before they continue?
- **NO.** Conveyors output in their facing direction. A gunner placed on an empty tile *adjacent* to a conveyor receives a stack only if that conveyor faces the gunner's non-facing side.
- The existing chain is built facing *toward core* (conveyors output toward core). To feed a gunner facing *toward enemy*, the conveyor outputting toward the gunner must be behind or beside the gunner.

**Problem:** Our conveyor chains are built with each conveyor facing toward core (opposite direction of travel). A forward gunner facing enemy is oriented 180° from the chain flow. The last conveyor in the chain faces *away* from enemy — its output goes toward core, not toward the gunner.

**Example:** Chain direction: Harvester → [conv→NORTH] → [conv→NORTH] → core. Gunner placed facing SOUTH (toward enemy). The last conveyor in the chain outputs NORTH (toward core). The gunner's non-facing sides are EAST, WEST, NORTH — the conveyor to the north outputs toward core, so it *would* feed into the gunner's NORTH side. **This actually works** if the gunner is placed on the conveyor's output tile and the conveyor is redirected.

**But:** A builder can't redirect an existing conveyor (can only destroy and rebuild). And placing a gunner on the conveyor tile destroys the conveyor. The chain breaks.

**Verdict: Not practical without deliberate design.** You'd need to plan the chain to terminate *at* the gunner position with the conveyor's output facing the gunner's side. This requires knowing gunner placement before building the chain — not how our current bot works.

**Scale cost:** 0 extra buildings (gunner replaces chain tip). But breaks Ti delivery to core.

---

### Option 2: Builder builds 1-2 conveyors from chain tip to gunner position

**Concept:** After placing the gunner N tiles ahead of the chain tip, the builder backtracks and builds 1-2 branch conveyors to connect the chain to the gunner's side.

**Mechanics:**
```
Chain tip: [conv→NORTH facing core]
                                     
[branch conv →EAST]  →  [Gunner facing SOUTH (enemy)]
```
- Chain tip still outputs toward core (unbroken)
- Branch conveyor off the chain tip outputs east toward the gunner
- Gunner receives stacks from its EAST side (a non-facing side) ✓
- Branch costs 1-2 conveyors = 3-6 Ti + 1-2% scale

**Flow:** Ti arrives at chain tip → simultaneously outputs north (to core) and east (to branch)? **No.** Conveyor outputs in exactly ONE direction — its facing direction. A single conveyor can't split flow.

**Fix:** Use a **splitter** at the branch point. Splitter accepts from behind, alternates output to 3 forward directions. Cost: 6 Ti + 1% scale.

Or: tap from a conveyor in the chain that's perpendicular — build a T-junction by placing the branch conveyor *beside* the chain, facing the gunner, *accepting from the chain*.

**Detailed layout (example, binary_tree map, builder moving north toward enemy):**
```
Chain: ... → [C→N] → [C→N] → [C→N] → core (north)
                                  ↓
              Branch: [C→E] →  [GUNNER facing SOUTH]
```
The branch conveyor at the chain tile accepts from WEST (chain outputs north, not into branch). **Problem:** To tap from the chain, the branch conveyor must accept a stack from the chain conveyor's output. But conveyors only pass stacks to the building *in their output direction*. If chain conveyors face NORTH, they don't feed anything facing EAST.

**Real fix:** The last non-core chain conveyor is replaced with a splitter, which alternates output in 3 directions (forward = north to core, and east/west to branches). The branch going EAST reaches the gunner's side.

**Splitter layout:**
```
... → [C→N] → [SPLITTER] → core (north, every other round)
                    ↓
              [C→E] → [GUNNER facing SOUTH]
```
Cost: 1 splitter (6 Ti) + 1-2 branch conveyors (3-6 Ti) = 9-12 Ti extra, +2-3% scale.

**Throughput:** Splitter alternates 3 outputs → each direction gets 1 stack every 3 rounds = 0.33 stacks/round. Gunner needs 2 stacks/shot. At 0.33 stacks/round to gunner, reloads every 6 rounds (not 1). **Low DPS but operational.**

Or use a bridge from chain to gunner's side position — bridge bypasses direction rules.

**Verdict: Works but complex.** Requires either a splitter tap or a bridge jump. Builder needs to place splitter, rebuild branch, then build gunner. Multiple actions = multiple rounds of work. Manageable but not trivial.

**Scale cost:** +12-20 Ti, +3-4% scale per forward gunner.

---

### Option 3: Road from core to gunner zone, then 1 conveyor at the end

**Concept:** Builder walks a road trail from core toward enemy (roads are walkable). At the gunner position, place 1 conveyor from the nearest main chain, then the gunner.

**Mechanics:**
- Roads cost 1 Ti (+0.5% scale), walkable by builder but carry NO resources
- Roads don't move Ti — they're purely mobility infrastructure
- Still need at least 1 conveyor to actually feed the gunner

**So road alone delivers nothing.** The "road to gunner zone" gets the builder there cheaply, but the gunner still needs a conveyor connection back to the main economy.

**Hybrid approach:** Builder walks road to gunner position, places gunner, then builds 1 conveyor from the nearest main-chain conveyor toward the gunner's non-facing side. If the main chain has a conveyor within 1 tile of the gunner's back/side, 1 conveyor suffices.

**On binary_tree specifically:** The tree structure means main chain conveyors pass through nodes. A gunner placed at a node can potentially be fed by a branch conveyor off that node with just 1 conveyor.

**Cost:** Roads themselves: N × 1 Ti (cheap). Final 1 conveyor to connect: 3 Ti. Total extra: 3-5 Ti + 0.5% per road tile.

**Verdict: Simplest for mobility, still needs the 1 feed conveyor.** Roads solve the "builder can't walk to gunner position" problem cheaply. The ammo chain still requires at minimum 1 properly-oriented conveyor.

---

## Verdict: Option 3 is Simplest for a Forward Push

For a binary_tree gunner push, the practical answer is:

**Walk road, place gunner at a node, build 1 conveyor from the back.**

### Why:

1. **Roads are cheap** (1 Ti vs 3 Ti conveyor) — builder can reach forward position without building a full conveyor trail
2. **Binary_tree geometry helps:** The tree has natural nodes where our existing economy chain passes. A gunner at or near a node needs only 1-2 conveyors to tap the chain.
3. **1 conveyor behind the gunner** (facing toward the gunner from the chain) = simplest ammo connection
4. **Scale cost:** Road trail (N × 0.5%) + 1-2 conveyors (+1-2%) vs Option 2's splitter path (+3-4%)

### Minimum viable layout:

```
[Main chain: conv→core]
        |
[1 branch conv→EAST] → [GUNNER facing WEST toward enemy]
        ↑
Builder walked here via roads
```

- Builder walks road to the chain tap point (near chain but not on it)
- Builds 1 conveyor outputting toward the gunner's side (EAST)
- Builds gunner facing WEST (toward enemy core)
- Chain delivers 1 stack/round to gunner (enough for 1 shot every 2 rounds)

### Throughput reality:

A single conveyor chain carries 1 stack/round. Gunner needs 2 stacks/shot. So with 1 feed conveyor: **fires every 2 rounds** (half rate). Still fires, still deals 10 damage/2 rounds = 5 DPS. Enemy core is 500 HP → kills in 100 rounds if gunner stays alive.

To get full reload rate (every round): need 2 parallel feed conveyors, or a splitter upstream.

### Builder walk path constraint:

Builder can only walk on conveyors, roads, allied core. On binary_tree, the map has defined corridors. Builder can only advance to gunner position if:
- The main chain already reaches there (can walk the conveyor chain), OR
- Builder pre-builds a road trail ahead of the chain

**For a push bot:** road trail is the right move — build 3-5 roads toward enemy node, then gunner + 1 feed conveyor. Total cost: ~5-8 Ti roads + 3 Ti conveyor + 10 Ti gunner = ~18-21 Ti. One-time investment.

---

## Implementation Sketch

```python
# In builder logic, when push_mode active:
# 1. Walk roads toward enemy via _nav(use_roads=True) — already exists in code
# 2. When within action range of desired gunner tile:
if can_build_gunner(gunner_pos, enemy_facing_dir):
    build_gunner(gunner_pos, enemy_facing_dir)
    # Next round: find nearest chain conveyor in vision
    # Build 1 conveyor from chain toward gunner's side
    # Done

# Enemy facing: use _get_enemy_direction() — already exists
```

Our codebase already has `_nav(use_roads=True)` and `_get_enemy_direction()`. The missing piece is just:
1. A trigger condition (when to start push — round, Elo, map type)
2. The gunner placement + 1-feed-conveyor logic (~20 lines)

---

## Binary_tree Specific Notes

- binary_tree is a "balanced" map (area ~30x30 = ~900 tiles)
- V61 already **wins** vs sentinel_spam and barrier_wall on binary_tree (tested)
- V61 **loses** vs ladder_hybrid_defense on binary_tree (7141 vs 40470 Ti — massive gap)
- A forward gunner push on binary_tree is most useful to counter ladder_hybrid_defense style opponents who out-eco us but can't fight back

The tree node closest to enemy core is the natural gunner position. Builder walks the main chain (already conveyor-paved by economy building), diverges at the midpoint node with 2-3 roads, places gunner + 1 feed conveyor.
