# Architectural Breakthrough Research: Movement vs Delivery Separation

## Date: 2026-04-08
## Goal: Identify the smallest change to separate movement (roads) from delivery (bridges/conveyors)

---

## Current Architecture (V61, 662 lines)

Our bot uses a **single `_nav` function** (line 400) with two modes:
- **Conveyor mode** (default): Builds conveyor facing `d.opposite()` on each tile before moving. This creates a conveyor chain back to core that serves as BOTH the walking path AND the resource delivery chain.
- **Road mode** (`use_roads=True`): Moves first, builds road only if blocked. Only used by `_walk_to` helper (line 544), which is currently **never called from the main builder flow**.

### The Dual-Use Problem

Every tile the builder walks on to reach ore gets a `d.opposite()` conveyor (3 Ti, +1% scale). This means:
- Exploration paths become permanent conveyor chains
- 70-101 conveyors per game = +70-101% cost scaling
- Many conveyors are on exploration paths that never carry resources
- Top teams use 9-32 conveyors + 25-33 bridges + roads

### Why Previous Attempts Failed (6+ failures)

The V42 bridge-first approach (lines 274-326) tried to add bridges AFTER building harvesters. But:
1. Bridge target radius is only 3 tiles (r^2 <= 9) -- too short for most ore
2. By the time the harvester is built, the builder has already laid a full conveyor chain to get there
3. Changing nav to roads-first breaks delivery entirely because roads don't transport resources
4. Each attempt broke the 66% baseline because the conveyor chain IS the delivery mechanism

---

## What Top Teams Actually Do

### Polska Gurom (1487 Elo): 33 bridges + 25 roads + 9 conveyors
- Roads for bot movement (cheap: 1 Ti, +0.5%)
- Bridges to hop resources from harvester to nearest chain/core
- Only 9 conveyors for short final connections

### MergeConflict (1521 Elo): 32 conveyors, 0 bridges
- Very short, direct conveyor chains
- Only 2 bots -- builds efficiently, doesn't explore wastefully
- 2,394 Ti/harvester vs our 903

### Axionite Inc (1880 Elo): 13 conveyors + 4 splitters
- Minimal conveyors with splitter-based distribution
- 38 barriers for defense

### Blue Dragon (2791 Elo): 308 conveyors + 33 bridges + 174 roads
- At grandmaster level, they use ALL three -- roads for movement, conveyors for chains, bridges for terrain

---

## The Fundamental Constraint

**Bridge target radius is only 3 tiles** (r^2 <= 9). This means a bridge can only hop resources 3 tiles. For ore that's 10+ tiles from core, you still need a chain of SOME kind (conveyors or bridge relays).

This is why simply switching to "roads for nav, bridge at harvester" doesn't work -- the bridge can't reach the core from distant ore, and there are no conveyors to relay through.

---

## The Smallest Viable Change

### Option A: "Relay Bridge" Strategy (MODERATE RISK)
Build roads during exploration nav, then place a chain of bridges (every 3 tiles) from harvester back toward core. Each bridge costs 20 Ti + 10% scale, so a 4-bridge relay = 80 Ti + 40% scale. Compare to 10 conveyors = 30 Ti + 10% scale. **Bridges are MUCH more expensive per hop** -- this only helps for short distances.

**Verdict: WORSE for distant ore, only helps for 1-3 tile hops. Not the breakthrough.**

### Option B: "Hybrid Nav" -- Roads Outbound, Conveyors Return (LOW RISK)
1. Builder walks to ore using **roads** (1 Ti, +0.5% each)
2. After building harvester, builder walks BACK toward core on the same road path
3. On the return trip, **destroy roads and replace with conveyors** facing core-ward
4. This means only the tiles between harvester and core get conveyors, not exploration dead-ends

**Problem:** Builder must retrace its path. Doubles movement time. And the road-to-conveyor replacement requires destroying the road first (action cooldown).

**Verdict: TOO SLOW -- doubles harvester setup time.**

### Option C: "Short Chain + Bridge Hop" (LOWEST RISK -- RECOMMENDED)
Keep current conveyor-based nav BUT add bridge hops to shorten chains:
1. Builder still lays conveyors as it walks (current behavior, proven stable)
2. BUT before starting the conveyor chain, check if a bridge can reach from harvester area to existing infra
3. If bridge can reach (distance <= 3 tiles to any allied conveyor/core tile), build ONLY the bridge, skip the conveyor chain
4. If bridge can't reach, fall back to current conveyor chain behavior

**This is what V42 already tries** (lines 274-326) but it only triggers AFTER the harvester is built, by which time conveyors are already laid.

**The fix:** Move bridge-check BEFORE navigation. When a builder picks an ore target:
- Calculate distance from ore to nearest allied conveyor/core tile
- If distance <= 3 tiles: navigate with **roads** (cheap), then bridge-hop the harvester output
- If distance > 3 tiles: navigate with **conveyors** (current behavior)

### Option D: "Fewer Bots, Shorter Walks" (ZERO RISK -- ACTUALLY RECOMMENDED)
The real insight from MergeConflict: they don't need bridges OR roads because they only build **32 conveyors with 7 harvesters** (avg 4.6 conveyors per harvester). We build **73 conveyors with 12 harvesters** (avg 6.1 per harvester).

The difference isn't the transport mechanism -- it's that:
1. **They only harvest ore NEAR the core** (short chains)
2. **They use only 2 bots** (no exploration waste)
3. **They don't explore far** -- no speculative conveyor chains to distant ore

**The smallest change:** Tighten ore scoring to STRONGLY prefer near-core ore. Currently our scoring (line 354) uses `builder_dist + core_dist * 2`. If we change this to `core_dist * 5` (or even `core_dist * 10`), builders will only target nearby ore, resulting in shorter chains.

---

## Recommendation: Two-Phase Approach

### Phase 1 (SAFE -- highest confidence of passing 66% baseline):
**Tighten ore proximity scoring.** Change line 354 from:
```python
score = builder_dist + core_dist * 2
```
to:
```python
score = builder_dist + core_dist * 4
```

This makes builders strongly prefer ore near the core, resulting in shorter conveyor chains. No architectural change needed. The chain length (and thus conveyor count) drops naturally.

Expected impact: -20-30 conveyors per game = -20-30% scaling = cheaper everything.

### Phase 2 (MODERATE RISK -- only after Phase 1 passes baseline):
**Bridge-before-nav for close ore.** When ore is within 3 tiles of existing infra:
- Navigate with roads instead of conveyors  
- Place a single bridge from harvester to the nearest chain tile
- Saves 3-9 conveyors per harvester (9-27 Ti + 3-9% scaling)

This only triggers for ore that's already near infra, so the bridge almost always has a valid target. The fallback is current conveyor behavior.

### Phase 3 (HIGHER RISK -- future work):
Implement MergeConflict's core insight: **hard cap at 2-3 bots** + **stop exploring once 5 harvesters are placed**. This eliminates speculative exploration conveyors entirely. But this changes bot spawning logic significantly.

---

## Why "Just Use Roads + Bridges" Keeps Failing

The fundamental issue: **our entire delivery system IS the conveyor chain laid during navigation**. You can't remove conveyors from nav without providing an alternative delivery mechanism. Bridges only reach 3 tiles. Roads don't transport resources.

The only safe path is to make the existing conveyor chains SHORTER, not to replace them with a different mechanism. Phase 1 (tighter ore scoring) does this with zero architectural risk.

---

## Key Numbers

| Metric | Current (V61) | Target (Phase 1) | MergeConflict |
|--------|--------------|-------------------|---------------|
| Conveyors/game | 70-101 | 40-50 | 32 |
| Conveyors/harvester | 6-8 | 3-5 | 4.6 |
| Cost scaling from conveyors | +70-101% | +40-50% | +32% |
| Ti/harvester throughput | 903 | ~1,500 (est.) | 2,394 |
| Bots | 8-10 | 8-10 (Phase 1) | 2 |

Phase 1 alone could close half the efficiency gap. Combined with bot cap reduction (Phase 3), we could match MergeConflict's efficiency.
