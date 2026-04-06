# Barrier Placement Strategy
## Cambridge Battlecode 2026
### Compiled: April 5, 2026

---

## BARRIER STATS RECAP

| Stat | Value |
|------|-------|
| HP | 30 |
| Cost | 3 Ti (base, scales with global cost multiplier) |
| Scale impact | +1% per barrier |
| Walkable | **NO** -- builders CANNOT walk on barriers |
| Blocks LoS | Yes -- gunner shots are blocked by barriers |
| Can be attacked | Enemy builders can attack buildings on their own tile for 2 dmg/2 Ti. But builders can only stand on walkable tiles. Since barriers are NOT walkable, enemy builders CANNOT stand on a barrier. They can only attack from an adjacent tile via `c.fire(pos)` if the barrier is within action radius (r^2 = 2). |
| Sentinel interaction | Sentinels hit "all tiles within 1 king-move of the forward line." Barriers on those tiles absorb the 18 damage. Sentinels CAN shoot over/around barriers since their pattern is area-based, not ray-based. |
| Heal | Allied builders can heal barriers: 4 HP for 1 Ti from action radius |

---

## QUESTION 1: Do Barriers Block Our Own Builders?

**YES.** Barriers are NOT walkable. Builders can only walk on:
- Conveyors (any variant, any direction, any team)
- Roads (either team)
- Allied core tiles

This is the single most important constraint for barrier placement. **A barrier wall with no gaps will trap our own builders inside.** Every barrier layout MUST include gaps (roads or conveyors) for builder passage.

---

## QUESTION 2: Can Enemies Destroy Barriers?

**Partially.** Enemy interaction with barriers:

1. **Enemy builder attack (`c.fire`):** Deals 2 damage per attack, costs 2 Ti. BUT the builder must be on the barrier's tile to fire at it. Since barriers are NOT walkable, an enemy builder CANNOT stand on a barrier tile. The builder must use `c.fire(pos)` where `pos` is a tile within action radius (r^2 = 2) that contains an enemy building. This means the builder must stand on an ADJACENT walkable tile and fire at the barrier. At 2 damage per attack, it takes **15 attacks** to destroy a 30 HP barrier, costing the enemy 30 Ti.

2. **Enemy sentinel fire:** 18 damage per shot. Destroys a barrier in 2 shots (18 + 18 = 36 > 30). With 3-round reload, that's 6 rounds to destroy one barrier.

3. **Enemy gunner fire:** 10 damage per shot (30 with Ax). Destroys a barrier in 3 shots (10 + 10 + 10 = 30). BUT gunner fire is blocked by the FIRST barrier it hits -- so barriers effectively shield everything behind them from gunners.

4. **Enemy breach fire:** 40 direct damage. One-shots a barrier. But breach requires refined axionite (nobody uses foundries).

**Key insight:** Barriers are primarily vulnerable to sentinels (2 shots to destroy) and builder attacks (15 attacks, expensive). Against gunners, barriers are EXCELLENT shields. Against most opponents at Diamond tier (who don't have armed turrets), barriers are nearly indestructible.

---

## QUESTION 3: Scale Cost Analysis

### 36 Barriers (Axionite Inc's approach)

| Metric | Value |
|--------|-------|
| Total Ti cost (at 1.0x scale) | 108 Ti |
| Total scale increase | +36% |
| Total HP added | 1080 HP |
| HP per Ti | 10.0 |
| HP per scale% | 30.0 |
| Cost with 36% scale already applied | Varies (built incrementally) |

**Incremental cost calculation:**
If barriers are built one at a time from a starting scale of 1.0x:
- Barrier #1: floor(1.00 * 3) = 3 Ti, scale becomes 1.01x
- Barrier #10: floor(1.09 * 3) = 3 Ti, scale becomes 1.10x
- Barrier #20: floor(1.19 * 3) = 3 Ti, scale becomes 1.20x
- Barrier #30: floor(1.29 * 3) = 3 Ti, scale becomes 1.30x
- Barrier #36: floor(1.35 * 3) = 4 Ti, scale becomes 1.36x

Total actual Ti spent: ~110-115 Ti (slightly above 108 due to rounding up at higher scales)

**But scale affects ALL future costs:**
At 1.36x scale, a sentinel that costs 30 Ti base now costs floor(1.36 * 30) = 40 Ti.
A harvester that costs 20 Ti base now costs floor(1.36 * 20) = 27 Ti.
A builder bot that costs 30 Ti base now costs floor(1.36 * 30) = 40 Ti.

### Is 36% Scale Too Expensive?

**It depends on timing.** If barriers are built AFTER the main economy is established (harvesters + conveyor chains), the scale increase is manageable because income is flowing. If barriers are built BEFORE economy, every subsequent harvester and builder costs 36% more, crippling expansion.

**Axionite Inc builds barriers AFTER economy.** In their hourglass game, they had 7 harvesters producing 19240 Ti by round 2000. The 38 barriers (+38% scale) were affordable because the economy supported it.

**For our bot at 1490 Elo:** We should NOT build 36 barriers. We should start with 4-8 barriers around the core (12-24 Ti, +4-8% scale) and scale up only after the economy is running.

---

## QUESTION 4: Optimal Placement Patterns

### Pattern A: Core Ring (Defensive)

```
Key: B = Barrier, R = Road, C = Core (3x3), . = empty

          B B B B B
          B R R R B
          B R . . B
          B R C C B     (Core is 3x3, shown partially)
          B R . . B
          B R R R B
          B B B B B
```

**Properties:**
- 20 barriers for full ring around core (one layer)
- Cost: ~60 Ti, +20% scale
- Roads inside the ring allow builders to move between core and barriers
- Gap(s) in the ring needed for builders to EXIT and build economy
- Total HP wall: 600 HP

**Problems:**
- Builders trapped inside unless gaps exist
- Gaps become attack vectors for enemies
- Barriers far from enemy don't serve any purpose

**Verdict:** Too many barriers, most wasted on sides not facing enemy. Better to concentrate on enemy-facing side.

### Pattern B: Enemy-Facing Wall (Directional)

```
Key: B = Barrier, R = Road, S = Sentinel, C = Core

ENEMY DIRECTION -->

     B B B B B
     B S B S B    <- Sentinels behind barrier gaps
     R R R R R    <- Road for builder mobility
     . . C . .    <- Core area
```

**Properties:**
- 8-10 barriers on the enemy-facing side only
- Sentinels behind small gaps in the wall
- Roads behind barriers for builder movement
- Cost: ~24-30 Ti, +8-10% scale

**Advantages:**
- Concentrated defense where attacks come from
- Sentinels can fire through gaps (their wide pattern goes around barriers)
- Builders can still exit from other sides of core
- Low scale cost

**Problems:**
- Doesn't protect from flanking attacks
- Requires knowing enemy direction (we detect this via symmetry)

**Verdict:** Good for focused defense. Best when combined with a few barriers on other sides.

### Pattern C: Chokepoint Wall (Narrow Maps)

```
NARROW MAP CORRIDOR:

Wall  B B B Wall
Wall  B S B Wall     <- Barrier + sentinel at chokepoint
Wall  R R R Wall
Wall  . C . Wall
```

**Properties:**
- 4-6 barriers across a narrow corridor
- Completely seals the chokepoint
- Sentinel behind barrier fires through gaps

**Advantages:**
- Maximum defensive value on narrow maps (hourglass, corridors)
- Enemy must destroy 30 HP per barrier to advance
- Sentinel covers the gap

**Verdict:** Extremely effective on narrow maps. Low cost, high impact.

### Pattern D: Conveyor Chain Protection

```
B . B . B . B
. C>C>C>C>C .     <- Conveyor chain (C> = conveyor facing right)
B . B . B . B
```

**Properties:**
- Barriers flanking conveyor chains
- Protects resource flow from enemy builder attacks
- Cost: 1 barrier per 2-3 conveyor tiles

**Advantages:**
- Prevents enemy from disrupting economy
- Enemy builders must path around barriers to reach conveyors

**Problems:**
- Very expensive for long chains
- Scale cost adds up fast
- Better to just build more harvesters than protect existing ones

**Verdict:** Not recommended. Better to invest Ti in more harvesters than in protecting existing chains. If a chain is destroyed, rebuild it.

---

## QUESTION 5: Optimal Barrier Count

### Recommended Quantities by Game Phase

| Phase | Round | Barriers | Cost | Scale | Purpose |
|-------|-------|----------|------|-------|---------|
| Early (economy first) | 1-100 | 0 | 0 Ti | +0% | Focus entirely on economy |
| First defense | 100-200 | 4-6 | 12-18 Ti | +4-6% | Minimal core protection |
| Post-economy | 200-500 | 8-12 | 24-36 Ti | +8-12% | Enemy-facing wall + sentinels |
| Late game | 500-2000 | 15-25 | 45-75 Ti | +15-25% | Extended perimeter if economy allows |

### Why NOT 36 Barriers (Axionite Inc Level)?

Axionite Inc builds 36-38 barriers because they have a strong economy (7 harvesters, 19240 Ti collected). We need to:
1. First establish our economy (harvesters + chains)
2. Then build barriers incrementally as resources allow
3. Only reach 36 barriers if the economy supports it (5+ harvesters running)

Building 36 barriers at round 100 with no economy would cost 108+ Ti from our starting 500, leaving only 392 Ti for everything else. This is suicide.

### Sweet Spot: 8-12 Barriers

**8 barriers** provides:
- 240 HP defensive wall
- Cost: 24 Ti (at base scale)
- Scale: +8%
- Enough to protect one side of core
- Affordable after 2-3 harvesters are running

This is the recommended initial barrier count. Scale up to 15-25 as economy grows.

---

## QUESTION 6: Timing

### Round-by-Round Priority

| Round | Priority | Why |
|-------|----------|-----|
| 1-30 | Build harvesters + conveyor chains | Economy first, always |
| 30-80 | Continue economy expansion | More harvesters = more income |
| 80-120 | First 4 barriers + first sentinel | Earliest Diamond-tier bots start attacking around now |
| 120-200 | 4 more barriers (total 8) | Solidify defense while economy runs |
| 200-500 | Scale to 12-15 barriers if economy supports | Add barriers as resources allow |
| 500+ | Scale to 20-25 barriers if economy is strong | Late-game fortification |

**Key rule:** Never build barriers before the first harvester is connected to core. Economy before defense.

### When an Enemy Builder is Spotted

If an enemy builder appears near our territory before round 100, immediately build 2-3 barriers between it and our core/harvesters. This is an emergency defensive measure worth the early scale cost.

---

## RECOMMENDED IMPLEMENTATION

### Phase 1: Initial Barrier Ring (Round 100-150)

After at least 2 harvesters are connected and producing:

```python
def should_build_barriers(c, core_pos, enemy_dir):
    """Check if we should start building barriers."""
    rnd = c.get_current_round()
    if rnd < 80:
        return False  # Too early, focus on economy
    
    ti = c.get_global_resources()[0]
    barrier_cost = c.get_barrier_cost()[0]
    
    # Need enough Ti to afford barriers AND still build economy
    if ti < barrier_cost + 100:  # Keep 100 Ti reserve
        return False
    
    # Count existing barriers
    barrier_count = 0
    for eid in c.get_nearby_buildings():
        if c.get_entity_type(eid) == EntityType.BARRIER and c.get_team(eid) == c.get_team():
            barrier_count += 1
    
    # Cap based on game phase
    cap = 4 if rnd < 150 else (8 if rnd < 300 else (15 if rnd < 600 else 25))
    return barrier_count < cap
```

### Phase 2: Placement Algorithm

```python
def place_barrier(c, pos, core_pos, enemy_dir):
    """Place a barrier between core and enemy direction."""
    if not enemy_dir or not core_pos:
        return False
    
    # Target: 2-4 tiles from core center, toward enemy
    dx, dy = enemy_dir.delta()
    
    # Try positions 2-4 tiles from core toward enemy
    for dist in range(2, 5):
        target = Position(core_pos.x + dx * dist, core_pos.y + dy * dist)
        
        # Try the target and adjacent tiles (create a wall)
        for offset_dir in [Direction.CENTRE, enemy_dir.rotate_left(), enemy_dir.rotate_right()]:
            bp = target.add(offset_dir) if offset_dir != Direction.CENTRE else target
            if c.can_build_barrier(bp):
                c.build_barrier(bp)
                return True
    
    return False
```

### Key Placement Rules

1. **Leave gaps for builders:** Never build a complete ring. Always have at least 2 road/conveyor gaps for builder passage.

2. **Face the enemy:** Concentrate barriers between core and detected enemy direction. Don't waste barriers on sides far from the enemy.

3. **Behind sentinels:** Place barriers 1-2 tiles IN FRONT of sentinels (between sentinel and enemy). The sentinel fires over/around barriers. The barriers absorb return fire.

4. **Around conveyor chain entry points:** Place 1-2 barriers protecting where conveyor chains enter the core area.

5. **Not on ore tiles:** Never place barriers on ore tiles -- these are needed for harvesters.

6. **Not on planned conveyor paths:** Don't block future conveyor chain routes with barriers.

---

## BARRIER INTERACTION WITH OTHER MECHANICS

### Barriers vs Enemy Sentinels

Enemy sentinels deal 18 damage, destroying a barrier in 2 shots. However, each barrier absorbs 18 damage that would otherwise hit our core (500 HP) or other buildings. One barrier absorbs 30 HP of damage, requiring 2 sentinel shots to destroy. This "wastes" 6 rounds of enemy sentinel time (2 shots * 3 round reload) per barrier.

**12 barriers absorb 360 HP of sentinel fire, requiring 24 sentinel shots and 72 rounds to clear.** This is significant defensive value.

### Barriers vs Enemy Builders

An enemy builder on an adjacent walkable tile can fire at a barrier for 2 damage per action. At 30 HP, it takes 15 attacks to destroy. Each attack costs the enemy 2 Ti, so destroying one barrier costs the enemy 30 Ti (same as the barrier's HP in Ti). Since barriers only cost us 3 Ti, we get a 10:1 Ti efficiency advantage.

**However:** The enemy builder must be on a tile adjacent to the barrier AND that tile must be walkable (road or conveyor). If barriers are placed on tiles with no adjacent walkable surfaces, enemy builders literally cannot attack them.

### Barriers and Builder Healing

Our builders can heal barriers: 4 HP per heal for 1 Ti. A builder standing on a road adjacent to a barrier can heal it repeatedly. This extends barrier lifespan significantly:
- Enemy sentinel deals 18 damage every 3 rounds = 6 DPS
- Our builder heals 4 HP per round for 1 Ti = 4 HPS
- Net damage: 2 HP per round (with healing)
- Barrier survives 15 rounds instead of 6 rounds (2.5x longer)

### Barriers and Line of Sight

Barriers block gunner shots. A line of barriers in front of our buildings prevents enemy gunners from targeting anything behind them. This makes barriers excellent anti-gunner defense.

Sentinels are NOT blocked by barriers (they use area-of-effect, not ray fire). This means:
- Our sentinels behind barriers can fire at enemies
- Enemy sentinels can fire at our barriers (and anything adjacent)

---

## COST-BENEFIT SUMMARY

### Barriers: When They're Worth It

| Scenario | Barriers Worth It? | Why |
|----------|-------------------|-----|
| Economy not yet established | NO | Every Ti should go to harvesters/conveyors |
| Economy running, no threats | MAYBE | Low priority, but cheap insurance |
| Economy running, enemy nearby | YES | 3 Ti for 30 HP is best defensive value in game |
| Narrow map chokepoint | YES | Seals the corridor completely |
| Late game with excess Ti | YES | Scale cost matters less when economy is huge |
| Very early game (round 1-50) | NO | Absolutely no barriers before first harvester |

### Barriers vs Other Defenses

| Defense | Cost | Scale | HP | Active Defense | DPS |
|---------|------|-------|----|---------------|-----|
| 1 barrier | 3 Ti | +1% | 30 | None (passive) | 0 |
| 1 road | 1 Ti | +0.5% | 5 | None (walkable) | 0 |
| 1 sentinel | 30 Ti | +20% | 30 | 18 dmg / 3 rounds | 6 |
| 10 barriers | 30 Ti | +10% | 300 | None (passive) | 0 |
| 1 sentinel + 5 barriers | 45 Ti | +25% | 180 | 18 dmg / 3 rounds | 6 |

**10 barriers = same cost as 1 sentinel, half the scale, 10x the HP.**
Before sentinels have ammo, barriers are strictly better.
After sentinels have ammo, barriers + sentinels together are best.

---

## FINAL RECOMMENDATIONS

1. **Build NO barriers before round 80.** Economy first.
2. **Build 4-6 barriers at round 80-120** on the enemy-facing side of core, 2-3 tiles out.
3. **Leave road gaps** in the barrier line for builder passage.
4. **Scale to 8-12 barriers by round 200** as economy allows.
5. **Place sentinels BEHIND barriers** so they fire through/over the wall.
6. **Scale to 15-25 barriers by round 500+** if economy is strong (5+ harvesters).
7. **Never exceed 25 barriers** unless economy has 7+ harvesters. The +25% scale cap keeps future costs manageable.
8. **On narrow maps:** Build 3-5 barriers across the chokepoint. Maximum value.
9. **Emergency barriers:** If enemy builder spotted near core before round 80, build 2-3 barriers immediately regardless of economy state.

---

*Analysis based on game documentation, Axionite Inc replay data (36-38 barriers per game), and barrier mechanic interactions. April 5, 2026.*
