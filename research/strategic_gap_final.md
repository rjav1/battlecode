# Strategic Gap Analysis: What Separates Top 50 From Us

## Date: 2026-04-08
## Context: 27 code changes failed. 400+ ladder matches at ~1463 Elo. 15 research documents.

---

## The Data (from replays + ladder)

| Team | Elo | Harvesters | Ti Mined | Ti/Harvester | Conveyors | Bots | Buildings |
|------|-----|-----------|----------|--------------|-----------|------|-----------|
| Blue Dragon | 2791 | 22 | 30,000+ | ~1,400 | 308 | ? | 500+ |
| Axionite Inc | 1880 | 7 | 19,240 | 2,749 | 13 | ? | ~70 |
| MergeConflict | 1521 | 7 | 16,760 | 2,394 | 32 | 2 | ~45 |
| Polska Gurom | 1487 | 5 | 6,640 | 1,328 | 9 | 2 | ~75 |
| **buzzing bees** | **1463** | **12** | **10,840** | **903** | **73** | **10** | **200+** |

---

## The ONE Thing Top Teams Do That We Don't

### They all have RELIABLE delivery chains. We don't.

**The math proves it:**

A harvester produces 1 stack (10 Ti) every 4 rounds. Over 2000 rounds, a harvester built at round 50 produces ~487 stacks = 4,870 Ti (theoretical maximum).

| Team | Harvesters | Theoretical Max | Actually Delivered | Delivery Rate |
|------|-----------|----------------|-------------------|---------------|
| MergeConflict | 7 | 34,090 | 16,760 | **49%** |
| Axionite Inc | 7 | 34,090 | 19,240 | **56%** |
| buzzing bees | 12 | 58,440 | 10,840 | **19%** |

**We deliver 19% of what our harvesters produce. MergeConflict delivers 49%. Axionite Inc delivers 56%.**

Even accounting for late-built harvesters, our delivery rate is catastrophically low. Most of our harvesters' output is lost — stuck in chains, going to dead ends, or never reaching core.

### What "reliable delivery" means concretely:

- **MergeConflict (49% delivery):** 32 conveyors for 7 harvesters = 4.6 conveyors/harvester. Short, direct chains. Each chain connects harvester → core without breaks.

- **Axionite Inc (56% delivery):** 13 conveyors for 7 harvesters = 1.9 conveyors/harvester. Even shorter chains. Ore is close to core, chains are 1-2 conveyors each.

- **buzzing bees (19% delivery):** 73 conveyors for 12 harvesters = 6.1 conveyors/harvester. But many of these 73 conveyors are NOT part of harvester chains — they're exploration dead-ends. The actual chain-per-harvester might be 3-5, but many chains are BROKEN (don't reach core).

---

## Why Our Chains Break

### Cause 1: BFS Chain Zigzags Miss Core Connection

d.opposite() creates a linked list: each conveyor points to the previous tile. This chain follows the exact BFS path. If the BFS path winds around walls, the chain winds around walls. The chain eventually terminates at... the first conveyor the builder placed near core.

**But does it connect to core?** Only if the first conveyor in the chain outputs TO a core tile. The first conveyor faces d.opposite() of the builder's first step. If the builder stepped NORTHEAST from core, the first conveyor faces SOUTHWEST. This conveyor outputs SOUTHWEST — AWAY from core if core is NORTHEAST of it.

**Wait — the builder spawns ON the core (core tiles are walkable). The first step is AWAY from core. The first conveyor faces d.opposite() = TOWARD core.** So the first conveyor SHOULD output into a core tile.

But what if the builder spawns on a core edge tile and steps diagonally? The first conveyor faces the opposite diagonal — which might output to a tile ADJACENT to core but not ON core. And that adjacent tile might be empty. Resources reach the first conveyor and... stop.

**This is testable.** If the first conveyor's output tile is a core tile, the chain connects. If not, it doesn't.

### Cause 2: Bridge Shortcuts That Break Chains

Our bridge-hop code (lines 274-326 of buzzing) tries to bridge from harvester area to core. If the bridge succeeds, resources bypass the conveyor chain. But if the bridge output tile already has a building, or the bridge target is wrong, resources go nowhere.

The bridge code builds bridges targeting "nearest allied chain tile closer to core." But if that chain tile already has resources flowing through it, adding more resources creates a bottleneck (conveyors hold max 1 stack).

### Cause 3: Multiple Builders Laying Overlapping Chains

Two builders heading toward the same ore area build parallel conveyor chains. Both chains carry resources from their harvesters. But if they cross, conveyors might accept resources from the wrong chain, creating circular flows or dead ends.

---

## What Top Teams Do Differently: THE STRATEGIC INSIGHT

**Top teams build PLANNED chains. We build EMERGENT chains.**

Our chains emerge from the builder's walk path. The chain topology is determined by BFS pathfinding, which optimizes for MOVEMENT (shortest path to ore), not DELIVERY (reliable connection to core). These are different objectives:
- BFS movement: shortest path from builder to ore, around walls
- Delivery: shortest chain from harvester to core, with guaranteed connection

Top teams appear to PLAN chains — they know where ore is, where core is, and build the minimum infrastructure to connect them. Their builders likely have distinct phases:
1. **Scout phase:** Walk (roads/conveyors) to find ore
2. **Build phase:** Build harvester + deliberate chain to core
3. **Next target:** Move to next ore

Our builder does 1 and 2 simultaneously — it builds conveyors as it walks, hoping the chain works out. This is why we have a 19% delivery rate.

---

## The Fundamental Problem We Can't Fix

**We can't separate scouting from building because builders need conveyors to walk.** A builder can't scout without conveyors (or roads), and d.opposite() conveyors ARE the chain. If we use roads for scouting, we need a second pass to build the chain (phoenix — proved to be 2x slower).

**The only alternative:** build conveyors during the walk (current approach) but VERIFY the chain connects to core before building the next harvester. If the chain is broken, fix it instead of building more harvesters.

### What "chain verification" would look like:
1. After building a harvester, the builder traces the conveyor chain backward toward core
2. At each conveyor, check: does this conveyor output to a tile with another conveyor or core?
3. If a break is found, build a conveyor or bridge to fix it
4. Only after verification, move to next ore target

**This is a CHAIN AUDIT — not a return-to-core, not a bridge-first, not a road-first. It's fixing broken chains in place.**

### Why we haven't tried this:
The builder would need to walk BACKWARD along its chain (toward core) checking connections. But it can't easily trace the chain — it doesn't remember which conveyors it built. It would need to:
- Walk toward core
- At each tile, check if the building is a conveyor facing a valid target
- If not, fix it

This is essentially the "return to core" idea but with CHAIN REPAIR during the walk. The phoenix2 test showed return-to-core never triggers because harvesters are within 7-10 tiles. But chain REPAIR would trigger whenever a chain breaks — which could be on every map.

---

## The Untested Approach: Chain Audit After Harvest

After building a harvester:
1. Walk toward core on the existing conveyor chain
2. At each step, check the conveyor under the builder
3. Verify it outputs to a tile with a conveyor or core
4. If broken: build a conveyor or bridge to fix the gap
5. Once the chain is verified to core, resume normal exploration

**Cost:** N rounds of walking (N = chain length, typically 7-10 tiles). Builder does nothing productive during the audit except fix breaks.

**Benefit:** Every harvester has a VERIFIED chain to core. Delivery rate jumps from 19% toward 50%+.

**Why this might work where others failed:** It doesn't change how we BUILD chains (d.opposite() during walk). It just VERIFIES them afterward. The builder already walks back on conveyors (free movement). The only cost is the time to check and fix, not a full second pass.

**Why this might fail:** If chains rarely break (the 19% delivery rate has another cause), the audit wastes builder time for no benefit.

---

## Summary: The ONE Strategic Gap

**Top teams deliver 49-56% of harvester output to core. We deliver 19%.** 

This 2.5x delivery efficiency gap explains everything:
- MergeConflict mines 2,394 Ti/harvester with 7 harvesters = 16,760 Ti
- We mine 903 Ti/harvester with 12 harvesters = 10,840 Ti
- If we matched their 49% delivery rate: 12 harvesters × 2,394 = 28,728 Ti. We'd WIN every game.

**The gap is not builder count, not conveyor count, not chain length, not military. It's CHAIN RELIABILITY — the percentage of harvester output that actually reaches core.**

We build more harvesters but deliver less because our chains have breaks. Top teams build fewer harvesters but every chain works.

---

## Recommendations

### If one more attempt is allowed:

**Chain Audit:** After building each harvester, walk backward on the chain toward core, verifying each conveyor outputs correctly. Fix any breaks. ~30 lines of code. Tests the hypothesis that chain breaks are our delivery bottleneck.

### If V61 is truly final:

Accept 1463 Elo. The delivery rate problem requires either:
1. Chain audit (untested, ~30 lines, moderate risk)
2. A fundamentally different approach to chain building (all failed)
3. Pre-planned chains (requires map knowledge we don't have at game start)

### The honest truth:

We've exhausted every optimization EXCEPT verifying that our chains actually work. We assumed they do because d.opposite() is mathematically correct. But "mathematically correct" doesn't mean "practically connected" — BFS paths, overlapping builders, bridge shortcuts, and edge cases at core tiles could all create breaks we've never measured.

**The next step, if there is one, is to MEASURE chain connectivity — add debug to count how many harvesters have verified paths to core. If it's < 50%, chain audit is the answer. If it's > 80%, the delivery gap has another cause.**
