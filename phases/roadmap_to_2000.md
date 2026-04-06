# Roadmap: Phases 8-12 -- From 1500 to 2200+ Elo
## Strategist Analysis | April 4, 2026
## Target: Candidate Master (2000) by April 20

---

## Overview: The Elo Ladder Has Distinct Floors

Each Elo bracket has a specific capability threshold. You do not need to build "everything" -- you need to build the RIGHT thing for each bracket. Building features above your bracket before mastering the current one is wasted effort.

| Bracket | Elo | What Beats This Tier | Evidence |
|---------|-----|---------------------|----------|
| Silver/Gold | 1400-1600 | 1 working harvester chain | dzwiek (1899) has 0 Ti collected and still sits in Diamond because most bots below 1800 also have no economy |
| Emerald | 1600-1800 | 2-4 harvester chains + roads | Any bot with functioning resource flow beats bots without |
| Diamond | 1800-2000 | 5-7 harvesters + armed sentinels + barriers + bridges | Axionite Inc (1880, peak 2038): 7 harvesters, 4 splitters, 38 barriers, 3 sentinels |
| Candidate Master | 2000-2200 | 8-12 harvesters + map adaptation + offensive capability | Contender teams: dual competency in economy AND military |
| Master | 2200-2400 | 15+ harvesters + massive conveyor networks + sentinel walls | MFF1 (2386): Core Destroyed AND Resource Victory wins |
| Grandmaster | 2400+ | 20+ harvesters + 300 conveyors + 30 bridges + 20 sentinels | Blue Dragon (2791): 10-130x resource collection advantage |

---

## PHASE 8: Solid Economy (1500 -> 1700)
### "Get resources flowing to core"
### Timeline: Days 1-2 (should already be in progress via v5 rewrite)

**Goal:** Bot consistently collects 3,000-10,000 Ti by round 2000 on all map types.

**What to build:**

1. **Directed conveyor chains (THE critical fix)**
   - Builder builds harvester on Ti ore
   - Builder walks from harvester toward core
   - At each tile, builds conveyor facing `pos.direction_to(core_pos)`
   - Chain terminates when builder is within dist^2 <= 8 of core center
   - Conveyors are ONLY built as part of harvester-to-core chains, never during exploration

2. **Road-based exploration**
   - Builders explore using roads (1 Ti, +0.5% scale)
   - Each builder assigned a sector by `my_id % num_sectors`
   - Roads provide builder mobility without polluting resource routing

3. **3-4 harvester chains by round 100**
   - 3 builders fan out in 3 directions from round 1
   - Each finds nearest Ti ore, builds harvester, chains back to core
   - After completing a chain, builder resumes exploring for more ore

4. **Scale discipline**
   - Do not build conveyors during exploration
   - Do not build more than 5 builders before round 100
   - Keep conveyor chains as short as possible (direct path to core)

**Gate criteria:**
- Beats starter bot 5/5 on default maps
- Collects > 0 Ti on every map (including pls_buy_cucats_merch via bridges or passive income)
- 3+ harvesters connected to core by round 100 on standard maps
- Submit to ladder, target: climb to ~1600-1700 Elo within 30 matches

**What NOT to build:**
- Sentinels (no ammo infrastructure yet)
- Barriers (not needed until bots attack you)
- Bridges (only if wall blocks a chain -- reactive, not proactive)
- Markers (overkill for 3-4 builders)
- Attackers (waste of economy builders)

---

## PHASE 9: Defense Layer (1700 -> 1850)
### "Stop dying to rushes and arm your sentinels"
### Timeline: Days 3-4

**Goal:** Bot defends core against basic rushes and has armed sentinels providing zone control. Collects 8,000-15,000 Ti by round 2000.

**What to build (in this order):**

1. **Barrier ring around core (cheap defense)**
   - After 3+ harvesters are running (round 100-150), build 10-15 barriers
   - Place barriers on empty tiles within dist^2 <= 12 of core center
   - Face them toward the enemy direction (from symmetry detection)
   - 10 barriers = 30 Ti, +10% scale -- very cheap for 300 HP of wall
   - Axionite Inc builds 36-38 barriers per game. Start with 10-15.

2. **Splitter-based sentinel ammo delivery**
   - Choose one harvester chain near core (the shortest/most reliable one)
   - Replace one conveyor in that chain (3-5 tiles from core) with a splitter
   - Splitter accepts from behind (chain direction), outputs to 3 forward directions
   - One forward output continues to core (conveyor facing core)
   - One side output goes to a branch conveyor facing perpendicular
   - Branch conveyor feeds a sentinel
   - Sentinel faces AWAY from ammo entry side (so it accepts ammo correctly)
   - Proven pattern from splitter_test: this works

3. **2-3 armed sentinels**
   - Place near core, facing enemy direction
   - Fed via splitter branches from 1-2 resource chains
   - Each sentinel needs 10 ammo per shot, fires every 3 rounds
   - Sentinel with stun (refined Ax ammo) adds +5 cooldown -- but we do not have refined Ax, so stick with Ti ammo for now
   - Even without stun, 18 damage per shot with r^2 = 32 vision is strong area denial

4. **More harvesters (scale to 5-7)**
   - With defense established, expand builder count to 7
   - Find more ore, build more harvesters, chain them back
   - Target: 5-7 harvesters by round 200, collecting 8,000-15,000 Ti total

**Gate criteria:**
- Bot survives to round 2000 on all maps (no core destroyed before round 500)
- Sentinels have ammo and fire at enemy units
- 5+ harvesters connected by round 200
- Win rate > 60% vs v5 (Phase 8 bot)
- Ladder target: 1800-1850 Elo

**What NOT to build:**
- Gunners (sentinels are better per-Ti at this level)
- Launchers (offensive feature, not defensive)
- Foundries/axionite (nobody uses it)
- Complex barrier patterns (simple ring is enough)

---

## PHASE 10: Bridge Expansion + Scale (1850 -> 2000)
### "Reach distant ore and out-collect everyone below 2000"
### Timeline: Days 5-7

**Goal:** Bot collects 15,000-25,000 Ti by round 2000. Works on ALL map types including complex terrain. Reaches Candidate Master (2000 Elo).

**What to build (in this order):**

1. **Proactive bridge placement**
   - When a builder encounters a wall while building a conveyor chain, build a bridge
   - Bridge on tile BEFORE wall, targeting tile BEYOND wall (dist^2 <= 9)
   - After the bridge, resume conveyor chain from the target tile toward core
   - This unlocks ore deposits behind walls that are unreachable with conveyors alone
   - Blue Dragon uses 33 bridges. We should target 5-10 at this phase.
   - On maps like pls_buy_cucats_merch, wasteland, butterfly -- bridges are mandatory for any economy

2. **Scale to 8-12 harvesters**
   - With bridges, ore deposits across the entire map become accessible
   - Target: 8 harvesters by round 300, 12 by round 500
   - Each new harvester chain may be 15-20 conveyors long with 1-2 bridges -- this is fine
   - A 20-conveyor chain costs 60 Ti, harvester costs 20 Ti. Total 80 Ti pays back in 32 rounds.

3. **More barriers (scale to 20-30)**
   - As income grows, invest in a thicker barrier wall
   - Axionite Inc uses 36-38. Target 20-30 in this phase.
   - Prioritize barriers on the enemy-facing side of core
   - Barriers at chokepoints (narrow map passages) are especially valuable

4. **Scale sentinels to 4-6**
   - More income means more splitter branches available
   - Build 1-2 additional splitter branches on different chains
   - Each branch feeds 1 sentinel
   - Position sentinels at barrier line, facing enemy approach

5. **Builder count to 8-10**
   - Economy can support 8-10 builders at this point
   - Assign ~6-7 to economy (harvesting + chaining)
   - Assign ~1-2 to infrastructure maintenance (repair broken chains, extend barriers)
   - Still no dedicated attackers -- pure economy/defense

6. **Map dimension awareness**
   - Read `c.get_map_width()` and `c.get_map_height()` on first round
   - Small maps (area < 625, i.e., < 25x25): be more aggressive, fewer harvesters needed, rush possible
   - Large maps (area > 1600, i.e., > 40x40): pure economy focus, more builders, more bridges
   - This is not full map adaptation -- just adjusting builder count and harvester targets based on map size

**Gate criteria:**
- Collects > 15,000 Ti on large maps by round 2000
- Works on ALL 38 maps (no 0-Ti games)
- 5+ bridges built on complex terrain maps
- 8+ harvesters connected by round 300
- Win rate > 55% vs Phase 9 bot
- Ladder target: 1950-2050 Elo

**What NOT to build:**
- Launchers (save for Phase 11)
- Map-specific strategies beyond size awareness
- Attackers (still not worth the economy hit)
- Gunners (sentinel is better)

---

## PHASE 11: Offense + Map Adaptation (2000 -> 2200)
### "Win on BOTH economy maps and military maps"
### Timeline: Days 8-11

**Why this matters:** The contender scouting report shows that the gap between 2000 and 2200+ is DUAL COMPETENCY. Teams below 2200 can win either military maps (Core Destroyed) or economy maps (Resource Victory), but not both. Teams above 2200 can win both. In a Bo5 with random maps, you need to win at least 3 out of 5 -- and maps will be a mix of types.

**What to build:**

1. **Launcher + thrown builder offense**
   - Build 1 launcher near the front line (toward enemy core direction)
   - Launcher range r^2 = 26 -- longer than any turret
   - Position a builder adjacent to the launcher
   - Throw the builder toward enemy base (target: tile near enemy core)
   - Thrown builder lands inside enemy territory and can:
     - `c.fire(pos)` to attack enemy buildings on its tile (2 damage, 2 Ti)
     - Walk on enemy conveyors (they are passable by any team)
     - Destroy enemy conveyor chains by attacking individual conveyors
   - Even if the builder dies quickly, disrupting enemy economy is high-value
   - Blue Dragon uses 1-3 launchers "sparingly" -- start with 1

2. **Map-specific strategy switching**
   - Detect map dimensions + approximate chokepoint density on round 1-5
   - **Small/narrow maps** (hourglass, corridors, face, gaussian): Build launcher + rush early, fewer harvesters, more sentinels at chokepoints
   - **Large/open maps** (wasteland, settlement, arena, default_large): Pure economy focus, max harvesters, max bridges
   - **Medium mixed maps** (cubes, battlebot, cold): Default balanced strategy
   - Detection method: Check map area (w*h). Also check if core is near map edge (suggests narrow map with opponent across a corridor).

3. **Builder raid capability**
   - After round 600 and 8+ harvesters, send 1-2 builders toward enemy base via roads
   - Builders can walk on enemy conveyors -- follow their chains to find their harvesters
   - Attack enemy conveyors to cut their supply chains
   - Destroying enemy buildings reduces THEIR cost scaling (double benefit)
   - Blue Dragon's weakness: they have 308 conveyors, each with only 20 HP. A single builder can destroy one in 10 attacks (20 rounds). Not fast, but every broken conveyor chain is a dead harvester.

4. **Sentinel wall at chokepoints (narrow maps)**
   - On narrow maps, build 4-6 sentinels in a line at the chokepoint
   - Back them with barriers
   - Feed ammo via splitter branches
   - This creates an impassable defensive line that buys time for economy
   - Kessoku Band (#2) builds 10 sentinels by round 148 on aggressive maps

5. **Scale harvesters to 12-15**
   - With bridges and builders fully operational, push toward 12-15 harvesters
   - This requires 15+ conveyor chains, 10+ bridges, and 200+ roads
   - Economy should produce 20,000+ Ti by round 2000

**Gate criteria:**
- Wins Core Destroyed on at least 2/5 maps per match (narrow maps)
- Wins Resource Victory on at least 2/5 maps per match (open maps)
- Launcher disruption causes measurable enemy Ti reduction
- Win rate > 55% vs Phase 10 bot
- Ladder target: 2100-2200 Elo

**What NOT to build:**
- Breach turrets (friendly fire risk, needs foundry)
- Foundries/axionite (still not worth it)
- Complex marker protocols (builders still operate independently)
- Counter-specific strategies per opponent (you cannot identify opponents during a match)

---

## PHASE 12: Master-Level Optimization (2200 -> 2400+)
### "Close the gap to the top"
### Timeline: Days 12-16 (if we reach 2200 -- optimistic but possible)

**Why this is different:** Above 2200, every opponent has a working economy, armed sentinels, and some offense. You cannot win by just "having economy" -- you need BETTER economy, FASTER expansion, and MORE efficient infrastructure than your opponent. This is where Blue Dragon's 308-conveyor, 33-bridge, 22-harvester economy becomes the target.

**What to build:**

1. **Conveyor dual-use (movement + transport)**
   - Blue Dragon builds 308 conveyors and 174 roads. At Grandmaster, conveyors serve BOTH as resource pipes AND builder walkways.
   - Instead of building separate road networks for exploration, build conveyor networks that serve both purposes.
   - This is more complex (conveyors must face correct direction for resources while also forming a connected walkable grid) but saves significant Ti and scale.
   - The insight: a conveyor facing EAST at position (5,5) is walkable by any builder regardless of direction. The conveyor's facing only affects resource flow, not walkability.
   - So: build conveyor networks in a grid pattern radiating from core. Resources flow inward along the grid. Builders walk anywhere on the grid.

2. **Massive bridge expansion (10-20+ bridges)**
   - Blue Dragon builds 33 bridges. At this level, bridges are used proactively, not reactively.
   - Build bridges at terrain gaps, wall boundaries, and between ore clusters
   - Each bridge costs 20 Ti + 10% scale but saves 5-10 conveyors (15-30 Ti, 5-10% scale)
   - Net scale efficiency is similar, but bridges provide terrain-crossing capability that conveyors cannot match.

3. **Sentinel scaling to 10-15**
   - Multiple splitter branches feeding a sentinel line
   - Position sentinels along the frontier (not just at core)
   - As economy expands outward, push sentinel line outward too
   - This creates a protected economic zone that grows over time
   - Kessoku Band: 10 sentinels by round 148 (very aggressive timing)
   - Blue Dragon: 20 sentinels by late game (gradual scaling)

4. **Marker-based builder coordination**
   - At 10+ builders, coordination matters. Without markers, builders duplicate work.
   - Simple marker protocol:
     - Core tiles store global state (builder count, harvester count, scale %)
     - Builders place ORE_CLAIMED markers on tiles where they plan to build harvesters
     - Builders read markers before walking to ore -- skip claimed tiles
   - This prevents the biggest coordination failure: two builders walking to the same ore and one wasting the trip.

5. **Adaptive builder count based on income**
   - Track income rate (Ti gained per 100 rounds via `get_global_resources()`)
   - If income > builder_cost * 2 per 100 rounds: spawn another builder
   - If income < builder_cost: stop spawning, focus on connecting existing harvesters
   - This self-tunes the economy to avoid over-spending on builders

6. **Repair and resilience**
   - Detect when a conveyor chain breaks (harvester exists but core Ti not increasing)
   - Send a builder to repair the chain (walk along it, rebuild missing conveyors)
   - This is critical against teams that raid your infrastructure

**Gate criteria:**
- 15+ harvesters connected by round 500
- 20,000+ Ti collected by round 2000
- Sentinel line operational with 10+ armed sentinels
- Win rate > 55% vs Phase 11 bot
- Ladder target: 2200-2400 Elo

---

## Schedule Mapping to Calendar

| Day | Date | Phase | Target Elo | Key Deliverable |
|-----|------|-------|------------|-----------------|
| 1-2 | Apr 5-6 | 8 | 1600 | Working economy, directed conveyor chains |
| 3-4 | Apr 7-8 | 9 | 1800 | Barrier ring, armed sentinels via splitters |
| 5-7 | Apr 9-11 | 10 | 2000 | Bridge expansion, 8-12 harvesters, Sprint 4 snapshot |
| 8-11 | Apr 12-15 | 11 | 2200 | Launcher offense, map adaptation, dual competency |
| 12-16 | Apr 16-20 | 12 | 2400 | Massive scaling, marker coordination, Blue Dragon tier |

**Reality check from the strategic assessment:**
- Reaching 1800 by Day 4: **likely (60-70%)** if conveyor chains work correctly
- Reaching 2000 by Day 7 (Sprint 4): **possible (30-40%)** if bridges and scaling work
- Reaching 2200 by Day 11: **stretch (15-25%)** requires dual competency
- Reaching 2400 by Day 16 (qualifier): **very unlikely (5-10%)** requires near-perfect execution

**The realistic target is 1800-2000 by April 20.** Anything above that is bonus.

---

## Resource Budget Per Phase

### Phase 8 (Economy)
- 3-4 harvesters x 20 Ti = 60-80 Ti
- 15-20 conveyors x 3 Ti = 45-60 Ti (3-5 per chain, 4 chains)
- 50-100 roads x 1 Ti = 50-100 Ti
- 5 builders x 30 Ti = 150 Ti (at base cost, higher with scale)
- **Total investment: ~350-400 Ti by round 100**
- **Income by round 200: ~2,000 Ti** (4 harvesters x 500 rounds of income)

### Phase 9 (Defense)
- 15 barriers x 3 Ti = 45 Ti
- 2 splitters x 6 Ti = 12 Ti
- 3 sentinels x 30 Ti = 90 Ti
- 2-3 more harvesters + chains = ~120 Ti
- **Total additional: ~270 Ti**
- Scale cost by this point: ~180% (50 conveyors + 6 harvesters + 5 builders + 3 sentinels + misc)

### Phase 10 (Bridges + Scale)
- 5-10 bridges x 20 Ti = 100-200 Ti
- 4-6 more harvesters + chains = ~250 Ti
- 15 more barriers = 45 Ti
- 3 more sentinels + splitter branches = ~120 Ti
- 3 more builders = ~120 Ti (at ~160% scale, cost is 48 Ti each)
- **Total additional: ~650 Ti**
- Scale by this point: ~250-300%

### Phase 11 (Offense)
- 1 launcher = 20 Ti
- 50+ more roads for raids = 50 Ti
- 4-6 more harvesters + chains = ~350 Ti (at ~250% scale)
- **Total additional: ~450 Ti**

---

## What Distinguishes Each Elo Bracket (Summary)

```
1500 Elo: Bot exists, explores, builds some buildings. No resource flow.
     |
     | FIX: Directed conveyor chains from harvester to core
     v
1700 Elo: 2-4 harvesters connected to core. Passive Ti collected.
     |
     | ADD: Barriers, armed sentinels, scale to 5-7 harvesters
     v
1850 Elo: Functional economy + basic defense. Wins resource race vs no-economy bots.
     |
     | ADD: Bridges for terrain crossing, 8-12 harvesters, map size awareness
     v
2000 Elo: Works on all maps. Consistent 15,000+ Ti by round 2000.
     |
     | ADD: Launcher offense, map-specific strategies, 12-15 harvesters
     v
2200 Elo: Dual competency (economy + military). Wins both Core Destroyed and Resource Victory.
     |
     | ADD: Massive conveyor networks, 15+ sentinels, marker coordination
     v
2400 Elo: Everything optimized. 20+ harvesters, 300+ conveyors, 30+ bridges, 20+ sentinels.
```

**The key insight: each 200 Elo is roughly one major capability addition, not a complete rewrite.** The bot evolves from "basic economy" to "economy + defense" to "economy + defense + terrain" to "economy + defense + terrain + offense" to "everything maximized." Each phase layers on top of the previous one.

---

## Daily Development Protocol

```
Morning (30 min):
  1. Check ladder matches from overnight (cambc matches)
  2. Watch 1-2 loss replays (cambc watch <replay>)
  3. Identify top failure mode (no economy? rushed? map failure?)

Build (3-4 hours):
  4. Implement the single highest-impact fix for today's failure mode
  5. Test: cambc run buzzing buzzing_prev default_medium1 --watch
  6. Test: cambc run buzzing buzzing_prev on 5 diverse maps
  7. Self-play: cambc run buzzing buzzing to verify no regressions
  8. CPU test: cambc test-run buzzing buzzing_prev on a 50x50 map

Ship (30 min):
  9. cambc submit bots/buzzing/
  10. Monitor first 5 ladder matches for regressions
  11. Note version number and key change in local log
```

**Rule: NEVER go more than 24 hours without submitting.** Ladder matches are the only real data. Local testing tells you if the bot does not crash. Ladder tells you if it actually wins.

---

*Roadmap complete. Build Phase 8 now. Ship today. Everything else follows.*
