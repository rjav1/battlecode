# Gunner Timing Analysis

## Current Gunner Timing (main.py:276)

```python
gunner_round = 150 if map_mode == "expand" else 200
```

| Map Mode | Current gunner_round | Prerequisite |
|----------|---------------------|--------------|
| tight    | N/A — skipped entirely (`map_mode != "tight"` guard on line 277) |
| balanced | 200 | harvesters_built >= 3 |
| expand   | 150 | harvesters_built >= 3 |

**Tight maps get NO gunners at all.** The condition on line 277 explicitly excludes `map_mode == "tight"`.

---

## Why Tight Maps Need Gunners at Round 60-80

### Path distances on tight maps

Tight maps are 25x25 or smaller (area <= 625, line 62). With a 25x25 map:
- Core centre is roughly at (12, 12)
- Enemy core centre is the symmetric mirror, e.g. (12, 12) rotated/reflected
- On a rotation-symmetric 25x25 map the two cores are ~17 tiles apart (diagonal)
- On a reflection-symmetric map they may be as close as 10-12 tiles apart

A builder bot moves 1 tile per turn (plus move cooldown accumulation). Enemy builders can reach the midpoint in ~6-8 turns and the core perimeter in 12-15 turns from the start. By round 137 (face) and round 190 (shish_kebab), enemy builders have had 130-190 rounds to erect attacking infrastructure — conveyors, barriers, turrets — right up to our core.

### Enemy arrival timeline estimate

| Round | Enemy activity (tight map) |
|-------|---------------------------|
| 1-5   | First builders spawn, move toward ore |
| 10-20 | First harvesters placed, economy starts |
| 30-60 | Builders spreading, some heading toward map centre |
| 60-80 | Enemy builders can be adjacent to our territory |
| 80-120 | Enemy can build conveyors/barriers near our core perimeter |
| 120+  | Sustained attack, our core taking damage |

A gunner placed at round 200 (current balanced timing) fires its first shot 200+ rounds after the game starts — long after enemy units have already established attack corridors.

### Tight map specific risk

The early barrier logic (lines 221-263) does fire for tight maps (`map_mode == "tight" and rnd >= 5`), placing up to 2 barriers near core. But barriers have only 30 HP and 3 Ti cost — they slow attackers briefly but do not stop them. Without a gunner backing the barriers, the defensive line collapses quickly.

---

## Recommended New Timing

| Map Mode | Recommended gunner_round | Rationale |
|----------|--------------------------|-----------|
| tight    | 60 | Enemy can arrive by round 60-80; must fire before round 80 |
| balanced | 120 | Maps 26x26-39x39, enemies arrive ~round 100-130 |
| expand   | 150 | Keep current; large maps give more time |

### Change required

1. **Remove the `map_mode != "tight"` guard** on line 277 to allow gunners on tight maps.
2. **Update gunner_round** with a three-way branch:

```python
if map_mode == "tight":
    gunner_round = 60
elif map_mode == "expand":
    gunner_round = 150
else:  # balanced
    gunner_round = 120
```

3. **Adjust prerequisite** for tight maps: `harvesters_built >= 1` instead of `>= 3`, since economy is smaller and a single gunner is critical for survival.

---

## Risk Assessment

### Cost of early gunner

- **Titanium cost:** 10 Ti (base gunner cost, line 523: `ti < c.get_gunner_cost()[0] + 10`)
- **Scale cost:** +10% to all future building costs (gunner scale increase = +10%)
- **Opportunity cost:** 10 Ti diverted from harvesters (harvester = 20 Ti base). On a tight map with 500 Ti start and 10 Ti/4 rounds passive income, 10 Ti at round 60 represents ~2.5 rounds of passive income — small.

### Economy impact on tight maps

At round 60 on a tight map:
- Passive income so far: 500 + (60/4 * 10) = 650 Ti earned
- Likely spent: 1-2 builders (30 Ti each), 1-2 harvesters (20 Ti each), conveyors (3 Ti each x ~10) = 140-200 Ti
- Available: ~450-510 Ti
- 10 Ti for a gunner is less than 3% of available resources — negligible

### Scale impact

Going from scale 1.0 to 1.10 on gunner costs (+10%) applies only to future gunners and other +10% buildings (bridges, launchers, breach). For early tight-map play focused on harvesters (+5% scale) and conveyors (+1% scale), the +10% gunner scale barely moves the needle on harvester costs.

### Summary: Risk is low

A round-60 gunner on a tight map costs ~10 Ti and 2-3% scale impact, but prevents core destruction at round 137. The asymmetry strongly favors early gunners.

---

## Code Interactions to Watch

### 1. Gunner builder assignment (lines 274-283)

The gunner builder is `(self.my_id or 0) % 5 == 1`. On tight maps with cap=3-7 builders (see lines 74), builder IDs cycle. With 3 builders at IDs [X, X+1, X+2], ID%5==1 hits roughly 1 in 5 builders. May need to widen to `% 5 in (1, 2)` on tight maps to ensure a gunner builder exists early.

### 2. Harvester prerequisite

Current: `harvesters_built >= 3`. For tight maps at round 60, reaching 3 harvesters may not be achievable (ore proximity, builder count). Should use `harvesters_built >= 1` for tight maps.

### 3. Ti reserve check (line 523)

```python
if ti < c.get_gunner_cost()[0] + 10:
    return False
```

This is fine — ensures 10 Ti buffer. No change needed.

### 4. Gunner count cap (lines 518-520)

```python
if gunner_count >= 3:
    return False
```

3 gunners is reasonable for tight maps. Could lower to 2 for tight maps to reduce scale impact, but 3 is fine.

### 5. Early barrier interaction (lines 221-263)

Early barriers are placed by `rnd <= 30` and `distance_squared(core_pos) <= 18`. Gunner placement walks toward core if `distance_squared(core_pos) > 25` (line 541). These two systems operate independently — barriers are placed early, gunner fires later. No conflict, but the gunner should ideally be placed **behind** the barrier line (closer to core), which the current `_place_gunner` logic handles by walking toward core.

### 6. `_place_gunner` placement range (line 541)

```python
if self.core_pos and pos.distance_squared(self.core_pos) > 25:
    self._walk_to(c, pos, self.core_pos)
```

Walk-to-core threshold is distance^2 > 25 (5 tiles). On tight maps where core is never far, this should trigger rarely — the builder should be close enough to place without extra walking.

---

## Summary of Recommended Changes

| Line | Current | Proposed |
|------|---------|----------|
| 277 | `if (map_mode != "tight"` | Remove `!= "tight"` guard |
| 276 | `gunner_round = 150 if map_mode == "expand" else 200` | Three-way: tight=60, balanced=120, expand=150 |
| 279 | `self.harvesters_built >= 3` | `(self.harvesters_built >= 1 if map_mode == "tight" else self.harvesters_built >= 3)` |
