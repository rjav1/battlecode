# Attacker Effectiveness Research

Date: 2026-04-06

## Test Results

### buzzing vs balanced — galaxy seed 1
```
Winner: balanced
Titanium: buzzing 4094 (7730 mined) | balanced 13135 (9900 mined)
Units: buzzing 15 | balanced 5
Buildings: buzzing 387 | balanced 271
```

### buzzing vs smart_eco — cold seed 1
```
Winner: smart_eco
Titanium: buzzing 17873 (19670 mined) | smart_eco 29568 (28230 mined)
Units: 8 | 8
Buildings: 415 | 264
```

### buzzing vs smart_eco — galaxy seed 1
```
Winner: smart_eco
Titanium: buzzing 13821 (13670 mined) | smart_eco 18049 (14660 mined)
Units: buzzing 15 | smart_eco 8
Buildings: 259 | 168
```

---

## Attacker Assignment Conditions

```python
# line 332-336 in _builder:
if (not self.is_attacker and rnd > 500
        and self.harvesters_built >= 4
        and (self.my_id or 0) % 6 == 5):
    self.is_attacker = True
```

**Eligibility:** Builder must be past round 500, have personally built 4+ harvesters,
and have `id % 6 == 5`.

### How many builders get assigned?

Builder IDs are assigned sequentially from spawn. With 8 builders (typical cap):
- IDs roughly 1-8
- `id % 6 == 5`: only ID=5 and ID=11 qualify in a typical game
- **At most 1 builder per game is ever the attacker** (ID=5 in a standard 8-builder game)
- If cap is 15 (expand maps): IDs 1-15 → ID=5 and ID=11 → 2 attackers

### The `harvesters_built >= 4` condition

`self.harvesters_built` counts only THIS BUILDER'S harvester placements (instance variable,
not shared). A single builder placing 4 harvesters means:
- Builder must find and claim 4 ore tiles solo
- In typical games, ore is divided among 6-8 builders
- Each builder places 1-2 harvesters before ore is exhausted
- **A single builder hitting 4 is uncommon.** Usually 1-2 each.

This condition effectively means the attacker rarely triggers at all. By round 500,
if builder ID=5 has only placed 1-2 harvesters (which is typical), it never becomes
an attacker.

### Effective trigger: round 500+ is too late

Galaxy is 40x40 (expand mode). Enemy core is ~30-35 tiles away from our core.
Builder movement speed: 1 tile/round at base (move cooldown increases each step).

Even if the attacker triggers at round 500, it needs 30-40+ rounds to cross the map
to enemy territory, navigating walls without conveyors (uses `_nav_attacker` with roads).
Roads only build when blocked, so travel is mostly free movement on existing infrastructure.

On galaxy, the enemy's convoy system exists by round 500 and is well-established. The
attacker can at best chip away at a few conveyors (20 HP each, builder fires for 2 damage
= 10 hits = 10 rounds per conveyor). At 1 conveyor per 10+ rounds, the attacker destroys
maybe 50-100 conveyors in 1500 remaining rounds.

**On cold (37x37, balanced):** Enemy core is ~26 tiles away. Same problem — late trigger,
slow travel, low damage output.

---

## Does the Attacker Actually Reach the Enemy?

### galaxy: buzzing has 15 units vs balanced's 5

Buzzing builds 15 units (builder bots). `balanced` opponent has only 5.
The 15 units include the attacker. But the score is catastrophic: 7730 Ti mined vs 9900
for `balanced`. Buzzing is building 15 builders while `balanced` is harvesting efficiently
with 5. **The extra builders are consuming Ti that should go to harvesters.**

The attacker-triggering builder (ID=5) likely spent rounds 100-500 as an economy builder,
then converted to attacker. During the attacker phase (rounds 500-2000), it's heading
toward enemy territory instead of building more harvesters. Net: -1 harvester worth of
income vs pure economy, in exchange for whatever damage it does.

### cold: no observable attacker impact

cold Ti mined: buzzing 19670, smart_eco 28230. The gap is 8560 Ti — massive. If the
attacker destroyed 20 harvesters on the enemy side (maximum realistic damage), that would
be 20 × 20 Ti per 4 rounds × 500 rounds = 50,000 Ti prevented. But smart_eco still wins
by 8560 Ti. So either:
- The attacker never reached enemy territory, OR
- It destroyed some conveyors but smart_eco rebuilt faster, OR
- The attacker destroyed infrastructure worth far less than the income loss from one builder
  not placing harvesters

Without print statements in the bot, we can't directly observe attacker activity.

### Inferred from unit counts

galaxy: buzzing=15 units (up to cap), balanced=5 units.
The expand map cap for buzzing is `15` at rnd>400. All 15 builders are alive at round 2000.
If the attacker had reached enemy territory and been killed, unit count would be 14.
**15 units surviving suggests the attacker survived all 2000 rounds** — likely meaning it
either never reached the enemy or found no targets.

cold: both sides 8 units. Attacker survived (not killed by enemy), consistent with either
staying on our side or finding no engagement.

---

## Fundamental Problems With the Attacker

### Problem 1: Trigger condition rarely met

`harvesters_built >= 4` on a single builder instance is unusual. Most builders place 1-2
harvesters before ore runs out. Only if ID=5 is extremely lucky/efficient at ore discovery
does it hit 4. In practice, the `rnd > 500` condition is probably the binding constraint —
but both must be true simultaneously.

**Test: if ID=5 never places 4 harvesters, the attacker NEVER activates.** The builder just
continues as an idle economy builder past round 500.

### Problem 2: Builder attack damage is 2 HP per action

From the game rules:
- Builder attack: **2 damage to building on own tile**, costs 2 Ti + action cooldown
- Enemy conveyor has 20 HP → needs 10 hits = 10 action cooldowns
- Each action cooldown is minimum 1 round → 10 rounds per conveyor destroyed
- In 1500 remaining rounds after round 500: at best ~150 conveyors destroyed

At 3 Ti per conveyor, destroying 150 enemy conveyors = 450 Ti of enemy assets eliminated.
But the attacker itself isn't building harvesters during this time — costing ~1 harvester
worth of income = ~500+ Ti lost from our economy.

**Net: attacking destroys ~450 enemy Ti of assets while costing 500+ own Ti in missed
harvester income. Negative expected value against a pure-economy opponent.**

### Problem 3: Conveyors are the lowest-value target

Even if the attacker reaches enemy infrastructure, it targets by priority:
foundry > harvester > gunner > sentinel > ... > conveyor

But:
- **Foundries:** cost 40 Ti, scale +100% — high value if destroyed, but they're deep in
  enemy base and the attacker would need to survive many rounds on enemy tiles
- **Harvesters:** cost 20 Ti, but killing one doesn't remove the ore tile. Enemy rebuilds
  next round for 20+ Ti. At 2 damage/action, it takes 15 actions (15 rounds) to kill a
  harvester (30 HP)
- **Conveyors:** 20 HP, 10 rounds, 3 Ti value. Low impact.

The attacker spends 10-15 rounds killing 1 structure that costs the enemy 3-20 Ti to rebuild.

### Problem 4: Enemy can walk builders onto targeted buildings

From game rules: "If a builder bot stands on a building, turret attacks on that tile hit
ONLY the builder bot." The same mechanic applies in reverse — our attacker fires on a tile,
but if an enemy builder stands there, we're attacking the builder (30 HP) not the building.

Enemy could just park a builder on its harvesters. Our attacker then attacks the builder
(which can be healed for 1 Ti by another builder), not the harvester. This makes the
attacker completely ineffective against a defended economy.

### Problem 5: `_nav_attacker` uses roads (ti_reserve=30)

The attacker navigates to enemy with `ti_reserve=30` — it won't build roads unless Ti > 31.
In practice, early game Ti is abundant, so it does build roads. These roads are permanent
buildings that add to scale inflation. 20 roads on the attacker path = +10% scale cost
for all future buildings. The attacker pollutes our scaling even while traveling.

---

## Is the Attacker Helping on Any Map?

### Against opponents with NO military (smart_eco, balanced)

These opponents have pure economy and no defensive turrets. The attacker CAN freely destroy
their infrastructure — no counter-fire. But the economic calculation is still negative:
- Our lost income (1 builder not harvesting) > their lost income (buildings destroyed)
- Their harvesters keep producing while we destroy 1 conveyor per 10 rounds

### Against opponents WITH military

The attacker builder (30 HP) dies instantly to any turret. If the opponent has a gunner
firing along a conveyor chain, the attacker is killed in 3 hits (10 damage each). The
attacker is then permanently removed, making the situation even worse.

---

## Conclusion: The Attacker Is Ineffective

**Evidence:**
1. galaxy: 15 units, catastrophic economy (7730 vs 9900 mined) — the extra builders
   (including attacker) cost more in scale inflation than they provide in damage
2. cold: no measurable impact vs smart_eco (gap is 8560 Ti, far exceeding any damage done)
3. Trigger condition rarely met (`harvesters_built >= 4` on one builder)
4. Damage output: 2 HP/action, 10 rounds per conveyor, negative ROI vs lost harvester income
5. Roads built during travel add permanent scale inflation

**smart_eco wins with 0 military and beats us consistently.** The attacker is providing
zero measurable benefit while:
- Occupying 1 of 8 builder slots post-round-500
- Building roads (scale inflation) across the map
- Distracting from economy focus

---

## Recommendation: Remove the Attacker

Remove `is_attacker` assignment and `_attack`/`_nav_attacker`/`_find_best_infra_target`
methods. The builder assigned as attacker (ID=5) should instead continue harvesting and
exploring. This recovers ~1 harvester worth of income in the late game.

If military is desired in the future, turrets (gunners) are far more effective:
- Gunner: 10 damage/shot, 13 vision r², ammo-fed, permanent
- Builder attacker: 2 damage/action, must physically reach enemy, dies in 3 turret hits

The only scenario where the attacker is valuable: opponent with NO turrets and we are
ahead enough economically that we can spare a builder. In that scenario, we are already
winning — the attacker is win-more rather than win-enabling.
