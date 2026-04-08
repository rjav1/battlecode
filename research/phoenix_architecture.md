# Phoenix Architecture: Roads + Bridges — Viability Assessment

## Date: 2026-04-08

---

## Concept

Separate movement (roads) from delivery (conveyors + bridges):
1. Walk to ore via roads (1 Ti, +0.5% each)
2. Build harvester
3. Walk BACK toward core building conveyors (d.opposite(), same as buzzing)
4. Bridge to core/chain when within 3 tiles

This is what Polska Gurom does: 25 roads + 33 bridges + 9 conveyors.

## Prototype: bots/phoenix/main.py (~240 lines)

### v1 (bridge-first, no chain walk-back):
- Builder walks roads to ore, builds harvester, tries to bridge to core
- **Result: 0 Ti mined on 7/10 maps.** Bridge can't reach core (r^2=9 = 3 tiles max). First harvesters are typically 5+ tiles from core. No conveyor chain exists to bridge to.

### v2 (chain walk-back):
- Builder walks roads to ore, builds harvester, then enters "chain mode" — walks back toward core building d.opposite() conveyors, tries to bridge when close enough
- **Result: 2/10 wins vs buzzing (default_medium1, wasteland_oasis). 0 Ti mined on 6/10 maps.**
- Where it works (default_medium1): 4970 Ti mined vs buzzing's 4960. Essentially tied but phoenix wins on passive Ti accumulation (fewer buildings = less spending).
- Where it fails: builder gets stuck during chain walk-back. The road it walked outbound is still there, blocking conveyor placement. Builder must destroy roads to place conveyors, adding action cost.

## Why This Architecture Fails (at ~200 lines)

### 1. The walk-back doubles travel time
Buzzing walks ONCE to ore, building conveyors along the way. Phoenix walks TWICE — once outbound via roads, once inbound via conveyors. Same number of conveyors, but 2x the travel rounds.

### 2. Roads block conveyor placement
The builder walks outbound on roads. When it walks back building conveyors, the roads are already there. It must destroy each road (free action, no cooldown) before placing a conveyor. But this adds an extra action per tile that competes with conveyor building.

### 3. Bridge r^2=9 is too small
Bridges only reach 3 tiles. Most ore is 5-10 tiles from core. The bridge can only shortcut the LAST 3 tiles of the chain. The first 2-7 tiles still need conveyors.

### 4. Missing buzzing's features
Phoenix lacks: marker-based ore claiming, wall/ore density detection, early barriers, sector exploration, map_mode adaptation. These features are load-bearing (proved by buzzing_v2 experiment: buzzing wins 8-2 vs minimal bot).

## The Fundamental Insight

**The roads-for-movement approach doesn't save conveyors.** The delivery chain still needs the same number of conveyors from harvester to core. Roads only save the 0-2 exploration conveyors that go past the ore tile. At 3 Ti per conveyor saved vs the 2x travel time cost, it's net negative.

**What Polska Gurom actually does differently:**
- 33 bridges = they chain bridges (bridge → bridge → core). Each bridge hops 3 tiles, so 3 bridges cover 9 tiles. This is what we're missing — not just 1 bridge per harvester, but a RELAY of bridges.
- 25 roads = movement infrastructure separate from delivery
- 9 conveyors = short connections between bridges

### Bridge relay math:
- Bridge: 20 Ti + 10% scale
- 3 bridges (9 tiles): 60 Ti + 30% scale
- 9 conveyors (9 tiles): 27 Ti + 9% scale
- Bridge relay is 2.2x MORE EXPENSIVE than conveyors for the same distance!

**But:** Bridges bypass directional restrictions. A chain of south-facing conveyors only carries resources south. A bridge chain can carry resources in ANY direction between hops. This makes bridge relays immune to wall-routing issues.

## Verdict: Phoenix Architecture is NOT Viable

1. **2x travel time** (outbound + inbound) vs buzzing's 1x
2. **Same conveyor count** for the delivery chain
3. **Missing 500 lines of features** that are load-bearing
4. **Bridge relays** are 2.2x more expensive than conveyor chains
5. **No evidence it would beat buzzing** even with perfect implementation (2/10 in prototype)

## What WOULD Work Instead

The d.opposite() conveyor architecture is not the ceiling — **our implementation of it is.** Buzzing at 1463 Elo loses because:
1. We build 70-100 conveyors where top teams build 30-40 (shorter chains)
2. We spawn 8-10 builders where top teams spawn 2-3
3. We hoard Ti instead of using it (10k+ unspent at round 1117)

These are TUNING problems, not architecture problems. The fix is:
- Tighter ore proximity scoring (shorter chains)
- Harder builder cap (fewer builders)
- Ti spend-down (build more harvesters or barriers when rich)

But we've already tried all of these and hit the 66% baseline wall. V61 may genuinely be our ceiling with this approach.
