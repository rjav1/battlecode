# High-Bank Ti Spending Outlet — Research Plan

## Problem Statement

When the bot hits its builder cap (governed by `_core` → cap logic), Ti accumulates
with nowhere to go. Observed bank values: 200–18,000 Ti. Competitors maintain banks
below 300 Ti, meaning they convert every round of income into board-state advantage.
Tiebreaker #5 is stored Ti (losing), but actually spending Ti on infrastructure compounds
advantage (more harvesters, stronger defenses, more resource flow → tiebreakers #1–4).

---

## What the Core Can Do With Excess Ti

The core's action set is:
1. `spawn_builder(pos)` — already capped
2. `convert(amount)` — refined Ax → Ti (1:4). We produce 0 refined Ax currently, so useless.
3. No healing API exists on Core in v37.

**Conclusion: Core cannot directly spend Ti.** All spending outlets must come from builder bots.

---

## Current Builder Spending Outlets (What's Already Coded)

| Outlet | Trigger Condition | Cap |
|--------|------------------|-----|
| Conveyors (nav) | Walking to ore targets | Unlimited but functionally stops when no ore target |
| Harvesters | Adjacent ore, ti >= cost+5 | Stops when all ore is covered |
| Bridges | Post-harvester shortcut | One-off per harvester |
| Barriers | rnd>=80, near core, ti>=50, barrier_count<6 | Hard cap at 6 |
| Gunners | id%5==1, timing+harvester reqs, gunner_placed<3 | Hard cap at 3 |
| Armed Sentinel | rnd>=1000, harvesters>=5, ti>=70 | One per builder (sentinel_step 0→5) |
| Roads (attacker nav) | Attacker builders only | No explicit cap |
| Early barriers | rnd<=30, per-builder | At most 2 per builder |

**All the main outlets have hard integer caps.** Once ore is fully covered, all harvesters built,
barriers at 6, gunners at 3, sentinels built — builders enter `_explore`, then `_nav` with
`explore_reserve=30` (far from core) which strongly throttles conveyor placement.

---

## Root Cause of Bank Accumulation

1. **Builder cap** prevents spawning more units to spend Ti.
2. **Barrier cap (6)** is very conservative — stops well before Ti is exhausted.
3. **Gunner cap (3)** stops spending on defense early.
4. **Exploration** with `explore_reserve=30` means far-from-core conveyors are not built
   even if Ti is available.
5. **No healing outlet** for builders — they can heal but nothing calls it unless at action_cooldown==0
   and adjacent to damaged friendlies. No proactive heal loop exists.

---

## Viable Spending Outlets

### Option A: Raise Barrier Cap When Ti is High (LOW RISK, HIGH IMPACT)

**What:** In `_build_barriers`, raise `barrier_count >= 6` threshold dynamically:
- If `ti > 500`: cap = 12
- If `ti > 1000`: cap = 20
- If `ti > 2000`: no cap (fill every candidate position)

**Why it works:** Barriers cost 3 Ti each. With 2000+ Ti, 20 extra barriers = 60 Ti drain.
Not enough alone, but it's free defense and scales naturally. Zero risk of misrouting resources.

**Where in code:** `_build_barriers` at line ~762 (`if barrier_count >= 6`).

**Risk:** Very low. Barriers block enemy path, improve defense. Only downside: slightly raises
cost scale for future buildings (each barrier = +1%). At 20 barriers: +20% scale increase.
At base barrier cost 3 Ti, 20 barriers = ~60 Ti. Scale impact: marginal.

---

### Option B: Raise Gunner Cap When Ti is High (MEDIUM RISK, HIGH IMPACT)

**What:** In `_place_gunner`, raise `gunner_count >= 3` threshold dynamically:
- If `ti > 300`: cap = 6
- If `ti > 800`: cap = 10
- If `ti > 2000`: cap = 15

**Why it works:** Gunners cost 10 Ti each. 10 extra gunners = ~100 Ti drain. Each gunner
provides real firepower if placed with ammo routing. Even without ammo routing they act as
blockers with 40 HP.

**Where in code:** `_place_gunner` at line ~590 (`if gunner_count >= 3`). Also the
`self.gunner_placed < 3` check in `_builder` at line ~341 needs updating.

**Risk:** Medium. Each gunner raises scale by +10%. 10 extra gunners = +100% scale.
However, at Ti 1000+, we can afford the scale increase. Gunners without ammo chains are
passive blockers, not active defenders. Need ammo routing for full value.

**Note:** The builder doing gunner work is `id%5==1`. Only 1 of every 5 builders builds
gunners. Need to also allow other builders to place gunners when bank is very high.

---

### Option C: Conditional Builder Cap Increase When Ti Very High (MEDIUM RISK, HIGH IMPACT)

**What:** In `_core`, when `ti > threshold`, raise cap above the map-mode maximum:
- If `ti > 500` AND existing cap is reached: add +2 to cap
- If `ti > 1000`: add +5 to cap
- If `ti > 2000`: add +10 to cap (hard ceiling at 49 total units)

**Why it works:** More builders = more infrastructure. Each builder consumes Ti via
conveyors/harvesters. Directly addresses root cause.

**Where in code:** `_core` at line ~116 (`if units >= cap`). Insert Ti-based override before
the `return`.

**Risk:** Medium-High. More builders raise scale by +20% each. 5 extra builders = +100% scale.
However, at Ti 1000+, you can afford the scale increase. The 2ms CPU limit becomes a concern:
49 units × 2ms each = 98ms total per round — within budget but tight on large maps.
Each extra builder needs a walkable path from core, which requires roads or conveyors.

---

### Option D: Proactive Heal Loop for Builders (VERY LOW RISK, LOW IMPACT)

**What:** In `_builder`, before the main logic, check if any adjacent friendly building
is below max HP and heal it. Cost: 1 Ti per heal.

**Why it works:** Uses action cooldown budget productively near core. Keeps infrastructure
alive longer. Reduces damage from attackers.

**Where in code:** Top of `_builder` after the core_pos detection block. Check `c.get_action_cooldown() == 0`,
scan adjacent tiles, if friendly building HP < max HP, call `c.heal(pos)`.

**Risk:** Very low. 1 Ti per heal. Won't drain large banks alone but reduces attrition.
Only meaningful if enemy is attacking (attacker builders, turrets, etc.).

---

### Option E: Lower Exploration Ti Reserve When Bank is High (LOW RISK, MEDIUM IMPACT)

**What:** In `_explore`, the `explore_reserve` is set to 30 when far from core.
Override this when Ti is very high:
- If `ti > 500`: explore_reserve = 10
- If `ti > 1000`: explore_reserve = 5 (always low reserve)

**Why it works:** Builders exploring far from core currently skip conveyor placement
(reserve=30). Lowering the reserve means they'll pave roads/conveyors everywhere,
spending Ti productively and extending the road network for future builder mobility.

**Where in code:** `_explore` at line ~568–572. Pass `ti` to the function and compute
`explore_reserve` dynamically.

**Risk:** Low. Conveyors far from core won't route resources correctly (no ore there), but
roads/conveyors are walkable — they improve future builder mobility. Each extra conveyor/road
raises scale by +0.5–1%. With 100 extra conveyors: +50–100% scale. At high Ti this is
acceptable because the buildings themselves cost little (3 Ti conveyors) and scale is
already high anyway.

---

### Option F: Extra Road Paving Near Core (LOW RISK, LOW IMPACT)

**What:** Dedicated road-paver pass for builders near core when Ti is high. Build roads on
every empty passable tile within r²=10 of core.

**Why it works:** Drains Ti at 1 Ti/road. Makes the core area more navigable for all builders.
Good for late-game multi-builder positioning.

**Where in code:** Add to `_builder` before the `_explore` call, when `ti > 300` and
`pos.distance_squared(core_pos) <= 20`.

**Risk:** Low but minimal impact per Ti spent. Roads cost 1 Ti so even 100 roads = 100 Ti.

---

## Recommended Priority Stack (Best ROI)

| Priority | Option | Ti per unit | Impact per Ti | Risk | Est Ti drain/round |
|----------|--------|-------------|---------------|------|-------------------|
| 1 | **C: Raise builder cap with Ti gate** | 30 Ti/builder | HIGH — more units = more infrastructure | Medium | 30–150 Ti |
| 2 | **B: Raise gunner cap with Ti gate** | 10 Ti/gunner | HIGH — more defense, actual spending | Medium | 10–100 Ti |
| 3 | **A: Raise barrier cap with Ti gate** | 3 Ti/barrier | MEDIUM — more defense, cheap | Low | 3–60 Ti |
| 4 | **E: Lower explore reserve at high Ti** | 1–3 Ti/conveyor | MEDIUM — board coverage | Low | Variable |
| 5 | **D: Proactive heal loop** | 1 Ti/heal | LOW — maintenance only | Very Low | 1–5 Ti |

---

## Recommended Implementation: Two-Tier Approach

### Tier 1: Core spawns more builders when bank > 500 Ti
In `_core`, after `if units >= cap: return`, add:
```python
# High-bank override: spawn extra builders to spend excess Ti
ti = c.get_global_resources()[0]
extra_cap_from_bank = 0
if ti > 2000:
    extra_cap_from_bank = 10
elif ti > 1000:
    extra_cap_from_bank = 5
elif ti > 500:
    extra_cap_from_bank = 2
if units >= cap + extra_cap_from_bank:
    return
```
This is the highest-leverage option because each builder is a spending agent.

### Tier 2: Builders spend more aggressively at high bank
In `_build_barriers`:
```python
# Dynamic barrier cap based on current Ti
barrier_cap = 6
ti = c.get_global_resources()[0]
if ti > 2000:
    barrier_cap = 20
elif ti > 1000:
    barrier_cap = 12
elif ti > 500:
    barrier_cap = 9
if barrier_count >= barrier_cap:
    return False
```

In `_place_gunner` and the `_builder` guard:
```python
# Dynamic gunner cap
gunner_cap = 3
ti = c.get_global_resources()[0]
if ti > 800:
    gunner_cap = 8
elif ti > 300:
    gunner_cap = 5
# Use gunner_cap instead of hardcoded 3
```

---

## Where Exactly in the Code

| Change | File | Line(s) | Description |
|--------|------|---------|-------------|
| Builder cap override | `bots/buzzing/main.py` | ~116 (after `if units >= cap`) | Add Ti-gated extra cap |
| Barrier cap dynamic | `bots/buzzing/main.py` | ~762 (`if barrier_count >= 6`) | Replace with Ti-scaled cap |
| Gunner cap dynamic | `bots/buzzing/main.py` | ~590 (`if gunner_count >= 3`) | Replace with Ti-scaled cap |
| Gunner builder guard | `bots/buzzing/main.py` | ~341 (`self.gunner_placed < 3`) | Replace with Ti-scaled cap |
| Explore reserve dynamic | `bots/buzzing/main.py` | ~568–572 | Pass ti, lower reserve at high bank |

---

## Risk Assessment Summary

**Main risk: Cost scaling.** Each entity built increases cost scale. At very high Ti we can afford
scale inflation, but it compounds — a 50% scale increase means harvesters cost 30 Ti instead of 20.
This is fine if Ti is 2000+, but could hurt late game if Ti drops back down (e.g., after we spent it
on 20 extra builders, then income dropped).

**Mitigation:** Gate all extra spending behind Ti thresholds with hysteresis. Only raise caps when
bank is high. The caps naturally become irrelevant if Ti drops below threshold.

**Secondary risk: CPU time.** 49 builders × 2ms = 98ms per round. On complex maps with BFS, this
could hit the 2ms limit. Extra builders = more BFS calls. Monitor via `c.get_cpu_time_elapsed()`.

**Expected impact:** Competitors spend 200–300 Ti/round on infrastructure in mid-game. We currently
spend ~50–100 Ti/round. Closing this gap means +100–200 Ti/round into board-state, compounding to
+5,000–10,000 Ti of infrastructure advantage by round 1000. That translates to more harvesters,
stronger defenses, better tiebreaker positioning.

---

## Conclusion

The highest-leverage fix is **Option C (conditional builder cap raise)** because each extra builder
is itself a Ti-spending machine that builds conveyors, harvesters, and defenses. This alone should
close most of the bank gap. Options A and B (dynamic barrier/gunner caps) are low-risk complements
that drain Ti on defense when bank is still high after spawning extra builders.

The implementation is straightforward — 3–4 localized changes in `_core`, `_build_barriers`, and
`_place_gunner`. No architectural changes required.
