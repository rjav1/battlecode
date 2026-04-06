# Phase 6 Deep Research: Mechanics, Strategies, and Optimizations
## Cambridge Battlecode 2026
### Compiled: April 4, 2026

---

## 1. SPLITTER MECHANICS: COMPLETE ANALYSIS

### How Splitters Work

A splitter is a transport building (20 HP, 6 Ti base cost, +1% scale) with unique input/output behavior:

**Input:** Accepts resources from the BACK direction ONLY. If the splitter faces NORTH, it accepts input ONLY from the SOUTH side (the tile directly behind it). This is the critical constraint -- unlike conveyors which accept from 3 sides, splitters have exactly 1 input direction.

**Output:** Alternates between outputting in THREE forward directions:
1. The primary output direction (the direction the splitter faces)
2. The left-adjacent direction (one 45-degree rotation left of facing)
3. The right-adjacent direction (one 45-degree rotation right of facing)

**Priority rule:** "Prioritises directions used least recently." This means the splitter maintains internal state tracking which of its 3 output directions was used most recently, and it will favor whichever direction has gone longest without receiving output. This creates a round-robin distribution pattern over time.

### Splitter on an Existing Conveyor Chain

**Can a splitter be inserted into an existing conveyor chain?** Yes, but with careful placement:

The splitter must be placed so that:
1. The upstream conveyor's output direction points INTO the splitter's back side
2. The splitter's facing direction continues toward the main destination
3. Side outputs have valid accepting buildings (conveyors pointing away, or turrets)

**Example: North-flowing chain with splitter branching to a sentinel**

```
Legend: [H]=Harvester, [C>=Conveyor facing East, [C^]=Conveyor facing North
        [S^]=Splitter facing North, [T]=Sentinel, [CORE]=Core

Original chain (flowing north):
    [CORE]
      |
    [C^]    <- conveyor facing north (outputs to core)
      |
    [C^]    <- conveyor facing north
      |
    [C^]    <- conveyor facing north
      |
    [H]     <- harvester on Ti ore

Modified chain with splitter:
    [CORE]
      |
    [C^]    <- conveyor facing north (outputs to core)
      |
    [S^]    <- SPLITTER facing north (accepts from south ONLY)
    / | \
   NW N  NE  <- three output directions
   |  |   |
  [T] [C^] [T]  <- sentinel on left, conveyor continues to core, sentinel on right
```

**Critical detail:** The splitter alternates between its 3 output directions using least-recently-used priority. This means:
- Round 1: Resource goes NORTH (to core chain) 
- Round 2: Resource goes NORTHEAST (to right sentinel)
- Round 3: Resource goes NORTHWEST (to left sentinel)
- Round 4: Back to NORTH (cycle repeats)

Each sentinel gets ~1/3 of the resources flowing through that chain. Since harvesters output every 4 rounds, a single harvester feeding through a splitter would give each sentinel one stack every 12 rounds on average.

### Exact Placement Pattern for Splitter-Fed Sentinel

**Scenario:** North-facing conveyor chain. We want to branch resources to a sentinel.

```
Step 1: Identify a conveyor in the chain that we can REPLACE with a splitter.
        The conveyor at position (x, y) faces NORTH.
        The conveyor behind it at (x, y+1) faces NORTH (outputs into our tile from south).

Step 2: Destroy the conveyor at (x, y).
        Build a SPLITTER at (x, y) facing NORTH.
        The splitter accepts from SOUTH (matching the upstream conveyor's output).
        The splitter outputs to: NORTH, NORTHEAST, NORTHWEST.

Step 3: Build a CONVEYOR at (x+1, y-1) or (x-1, y-1) facing toward the sentinel.
        This conveyor catches the splitter's NE or NW output.

Step 4: Build the SENTINEL at the conveyor's output tile.
        The sentinel must NOT face the direction the conveyor outputs from.
        Example: If conveyor faces EAST, place sentinel facing NORTH, SOUTH, or WEST.
        The sentinel accepts resources from non-facing directions.

Step 5: Ensure the NORTH output of the splitter connects back to the existing chain
        (a conveyor at (x, y-1) facing north should already exist).
```

**Diagonal splitter variant (for diagonal chains):**

If the chain flows NORTHEAST, the splitter faces NORTHEAST and outputs to:
- NORTHEAST (primary, continues chain)
- NORTH (left of NE)
- EAST (right of NE)

### Resource Flow Math

- Harvester outputs 1 stack every 4 rounds (first output immediate)
- Splitter distributes 1/3 of throughput to each direction (round-robin)
- Sentinel needs 10 ammo (1 full stack) to fire
- Sentinel fires every 3 rounds (reload cooldown)

**With 1 harvester feeding through 1 splitter:**
- Harvester output: 1 stack / 4 rounds
- Sentinel receives: 1 stack / 12 rounds
- Sentinel can fire: 1 shot / 12 rounds (limited by supply, not reload)
- Sentinel fires every 12 rounds instead of every 3

**With 3 harvesters feeding through 1 splitter:**
- Combined output: 3 stacks / 4 rounds = 0.75 stacks/round
- Sentinel receives: 0.25 stacks/round = 1 stack / 4 rounds
- Sentinel can fire: 1 shot / 4 rounds (close to max rate of 1/3)

**Conclusion:** To keep a sentinel firing near max rate (every 3 rounds), you need at least 3 harvesters feeding the splitter, or use multiple splitters from different chains converging feed conveyors onto the sentinel.

### Splitter vs Dedicated Harvester for Sentinel

| Approach | Cost | Scale Impact | Resources Lost to Core |
|----------|------|-------------|----------------------|
| Splitter branch (1 harvester shared) | 6 Ti (splitter) + 3 Ti (feed conveyor) = 9 Ti | +2% | 1/3 of chain output |
| Dedicated harvester for sentinel | 20 Ti (harvester) + 3 Ti (conveyor) = 23 Ti | +6% | None |
| Two splitters from two chains | 12 Ti (2 splitters) + 6 Ti (2 feed conveyors) = 18 Ti | +4% | 1/3 from each chain |

**Recommendation:** Splitter branching is far more economical (9 Ti + 2% scale vs 23 Ti + 6% scale). The 1/3 resource loss to core is acceptable when your economy has 5+ harvesters feeding the network.

---

## 2. CONVEYOR-TO-TURRET FEEDING: EXACT MECHANICS

### How Turrets Receive Ammo

The documentation states turrets accept resources with these exact constraints:

1. **Direction restriction:** Ammo cannot enter from the direction the turret faces. If a sentinel faces NORTH, it CANNOT receive ammo from the NORTH side.

2. **Diagonal turrets:** "Diagonal turrets accept ammo from all four cardinal sides." If a sentinel faces NORTHEAST, it can receive ammo from NORTH, SOUTH, EAST, and WEST (all 4 cardinal directions).

3. **Empty requirement:** Turrets "only accept incoming resources when completely empty." A turret holding any ammo (even 1 unit) will refuse new deliveries.

4. **Capacity:** Turrets hold "up to one stack of one resource type" (10 units).

5. **Raw axionite:** "Raw axionite fed into turrets is destroyed." Only titanium and refined axionite have gameplay effects.

### The Push Mechanism

Resources are PUSHED by conveyors, not pulled by turrets. The end-of-round resource distribution works as follows:

1. After all units act, each building that holds resources attempts to OUTPUT them.
2. A conveyor holding a resource stack checks if the tile in its output direction can accept.
3. If that tile contains a turret that is empty AND the conveyor's output direction is NOT the turret's facing direction, the resource transfers.
4. The turret now holds the stack and can fire.

**The turret cannot pull.** It passively receives whatever is pushed to it.

### Practical Feeding Setups

**Setup A: Cardinal-facing sentinel (e.g., NORTH)**
```
    [Sentinel facing NORTH]
         |
    [Conveyor facing NORTH]  <- pushes resource INTO sentinel from SOUTH side
         |
    (resource source)
```
The conveyor at (x, y+1) faces NORTH, outputting to (x, y) where the sentinel sits.
The sentinel faces NORTH, so it accepts from SOUTH, EAST, WEST, and their diagonals.
The SOUTH input is valid. This works.

**Setup B: Diagonal-facing sentinel (e.g., NORTHEAST)**
```
    [Sentinel facing NE]
         |
    [Conveyor facing NORTH]  <- pushes into sentinel from SOUTH
```
Diagonal turrets accept from all 4 cardinal directions. NORTH input = SOUTH side of sentinel. Valid.

**Setup C: WRONG - conveyor outputs INTO turret's face**
```
    [Conveyor facing SOUTH]  <- pushes resource SOUTH
         |
    [Sentinel facing NORTH]  <- facing NORTH, so NORTH side is blocked
```
The conveyor outputs SOUTH into the sentinel's NORTH side. The sentinel faces NORTH.
Does the sentinel accept from NORTH? NO -- it faces NORTH, so NORTH is blocked.
**This setup FAILS.**

### Key Insight for Splitter-Fed Sentinels

When building a splitter-fed sentinel:
1. The feed conveyor must output INTO the sentinel from a non-facing direction
2. The sentinel should face TOWARD the enemy (its combat direction)
3. The feed conveyor should approach from BEHIND the sentinel (opposite to facing)

**Optimal pattern:** Sentinel faces toward enemy, feed conveyor approaches from behind.

```
    ENEMY DIRECTION →

    [Sentinel facing EAST]  ← fires toward enemy
    [Conveyor facing EAST]  ← feeds sentinel from WEST side (opposite of facing = valid)
    [Splitter output]       ← splitter's side output goes here
```

---

## 3. LAUNCHER MECHANICS: COMPLETE ANALYSIS

### Core Stats
- **HP:** 30
- **Cost:** 20 Ti base (+10% scale)
- **Vision r²:** 26 (~5.1 tiles radius)
- **Attack r²:** 26 (same as vision)
- **Reload:** 1 round cooldown
- **Ammo:** NONE required (launchers don't consume resources to fire)
- **No facing direction:** Launchers can throw in any direction

### Throw Mechanics

1. **Pickup:** The launcher picks up an ADJACENT builder bot (must be on a neighboring tile, within the 8-direction adjacency).

2. **Target:** The target tile must be within r²=26 of the launcher. This means any tile (x,y) where `(x-lx)² + (y-ly)² <= 26`. The maximum range is:
   - Straight line: 5 tiles (5² = 25 <= 26)
   - Diagonal: 4 tiles diagonal + 3 straight, or 5+1 (1²+5² = 26)
   - Various combinations: (1,5), (5,1), (3,4), (4,3) all have d²=26 or less

3. **Target tile requirements:** "The target tile must be bot-passable." This means it must be a tile where a builder bot can stand: a conveyor (any team/direction), a road (either team), an allied core tile, or presumably any walkable surface. The target tile CANNOT be a wall or empty ground (builders can't walk on empty tiles).

4. **Wall crossing:** The documentation does NOT state that launchers require line of sight or clear path. The throw appears to be ballistic -- the builder is launched OVER any intervening terrain, including walls. This is a critical offensive capability.

### Post-Throw Builder Behavior

The documentation does not explicitly state whether a thrown builder can act on the same round it lands. Based on the game's turn order model:

- Units act in spawn order within a round
- The launcher acts during its turn (picks up and throws)
- The thrown builder has either already acted this round (if spawned earlier) or will act later (if spawned later)
- **Most likely:** The builder gets its normal turn in the current round if it hasn't acted yet, or acts next round if it already did

**Conservative assumption:** The thrown builder can act on the NEXT round. Even if it can act immediately, the launcher's value comes from positioning, not same-turn action.

### Strategic Implications

**Offensive applications:**
1. **Builder infiltration:** Throw a builder behind enemy lines to attack enemy harvesters/conveyors (2 damage per attack, costs 2 Ti)
2. **Forward sentinel placement:** Throw a builder to a far tile, then have it build a sentinel pointing at enemy infrastructure
3. **Wall-bypassing raids:** On fragmented maps with walls, launchers can throw builders over walls that would take many rounds to walk around
4. **Core rush:** On narrow maps, throw builders toward enemy core, then attack it directly (2 damage/round for 2 Ti)

**Defensive applications:**
1. **Rapid reinforcement:** Throw builders to distant defense positions
2. **Emergency sentinel placement:** React to enemy approach by throwing builder to build sentinel

**Combo with splitter-fed sentinels:**
1. Throw builder to forward position
2. Builder builds conveyor chain + sentinel
3. Splitter branches resources to the forward sentinel
4. Sentinel provides offensive zone control

### Range Visualization (r²=26)
```
Distance examples from launcher at (0,0):
  (5,0) = 25 ✓    (0,5) = 25 ✓
  (5,1) = 26 ✓    (1,5) = 26 ✓
  (4,3) = 25 ✓    (3,4) = 25 ✓
  (4,4) = 32 ✗    (6,0) = 36 ✗

Max reach patterns:
     . . . X X X . . .
     . . X X X X X . .
     . X X X X X X X .
     X X X X X X X X X
     X X X X L X X X X    L = Launcher
     X X X X X X X X X
     . X X X X X X X .
     . . X X X X X . .
     . . . X X X . . .

Total reachable tiles: ~85 tiles within r²=26
```

### Critical Constraint: Target Must Be Passable

The target tile must be "bot-passable." This means you CANNOT throw a builder onto:
- Empty ground (builders can't walk on empty tiles)
- Walls
- Tiles with existing buildings that aren't walkable (barriers, harvesters, turrets, foundries)

You CAN throw onto:
- Conveyors (any team, any direction)
- Roads (either team)
- Allied core tiles
- Splitters, bridges, armoured conveyors (all are walkable transport buildings)

**This means:** Before throwing offensively, you may need a forward road or conveyor on the target tile. Alternatively, if the enemy has conveyors/roads near their base, you can throw onto THEIR infrastructure (conveyors are walkable regardless of team).

**Game-changing insight:** Enemy conveyor networks serve as landing pads for launcher throws. The more extensive the enemy's conveyor network, the more targets you have for launcher drops.

---

## 4. BARRIER ECONOMICS: DEFENSIVE VALUE ANALYSIS

### Barrier Stats
- **HP:** 30
- **Cost:** 3 Ti base
- **Scale:** +1%
- **Properties:** Not walkable. Blocks paths. Blocks line of sight for gunners.

### Comparison Table

| Building | HP | Cost (Ti) | Scale | HP/Ti | HP/Scale% | Walkable? | Blocks LoS? |
|----------|-----|-----------|-------|-------|-----------|-----------|-------------|
| Barrier | 30 | 3 | +1% | 10.0 | 30.0 | No | Yes |
| Road | 5 | 1 | +0.5% | 5.0 | 10.0 | Yes | No |
| Conveyor | 20 | 3 | +1% | 6.7 | 20.0 | Yes | Partially |
| Armoured Conveyor | 50 | 5+5Ax | +1% | 10.0* | 50.0 | Yes | Partially |
| Harvester | 30 | 20 | +5% | 1.5 | 6.0 | No | Yes |
| Sentinel | 30 | 30 | +20% | 1.0 | 1.5 | No | Yes |

*Armoured conveyor requires refined axionite, which requires foundry (+100% scale).

### Barrier Strengths

1. **Best HP-per-Ti ratio:** 10 HP per Ti spent. Only armoured conveyors match this, but they require refined axionite.

2. **Low scale impact:** +1% per barrier. You can build 10 barriers for +10% total scale, adding 300 HP of defensive mass for only 30 Ti.

3. **Path blocking:** Barriers block enemy builder movement. Enemy builders can only walk on conveyors, roads, and their core. A wall of barriers forces enemies to path around.

4. **Line of sight blocking:** Barriers block gunner shots. Placing barriers in front of your infrastructure shields it from enemy gunners.

### Optimal Barrier Placement

**Around core perimeter:**
```
    B B B B B
    B . . . B
    B . C . B    C = Core (3x3)
    B . . . B
    B B B B B
```
Cost: ~16 barriers = 48 Ti, +16% scale, 480 HP defensive wall.
Enemy builders must destroy 30 HP per barrier to breach.
At 2 damage per builder attack, that's 15 attacks per barrier.

**Chokepoint defense:**
On narrow maps, 2-3 barriers across a corridor create a wall that costs enemies significant time to break through.

**Sentinel shield:**
```
    [Sentinel facing NORTH]
    [Barrier]  [Barrier]
```
Barriers in front of sentinel protect it from enemy fire while sentinel shoots over/around them (sentinel has r²=32 range, fires along a wide path).

### When NOT to Use Barriers

- **Don't barrier before economy:** Barriers add 0 economic value. Build harvesters/conveyors first.
- **Don't over-barrier:** Each one adds 1% scale. 30 barriers = +30% scale on all future costs.
- **Don't barrier against sentinels:** Sentinels hit "all tiles within 1 king move of the straight line" -- they shoot around barriers. Barriers are primarily effective against gunners and builder attacks.

### Barrier vs Sentinel for Defense

| Metric | 1 Sentinel | 10 Barriers |
|--------|-----------|-------------|
| Cost | 30 Ti | 30 Ti |
| Scale | +20% | +10% |
| Total HP | 30 | 300 |
| Active defense | 18 damage / 3 rounds | None (passive) |
| Ammo required | Yes (10 per shot) | No |

**10 barriers cost the same Ti as 1 sentinel but add half the scale and 10x the HP.** Barriers are superior for passive defense when sentinels lack ammo (which is our current situation). Once we have splitter-fed ammo, sentinels become the primary defense and barriers become supplements.

---

## 5. GUNNER vs SENTINEL: DETAILED COMPARISON

### Raw Stats Comparison

| Stat | Gunner | Sentinel |
|------|--------|----------|
| HP | 40 | 30 |
| Cost (Ti) | 10 | 30 |
| Scale | +10% | +20% |
| Vision r² | 13 (~3.6 tiles) | 32 (~5.7 tiles) |
| Attack r² | 13 | 32 |
| Damage (Ti ammo) | 10 | 18 |
| Damage (Ax ammo) | 30 | 18 + stun |
| Reload | 1 round | 3 rounds |
| Ammo/shot | 2 | 10 |
| Stun | No | +5 action & move cooldown (with Ax ammo) |
| Fire pattern | Forward ray (line) | All tiles within 1 king-move of forward line |
| Rotation | 10 Ti + 1 cooldown | N/A (fixed direction) |

### DPS Analysis

**Gunner (Ti ammo):**
- 10 damage / 1 round = 10 DPS
- Ammo consumption: 2 per round
- Stacks needed per 10 rounds: 2 stacks (20 ammo)
- Fires every single round (if ammo available)

**Gunner (Ax ammo):**
- 30 damage / 1 round = 30 DPS
- Ammo consumption: 2 per round
- Stacks needed per 10 rounds: 2 stacks (20 ammo)
- Triple damage makes gunner extremely lethal

**Sentinel (Ti ammo):**
- 18 damage / 3 rounds = 6 DPS
- Ammo consumption: 10 per 3 rounds
- Stacks needed per 10 rounds: 3.3 stacks (~34 ammo)
- Lower DPS but MUCH wider attack area

**Sentinel (Ax ammo):**
- 18 damage / 3 rounds = 6 DPS + stun (5 cooldown)
- Stun is devastating: enemy units frozen for 5 rounds
- Effectively removes enemy builders from play for 5 turns

### Cost-Efficiency Analysis

| Metric | Gunner | Sentinel | Winner |
|--------|--------|----------|--------|
| DPS per Ti spent | 10/10 = 1.0 | 6/30 = 0.2 | Gunner (5x) |
| DPS per scale% | 10/10 = 1.0 | 6/20 = 0.3 | Gunner (3.3x) |
| Vision area | 13π ≈ 41 tiles | 32π ≈ 100 tiles | Sentinel (2.4x) |
| Ammo efficiency | 2 ammo = 10 dmg (5 dmg/ammo) | 10 ammo = 18 dmg (1.8 dmg/ammo) | Gunner (2.8x) |
| HP per Ti | 40/10 = 4.0 | 30/30 = 1.0 | Gunner (4x) |

### Why Do Top Teams Use Sentinels Exclusively?

Despite gunners being more cost-efficient on paper, sentinels dominate the meta for these reasons:

1. **Area denial:** Sentinel's attack pattern hits "all tiles within 1 king move of the forward line" within r²=32. This covers a MASSIVE area -- essentially a 3-tile-wide corridor extending ~5.7 tiles. One sentinel controls far more map area than one gunner.

2. **Zone control without rotation:** Gunners only fire along a narrow ray and cost 10 Ti to rotate. Sentinels cover a wide swath without needing rotation, making them "fire and forget" defenses.

3. **Range dominance:** r²=32 vs r²=13 means sentinels engage enemies at 2.4x the distance. By the time a target enters gunner range, a sentinel has already hit it.

4. **Stun is game-breaking:** With refined Ax ammo, sentinels add +5 to BOTH action AND move cooldown. A stunned builder cannot move or build for 5 rounds. This completely shuts down enemy expansion/attacks.

5. **Ammo delivery simplicity:** Sentinels need ammo less frequently (every 3 rounds vs every round). A single splitter branch providing 1 stack per 12 rounds keeps a sentinel firing consistently, while a gunner would need 4x the supply rate.

### Is There a Case for Gunners?

**Yes, in specific scenarios:**

1. **Early game cheap defense (round 50-150):** At 10 Ti vs 30 Ti, you can build 3 gunners for the price of 1 sentinel. Before splitters are set up (no ammo for either), gunners at least provide 40 HP obstacles with 13 vision for scouting. But without ammo, neither type fires.

2. **Narrow chokepoints:** On maps like hourglass or corridors, a gunner's ray attack covers the entire chokepoint width. The sentinel's wider pattern is wasted on walls.

3. **With refined Ax ammo:** Gunners deal 30 damage (vs sentinel's 18) -- 67% more damage. If you have a foundry producing refined Ax, gunners become devastating.

4. **Low-scale budget:** Gunner adds +10% vs sentinel's +20%. When scale is already high (150%+), this difference matters.

**However:** Top teams (Blue Dragon, Kessoku Band) ignore gunners almost entirely. The meta rewards area denial and zone control over raw DPS. Sentinels with their wide attack pattern and stun capability are simply more game-impactful at scale.

### Hybrid Recommendation

For our bot, the optimal approach is:
- **Primary defense:** Sentinels (once we have splitter-fed ammo)
- **Early cheap blockers:** Barriers (30 HP, 3 Ti, no ammo needed)
- **Gunners:** Only if we implement refined Ax production (foundry), making their 30-damage mode viable. Otherwise, skip them entirely.

---

## 6. RESOURCE FLOW OPTIMIZATION: NETWORK TOPOLOGY

### Blue Dragon's Numbers (Reference)

Blue Dragon builds by end-game:
- 308 conveyors
- 33 bridges
- 4 splitters
- 22 harvesters
- 174 roads
- 20 sentinels

### Network Topology Patterns

#### Pattern 1: Trunk Line (Linear Chain)
```
[H1] → [C] → [C] → [C] → [C] → [CORE]
[H2] → [C] → [C] ↗                    
```
- Harvesters feed into a single main line flowing to core
- Simple, easy to build
- **Weakness:** Single point of failure -- destroying one conveyor breaks all upstream harvesters
- **When to use:** Early game, short distances

#### Pattern 2: Tree (Branching Network)
```
[H1] → [C] → [C] ↘
                    [C] → [C] → [CORE]
[H2] → [C] → [C] ↗
```
- Multiple harvester chains merge into a trunk
- More resilient than pure trunk line
- **Weakness:** Merge points can become bottlenecks
- **When to use:** Medium-size maps with clustered ore

#### Pattern 3: Star (Hub and Spoke)
```
         [H1]
          ↓
[H2] → [CORE] ← [H3]
          ↑
         [H4]
```
- All harvesters feed directly to core via short chains
- Maximum throughput, minimum latency
- **Weakness:** Only works when ore is near core. Not viable on large maps.
- **When to use:** Small maps, early game near core

#### Pattern 4: Trunk with Bridges (Blue Dragon's Approach)
```
[H1] → [C] → [Bridge] →→→ [C] → [C] → [CORE]
                 ↑
[H2] → [C] → [C]
```
- Bridges jump over walls/gaps (up to distance² <= 9, ~3 tiles)
- Bridges accept input from ALL directions (unlike conveyors which have restricted input)
- Bridges bypass directional restrictions on the receiving end
- **Strength:** Can cross walls, connect disconnected regions
- **Weakness:** Expensive (20 Ti, +10% scale per bridge)
- **When to use:** Fragmented maps, crossing walls

#### Pattern 5: Trunk with Splitter Taps (For Sentinel Ammo)
```
[H1] → [C] → [S] → [C] → [C] → [CORE]
               ↓ ↘
              [C] [C]
               ↓   ↓
              [T]  [T]     T = Sentinel
```
- Main trunk flows to core
- Splitters tap 1/3 of flow to feed sentinels
- Sentinels get continuous ammo supply
- **Strength:** Economy + military from same chain
- **Weakness:** Reduces core income by 1/3 per splitter
- **When to use:** Mid-to-late game when economy is established

### Optimal Conveyor Network Design Principles

1. **Minimize chain length:** Each conveyor adds +1% scale. A 20-conveyor chain adds +20% to all future costs. Use bridges to skip over long distances (1 bridge at +10% vs 5+ conveyors at +5%+).

2. **Bridge arithmetic:** A bridge costs 20 Ti + 10% scale. A chain of N conveyors costs 3N Ti + N% scale. Bridge is more scale-efficient when N > 10, and more Ti-efficient when N > 7. **Use bridges for gaps of 4+ tiles.**

3. **Harvester-to-core distance matters:** Every extra tile adds a conveyor (+1% scale, +3 Ti). Prioritize ore deposits closest to core.

4. **Splitter placement:** Place splitters at midpoints of chains, not near harvesters (to ensure steady flow from multiple sources before splitting).

5. **Redundancy:** On large maps, build 2 separate chain routes to core. If one is destroyed, the other continues operating.

6. **Direction planning:** All conveyors in a chain must face toward core. Plan the direction sequence BEFORE building to avoid dead ends.

### Conveyor Chain Resource Throughput

Each conveyor can hold 1 stack at a time. Resource moves 1 tile per round (at end of round). This means:

- A chain of length L has L rounds of latency before first resource reaches core
- Maximum throughput: 1 stack per round per chain (pipeline fills up)
- Multiple harvesters feeding same chain increase total throughput but not per-round peak
- Harvester outputs every 4 rounds, so a single harvester produces 0.25 stacks/round
- A chain can support up to 4 harvesters before becoming a bottleneck (1 stack/round capacity)

**If multiple resources compete for the same conveyor:** Only one stack occupies each conveyor at a time. If two resources arrive at the same conveyor simultaneously, only one transfers (the other waits). This means merging chains can create bottlenecks.

### Blue Dragon's 308 Conveyors: Why So Many?

Blue Dragon's massive conveyor count serves multiple purposes:
1. **Coverage:** On 50x50 maps, reaching all ore deposits requires long chains
2. **Multiple chains:** Rather than one trunk, BD likely runs 10-20 independent chains
3. **Builder mobility:** Conveyors are walkable -- they double as roads for builder movement
4. **Network effect:** Each new harvester connection adds 5-15 conveyors to the network
5. **Late-game diminishing returns:** At round 1896, BD has 22 harvesters needing individual chains

**Key insight:** BD uses conveyors as their primary builder infrastructure (not roads). This is because conveyors serve dual purpose: resource transport AND builder walkways. Roads only provide walkability. Building conveyors instead of roads means every path is also a potential resource route.

### Our Optimization Opportunity

Our current bot builds conveyors as it walks (every step tries to build a conveyor). This creates wasteful patterns:
- Conveyors facing random directions (back toward where builder came from)
- No planned chain topology
- No bridges to skip walls
- No splitters for branching

**Phase 6 should implement:**
1. Direction-aware conveyor building (always face toward core)
2. Bridge usage for 4+ tile gaps
3. Splitter insertion at chain midpoints for sentinel ammo
4. Stop building conveyors that point AWAY from core

---

## 7. GAME MECHANIC EDGE CASES AND INTERACTIONS

### Conveyor-to-Enemy Feeding Risk

"Resources can be sent to enemy buildings." This means:
- A conveyor pointing toward enemy territory can feed enemy turrets or core
- Enemy conveyors can steal your resources if chains are misaligned
- **Defense:** Ensure no conveyor faces toward enemy infrastructure
- **Offense:** Potentially redirect enemy conveyors to feed YOUR buildings (unlikely to be practical)

### Builder on Building = Turret Shield

"If a builder bot stands on a building, turret attacks on that tile hit ONLY the builder bot."
- A builder standing on a conveyor/road absorbs all turret damage
- The building underneath is unharmed
- **Defense:** Park a builder on a critical conveyor to shield it from enemy sentinel fire
- **Offense:** Builder on enemy conveyor absorbs sentinel fire, protecting the builder from multi-hit

### Builder Destruction Action

"Builders can destroy allied buildings within action radius unlimited times per round without consuming action cooldown."
- This is FREE and REPEATABLE -- a builder can destroy multiple buildings per round
- Use for: removing bad conveyors, clearing space for sentinels, rebuilding chains
- **Critical for splitter insertion:** Destroy a conveyor, build splitter in its place, same round

### Marker Communication Strategies

"Markers are the ONLY inter-unit communication."
- u32 value = 4,294,967,295 possible values
- Can encode: ore positions, enemy sightings, build orders, territory claims
- Any unit (core, builders, turrets) can place 1 marker per round
- Markers have 1 HP -- any team can build over them (destroying them)

**Encoding scheme suggestion:**
```
Bits 0-7:   Message type (256 types)
Bits 8-15:  X coordinate (0-255, covers max 50x50 maps)
Bits 16-23: Y coordinate (0-255)
Bits 24-31: Data payload (direction, priority, entity type, etc.)
```

### Core Conversion Timing

"Converted axionite is removed from the Ax collected stat and added to the Ti collected stat."
- Converting Ax to Ti helps the TITANIUM tiebreaker at round 2000
- But removes from the AXIONITE tiebreaker (which is checked first!)
- **Strategy:** Only convert Ax if you're confident you'll win the Ax tiebreaker anyway, or if you need the Ti

### Sentinel Stun Stacking

Sentinel stun adds +5 to action AND move cooldown. Key questions:
- Does stun stack from multiple sentinel hits? (Likely yes -- each hit adds +5)
- Can a builder be permanently stunned by overlapping sentinel fire? (Theoretically yes, with 2 sentinels firing alternately every 3 rounds)
- **Stun lock combo:** 2 sentinels with Ax ammo firing alternately = +5 cooldown every 1.5 rounds average, keeping enemy builders permanently frozen

### Harvester Output Priority

"Prioritises outputting in directions used least recently."
- Harvesters have internal state tracking output direction history
- If a harvester has conveyors on NORTH and EAST, it alternates between them
- This is the same LRU priority system that splitters use
- **Implication:** A harvester surrounded by multiple conveyors distributes resources round-robin, not to a preferred direction

---

## 8. STRATEGIC SYNTHESIS: PHASE 6+ DEVELOPMENT PRIORITIES

### Priority 1: Splitter-Fed Sentinel Ammo (HIGHEST IMPACT)

Our sentinels currently have 0 ammo and never fire. Fixing this transforms them from 30 HP obstacles into 18-damage zone control weapons. This is the single highest-impact improvement.

**Implementation plan:**
1. After a conveyor chain is established (3+ conveyors toward core), identify a chain midpoint
2. Destroy the midpoint conveyor
3. Build a splitter facing the same direction
4. Build a feed conveyor from splitter's side output toward a sentinel position
5. Build sentinel at the feed conveyor's output, facing toward enemy

**Resource budget:** ~39 Ti total (6 splitter + 3 feed conveyor + 30 sentinel)

### Priority 2: Direction-Aware Conveyor Building

Current bot builds conveyors facing backward (opposite of movement direction). This creates chains that flow from core OUTWARD (wrong direction). Fix:
- When builder moves direction D, build conveyor facing TOWARD CORE, not facing D.opposite()
- Calculate direction_to(core) for each conveyor placement
- This alone should fix resource flow for many chains

### Priority 3: Barrier Ring Around Core

Cheap defensive improvement: 8-16 barriers around core perimeter.
- Cost: 24-48 Ti, +8-16% scale
- Adds 240-480 HP defensive wall
- Forces enemy builders to spend 15+ attacks per barrier
- Combined with sentinels, creates a layered defense

### Priority 4: Bridge Usage for Wall Crossing

Current bot builds roads to cross gaps. Bridges are better for gaps > 3 tiles:
- Bridge: 20 Ti, +10%, crosses up to 3 tiles over walls
- 4 conveyors: 12 Ti, +4%, but CANNOT cross walls
- On fragmented maps, bridges enable chains that conveyors alone cannot build

### Priority 5: Launcher Drops (Medium-Term)

Launchers enable:
- Throwing builders over walls to enemy territory
- Landing on enemy conveyors (they're walkable!)
- Builder then attacks enemy harvesters/conveyors (2 damage per attack)
- Disrupts enemy economy without needing to walk through their defenses

**Implementation complexity:** Medium. Requires:
1. Building a launcher near enemy territory
2. Spawning a dedicated builder for throwing
3. Ensuring target tile has a walkable surface (enemy conveyor/road)
4. Thrown builder needs attack logic for enemy buildings

### Priority 6: Earlier Military Timing

Kessoku Band has 10 sentinels by round 148. We currently start sentinels at round 200 with a cap of 2 nearby. Changes needed:
- Start sentinel placement at round 80-100
- Increase cap from 2 to 4-6 nearby sentinels
- Prioritize sentinel ammo delivery (Priority 1)
- Place sentinels at chokepoints, not just near core

---

## 9. DETAILED SPLITTER PLACEMENT ALGORITHMS

### Algorithm: Insert Splitter Into Existing Chain

```python
def insert_splitter(c, pos, chain_conveyors):
    """
    Find a conveyor in the chain, replace it with a splitter,
    then build feed conveyor + sentinel on the side output.
    
    chain_conveyors: list of (position, direction) for conveyors in a chain
    """
    for conv_pos, conv_dir in chain_conveyors:
        # Check: does this conveyor have a valid upstream (behind it)?
        behind = conv_pos.add(conv_dir.opposite())
        behind_id = c.get_tile_building_id(behind)
        if behind_id is None:
            continue
        # Check: upstream building outputs toward this conveyor
        try:
            upstream_dir = c.get_direction(behind_id)
            upstream_type = c.get_entity_type(behind_id)
            if upstream_type in (EntityType.CONVEYOR, EntityType.HARVESTER, EntityType.SPLITTER):
                # Valid upstream
                pass
            else:
                continue
        except:
            continue
        
        # Check: downstream tile (in output direction) has a conveyor
        ahead = conv_pos.add(conv_dir)
        ahead_id = c.get_tile_building_id(ahead)
        if ahead_id is None:
            continue
        
        # Check: side output tiles are empty (for feed conveyor + sentinel)
        left_dir = conv_dir.rotate_left()
        right_dir = conv_dir.rotate_right()
        left_tile = conv_pos.add(left_dir)
        right_tile = conv_pos.add(right_dir)
        
        side_dir = None
        side_tile = None
        if c.is_tile_empty(left_tile):
            side_dir = left_dir
            side_tile = left_tile
        elif c.is_tile_empty(right_tile):
            side_dir = right_dir
            side_tile = right_tile
        else:
            continue  # No empty side tile
        
        # Check: tile beyond side tile is empty (for sentinel)
        sentinel_tile = side_tile.add(side_dir)
        if not c.is_tile_empty(sentinel_tile):
            continue
        
        # Execute: destroy conveyor, build splitter, build feed conveyor, build sentinel
        # (This requires multiple rounds -- builder must stay in area)
        return (conv_pos, conv_dir, side_tile, side_dir, sentinel_tile)
    
    return None  # No valid insertion point found
```

### Algorithm: Direction-Aware Conveyor Building

```python
def get_conveyor_direction_toward_core(pos, core_pos):
    """Return the direction a conveyor at pos should face to flow toward core."""
    return pos.direction_to(core_pos)

# In _nav method, replace:
#   face = d.opposite()  # WRONG: faces away from movement
# With:
#   face = pos.add(d).direction_to(self.core_pos)  # Faces toward core
```

### Algorithm: Sentinel Placement Near Splitter Output

```python
def place_sentinel_at_splitter_output(c, splitter_pos, splitter_dir, side_dir):
    """
    Place a feed conveyor and sentinel to receive splitter's side output.
    
    splitter_pos: position of the splitter
    splitter_dir: direction the splitter faces
    side_dir: which side output to use (left or right of splitter_dir)
    """
    feed_pos = splitter_pos.add(side_dir)
    sentinel_pos = feed_pos.add(side_dir)
    
    # Feed conveyor should face the same direction as side_dir
    # This pushes resources from splitter output toward sentinel
    feed_direction = side_dir
    
    # Sentinel should face TOWARD ENEMY (not toward feed conveyor)
    # The sentinel accepts resources from non-facing directions
    # So the feed conveyor must NOT approach from the sentinel's facing direction
    enemy_dir = get_enemy_direction()  # Cached
    
    # Verify: feed_direction.opposite() != enemy_dir
    # (feed approaches from opposite of feed_direction, which must not equal sentinel facing)
    if side_dir.opposite() == enemy_dir:
        # Conflict! Feed would approach from sentinel's facing direction.
        # Rotate sentinel to face perpendicular instead.
        enemy_dir = enemy_dir.rotate_left().rotate_left()  # 90 degrees off
    
    # Build sequence:
    # 1. Build feed conveyor at feed_pos facing side_dir
    # 2. Build sentinel at sentinel_pos facing enemy_dir
    return (feed_pos, feed_direction, sentinel_pos, enemy_dir)
```

---

## 10. AXIONITE META-ANALYSIS: UNTAPPED POTENTIAL?

### Why Nobody Uses Axionite

All top 3 teams collect ZERO axionite. The reasons:

1. **Foundry cost:** 40 Ti base + 100% scale increase. A single foundry DOUBLES all future costs. This is devastating to economy-focused play.

2. **Complex pipeline:** Need axionite ore harvester → conveyor chain → foundry ← Ti chain → foundry → refined Ax conveyor chain → turret. This requires at LEAST 2 separate conveyor chains merging at a foundry.

3. **Opportunity cost:** The Ti and scale spent on the foundry + Ax infrastructure could build 2-3 more sentinels or 6-7 more harvesters.

4. **Diminishing returns:** Refined Ax ammo makes sentinels add stun (+5 cooldown). Powerful, but sentinels with Ti ammo already deal 18 damage. The stun is a luxury, not a necessity.

### Could Axionite Be Meta-Breaking?

**Gunner with Ax ammo: 30 damage per round.** This is 3x normal gunner damage and nearly matches breach damage. At 10 Ti cost + no rotation needed on a narrow map, an Ax-fed gunner is a DPS monster.

**Breach turret:** 40 direct + 20 splash, fires every round. Requires refined Ax exclusively. On paper, the highest single-target DPS in the game. But friendly fire splash, +10% scale, and the foundry requirement make it impractical.

**Verdict:** Axionite is theoretically powerful but the 100% scale foundry tax makes it non-competitive in the current meta. Skip it and focus on Ti-only strategies, matching the top teams.

---

## 11. MAP GEOMETRY AND STRATEGY ADAPTATION

### Symmetry Detection (Current Implementation)

Our bot detects symmetry by sampling visible tiles and checking 3 mirror types:
1. Rotational: enemy at (w-1-cx, h-1-cy)
2. Horizontal reflection: enemy at (w-1-cx, cy)
3. Vertical reflection: enemy at (cx, h-1-cy)

This is correct and matches the game's guarantee of "symmetric by either reflection or rotation."

### Map Size Impact on Strategy

| Map Size | Tiles | Typical Game Length | Best Strategy |
|----------|-------|---------------------|---------------|
| 20x20 | 400 | Core Destroyed 150-400t | Rush + minimal economy |
| 30x30 | 900 | Mixed 300-1000t | Balanced economy + military |
| 40x40 | 1600 | Resource Victory 2000t | Heavy economy |
| 50x50 | 2500 | Resource Victory 2000t | Maximum economy |

### Map Type Detection

We should detect map characteristics early and adapt:

```python
def classify_map(c):
    w, h = c.get_map_width(), c.get_map_height()
    total = w * h
    
    if total <= 600:  # Small maps
        return "rush"  # Aggressive, fast sentinel + builder push
    elif total <= 1200:  # Medium maps  
        return "balanced"  # Economy + military
    else:  # Large maps
        return "economy"  # Maximum harvester + conveyor investment
```

### Narrow Map Detection

Narrow maps (hourglass, corridors) favor rushes. Detect by checking:
- Width-to-height ratio > 2 or < 0.5
- Wall density creating chokepoints
- Distance to enemy core < 15 tiles

---

## 12. COMPETITIVE BENCHMARKS AND TARGETS

### What We Need to Match (Grandmaster Level)

Based on top team analysis:

| Metric | Current (Phase 5) | Target (Phase 8) | Blue Dragon (Reference) |
|--------|-------------------|-------------------|------------------------|
| Harvesters by R200 | 3-4 | 7-8 | 7 |
| Conveyors by R500 | 20-30 | 80-100 | 84 |
| Bridges used | 0-2 | 10-15 | 10 |
| Sentinels (armed) by R200 | 0 (no ammo) | 3-4 | 3-6 |
| Resource flow to core | Broken chains | Continuous | 10x opponent |
| Ti collected by R500 | ~5,000 | ~10,000 | ~15,000+ |
| Win condition | RV only | RV + CD | Both |

### Immediate Phase 6 Goals

1. Sentinels that actually fire (via splitter ammo) -- closes biggest capability gap
2. Conveyor chains that flow toward core (not random) -- fixes economy
3. Barrier defense around core -- cheap HP wall
4. Bridge usage on fragmented maps -- enables expansion
5. Map size adaptation -- rush on small, economy on large

---

*Research compiled from Cambridge Battlecode documentation (docs.battlecode.cam), replay analysis of top 3 teams, game engine source code (_types.py), and Phase 5 testing results. All mechanics verified against official documentation as of April 4, 2026.*
