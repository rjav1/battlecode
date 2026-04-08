# Forward Gunner Push — Implementation Design

## Date: 2026-04-08
## Input: research/forward_gunner_ammo.md

---

## Viability Assessment

The forward_gunner_ammo report correctly identifies the core problem: **d.opposite() chains flow toward core and cannot feed forward.** Conveyors only output in their facing direction. A chain of south-facing conveyors sends resources south (to core), never north (to gunner).

### Three ways to get ammo to a forward gunner:

1. **Bridge hop** (20 Ti + 10% scale) — bridge from chain to gunner. Bridges bypass direction restrictions. Expensive but reliable.

2. **Dedicated forward chain** — build conveyors facing NORTH from a harvester toward the gunner. Entire chain is gunner ammo, not core economy. Expensive in conveyors but doesn't need a bridge.

3. **Harvester auto-split** — build gunner adjacent to a mid-map harvester. Harvester splits output between core chain and gunner. Cheapest but limits gunner placement to ore-adjacent positions.

**None of these are cheap.** Minimum cost: 10 Ti (gunner) + 20 Ti (bridge or 6-7 conveyors) + 10% scale (gunner) + 1-10% scale (infrastructure). Total: ~30-40 Ti + 11-20% scale.

---

## Critical Problem: Is It Worth It?

**Gunner DPS:** 10 damage per shot, 1 round reload, needs 2 ammo stacks per shot. With 1 feed conveyor (1 stack/round), fires every 2 rounds = 5 DPS.

**Enemy core HP:** 500.

**Time to kill:** 500 / 5 = **100 rounds.** If gunner placed at round 1000, core dies at round 1100.

**But:** Gunner vision r^2 = 13 (~3.6 tiles). Gunner fires along forward ray. Enemy core is 3x3. Gunner must be within ~3 tiles of core AND have line of sight. Enemy buildings/walls block the ray.

**At our Elo (1480):** Most games are resource victories at round 2000. A gunner placed at round 1000 that kills core at round 1100 is a WIN — if it works. But:
- Builder must REACH enemy core area (~15-25 tiles from our core)
- Builder needs walkable path (conveyors or roads) the entire way
- If builder walks conveyors, it already laid a 15-25 conveyor chain (+15-25% scale)
- If builder walks roads, it laid 15-25 roads (+7.5-12.5% scale) but no ammo chain

**The builder walking to enemy core is the REAL cost** — 15-25 rounds of travel, 15-75 Ti of infrastructure, 7-25% scale.

---

## Simplest Implementation: Gunner on Existing Chain

Our builder already walks toward ore laying conveyors. Some of those chains extend past mid-map toward the enemy. Instead of building a separate push infrastructure, **use the existing chain**.

The key insight from the report (Option 1 revised): the builder's chain already extends forward. The chain tip is the furthest-from-core conveyor. If we:

1. Build the gunner on the tile BEHIND the chain tip (between the last two conveyors)
2. Destroy the last conveyor (chain tip)
3. The second-to-last conveyor now has nothing in its output path — its output goes to an empty tile
4. Build a NEW conveyor on that empty tile facing THE GUNNER

Wait, this is getting complicated. Let me think about the simplest layout.

**Actually simplest:** Don't tap the existing chain. Just build a harvester on enemy-side ore + 1 conveyor + gunner. If the builder finds ore near the enemy, it can:
1. Build harvester on ore (already does this)
2. Build conveyor adjacent to harvester, facing gunner position
3. Build gunner 1 tile further, facing enemy

This is EXACTLY the sentinel auto-split pattern, but with a gunner instead of sentinel, and placed near enemy rather than near core.

**But we just proved sentinel auto-split regresses by 12%.** The same problem applies: builder time spent placing gunner = time NOT finding ore.

---

## Honest Assessment

**The forward gunner push is NOT viable for reaching 1600 Elo.** Here's why:

1. **Games at 1480 are decided by economy.** A gunner that fires 5 DPS is worth less than a harvester that produces 2.5 Ti/round (10 Ti every 4 rounds).

2. **Builder time is the scarcest resource.** Every round spent placing gunner infrastructure is a round not finding ore. We proved this with the sentinel auto-split regression (-12%).

3. **The ammo delivery problem adds complexity and cost.** Minimum 30-40 Ti + 11-20% scale for a working gunner, plus the builder's travel time.

4. **Gunner is easily countered.** Enemy builder can stand on the gunner tile and take hits instead of the core. Gunner does 10 damage to builder (30 HP), kills in 3 shots (6 rounds). But enemy spawns new builders from core.

5. **Gunner damage is low.** 10 damage/shot (5 DPS with half ammo rate). Enemy core has 500 HP. Takes 100 rounds with perfect conditions. Any disruption (blocked line of sight, enemy builder absorbing shots) delays this dramatically.

### When it WOULD be viable:
- At 1600+ Elo where opponents defend and pure economy isn't enough to win
- On maps where we can't win on resources (e.g., losing 4-1 on resource games)
- In specific matchups where opponent doesn't build near their core

---

## If We Build It Anyway: Minimal Implementation (~25 lines)

Only trigger on one specific condition: round > 1200, Ti > 2000 (hoarding), and builder is near enemy core area.

```python
# In _builder, after harvester/ore logic:
# Late-game gunner push — only when hoarding Ti and near enemy half
if (rnd > 1200 and not hasattr(self, '_gunner_done')
        and c.get_global_resources()[0] > 2000):
    enemy_core = self._get_enemy_core_pos(c)
    if enemy_core and pos.distance_squared(enemy_core) < 100:
        enemy_dir = self._get_enemy_direction(c)
        if enemy_dir and c.get_action_cooldown() == 0:
            ti = c.get_global_resources()[0]
            gc = c.get_gunner_cost()[0]
            if ti >= gc + 20:
                # Try to build gunner facing enemy direction
                for d in DIRS:
                    gp = pos.add(d)
                    if c.can_build_gunner(gp, enemy_dir):
                        c.build_gunner(gp, enemy_dir)
                        self._gunner_done = True
                        # Ammo: try bridge from nearest chain to gunner
                        # Or: just let gunner sit empty as a scare tactic
                        return
```

**Without ammo delivery, the gunner is a 10 Ti + 10% scale scarecrow.** It won't fire. But it might deter enemy builders from walking through its vision range (enemies don't know it's empty).

**With ammo:** Add a bridge from nearest conveyor to gunner (20 Ti + 10% scale). Total ~30 Ti + 20% scale. Fires every 2 rounds at 5 DPS. Kills core in 100 rounds IF unobstructed.

---

## Recommendation

**Do not implement for V62.** The gunner push fails the same test as sentinels: builder time and scale cost exceed the benefit at our Elo tier.

**Save for V64+ (post-1600 Elo)** when:
1. Military becomes necessary to win
2. We have a dedicated "attacker" builder role (separate from economy builders)
3. We can afford the 30-40 Ti + 20% scale investment without hurting economy

**If forced to implement now:** The scarecrow variant (gunner without ammo, round > 1200, Ti > 2000) is < 15 lines and costs only 10 Ti + 10% scale. It might discourage enemy builder pushes. But it probably doesn't pass the 66% baseline.
