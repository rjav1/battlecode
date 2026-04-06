# vs Rusher Debug — Why We Win Only 25%

**Date:** 2026-04-06
**Maps tested:** face, arena, shish_kebab, default_small1 (all seed 1)

---

## Test Results

| Map | Buzzing Ti | Buzzing Buildings | Rusher Ti | Rusher Buildings | Winner |
|-----|-----------|------------------|-----------|-----------------|--------|
| face | 2422 (570 mined) | 28 | 7634 (9930 mined) | 259 | rusher |
| arena | 2082 (870 mined) | 28 | 2847 (4970 mined) | 339 | rusher |
| shish_kebab | 3057 (120 mined) | 10 | 5529 (4960 mined) | 205 | rusher |
| default_small1 | 2123 (50 mined) | 26 | 8187 (9940 mined) | 281 | rusher |

**All 4 games lost by resources tiebreak at round 2000.**

Key observation: rusher is winning via **PURE ECONOMY**, not combat. Mining rate gap is 6-200x. Rusher has 10-15x more buildings than buzzing.

---

## Root Cause Analysis

### 1. Rusher Wins Economy, Not Combat

Rusher mined 9930 Ti on face vs buzzing's 570 — a 17x gap. This is not about combat effectiveness; it's about infrastructure. Rusher built 259 buildings vs buzzing's 28. Rusher's economy builders create 4 harvesters with dedicated conveyor chains. Buzzing is barely delivering anything.

### 2. Rusher Attackers Use Our Own Conveyors as Highways

**Critical game mechanic:** Builder bots can walk on ANY team's conveyors/roads. Rusher attackers (all builders born after round 2) head toward enemy, but instead of fighting through terrain, they **walk on buzzing's own conveyor chains** toward our core.

Timeline on tight maps (face, default_small1):
- Rusher attackers spawn rounds 3-8
- Buzzing's first conveyor chain extends 5-10 tiles from core (toward ore)
- Rusher attacker can use those conveyors as a free highway
- Arrives in buzzing's base area by **round 24-28**

### 3. Gunner Too Late, No Ammo Supply

Buzzing's gunner placement on tight maps requires:
- `rnd > 30` AND
- `harvesters_built >= 1`

So even if the first harvester builds at round 20, gunner eligibility starts at round 31. **Rusher attackers arrive at round 24-28 — before the gunner is placed.**

More critically: buzzing **never builds a dedicated ammo supply conveyor** to the gunner. The gunner is placed adjacent to core facing enemy direction, but no conveyor explicitly feeds it. If a conveyor chain happens to pass by the gunner's non-facing side, it gets ammo; otherwise it sits idle. Once rusher destroys conveyors, gunner ammo supply = 0.

### 4. Barriers in Wrong Position

Buzzing places barriers 2-3 tiles from core **in the direction of the enemy core**. This protects against a frontal approach. But rusher attackers approach via buzzing's OWN conveyor chains (which run from core toward ore in a different direction). The barriers don't guard the conveyor corridors.

Rusher attacker logic (`_attack` in rusher/main.py):
```python
elif etype in (EntityType.CONVEYOR, EntityType.SPLITTER, EntityType.ARMOURED_CONVEYOR):
    prio = 5  # Highest priority — kills our delivery chain
elif etype == EntityType.ROAD:
    prio = 4
```
Once on a conveyor tile, attacker fires: `c.fire(pos)` dealing 2 damage (costs 2 Ti). A conveyor has 20 HP → needs 10 attacks to destroy. Attacker can destroy a conveyor every ~10 rounds.

### 5. Early Builder Cap Too Low

Buzzing tight cap: **3 builders until round 20** (then 7).
Rusher cap: **4 builders until round 8** (then 6).

Rusher gets its first 4 builders out in 8 rounds. Buzzing only gets 3 until round 20. This means rusher's economy builders (first 2) are running earlier and building harvesters sooner.

### 6. Barrier Anti-Rush Fires Too Early

Buzzing's early barrier logic:
```python
early_barrier_ok = (map_mode == "tight" and rnd >= 5 and (self.my_id or 0) % 5 != 0)
```

This means 80% of builders on tight maps spend their first turns building 2 barriers instead of walking toward ore. With only 3 builders allowed until round 20, potentially all 3 are building barriers instead of harvesters.

---

## Specific Failure on default_small1

Only **50 Ti mined** in 2000 rounds. That's approximately:
- 50 Ti / 10 Ti per stack = 5 stacks delivered
- 5 stacks / (1 stack per 4 rounds) = 20 rounds of active harvester delivery
- Meaning: harvester ran for only ~20 rounds out of 2000!

This suggests rusher attackers destroyed buzzing's conveyor chain within 20-30 rounds of the first harvester being built, permanently cutting off deliveries.

---

## Does the Gunner Actually Fire?

On tight maps at round 30, buzzing places a gunner (if 1+ harvester). But:
1. Attacker already inside our conveyor area destroying buildings
2. No dedicated ammo supply pipeline to gunner
3. Gunner fires along a ray: attacker ON our conveyor is in the path, BUT gunner needs ammo first
4. With conveyors disrupted, no ammo arrives → gunner never fires

The 570 Ti mined on face map (vs 50 on default_small1) suggests some variance — on face, conveyors survived longer, allowing partial delivery.

---

## Recommendations (Priority Order)

### Fix 1: Emergency — Earlier Gunner, No Harvester Requirement (tight maps)
**Change:** On tight maps, lower `gunner_round` from 30 to 15, remove `harv_req` for tight maps.
**Why:** Gunner needs to be placed BEFORE rusher arrives (~round 24). Even without a harvester, if a conveyor feeds the gunner it will help.

### Fix 2: Emergency — Dedicated Ammo Conveyor to Gunner
**Change:** After placing gunner, one builder should immediately build 1-2 conveyors from core to gunner's side.
**Why:** Without ammo supply, gunner is useless. Needs a short direct conveyor from core output to gunner's non-facing side.

### Fix 3: High — Suppress Early Barriers on Tight Maps
**Change:** Remove early barrier placement on tight maps entirely (or delay to round 50+).
**Why:** Barriers consume builder action time and Ti but don't stop rusher from using our conveyors. Economy investment beats defensive investment here.

### Fix 4: High — Raise Early Builder Cap on Tight Maps
**Change:** On tight maps, raise cap from 3 to 4 before round 20 (match rusher).
**Why:** Rusher deploys 4 builders by round 8, giving it 2 economy + 2 attacker simultaneously. We only get 3 builders until round 20.

### Fix 5: Medium — Shorter Conveyor Chains to Ore (Bridge Direct Delivery)
**Change:** On tight maps, prefer bridge-direct delivery from ore to core instead of long conveyor chains.
**Why:** Long conveyor chains give rusher a highway into our base AND give more targets to destroy. A bridge bypasses this entirely — rusher can't walk on a bridge (bridge is a building, not walkable). Also fewer individual building targets.

### Fix 6: Medium — Barrier Placement IN Conveyor Path
**Change:** Build barriers adjacent to conveyor chains where they exit toward ore, creating chokepoints.
**Why:** Rusher attacker must enter our conveyor chain somewhere. A barrier in the conveyor path forces the attacker to go around (they can't fire through barriers easily).

### Fix 7: Low — Match Rusher's Economy Model
**Change:** Spawn the first 2 builders specifically as pure economy (no barriers, no gunner tasks), then switch to defense.
**Why:** Rusher's power comes from 2 dedicated economy builders who immediately build 4 harvesters. We should replicate this — first 2 builders = pure economy, later builders = defense/gunner.

---

## What Rusher Does Right

1. **2 pure economy builders** (born rounds 1-2): no barriers, no gunner — straight to ore
2. **4 harvesters max** per economy builder chain (high limit)
3. **Attackers use roads for movement** (Ti reserve 30 for attacker nav = careful spending)
4. **Attacker priority: conveyors > roads > core** — disrupts economy not just deals damage
5. **Small builder cap** keeps resource costs low, all investment goes to buildings

---

## Summary

We lose to rusher because rusher wins on economy (17x mining advantage), not combat. Rusher's attackers infiltrate our conveyor networks and systematically destroy our delivery infrastructure. Our barriers, gunner, and defensive structures either fire too late, have no ammo supply, or guard the wrong angles. The fix requires: earlier gunner with dedicated ammo pipeline, suppressing early barriers that waste builder time, and potentially matching rusher's economy-first builder assignment.
