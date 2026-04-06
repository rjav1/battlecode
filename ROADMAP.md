# BATTLECODE 2026 INTERNATIONAL QUALIFIER -- WINNING ROADMAP
## Team "buzzing bees" | Target: #1 | Qualifier: April 20, 2026
## Advisor Alpha -- Quantitative Game-Theoretic Analysis

---

# TABLE OF CONTENTS

1. Situation Assessment & Timeline
2. Game-Theoretic Analysis & Resource Economy Model
3. Nash Equilibria & Dominant Strategy Identification
4. Meta-Game Analysis Framework
5. Bot Architecture Design
6. Marker Communication Protocol
7. Development Phases (Zero to #1)
8. Optimization & Testing Pipeline
9. Edge Cases, Exploits & Non-Obvious Mechanics
10. Risk Analysis & Hedging
11. Appendices: Mathematical Models, Lookup Tables, Parameter Grids

---

# 1. SITUATION ASSESSMENT & TIMELINE

## Current State
- Rank: #486 of 572 (unrated, 0 matches, 0 submissions)
- Top team: Blue Dragon at ~2791 Elo (Grandmaster)
- Elo starts at 1500. Need 100+ matches to earn a rank.
- Sprint 4 snapshot: April 11 (7 days away)
- INTERNATIONAL QUALIFIER: April 20 (16 days away)
- Matches run every 10 minutes on the ladder

## Assets
- Unlimited compute for local testing (cambc run -- no time limit locally)
- Remote test-runs available (cambc test-run -- 2ms enforced on AWS Graviton3)
- AI agents for parallel development streams
- 38 maps available for testing
- Full SDK source and documentation

## Critical Path Calculation
- 16 days = 384 hours = ~2,300 10-minute matchmaking windows
- At 1 match per 10 minutes, theoretical max ~2,300 rated matches
- Need ~100 matches just to get rated
- Elo gain per match depends on opponent rating and win/loss
- Estimated Elo climb from 1500 to 2400+: requires ~70-80% win rate over 200+ matches
- IMPLICATION: Must submit a competitive bot within 3-4 days to accumulate matches

## Time Budget (16 days)

| Phase | Days | Goal |
|-------|------|------|
| 0: Foundation | Days 1-2 | Working economy bot, first submission |
| 1: Competitive | Days 3-5 | Defeat starter bots, reach ~1600 Elo |
| 2: Meta-aware | Days 6-8 | Study replays, counter top strategies |
| 3: Optimization | Days 9-12 | Parameter tuning, map-specific logic |
| 4: Edge polish | Days 13-16 | Exploit hunting, defensive hardening |

---

# 2. GAME-THEORETIC ANALYSIS & RESOURCE ECONOMY MODEL

## 2.1 Resource Flow as a Markov Chain

The game's economy is a resource-production pipeline with discrete timesteps
(rounds). Model it as follows:

```
State: (Ti_stored, Ax_stored, n_harvesters_Ti, n_harvesters_Ax,
        n_foundries, n_conveyors, scale_percent, round)

Transitions:
  - Every 4 rounds: +10 Ti passive
  - Each Ti harvester: +10 Ti every 4 rounds (after conveyor delay)
  - Each Ax harvester: +10 Raw Ax every 4 rounds (after conveyor delay)
  - Each foundry: consumes 10 Ti + 10 Raw Ax, produces 10 Refined Ax
  - Core conversion: 1 Refined Ax -> 4 Ti
```

## 2.2 Income Rate Calculations

### Passive Income
- Base: 10 Ti / 4 rounds = 2.5 Ti/round
- Over 2000 rounds: 10 * (2000/4) = 5,000 Ti from passive alone

### Harvester ROI Analysis

Let S = current scale_percent / 100. Cost to build one Ti harvester:

```
harvester_cost = floor(S * 20) Ti
conveyor_cost_per_tile = floor(S * 3) Ti
builder_cost = floor(S * 30) Ti (amortized across multiple tasks)
```

For a harvester at distance D from core (in conveyor tiles):

```
Total investment = floor(S * 20) + D * floor(S * 3) Ti
                 + partial builder amortization

Revenue = 10 Ti every 4 rounds (once pipeline full)
         = 2.5 Ti/round steady-state

Pipeline fill time = D rounds (resource travels 1 tile/round)
First output: immediate on build round, then every 4 rounds
```

**Payback period** (at scale=1.0, D=3):
```
Investment = 20 + 3*3 = 29 Ti
Revenue rate = 2.5 Ti/round
Payback = ceil(29 / 2.5) = 12 rounds

With pipeline delay: first Ti arrives at round D + build_round
Effective payback: ~12 + D rounds = ~15 rounds
```

**KEY FINDING: Harvesters pay for themselves in ~15 rounds. Over 2000 rounds,
each harvester generates ~490 Ti gross. The ROI is massive.**

### Scale Impact on Harvester ROI

Each harvester adds +5% scale. The N-th harvester costs:

| Harvester # | Scale% | Harvester Cost | Marginal Scale Hit |
|-------------|--------|----------------|--------------------|
| 1 | 100% | 20 Ti | +5% to all future builds |
| 2 | 105% | 21 Ti | +5% |
| 3 | 110% | 22 Ti | +5% |
| 4 | 115% | 23 Ti | +5% |
| 5 | 120% | 24 Ti | +5% |
| 6 | 125% | 25 Ti | +5% |
| 8 | 135% | 27 Ti | +5% |
| 10 | 145% | 29 Ti | +5% |

At +5% per harvester, 10 harvesters only add +50% total scale from harvesters
alone. The revenue (25 Ti/round from 10 harvesters) dwarfs the cost increase.

**OPTIMAL HARVESTER COUNT: Build as many as ore tiles allow, up to about 10-12.
The marginal ROI remains positive even at high scale. The binding constraint
is available ore tiles and conveyor path length, not diminishing returns.**

### Builder Bot Economy

Each builder costs 30 Ti (scaled) and adds +20% scale. Builders are the most
expensive scale contributors after foundries. The key question: how many
builders to spawn?

```
Minimum viable: 2-3 builders (one for each expansion direction)
Maximum useful: 5-6 builders (diminishing utility -- they block each other)
Optimal for economy phase: 3-4 builders

Scale impact of 4 builders: +80% (huge!)
Scale impact of 3 builders: +60%
```

**CRITICAL INSIGHT: Each unnecessary builder permanently inflates all future
costs by 20%. Spawn exactly as many as needed, no more. 3 is the sweet spot
for early game. Build a 4th only when you need a dedicated military builder.**

### Foundry Economics

Foundry costs 40 Ti and adds +100% scale (!). This is the most punishing
single building in the game. Analysis:

```
Without foundry (scale starts at 100%):
  Builder cost: 30 Ti

After 1 foundry (scale jumps by +100%):
  If current scale was 160% (after 3 builders), new scale = 260%
  Builder cost: floor(2.60 * 30) = 78 Ti
  Harvester cost: floor(2.60 * 20) = 52 Ti
```

**FOUNDRY DECISION RULE: Only build a foundry if:**
1. You have access to axionite ore AND need refined Ax for turrets/tiebreaker
2. You have already built most of your planned infrastructure (so scale penalty
   is less damaging)
3. You are planning a sentinel-stun or breach strategy
4. It is past round ~300 and your economy is stable

**Alternative: If you don't need refined Ax, NEVER build a foundry.** The
tiebreaker advantage (refined Ax delivered to core is tiebreaker #1) may
justify exactly 1 foundry in long games.

### Conveyor Chain Length Analysis

Resources move 1 tile per round in stacks of 10. A chain of length L means:
- L rounds of latency from harvester to core
- Once pipeline is full, throughput = 1 stack / 4 rounds (limited by harvester)
- Total cost: L * 3 Ti (at base scale) + L * 1% scale

For a 10-tile conveyor chain:
```
Cost: 30 Ti + 10% scale
Latency: 10 rounds
Throughput at steady state: 2.5 Ti/round (same as shorter chains)
```

**FINDING: Conveyor length does NOT affect steady-state throughput. It only
affects latency. Longer chains cost more Ti and scale but produce the same
income rate. MINIMIZE CHAIN LENGTH.**

### Bridge vs. Long Conveyor

Bridge: 20 Ti, +10% scale, teleports up to dist^2=9 (3 tiles)
Equivalent 3 conveyors: 9 Ti, +3% scale

Bridge saves 2 rounds of latency but costs 11 more Ti and 7% more scale.
**Bridges are only justified when physical obstacles (walls) block conveyors.**

## 2.3 Total Economy Potential

Over 2000 rounds, theoretical max Ti generation:

```
Passive: 5,000 Ti
6 Ti harvesters: 6 * 490 = 2,940 Ti
Ax->Ti conversion (4 Ax harvesters through foundry, then convert):
  4 Ax harvesters * ~490 Raw Ax / 10 stacks = ~196 stacks
  Foundry converts ~196 stacks (limited by Ti input to foundry)
  Actually limited: foundry needs BOTH Ti + Raw Ax simultaneously
  Realistic: ~100 refined Ax stacks -> convert 1000 Ax -> 4000 Ti

Theoretical max Ti: ~12,000 Ti over a full game
```

Most games will produce 3,000-8,000 Ti depending on harvester count and
game duration.

## 2.4 Tiebreaker Optimization

In order of priority:
1. Refined Ax delivered to core (requires foundry pipeline)
2. Ti delivered to core (from harvesters)
3. Living harvesters (count at game end)
4. Stored Ax
5. Stored Ti

**For pure tiebreaker play:**
- Maximize harvester count (helps TB #2 and #3)
- Build exactly 1 foundry, run Ax through it, deliver refined Ax to core (TB #1)
- Do NOT convert refined Ax to Ti at core if you're winning on TB #1
- Protect harvesters (they count for TB #3)

**KEY: c.convert() moves Ax from "Ax collected" stat to "Ti collected" stat.
If you're ahead on TB #1 (refined Ax delivered), do NOT convert -- keep the
Ax stat high. If you're behind on TB #1, convert to try winning TB #2 instead.**

---

# 3. NASH EQUILIBRIA & DOMINANT STRATEGY IDENTIFICATION

## 3.1 Strategy Space Decomposition

Every bot strategy is a point in a multi-dimensional space:

```
Axes:
  - Economy aggressiveness (harvester count, timing)
  - Builder count (spawn rate)
  - Military investment (turrets, launchers)
  - Foundry timing (if at all)
  - Offense vs. defense allocation
  - Map control (road/conveyor network extent)
```

## 3.2 Pure Strategy Archetypes

### Archetype A: "Economic Turtle"
- 6-10 harvesters, heavy conveyor networks
- Barriers and gunners for defense
- Win via tiebreaker (Ti + Ax delivered to core)
- Minimal builders (3), minimal military
- Strength: Dominates passive opponents
- Weakness: Loses to early aggression, launcher raids

### Archetype B: "Rush / Early Aggression"
- 2-3 harvesters, minimal economy
- Quick road network toward enemy
- Builder bots attack enemy harvesters and conveyors
- Launcher throws bots into enemy base
- Strength: Punishes greedy economy builds
- Weakness: Falls behind if rush fails, loses tiebreakers

### Archetype C: "Fortress / Turret Wall"
- Moderate economy (4-5 harvesters)
- Heavy investment in sentinels + gunners with ammo supply
- Create kill zones that enemy builders cannot cross
- Strength: Near-impervious to builder raids
- Weakness: Expensive, may lose tiebreakers to pure economy

### Archetype D: "Adaptive / Meta"
- Scouts enemy strategy early (marker-based intel)
- Adapts: turtle vs. rushers, rush vs. turtles
- Moderate everything, adjusts ratios dynamically
- Strength: No bad matchups
- Weakness: Harder to implement well, jack-of-all-trades risk

## 3.3 Nash Equilibrium Analysis

In a 2-player symmetric zero-sum game (which this is, given symmetric maps),
the Nash equilibrium is a mixed strategy. Using a simplified payoff matrix:

```
              Opponent
              Turtle  Rush   Fortress  Adaptive
You:
Turtle        0       -1     +0.5      0
Rush          +1       0     -0.5     -0.3
Fortress     -0.5    +0.5    0        -0.2
Adaptive      0      +0.3   +0.2      0
```

The mixed NE weights roughly:
- Adaptive gets the highest floor (never loses badly)
- Rush has high variance (big wins, big losses)
- Turtle is exploitable but wins the majority of low-skill matchups
- Fortress is stable but doesn't generate enough winning edge

**RECOMMENDED STRATEGY: Adaptive with a Turtle default.**

Rationale:
1. Most opponents in the 1500-1800 range will be weak economy bots. A strong
   turtle crushes these.
2. Against top teams, the adaptive layer detects their approach and shifts
   resource allocation.
3. The adaptive layer is an INFORMATION EDGE -- most bots cannot adapt.

## 3.4 Dominant Sub-Strategies (Always Correct)

These actions are dominant regardless of opponent strategy:

1. **Build harvesters on all accessible ore as fast as possible.**
   Income > everything. A harvester built on round 10 generates 247 more Ti
   than one built on round 500.

2. **Minimize builder count.** Each builder is +20% scale for a 30 HP unit
   that moves 1 tile per round. Use the minimum to accomplish tasks.

3. **Build conveyors, not roads, as your walker network.** Conveyors cost only
   2 more Ti than roads (3 vs 1) but also transport resources. Roads are
   dead infrastructure. The only exception: roads cost 0.5% scale vs 1% for
   conveyors, so in scale-constrained late-game, roads are cheaper.

4. **Place harvesters with conveyor chains BEFORE building turrets.** Turrets
   without ammo are expensive paperweights (except launchers).

5. **Build exactly 0 or 1 foundry.** Never 2+. The +100% scale is devastating.

6. **Infer enemy core position from symmetry on round 1.** Use
   `Position(w-1-x, h-1-y)` for point symmetry or the appropriate reflection.
   This gives you a target for military operations from the start.

7. **Use markers aggressively for coordination.** A well-encoded marker system
   lets your 3-4 builders act like a coordinated team rather than independent
   random walkers.

---

# 4. META-GAME ANALYSIS FRAMEWORK

## 4.1 Replay Study Protocol

### Data Collection
1. Use the matches page (filterable by team, date) to find top-20 teams
2. Download replays of their recent matches
3. For each replay, record:

```
Game Metrics Template:
{
  team_name: "",
  elo: 0,
  map: "",
  result: "win/loss",
  round_ended: 0,
  win_condition: "core_destroyed/tiebreaker_N/coinflip",

  economy: {
    first_harvester_round: 0,
    total_harvesters: 0,
    harvester_placement_pattern: "cluster/spread/linear",
    foundry_count: 0,
    foundry_build_round: 0,
    max_conveyor_chain_length: 0,
    bridge_count: 0,
  },

  military: {
    builder_count_max: 0,
    gunner_count: 0,
    sentinel_count: 0,
    breach_count: 0,
    launcher_count: 0,
    first_turret_round: 0,
    turret_placement: "perimeter/forward/choke",
  },

  tactics: {
    uses_launcher_assault: bool,
    uses_barrier_walls: bool,
    uses_builder_raids: bool,
    uses_conveyor_as_walkway: bool,
    marker_usage: "none/basic/advanced",
    adapts_to_enemy: bool,
  },

  timing: {
    builder_spawn_rounds: [int],
    economy_to_military_transition: 0,
    first_offensive_action: 0,
  }
}
```

### Pattern Extraction
After collecting 20-30 game profiles from top teams:

1. **Cluster strategies:** Group teams by (economy_size, military_mix,
   timing_profile). Look for meta archetypes.

2. **Counter-identification:** For each archetype, identify what beats it.
   If 60% of top teams turtle, build a rush variant. If 60% rush, turtle
   with sentinel defense.

3. **Timing windows:** Identify when top teams are vulnerable. Most bots
   have a "power trough" between economy setup and military deployment.
   Exploit this window.

4. **Map-specific adaptations:** Do top teams change strategy per map?
   Small maps may favor rushing; large maps favor economy.

## 4.2 Leaderboard Monitoring

Track the Elo ladder daily:

```
Date | #1 Team | #1 Elo | #5 Elo | #10 Elo | #20 Elo | Our Rank | Our Elo
```

Key signals:
- If top Elo is climbing fast, the meta is evolving rapidly -- iterate faster
- If top Elo plateaus, the meta is settled -- find one counter
- Large Elo gaps between #1 and #5 mean #1 has a unique edge to reverse-engineer

## 4.3 Automated Scrimmaging

Use `cambc test-run` to measure performance:

```
For each candidate bot version:
  Run against:
    - starter bot (baseline sanity check)
    - our previous best (regression test)
    - saved replays of top team strategies (if reproducible)
  
  Win rate over 20+ games (across different maps and seeds)
  Record: win%, avg_round_ended, avg_tiebreaker_scores
```

Create a version log:

```
v0.1 - basic economy   -> beats starter 5/5
v0.2 - conveyor chains -> beats v0.1 5/5
v0.3 - turret defense  -> beats v0.2 4/5
...
```

---

# 5. BOT ARCHITECTURE DESIGN

## 5.1 Overall Architecture

```python
class Player:
    def __init__(self):
        # === Persistent state (survives across rounds for THIS unit) ===
        self.role = None           # assigned on first run
        self.target = None         # current objective position
        self.state = "INIT"        # state machine phase
        self.build_queue = []      # planned builds
        self.known_ore = []        # discovered ore positions
        self.enemy_core_est = None # estimated enemy core position
        self.round_born = 0        # round this unit was created

    def run(self, c: Controller) -> None:
        etype = c.get_entity_type()
        if etype == EntityType.CORE:
            self.run_core(c)
        elif etype == EntityType.BUILDER_BOT:
            self.run_builder(c)
        elif etype == EntityType.GUNNER:
            self.run_gunner(c)
        elif etype == EntityType.SENTINEL:
            self.run_sentinel(c)
        elif etype == EntityType.BREACH:
            self.run_breach(c)
        elif etype == EntityType.LAUNCHER:
            self.run_launcher(c)
```

## 5.2 Core State Machine

```
CORE STATES:
  BOOTSTRAP -> ECONOMY -> MILITARY -> ENDGAME

BOOTSTRAP (rounds 1-5):
  - Estimate enemy core position
  - Scan visible ore tiles
  - Spawn first 2-3 builders
  - Assign builder roles via markers

ECONOMY (rounds 6-150):
  - Spawn builders as needed (up to 3-4)
  - Place markers for builder assignments
  - Monitor resource income
  - Convert refined Ax if available
  - Transition trigger: 3+ harvesters online AND Ti > 200

MILITARY (rounds 150-1200):
  - Spawn military builder if needed
  - Begin turret construction orders (via markers)
  - Monitor enemy scouting markers
  - Transition trigger: round > 1200 OR enemy core spotted

ENDGAME (rounds 1200-2000):
  - Maximize tiebreaker stats
  - Defensive mode (protect harvesters)
  - Convert Ax to Ti only if winning TB #1
```

## 5.3 Builder Role Assignment

Since units cannot share globals, role assignment must happen through markers
or positional convention.

**Method 1: Birth-order convention**
- Core tracks `self.num_spawned`
- Builder tracks its birth ID (from spawn order)
- But builders don't know their birth order unless the core communicates it

**Method 2: Marker-based role assignment**
- Core places a marker on the spawn tile with role encoded
- Builder reads the marker on its birth tile in its first run() call
- Marker value encodes: [ROLE:4][TARGET_X:10][TARGET_Y:10][EXTRA:8]

**Method 3: Self-assignment by scanning**
- Builder scans nearby ore tiles on its first turn
- Picks the nearest unoccupied ore tile
- Claims it by placing a CLAIM marker
- Other builders see the CLAIM and pick different tiles

**RECOMMENDED: Hybrid of Method 2 + Method 3.**
- Core assigns general direction (N/S/E/W quadrant) via marker
- Builder self-assigns specific ore tile within that quadrant
- Claims via marker prevent duplication

### Builder Roles

```
HARVESTER_BUILDER:
  1. Move toward assigned ore tile
  2. Build harvester on ore
  3. Build conveyor chain back toward core
  4. Return to core area for next assignment

MILITARY_BUILDER:
  1. Build turrets at designated defensive positions
  2. Build ammo supply conveyors for turrets
  3. Heal damaged friendly structures
  4. Attack enemy buildings if on offensive

SCOUT:
  1. Move toward enemy territory
  2. Place markers reporting enemy positions
  3. Sabotage enemy conveyors (if reachable)
```

## 5.4 Builder State Machine (Harvester Builder)

```
States: INIT -> MOVING_TO_ORE -> BUILD_HARVESTER -> BUILD_CONVEYOR_CHAIN
        -> RETURN_TO_BASE -> AWAIT_TASK

INIT:
  - Read any marker on current tile (role assignment)
  - Scan for nearest ore tile without harvester
  - Set target = nearest ore tile
  - Transition -> MOVING_TO_ORE

MOVING_TO_ORE:
  - Build road/conveyor toward target
  - Move toward target
  - If arrived adjacent to target -> BUILD_HARVESTER
  - If blocked for 5+ rounds -> re-target or RETURN_TO_BASE

BUILD_HARVESTER:
  - If can_build_harvester(target): build it
  - Record harvester position
  - Transition -> BUILD_CONVEYOR_CHAIN

BUILD_CONVEYOR_CHAIN:
  - Plan chain: from harvester position back to core
  - Build conveyors pointing toward core, one per round
  - Move along the chain as you build it
  - When chain reaches core vicinity -> RETURN_TO_BASE

RETURN_TO_BASE:
  - Move toward core
  - Transition -> AWAIT_TASK

AWAIT_TASK:
  - Read markers for new assignments
  - If no task and idle > 10 rounds, scan for unharvested ore
  - If no ore available, switch to MILITARY_BUILDER role
```

## 5.5 Pathfinding Under Constraints

Builders can only walk on conveyors, roads, and allied core tiles. This means
pathfinding is highly constrained -- you build the path as you go.

### A* is Too Expensive (2ms budget)

Full A* on a 50x50 grid takes O(2500 * log(2500)) ~= 30,000 operations.
At Python speeds, this is ~1-2ms. Too risky.

### Recommended: Greedy Direction-First

```python
def move_toward(self, c, target):
    pos = c.get_position()
    if c.get_move_cooldown() > 0:
        return False

    best_dir = pos.direction_to(target)
    if best_dir == Direction.CENTRE:
        return False

    # Priority order: direct, left 45, right 45, left 90, right 90
    candidates = [
        best_dir,
        best_dir.rotate_left(),
        best_dir.rotate_right(),
        best_dir.rotate_left().rotate_left(),
        best_dir.rotate_right().rotate_right(),
    ]

    for d in candidates:
        if c.can_move(d):
            c.move(d)
            return True

    # Can't move -- try building a road/conveyor
    if c.get_action_cooldown() == 0:
        for d in candidates[:3]:
            adj = pos.add(d)
            if c.can_build_conveyor(adj, d):
                c.build_conveyor(adj, d)
                return False  # will move next round

    return False
```

### Advanced: BFS with Caching

Pre-compute a partial BFS from core position outward. Cache the "path map"
in the Player instance (persists across rounds). Only recompute when the
map state changes (new buildings detected).

```python
def compute_path_bfs(self, c, start, goal, max_steps=30):
    """BFS limited to max_steps nodes for CPU safety."""
    from collections import deque
    queue = deque([(start, [])])
    visited = {start}
    steps = 0
    DIRS = [d for d in Direction if d != Direction.CENTRE]

    while queue and steps < max_steps:
        pos, path = queue.popleft()
        steps += 1
        if pos == goal:
            return path
        for d in DIRS:
            npos = pos.add(d)
            if npos not in visited and c.is_in_vision(npos):
                if c.is_tile_passable(npos) or c.is_tile_empty(npos):
                    visited.add(npos)
                    queue.append((npos, path + [d]))
    return None  # no path found in budget
```

## 5.6 Conveyor Chain Builder Algorithm

This is the most critical infrastructure routine.

```python
def plan_conveyor_chain(self, c, harvester_pos, core_pos):
    """Plan a sequence of conveyor positions from harvester to core."""
    chain = []
    current = harvester_pos
    max_len = 30  # safety limit

    while current.distance_squared(core_pos) > 2 and len(chain) < max_len:
        direction = current.direction_to(core_pos)
        next_pos = current.add(direction)

        # Check if next position is valid for conveyor
        if c.is_in_vision(next_pos):
            env = c.get_tile_env(next_pos)
            if env == Environment.WALL:
                # Try to route around wall
                for alt_d in [direction.rotate_left(), direction.rotate_right()]:
                    alt_pos = current.add(alt_d)
                    if c.is_in_vision(alt_pos) and c.get_tile_env(alt_pos) != Environment.WALL:
                        chain.append((alt_pos, alt_d))
                        current = alt_pos
                        break
                else:
                    break  # stuck, need bridge
            else:
                chain.append((next_pos, direction))
                current = next_pos
        else:
            # Beyond vision, plan optimistically
            chain.append((next_pos, direction))
            current = next_pos

    return chain
```

**IMPORTANT: Build the conveyor chain FACING TOWARD CORE, not away from it.**
Conveyors output in their facing direction. So each conveyor in the chain
should face the direction of the next conveyor (toward core).

Wait -- actually, the resource originates at the harvester and flows toward the
core. So the conveyor facing direction must point TOWARD the core. The harvester
outputs to an adjacent tile. The first conveyor must accept from the harvester's
side and output toward core.

```
[Harvester] -> [Conv facing EAST] -> [Conv facing EAST] -> [Core]
                                                            
                The harvester just outputs to adjacent tiles.
                The conveyor on that tile accepts from its 3 non-output sides.
                If the conveyor faces EAST, it accepts from N, S, W.
                So the harvester should be to the WEST of the first conveyor.
```

**CRITICAL DESIGN RULE: Plan the chain from harvester to core. Each conveyor
faces in the direction of flow (toward core). Place the first conveyor adjacent
to the harvester, on the core-ward side, facing toward core.**

---

# 6. MARKER COMMUNICATION PROTOCOL

## 6.1 Design Constraints

- Each marker stores exactly one u32 (0 to 4,294,967,295)
- Markers have 1 HP -- trivially destroyed by enemies
- Any unit can place 1 marker per round (no action cooldown cost)
- Only readable by friendly units within vision range
- Markers are placed on tiles (any tile)
- Only one marker per tile (placing overwrites)
- Enemy markers cannot be overwritten -- must build over them

## 6.2 Encoding Standard

```
u32 layout: [TYPE:4][ROUND_MOD:6][X:8][Y:8][DATA:6]

TYPE (4 bits, 16 message types):
  0x0 = NOP / heartbeat
  0x1 = ORE_FOUND (unclaimed ore at position)
  0x2 = ORE_CLAIMED (builder has claimed this ore)
  0x3 = HARVESTER_BUILT (harvester exists here)
  0x4 = ENEMY_SPOTTED (enemy entity at position)
  0x5 = ENEMY_CORE (enemy core at position)
  0x6 = BUILD_TURRET_HERE (turret build order)
  0x7 = RALLY_POINT (builders should gather here)
  0x8 = DANGER_ZONE (area under enemy fire)
  0x9 = BUILDER_ROLE (role assignment from core)
  0xA = NEED_HELP (structure under attack)
  0xB = CONVEY_CHAIN_START (start of a conveyor chain)
  0xC = ECONOMY_STATUS (resource level report)
  0xD = ATTACK_ORDER (offensive target)
  0xE = DEFENSE_ORDER (defensive position)
  0xF = RESERVED

ROUND_MOD (6 bits): current_round % 64
  Used to judge freshness. Markers older than ~64 rounds are stale.

X (8 bits): target x coordinate (supports maps up to 256 wide -- 50 is max)
Y (8 bits): target y coordinate
DATA (6 bits): extra payload (role type, entity type, priority, etc.)
```

```python
def encode_marker(msg_type, round_num, x, y, data=0):
    return ((msg_type & 0xF) << 28) | \
           ((round_num % 64) << 22) | \
           ((x & 0xFF) << 14) | \
           ((y & 0xFF) << 6) | \
           (data & 0x3F)

def decode_marker(val):
    msg_type = (val >> 28) & 0xF
    round_mod = (val >> 22) & 0x3F
    x = (val >> 14) & 0xFF
    y = (val >> 6) & 0xFF
    data = val & 0x3F
    return msg_type, round_mod, x, y, data

def is_marker_fresh(round_mod, current_round, max_age=30):
    current_mod = current_round % 64
    age = (current_mod - round_mod) % 64
    return age <= max_age
```

## 6.3 Marker Placement Strategy

### Core Markers
- Core places 1 marker per round adjacent to itself
- Use for: builder role assignments, economy status, rally points
- Rotate positions to avoid overwriting important markers

### Builder Markers
- Place claim markers at ore tiles they're targeting
- Place enemy-spotted markers when scanning reveals enemies
- Place help markers if stuck or under attack

### Reading Protocol
```python
def scan_markers(c):
    """Scan all visible markers and categorize them."""
    my_team = c.get_team()
    messages = {
        'ore': [], 'enemy': [], 'orders': [],
        'claims': [], 'status': []
    }

    for eid in c.get_nearby_entities():
        if c.get_entity_type(eid) != EntityType.MARKER:
            continue
        if c.get_team(eid) != my_team:
            continue

        val = c.get_marker_value(eid)
        msg_type, round_mod, x, y, data = decode_marker(val)
        pos = Position(x, y)

        if not is_marker_fresh(round_mod, c.get_current_round()):
            continue  # ignore stale markers

        if msg_type == 0x1:
            messages['ore'].append(pos)
        elif msg_type == 0x2:
            messages['claims'].append(pos)
        elif msg_type == 0x4 or msg_type == 0x5:
            messages['enemy'].append((pos, data))
        elif msg_type in (0x6, 0x7, 0xD, 0xE):
            messages['orders'].append((msg_type, pos, data))
        elif msg_type == 0xC:
            messages['status'].append(data)

    return messages
```

## 6.4 Anti-Marker Tactics

- Enemy markers can reveal YOUR positions to their units
- If you see enemy markers near your base, build over them (any building
  on the tile destroys the marker)
- Your gunners can target enemy markers (but markers don't block LOS)
- Consider placing decoy buildings on enemy marker positions

---

# 7. DEVELOPMENT PHASES (ZERO TO #1)

## PHASE 0: Foundation (Days 1-2)

### Day 1 Goals
- [ ] Create `bots/v01/main.py` with basic skeleton
- [ ] Implement core spawning (3 builders, budget-aware)
- [ ] Implement builder: find nearest ore, build harvester
- [ ] Implement builder: build straight-line conveyor chain to core
- [ ] Test locally vs. starter bot on 5 maps
- [ ] First submission to ladder

### Day 1 Deliverables
```
v0.1 Bot Capabilities:
- Core spawns 3 builders
- Builders find ore, build harvesters
- Builders build basic conveyor chains
- No military, no markers, no pathfinding
- Should beat starter bot 5/5
```

### Day 2 Goals
- [ ] Fix conveyor chain direction bugs (MOST COMMON BUG)
- [ ] Add wall avoidance to conveyor routing
- [ ] Add ore prioritization (Ti before Ax in early game)
- [ ] Add builder role differentiation (expand N, S, E based on ore location)
- [ ] Add basic core resource management (convert Ax, budget for builders)
- [ ] Run 20+ matches on ladder

### Day 2 Deliverables
```
v0.2 Bot Capabilities:
- Reliable economy (harvesters + conveyor chains that work)
- Ore prioritization
- Basic builder coordination (don't all go to same ore)
- Budget-aware spawning
- Should reach ~1500-1550 Elo
```

## PHASE 1: Competitive Core (Days 3-5)

### Day 3: Defense Layer
- [ ] Add gunner turrets at core perimeter (facing away from core)
- [ ] Build ammo supply conveyors for gunners (from Ti harvester chain)
- [ ] Add barrier walls at key approach vectors
- [ ] Implement builder heal action (heal damaged buildings)

### Day 4: Scout and Adapt
- [ ] Implement enemy detection (scan vision for enemy entities)
- [ ] Place enemy-spotted markers
- [ ] Infer enemy core position from map symmetry
- [ ] Add adaptive builder count (more if under attack, fewer if peaceful)
- [ ] Implement builder flee behavior (if enemy turret in vision)

### Day 5: Launcher Rush
- [ ] Implement launcher + builder offensive combo
- [ ] Builder travels to launcher, gets thrown toward enemy core
- [ ] Thrown builder destroys enemy conveyors and harvesters
- [ ] Test rush timing (what round to launch? ~round 200-300)

### Phase 1 Deliverables
```
v0.5 Bot Capabilities:
- Solid economy with 4-6 harvesters
- Gunner defense ring around core
- Basic enemy detection and marker communication
- Launcher rush capability
- Should reach 1600-1700 Elo
```

## PHASE 2: Meta-Aware (Days 6-8)

### Day 6: Replay Analysis
- [ ] Watch 10+ replays of top-20 teams
- [ ] Fill out Game Metrics Template for each
- [ ] Identify dominant meta strategies
- [ ] Identify our bot's weaknesses against top teams

### Day 7: Counter-Strategy Implementation
- [ ] If meta is turtle: implement faster rush timing
- [ ] If meta is rush: implement early sentinel defense with stun
- [ ] If meta is mixed: implement adaptive detection + response
- [ ] Add round-based strategy transitions (economy -> military -> endgame)

### Day 8: Advanced Communication
- [ ] Full marker protocol implementation
- [ ] Builder task queue system via markers
- [ ] Core broadcasts economy status
- [ ] Builders report enemy positions
- [ ] Coordinated multi-builder actions

### Phase 2 Deliverables
```
v1.0 Bot Capabilities:
- Adaptive strategy selection
- Full marker communication
- Counter-strategies for known meta approaches
- Tiebreaker optimization
- Should reach 1800-2000 Elo
```

## PHASE 3: Optimization (Days 9-12)

### Day 9-10: Parameter Tuning
- [ ] Build parameter sweep framework (see Section 8)
- [ ] Tune: builder_count, harvester_target, turret_count, turret_types,
      rush_timing, economy_to_military_round, conveyor_vs_road_ratio
- [ ] Test each parameter variation over 20 games
- [ ] Select Pareto-optimal parameter set

### Day 11: Map-Specific Adaptation
- [ ] Classify maps: small (<25x25), medium (25-35), large (>35)
- [ ] Adjust strategy per size: small=rush, medium=balanced, large=economy
- [ ] Identify ore cluster patterns per map
- [ ] Build map analyzer (scan ore positions in round 1, choose strategy)
- [ ] Handle different symmetry types (reflection vs. rotation)

### Day 12: CPU Optimization
- [ ] Profile CPU usage per unit type per round
- [ ] Optimize hot paths (ore scanning, marker reading, pathfinding)
- [ ] Add CPU time guards (bail if >1500us)
- [ ] Pre-compute lookup tables in __init__ where possible
- [ ] Reduce function call overhead (inline critical paths)

### Phase 3 Deliverables
```
v2.0 Bot Capabilities:
- Tuned parameters across all map types
- Map-specific opening strategies
- CPU-optimized to stay well within 2ms
- Should reach 2000-2200 Elo
```

## PHASE 4: Edge Polish (Days 13-16)

### Day 13: Exploit Implementation
- [ ] Implement all exploits from Section 9
- [ ] Test each exploit's win rate contribution
- [ ] Implement enemy conveyor hijacking (if viable)
- [ ] Implement enemy turret ammo denial

### Day 14: Defensive Hardening
- [ ] Handle all failure modes (stuck builders, dead harvesters, cut conveyors)
- [ ] Redundant conveyor paths (backup routes if primary cut)
- [ ] Builder replacement logic (if builder dies, spawn replacement)
- [ ] Anti-launcher defense (barriers around core)

### Day 15: Final Tuning
- [ ] Run 100+ games against top ladder opponents
- [ ] Identify remaining weaknesses
- [ ] Patch specific losing matchups
- [ ] Final parameter optimization

### Day 16: Submission Lock
- [ ] Final comprehensive test (50+ games across all maps)
- [ ] Verify no CPU timeouts on any map
- [ ] Submit final version
- [ ] Monitor ladder performance
- [ ] Hot-fix submission if critical bugs found

### Phase 4 Deliverables
```
v3.0 Bot Capabilities:
- All known exploits implemented
- Defensive hardening against all known attacks
- Map-specific tuned parameters
- Robust error handling
- Target: 2200+ Elo, Grandmaster potential
```

---

# 8. OPTIMIZATION & TESTING PIPELINE

## 8.1 Local Testing Framework

```bash
# Run a single match
cambc run v3 starter arena --seed 42

# Run against multiple maps
for map in arena default_small1 default_medium1 default_large1 butterfly corridors; do
    cambc run v3 v2 $map --seed $RANDOM
done

# Remote test (enforced 2ms)
cambc test-run v3 starter
```

### Automated Test Script

```bash
#!/bin/bash
# test_suite.sh -- Run N games and tally results
BOT_A=$1
BOT_B=$2
N=${3:-20}
WINS_A=0
WINS_B=0
MAPS=(arena default_small1 default_small2 default_medium1 default_medium2
      default_large1 default_large2 butterfly corridors binary_tree
      cold cubes dna galaxy hooks)

for i in $(seq 1 $N); do
    MAP=${MAPS[$((RANDOM % ${#MAPS[@]}))]}
    SEED=$RANDOM
    RESULT=$(cambc run $BOT_A $BOT_B $MAP --seed $SEED 2>&1 | tail -1)
    # Parse result and tally
    echo "Game $i on $MAP (seed $SEED): $RESULT"
done

echo "Results: $BOT_A wins $WINS_A / $N, $BOT_B wins $WINS_B / $N"
```

## 8.2 Parameter Sweep Framework

Key tunable parameters:

```python
PARAMS = {
    'max_builders': [2, 3, 4, 5],
    'harvester_target': [3, 4, 5, 6, 8],
    'economy_to_military_round': [80, 120, 150, 200],
    'turret_count': [2, 3, 4, 6],
    'turret_type_ratio': ['all_gunner', 'gunner_sentinel_mix', 'sentinel_heavy'],
    'rush_enabled': [True, False],
    'rush_round': [150, 200, 250, 300],
    'foundry_enabled': [True, False],
    'foundry_round': [200, 300, 400],
    'defensive_barriers': [0, 4, 8],
}
```

For each parameter combination:
1. Generate a bot variant with those params
2. Run 10 games against the current best bot
3. Record win rate and tiebreaker performance
4. Select top-K performers
5. Repeat with finer grid around winners

This is equivalent to hyperparameter optimization in ML. Use a simple grid
search first, then Bayesian optimization if time permits.

## 8.3 A/B Testing Protocol

When making a change:

```
1. Baseline: current best bot (e.g., v2.3)
2. Challenger: modified bot (e.g., v2.4)
3. Run 20 games: 10 as Team A, 10 as Team B (to control for side bias)
4. Record: wins, losses, margin (rounds or tiebreaker gap)
5. Statistical significance: need >60% win rate over 20 games (p < 0.05
   binomial test)
6. If significant: promote challenger to new baseline
7. If not: reject change or refine further
```

## 8.4 Regression Testing

Maintain a suite of "milestone bots" that represent known strategy types:

```
test_bots/
  turtle_basic/     # Pure economy, no military
  rush_naive/       # Builder rush at round 100
  turret_heavy/     # Lots of gunners
  launcher_rush/    # Launcher throws at round 200
  balanced/         # Our v1.0
```

Each new version must beat ALL milestone bots >80% to avoid regression.

## 8.5 CPU Profiling

```python
# Add to bot for profiling
import time

class Player:
    def __init__(self):
        self._timings = {}

    def _time(self, label, fn, *args):
        t0 = time.perf_counter_ns()
        result = fn(*args)
        dt = (time.perf_counter_ns() - t0) / 1000  # microseconds
        self._timings[label] = self._timings.get(label, 0) + dt
        return result

    def run(self, c):
        self._time('scan', self.scan_environment, c)
        self._time('decide', self.make_decision, c)
        self._time('act', self.execute_action, c)
        # Print timing summary occasionally
        if c.get_current_round() % 100 == 0:
            import sys
            print(self._timings, file=sys.stderr)
```

---

# 9. EDGE CASES, EXPLOITS & NON-OBVIOUS MECHANICS

## 9.1 Exploitable Mechanics

### E1: Conveyor Direction Hijack
Conveyors are walkable by EITHER team's builder bots. If you build conveyors
into enemy territory, enemy builders can walk on them too. BUT: your conveyors
carry resources in YOUR direction. If an enemy conveyor points toward YOUR
buildings, it will FEED you resources.

**Exploit:** Build conveyors adjacent to enemy harvesters, pointing toward your
territory. If the harvester outputs to your conveyor, you steal their resources.

**Risk:** Low. If you have a builder near enemy harvesters, this is free income.

### E2: Builder Bot on Building Protection
"If a builder bot stands on a building, turret attacks on that tile hit ONLY
the builder bot." This means a 30 HP builder bot acts as a shield for any
building under it.

**Defensive exploit:** Park a builder on your core. Enemy turret fire hits the
30 HP builder, not the 500 HP core. Heal the builder (4 HP for 1 Ti). Net:
you absorb 30 HP of turret damage for 30 Ti + repair costs.

**Offensive exploit:** Park YOUR builder on an enemy building you want to
protect (e.g., an enemy conveyor you're hijacking). Enemy turrets can't
destroy their own building without going through your builder first.

### E3: Destroy Allied Buildings (No Cooldown)
`c.destroy(pos)` removes an allied building with no action cooldown cost. This
means a builder can destroy unlimited allied buildings per round. Uses:

- **Conveyor rerouting:** Destroy old conveyors and rebuild in new direction
- **Scale reduction:** Destroy unused buildings to reduce your own scale%
- **Clearing paths:** Destroy barriers or conveyors to make room
- **Trap removal:** If enemy conveyors are feeding them, destroy and rebuild

### E4: Turret Ammo Type Matters Enormously
- Gunner with Ti ammo: 10 damage. With refined Ax: 30 damage (3x!)
- Sentinel with refined Ax: adds +5 stun to BOTH action AND move cooldown
- A stunned builder can't move OR act for 5 extra rounds

**Exploit:** A single sentinel with refined Ax stun shuts down enemy builders
for 5 rounds. Two sentinels can perma-stun a builder (sentinel reload is 3
rounds, stun lasts 5). This is the strongest defensive ability in the game.

### E5: Marker Positioning for Information Asymmetry
Markers have 1 HP and are trivially destroyed. But they're free to place.
Place markers in YOUR territory for coordination. Place markers in NO-MAN'S
LAND for scouting. NEVER place markers in enemy territory (they'll see them
and extract information about your strategy).

**Counter-intel:** If you see enemy markers, read them! They might reveal
enemy ore locations, builder targets, or strategy phase. Then destroy them
by building over them.

### E6: Map Symmetry Exploitation

Maps are symmetric (reflection or rotation). Use this to:

1. **Immediately know enemy core position** (round 1, no scouting needed)
2. **Infer enemy ore locations** -- mirror your ore positions
3. **Predict enemy expansion paths** -- they'll expand toward the same
   relative ore positions you do

```python
def get_enemy_core_pos(c):
    my_pos = c.get_position()  # core position
    w, h = c.get_map_width(), c.get_map_height()

    # Point symmetry (180-degree rotation) -- most common
    return Position(w - 1 - my_pos.x, h - 1 - my_pos.y)

# For reflection symmetry, try:
# Horizontal: Position(w - 1 - my_pos.x, my_pos.y)
# Vertical: Position(my_pos.x, h - 1 - my_pos.y)
```

**Detection:** On round 1, check if your core is in the NW quadrant or not.
If core is near (0,0), enemy is near (w-1, h-1). This determines the
"orientation" for all strategic planning.

### E7: Harvester Output Direction Manipulation
Harvesters output to the "least-recently-used" adjacent direction. By
controlling which adjacent tiles have buildings, you can force the harvester
to output in a specific direction.

**Setup:** Place the conveyor chain on exactly ONE side of the harvester.
The harvester will output to that side consistently (it's the only accepting
tile).

### E8: Splitter for Turret Ammo Distribution
Splitters alternate output across 3 forward directions. Feed a splitter from a
harvester, and it naturally distributes ammo to 3 turrets evenly. This is the
most efficient turret ammo supply system.

### E9: Foundry Timing for Scale Gaming
Build the foundry AFTER all other expensive infrastructure (builders, sentinels,
harvesters). The +100% scale hits everything built AFTER the foundry. If you
build all 4 builders, 6 harvesters, and 4 turrets BEFORE the foundry, the
foundry's scale penalty only affects future builds (which should be cheap
conveyors and roads anyway).

**Optimal foundry timing:** Round 300-500, after all major infrastructure is
built.

### E10: Unit Cap as a Weapon
Max 50 units per team (including core). If you can force the enemy to fill
their unit cap with low-value entities (roads, markers, barriers), they can't
build turrets or harvesters.

Wait -- markers, roads, barriers, and conveyors are BUILDINGS, not UNITS.
Check the API: `get_unit_count()` counts "living units." The entity types
categorized as units are: core, builder_bot, gunner, sentinel, breach, launcher.

**So the 50-unit cap applies to: Core + Builder Bots + Turrets (gunner/sentinel/breach/launcher).** 
Buildings (conveyors, roads, barriers, harvesters, foundries, bridges) do NOT count.

This means:
- You can build unlimited conveyors, roads, harvesters, etc.
- The cap constrains builder bots + turrets
- With 1 core + 4 builders, you have room for 45 turrets
- With 1 core + 3 builders + 6 turrets, you have 40 slots remaining

**Strategic implication:** Don't waste unit slots on unnecessary builders.
3-4 builders + rest as turrets gives optimal unit allocation.

### E11: Building on Enemy Conveyors
Builder bots can walk on enemy conveyors. If the enemy has a conveyor network,
YOUR builders can walk on it to reach their base without building roads.

**Exploit:** Walk your builders on enemy conveyor infrastructure to reach their
harvesters and destroy them. You save the road/conveyor cost entirely.

### E12: Launcher Range Exploit
Launcher range is r^2 = 26 (~5.1 tiles). This is longer than most turret
attack ranges. A launcher can throw a builder bot OVER enemy defenses,
bypassing gunner kill zones entirely.

**Tactic:** Build a launcher at the edge of your territory, throw builders
directly onto enemy core tiles. The builder then has 1 turn of safety before
enemy turrets can react.

## 9.2 Timing Attacks

### T1: First Harvester Advantage
The first player to get a harvester online gains +2.5 Ti/round over the
opponent. Over 100 rounds, this compounds to +250 Ti -- enough for 8 extra
conveyors or a turret.

**Optimal opener:**
```
Round 1: Core spawns builder #1
Round 2: Builder #1 builds road/conveyor toward nearest ore
         Core spawns builder #2
Round 3: Builder #1 moves toward ore
Round 4: Builder #1 builds harvester on ore (if adjacent)
Round 5: Builder #1 starts conveyor chain back to core
```

If ore is 3 tiles from core, first harvester by round ~6-8. If 6 tiles away,
round ~12-15. Conveyor chain delay adds D more rounds.

### T2: Rush Timing Window
The opponent is most vulnerable between rounds 100-200:
- Their economy is online but not yet generating surplus
- Their military is minimal or nonexistent
- Their builders are dispersed (building infrastructure)

A launcher rush at round 200 hits during this window.

### T3: Foundry Timing Window
If an opponent builds a foundry at round 100, their scale jumps +100% at a
time when they still need to build harvesters, turrets, etc. Attack during
rounds 100-200 when their costs are inflated and their military is
underdeveloped.

### T4: Late-Game Tiebreaker Race
After round 1200, start maximizing tiebreaker stats:
- Ensure all conveyor chains are delivering to core
- Build additional harvesters on any unclaimed ore
- If you have a foundry, push refined Ax to core
- Stop building new infrastructure (save Ti for collection stat)

## 9.3 Resource Denial Strategies

### D1: Cut Enemy Conveyor Lines
A single builder can destroy an enemy conveyor (2 damage for 2 Ti, own tile
only). A 20 HP conveyor takes 10 attacks = 20 Ti and 10 rounds. But you can
also build on the tile (blocking rebuilds).

**Faster method:** Build a barrier on the enemy's conveyor path. The conveyor
chain is broken at that point. Cost: 3 Ti. The enemy must build around it
or destroy it.

Wait -- you can only build on empty tiles. You can't build ON an enemy conveyor.
You also can't destroy enemy buildings with `c.destroy()` (that's allied-only).
You can only attack buildings on your own tile with `c.fire()`.

**Corrected approach:** Walk a builder onto the enemy conveyor (you can walk on
enemy conveyors). Use `c.fire(c.get_position())` to attack the building under
you. 2 damage per round, 10 rounds to destroy a 20 HP conveyor. Then build
your own building (barrier) on that tile to block rebuilds.

### D2: Harvest Their Ore
If you can reach an enemy ore tile before they do, build your own harvester on
it. They can't build a harvester on a tile that already has a building.

**Map symmetry exploit:** You know where their ore is (mirror your ore
positions). Race a builder there to deny their economy.

### D3: Turret Ammo Denial
Enemy turrets need ammo via conveyors. If you cut the ammo conveyor, the turret
becomes useless after its current ammo is spent. A gunner has 2 ammo, a sentinel
has 10, a breach has 5. Without resupply, they fire once or twice and then
are dead weight.

---

# 10. RISK ANALYSIS & HEDGING

## 10.1 Technical Risks

### R1: CPU Timeout (CRITICAL)
- **Risk:** Bot exceeds 2ms on complex rounds, causing unit to skip its turn
- **Impact:** Lost actions, frozen builders, unresponsive turrets
- **Mitigation:**
  - Time-check at 1500us, bail early
  - Cache expensive computations across rounds
  - Use `get_nearby_tiles()` (bounded by vision) not full-map scans
  - Pre-compute ore lists, path plans in __init__
  - Profile on largest maps (50x50) with maximum entities

### R2: Conveyor Chain Bugs (HIGH)
- **Risk:** Conveyors built facing wrong direction, resources go nowhere
- **Impact:** Zero income from harvester, wasted Ti
- **Mitigation:**
  - Extensive testing on all map shapes
  - Visual debugging with `draw_indicator_line()` to trace chains
  - Assertion checks in code (direction should point toward core)
  - Test every conveyor build with a simulation

### R3: Builder Gets Stuck (HIGH)
- **Risk:** Builder can't find path (surrounded by unwalkable tiles)
- **Impact:** Wasted builder, wasted 30 Ti + 20% scale
- **Mitigation:**
  - Stuck detection: if builder hasn't moved in 5 rounds, enter "unstick" mode
  - Unstick: destroy adjacent allied buildings to create path, or self-destruct
  - Builder always builds road/conveyor before trying to move
  - Fall back to random direction if target direction blocked

### R4: Economy Failures (MEDIUM)
- **Risk:** All harvesters destroyed, no income besides passive
- **Impact:** Slow death as enemy outeconomies you
- **Mitigation:**
  - Redundant harvesters (build on multiple ore clusters)
  - Protective barriers around harvesters
  - Rapid rebuilding protocol: detect harvester death, spawn new builder,
    rush to rebuild
  - Sentinel defense near harvesters

### R5: Game Update / Rule Change (LOW)
- **Risk:** Game organizers patch rules before qualifier
- **Impact:** Strategy may become invalid
- **Mitigation:**
  - Monitor discord for announcements
  - Keep bot architecture modular (easy to swap strategies)
  - Re-read docs before final submission

## 10.2 Strategic Risks

### R6: Counter-Exploited (HIGH)
- **Risk:** Top teams develop specific counters to our strategy
- **Impact:** Win rate drops against top opponents
- **Mitigation:**
  - Multiple strategy modes (adaptive bot can switch)
  - Don't reveal final strategy too early (save v3.0 for last few days)
  - Build counters for likely counters to our strategy

### R7: Map-Specific Weakness (MEDIUM)
- **Risk:** Some maps are structurally bad for our approach
- **Impact:** Lose specific games in best-of-5
- **Mitigation:**
  - Test on ALL 38 maps
  - Map classifier in round 1 (size, ore distribution, wall density)
  - Map-specific parameter adjustments
  - Minimize number of "auto-loss" maps

### R8: Insufficient Match Count (MEDIUM)
- **Risk:** Not enough rated matches to reach high Elo by qualifier
- **Impact:** Low seeding or not qualifying
- **Mitigation:**
  - Submit early (day 2) and iterate
  - Keep bot competitive at all times (never submit a broken bot)
  - Each submission should be strictly better than the last
  - Elo gains compound: early wins against weak bots are easy Elo

### R9: Late-Game Tiebreaker Loss (MEDIUM)
- **Risk:** Win economy but lose on tiebreaker technicalities
- **Impact:** Lose close games
- **Mitigation:**
  - Understand tiebreaker order perfectly
  - Implement tiebreaker optimization starting at round 1200
  - Track refined Ax delivered, Ti delivered, harvester count
  - Make strategic decisions based on tiebreaker position

## 10.3 Risk-Adjusted Development Priority

Rank all tasks by: Impact * P(occurrence) / Development_cost

| Priority | Task | Risk Addressed | Est. Hours |
|----------|------|----------------|------------|
| 1 | Basic economy (harvest + convey) | R4, core functionality | 4h |
| 2 | Conveyor chain correctness | R2 | 3h |
| 3 | CPU time management | R1 | 2h |
| 4 | Builder unstuck logic | R3 | 2h |
| 5 | Gunner defense | R6, R4 | 3h |
| 6 | Marker communication | core functionality | 4h |
| 7 | Launcher rush | offensive capability | 3h |
| 8 | Map-specific adapter | R7 | 4h |
| 9 | Tiebreaker optimizer | R9 | 2h |
| 10 | Sentinel stun defense | R6 | 3h |

---

# APPENDIX A: CRITICAL PARAMETER LOOKUP TABLE

## A.1 Scale Progression Calculator

Starting at 100%. Common build orders and their scale impact:

```
Economy Opening (recommended):
  3 builders: +60%   -> 160%
  6 harvesters: +30% -> 190%
  15 conveyors: +15% -> 205%
  10 roads: +5%      -> 210%
  Total: scale 210% (all costs ~2.1x base)

Aggressive Opening (risky):
  5 builders: +100%  -> 200%
  4 harvesters: +20% -> 220%
  10 conveyors: +10% -> 230%
  2 gunners: +20%    -> 250%
  1 foundry: +100%   -> 350%
  Total: scale 350% (all costs ~3.5x base)

Lean Opening (conservative):
  2 builders: +40%   -> 140%
  4 harvesters: +20% -> 160%
  10 conveyors: +10% -> 170%
  5 roads: +2.5%     -> 172.5%
  Total: scale 172.5% (all costs ~1.73x base)
```

## A.2 Cost Table at Various Scale Levels

| Entity | Base | 150% | 200% | 250% | 300% |
|--------|------|------|------|------|------|
| Builder | 30 Ti | 45 | 60 | 75 | 90 |
| Harvester | 20 Ti | 30 | 40 | 50 | 60 |
| Conveyor | 3 Ti | 4 | 6 | 7 | 9 |
| Road | 1 Ti | 1 | 2 | 2 | 3 |
| Gunner | 10 Ti | 15 | 20 | 25 | 30 |
| Sentinel | 30 Ti | 45 | 60 | 75 | 90 |
| Foundry | 40 Ti | 60 | 80 | 100 | 120 |
| Barrier | 3 Ti | 4 | 6 | 7 | 9 |
| Bridge | 20 Ti | 30 | 40 | 50 | 60 |
| Launcher | 20 Ti | 30 | 40 | 50 | 60 |
| Breach | 15 Ti | 22 | 30 | 37 | 45 |

## A.3 DPS Comparison Table

| Turret | DPS (Ti ammo) | DPS (Refined Ax) | Cost | DPS/Cost |
|--------|---------------|-------------------|------|----------|
| Gunner | 10/1=10 | 30/1=30 | 10 Ti | 1.0 (3.0 Ax) |
| Sentinel | 18/3=6 | 18/3+stun=6+ | 30 Ti | 0.2 (0.2+stun) |
| Breach | N/A | (40+20)/1=60 | 15+10Ax | ~2.4 (Ax only) |

**Gunner is the most cost-efficient DPS per Ti. Breach has highest raw DPS
but requires refined Ax for both construction and ammunition.**

## A.4 Effective HP/Cost Ratio

| Building | HP | Cost | HP/Ti |
|----------|----|----|-------|
| Barrier | 30 | 3 | 10.0 |
| Conveyor | 20 | 3 | 6.67 |
| Armoured Conveyor | 50 | 5+5Ax | 5.0 (Ti only) |
| Harvester | 30 | 20 | 1.5 |
| Foundry | 50 | 40 | 1.25 |
| Gunner | 40 | 10 | 4.0 |
| Sentinel | 30 | 30 | 1.0 |
| Breach | 60 | 15+10Ax | 2.4 (Ti only) |
| Road | 5 | 1 | 5.0 |

**Barriers are the most cost-efficient HP in the game (10 HP per Ti).
Use them liberally for defensive walls.**

## A.5 Vision Range Reference (Tiles from Entity)

```
Core:      r^2=36  -> ~6.0 tiles   (12x12 visible area roughly)
Builder:   r^2=20  -> ~4.5 tiles   (9x9 visible area roughly)
Sentinel:  r^2=32  -> ~5.7 tiles   (11x11 visible area roughly)
Launcher:  r^2=26  -> ~5.1 tiles   (10x10 visible area roughly)
Gunner:    r^2=13  -> ~3.6 tiles   (7x7 visible area roughly)
Breach:    r^2=13  -> ~3.6 tiles   (7x7 visible area roughly)
```

---

# APPENDIX B: OPENING BOOK

## B.1 Standard Economic Opening (Recommended Default)

```
Round 1:
  Core: spawn builder #1 toward nearest Ti ore
  
Round 2:
  Core: spawn builder #2 toward second nearest ore
  Builder #1: build conveyor/road toward ore, move

Round 3:
  Core: spawn builder #3
  Builders: continue moving toward ore

Rounds 4-10:
  Builders: reach ore, build harvesters
  Start conveyor chains back to core

Rounds 11-25:
  Complete conveyor chains
  Builders return for next assignment or go to more ore

Rounds 25-50:
  All harvesters online (target: 4-6)
  Builders start defensive infrastructure

Rounds 50-100:
  Gunners placed at 2-3 key positions
  Ammo supply conveyors for gunners
  Barriers at approach vectors

Round 100+:
  Economy surplus, begin mid-game strategy
```

## B.2 Rush Opening (Anti-Turtle)

```
Round 1-3:
  Spawn 2 builders, send toward ore
  
Round 4-10:
  Build 2 harvesters, minimal conveyor chains

Round 10-50:
  Build conveyors/roads toward enemy base
  Spawn builder #3 for rush
  Build launcher near midfield

Round 50-100:
  Launch builder into enemy base
  Sabotage enemy harvesters and conveyors

Round 100+:
  Continue disruption while building own economy
```

## B.3 Fortress Opening (Anti-Rush)

```
Round 1-3:
  Spawn 2 builders, build harvesters on closest ore only

Round 4-15:
  Short conveyor chains (close ore only)
  Build barriers around core perimeter

Round 15-40:
  Build 2 sentinels facing likely approach directions
  Ammo supply for sentinels

Round 40-100:
  Expand economy once defenses are set
  Additional gunners at extended perimeter

Round 100+:
  Economy catch-up, then transition to offense
```

---

# APPENDIX C: MAP CLASSIFICATION SYSTEM

## C.1 Map Size Classification

```python
def classify_map(c):
    w, h = c.get_map_width(), c.get_map_height()
    area = w * h
    if area <= 625:    # <=25x25
        return 'SMALL'
    elif area <= 1225:  # <=35x35
        return 'MEDIUM'
    else:               # >35x35
        return 'LARGE'
```

## C.2 Strategy by Map Size

| Map Size | Economy Weight | Military Weight | Recommended Opening |
|----------|---------------|-----------------|---------------------|
| Small | 40% | 60% | Rush or Fortress |
| Medium | 60% | 40% | Standard Economic |
| Large | 70% | 30% | Heavy Economic |

## C.3 Ore Distribution Analysis (Round 1)

```python
def analyze_ore(c):
    """Scan visible ore and classify distribution."""
    pos = c.get_position()
    ti_ores = []
    ax_ores = []
    
    for tile in c.get_nearby_tiles():
        env = c.get_tile_env(tile)
        if env == Environment.ORE_TITANIUM:
            ti_ores.append(tile)
        elif env == Environment.ORE_AXIONITE:
            ax_ores.append(tile)
    
    # Classify
    avg_dist = sum(pos.distance_squared(t) for t in ti_ores) / max(len(ti_ores), 1)
    
    return {
        'ti_count': len(ti_ores),
        'ax_count': len(ax_ores),
        'avg_ti_dist_sq': avg_dist,
        'has_close_ore': any(pos.distance_squared(t) <= 8 for t in ti_ores),
        'has_ax': len(ax_ores) > 0,
    }
```

## C.4 Symmetry Detection

```python
def detect_symmetry(c):
    """Try to detect map symmetry type by checking a few tiles."""
    pos = c.get_position()
    w, h = c.get_map_width(), c.get_map_height()
    
    # Point symmetry: env(x,y) == env(w-1-x, h-1-y)
    # Horizontal reflection: env(x,y) == env(w-1-x, y)
    # Vertical reflection: env(x,y) == env(x, h-1-y)
    
    # Test with visible tiles
    point_match = 0
    h_match = 0
    v_match = 0
    total = 0
    
    for tile in c.get_nearby_tiles():
        x, y = tile.x, tile.y
        env = c.get_tile_env(tile)
        
        # Check point symmetric position
        px, py = w-1-x, h-1-y
        if 0 <= px < w and 0 <= py < h:
            p_pos = Position(px, py)
            if c.is_in_vision(p_pos):
                if c.get_tile_env(p_pos) == env:
                    point_match += 1
                total += 1
    
    if total > 0 and point_match / total > 0.9:
        return 'POINT'
    # Would need more sophisticated detection for other types
    # Default to point symmetry (most common)
    return 'POINT'
```

---

# APPENDIX D: COMPLETE DECISION TREE

## D.1 Core Decision Tree (per round)

```
CORE ROUND:
  |
  +-> Check: need to convert Ax to Ti?
  |   |
  |   +-> If refined Ax > 20 AND (winning TB#1 AND not gaining more Ax):
  |       convert(ax - 10)
  |
  +-> Check: should spawn builder?
  |   |
  |   +-> Count active builders (unit_count - 1 - turret_count)
  |   +-> If below target AND can afford AND unit_cap not hit:
  |   |   spawn builder
  |   +-> If active builders at target:
  |       skip
  |
  +-> Place strategic marker
      |
      +-> Round % 4 == 0: broadcast economy status
      +-> Round % 4 == 1: broadcast rally point (if needed)
      +-> Round % 4 == 2: broadcast build orders
      +-> Round % 4 == 3: broadcast threat intel
```

## D.2 Builder Decision Tree (per round)

```
BUILDER ROUND:
  |
  +-> If INIT state:
  |   |
  |   +-> Read nearby markers for role assignment
  |   +-> Scan for ore tiles
  |   +-> Set target, transition to appropriate state
  |
  +-> If MOVING_TO_ORE:
  |   |
  |   +-> Am I adjacent to target ore?
  |   |   +-> YES: transition to BUILD_HARVESTER
  |   |   +-> NO: move_toward(target)
  |   +-> Stuck for 5+ rounds?
  |       +-> Re-target or self-destruct
  |
  +-> If BUILD_HARVESTER:
  |   |
  |   +-> can_build_harvester(target)?
  |   |   +-> YES: build it, transition to BUILD_CHAIN
  |   |   +-> NO: wait or re-target
  |
  +-> If BUILD_CHAIN:
  |   |
  |   +-> Next conveyor in chain built?
  |   |   +-> YES: advance to next position
  |   |   +-> NO: build it
  |   +-> Chain complete (reached core area)?
  |       +-> YES: transition to AWAIT_TASK
  |
  +-> If MILITARY:
  |   |
  |   +-> Have build order from markers?
  |   |   +-> YES: move to position, build turret/barrier
  |   |   +-> NO: default to defensive positions
  |   +-> See enemy? Place enemy-spotted marker
  |
  +-> If ATTACK:
  |   |
  |   +-> On enemy building? fire() if can
  |   +-> Not on enemy building? move toward target
  |
  +-> EVERY STATE: check for enemies in vision, place markers if found
```

---

# APPENDIX E: QUANTITATIVE BENCHMARKS

## E.1 Target Performance Metrics

| Metric | Phase 0 | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|--------|---------|---------|---------|---------|---------|
| Win vs starter | 100% | 100% | 100% | 100% | 100% |
| Harvesters by R100 | 2-3 | 4-5 | 5-6 | 5-8 | 5-8 |
| First harvester round | <20 | <15 | <10 | <8 | <8 |
| Ti at R200 | >300 | >500 | >600 | >700 | >700 |
| Turrets by R200 | 0 | 2-3 | 3-4 | 4-6 | 4-6 |
| Builder waste | High | Medium | Low | Low | Minimal |
| CPU per unit avg | <1500us | <1200us | <1000us | <800us | <600us |
| Target Elo | 1500 | 1650 | 2000 | 2200 | 2400+ |

## E.2 Income Benchmarks

```
Passive only (2000 rounds): 5,000 Ti total
+ 4 Ti harvesters: 5,000 + 4*490 = 6,960 Ti
+ 6 Ti harvesters: 5,000 + 6*490 = 7,940 Ti
+ 8 Ti harvesters: 5,000 + 8*490 = 8,920 Ti
+ Foundry Ax conversion: additional 2,000-4,000 Ti
```

## E.3 Combat Math

### Builder vs. Building (fire on own tile)
```
Attack: 2 damage, costs 2 Ti per round
To destroy:
  Conveyor (20 HP): 10 rounds, 20 Ti
  Barrier (30 HP): 15 rounds, 30 Ti
  Gunner (40 HP): 20 rounds, 40 Ti
  Harvester (30 HP): 15 rounds, 30 Ti
  Foundry (50 HP): 25 rounds, 50 Ti
  Core (500 HP): 250 rounds, 500 Ti -- not practical solo
```

### Turret vs. Builder
```
Gunner (Ti ammo): 10 damage, kills builder in 3 shots (3 rounds)
Gunner (Ax ammo): 30 damage, kills builder in 1 shot (1 round)
Sentinel: 18 damage, kills builder in 2 shots (6 rounds)
Sentinel (Ax stun): 18 damage + 5 round stun, kills in 2 shots
Breach: 40 damage, kills builder in 1 shot (plus 20 splash)
```

### Core Rush Math
```
Each builder does 2 dmg/round to a building on its tile.
Core has 500 HP.
Solo builder: 250 rounds to kill core (not viable).
5 builders on core: 10 dmg/round -> 50 rounds (somewhat viable).
10 builders on core: 20 dmg/round -> 25 rounds (viable but expensive).

Alternative: 2 breach turrets near core
  Each breach: 40 + 20 splash = 60 total dmg/round
  2 breaches: 120 dmg/round -> ~5 rounds to kill core
  BUT: need refined Ax ammo supply, expensive setup
```

---

# APPENDIX F: DAILY EXECUTION CHECKLIST

## Day 1 Checklist
- [ ] Set up development environment
- [ ] Create v0.1 bot with basic economy
- [ ] Test on 5 maps locally
- [ ] Fix critical bugs
- [ ] First ladder submission
- [ ] Monitor first 10 matches

## Day 2 Checklist
- [ ] Fix conveyor chain bugs from Day 1
- [ ] Add wall avoidance
- [ ] Add ore prioritization
- [ ] Submit v0.2
- [ ] Monitor ladder results
- [ ] Begin replay analysis of top teams

## Day 3 Checklist
- [ ] Add gunner defense
- [ ] Add ammo supply system
- [ ] Add barrier walls
- [ ] Submit v0.3
- [ ] A/B test: v0.3 vs v0.2 (20 games)

## Day 4 Checklist
- [ ] Add enemy detection
- [ ] Add marker communication
- [ ] Add adaptive builder count
- [ ] Submit v0.4

## Day 5 Checklist
- [ ] Add launcher rush
- [ ] Add offensive builder behavior
- [ ] Submit v0.5
- [ ] Evaluate: are we on track for 1700+ Elo?

## Day 6-7 Checklist
- [ ] Replay analysis complete (10+ top team games)
- [ ] Counter-strategies identified
- [ ] Counter-strategies implemented
- [ ] Submit v1.0

## Day 8-9 Checklist
- [ ] Full marker protocol
- [ ] Map classifier
- [ ] Strategy adapter
- [ ] Submit v1.5

## Day 10-12 Checklist
- [ ] Parameter sweep complete
- [ ] CPU optimized
- [ ] 50+ local test games
- [ ] Submit v2.0

## Day 13-14 Checklist
- [ ] Exploit implementations
- [ ] Defensive hardening
- [ ] Submit v2.5

## Day 15-16 Checklist
- [ ] Final testing (100+ games)
- [ ] Bug fixes
- [ ] Submit v3.0 (FINAL)
- [ ] Monitor and hot-fix if needed

---

# APPENDIX G: COMPETITIVE INTELLIGENCE

## G.1 Elo Ladder Tracking Template

```
Date | Our Elo | Our Rank | Matches | Top 10 Elo Range | Notes
-----|---------|----------|---------|-------------------|------
D1   | 1500    | 486      | 0       | 2400-2791         |
D2   |         |          |         |                   |
D3   |         |          |         |                   |
...  |         |          |         |                   |
D16  |         |          |         |                   |
```

## G.2 Opponent Scouting Sheet

```
Team Name:
Current Elo:
Strategy Archetype: [Turtle / Rush / Fortress / Adaptive / Unknown]
Key Observations:
  - Economy pattern:
  - Military pattern:
  - Timing:
  - Weaknesses:
Counter-strategy:
```

---

# APPENDIX H: THE WINNING FORMULA (SUMMARY)

## The Core Thesis

The game rewards **economic efficiency** above all. In the absence of
successful core destruction (rare at high level), tiebreakers determine the
winner. Tiebreakers reward resource delivery to core, which is a pure economy
metric.

**Therefore: the winning bot is the one with the best economy, defended just
enough to survive.**

## The Optimal Strategy Profile

```
1. ECONOMY FIRST: 5-8 harvesters online by round 100
2. LEAN BUILDERS: exactly 3 builders, no more
3. EFFICIENT CONVEYORS: shortest possible chains, no bridges unless forced
4. TIMING DEFENSE: gunners + sentinels at round 100-150, not before
5. FOUNDRY LATE: 1 foundry at round 300+ if Ax is available
6. TIEBREAKER AWARE: maximize refined Ax delivery after round 1200
7. ADAPTIVE OFFENSE: launcher rush only if enemy is vulnerable
8. MAP AWARE: adjust timings based on map size and ore proximity
```

## The One-Line Summary

**Build the best economy as fast as possible, defend it just enough, and
maximize resource delivery to core for tiebreakers. Rush only when the
expected value is positive.**

---

END OF ROADMAP
Document version: 1.0
Generated: April 4, 2026
Next review: April 7, 2026 (after Phase 0 completion)
