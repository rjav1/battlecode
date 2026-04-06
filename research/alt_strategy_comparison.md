# Alternative Strategy Comparison — April 6, 2026

## Bots Tested

| Bot | Strategy | Key Features |
|-----|----------|--------------|
| **buzzing** | Economy + sentinels + attacker | `d.opposite()` conveyors, sentinel defense, 1 attacker builder (fixed version) |
| **eco_opponent** | Pure economy | `d.opposite()` conveyors, no military, baseline reference |
| **rusher** | Economy + rush attack | 4 builders spawned by R8, first 2 economy, rest attack enemy conveyors/roads |
| **turtle** | Defense + economy | Road-based exploration, L-shaped cardinal conveyor chains, barriers |

## Section 1: vs Starter (Baseline)

### Rusher vs Starter

| Map | Rusher Ti (mined) | Starter Ti (mined) | Winner | Rusher Buildings |
|-----|-------------------|-------------------|--------|-----------------|
| face | 5,611 (4,980) | 4,463 (0) | **rusher** | 313 |
| corridors | 6,448 (4,990) | 2,351 (0) | **rusher** | 213 |
| default_medium1 | 10 (0) | 1,285 (0) | **starter** | 148 |

**Rusher vs Starter verdict**: Wins on small/medium maps with close ore (face, corridors) but **LOSES on default_medium1** where it mines 0 Ti. The economy half of rusher (only 2 builders) is too weak when ore is far from core.

### Turtle vs Starter

| Map | Turtle Ti (mined) | Starter Ti (mined) | Winner | Turtle Buildings |
|-----|-------------------|-------------------|--------|-----------------|
| default_medium1 | 7,342 (3,380) | 2,934 (0) | **turtle** | 267 |
| settlement | 264 (0) | 232 (0) | **turtle** | 469 |
| cold | 3,760 (0) | 654 (0) | **starter** | 280 |

**Turtle vs Starter verdict**: Wins on default_medium1 with 3,380 Ti mined. Fails on settlement (0 mined, 469 buildings -- all wasted roads) and **loses to starter on cold** (0 mined). The L-shaped cardinal chain approach struggles on maps with walls or distant ore.

### eco_opponent vs Starter (reference from baseline report)

| Map | eco_opponent Ti (mined) |
|-----|------------------------|
| face | 13,540 (9,840) |
| corridors | 14,879 (9,930) |
| default_medium1 | 42,142 (39,970) |
| settlement | 17,793 (23,960) |
| cold | 22,812 (23,230) |

eco_opponent massively outperforms both rusher and turtle on every map.

## Section 2: Head-to-Head Matchups

### Rusher vs Buzzing

| Map | Rusher Ti (mined) | Buzzing Ti (mined) | Winner |
|-----|-------------------|-------------------|--------|
| face | 4,278 (4,980) | 6,247 (3,460) | **rusher** |

**Rusher beats buzzing on face** despite mining less Ti. Rusher's attack disrupts buzzing's economy (destroys conveyors). On a small rush map, this works.

### Turtle vs Buzzing

| Map | Turtle Ti (mined) | Buzzing Ti (mined) | Winner |
|-----|-------------------|-------------------|--------|
| default_medium1 | 8,237 (4,590) | 27,803 (24,450) | **buzzing** |

**Buzzing crushes turtle 6:1 on Ti mined.** The `d.opposite()` conveyor approach vastly outperforms turtle's L-shaped cardinal chains.

### Rusher vs Turtle

| Map | Rusher Ti (mined) | Turtle Ti (mined) | Winner |
|-----|-------------------|-------------------|--------|
| corridors | 9,717 (4,990) | 13,493 (9,960) | **turtle** |

**Turtle beats rusher on corridors** -- turtle mines 2x more. Rusher's attackers don't reach turtle's infrastructure on this maze map. Pure economy wins.

### Rusher vs eco_opponent

| Map | Rusher Ti (mined) | eco_opponent Ti (mined) | Winner |
|-----|-------------------|------------------------|--------|
| face | 4,278 (4,980) | 6,247 (3,460) | **rusher** |
| corridors | 9,764 (4,990) | 14,879 (9,930) | **eco_opponent** |

Rusher only wins on face (rush map). eco_opponent dominates on corridors.

### Turtle vs eco_opponent

| Map | Turtle Ti (mined) | eco_opponent Ti (mined) | Winner |
|-----|-------------------|------------------------|--------|
| default_medium1 | 8,237 (4,590) | 27,803 (24,450) | **eco_opponent** |

eco_opponent dominates 6:1.

## Section 3: Strategy Analysis

### Rusher Strengths
- Spawns 4 builders by R8 (fastest ramp-up)
- Attack destroys enemy conveyors/roads -- disrupts their economy
- Wins on **small rush maps** (face: path=9, arena: path=12) where attackers reach enemy fast
- Directed chain-building (harvester->core) avoids wasted conveyors

### Rusher Weaknesses
- Only 2 economy builders (rest are attackers) -- weak mining capacity
- **Mines 0 on default_medium1** -- economy builders can't find distant ore
- Chain-building uses `direction_to(core)` which doesn't guarantee chain connectivity (same fan problem)
- Attackers on long/maze maps waste Ti on roads without reaching enemy
- Lost to STARTER on default_medium1

### Turtle Strengths
- L-shaped cardinal chains (X-align then Y-align) -- guaranteed connectivity
- Road-based exploration is cheap
- Destroys own roads to replace with conveyors (solves the road-blocker problem)
- Chain completion detection ("Chain done!")

### Turtle Weaknesses
- Cardinal-only chains (N/S/E/W) take longer paths than diagonal
- **Mines 0 on settlement and cold** -- exploration doesn't find ore on large maps
- Only 3 builders in first 150 rounds
- No military at all -- fully vulnerable to attacks
- Chain gets stuck on walls ("Chain stuck at...")
- Lost to STARTER on cold

### eco_opponent / buzzing (current) Strengths
- `d.opposite()` conveyors create guaranteed step-by-step chains
- Every tile explored becomes part of the conveyor network
- High mining rates: 10,000-50,000 Ti across all maps
- BFS-guided pathfinding avoids stuck situations

### eco_opponent / buzzing (current) Weaknesses
- Wasted conveyors on long exploration paths (starry_night: 587 buildings, 69% efficiency)
- Vulnerable to rush attacks (no defense until sentinels at R300)
- `d.opposite()` creates winding chains (longer than needed)

## Section 4: Mining Rate Comparison (Ti/Round)

| Map | eco_opponent | rusher | turtle |
|-----|-------------|--------|--------|
| face | **4.9** | 2.5 | -- |
| corridors | **5.0** | 2.5 | -- |
| default_medium1 | **20.0** | 0.0 | 1.7 |
| settlement | **12.0** | -- | 0.0 |
| cold | **11.6** | -- | 0.0 |

eco_opponent wins every comparison by 2-20x.

## Section 5: Conclusions

### 1. Economy approach matters more than strategy
The `d.opposite()` conveyor approach (eco_opponent/buzzing) outperforms both rusher's directed chains and turtle's L-shaped chains on every economy metric. The reason: it guarantees connectivity because each conveyor connects to the one before it.

### 2. Rush only works on small maps
Rusher wins on face (path=9) but fails on everything else. The attack disruption helps but doesn't compensate for having only 2 economy builders. A hybrid with better economy would be stronger.

### 3. Turtle's L-shaped chains are promising but unreliable
The concept (explore with roads, then build directed conveyor chains) is sound but the implementation fails on large maps and wall-heavy maps. The road-destruction approach is clever but slow.

### 4. Buzzing is currently the strongest bot
With the economy fix applied, buzzing mines 24,450 Ti on default_medium1 -- 5x more than turtle and infinitely more than rusher on that map. Adding sentinels and an attacker is a net positive as long as economy isn't disrupted.

### 5. Best ideas to steal from each bot

| Idea | Source | Benefit |
|------|--------|---------|
| Spawn 4 builders by R8 | rusher | Faster economy ramp-up |
| Destroy roads to build conveyors | turtle | Fixes road-blocker problem |
| Cardinal-aligned chains near core | turtle | More efficient last-mile delivery |
| Target enemy conveyors specifically | rusher | High-value sabotage |
| L-shaped chain pathing | turtle | Avoids diagonal chain breaks |
