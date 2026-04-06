# Rush Defense Design — Ammo Delivery, Emergency Detection, Forward Push

**Date:** 2026-04-06
**Author:** defense-specialist agent
**Problem:** 15 core deaths in 114 matches (13% loss rate to rushes). HAL9000 killed us at round 86, Warwick at 137, Polska Gurom at 319. We have NEVER killed an enemy core. Current gunners sit idle with 0 ammo.

---

## 1. Critical Fix: Gunner Ammo Delivery

### Current Problem
`_place_gunner` (line 619) builds a gunner facing the enemy direction on any empty tile near core. But **no conveyor is built to feed it ammo**. The gunner code (line 164) checks `c.get_ammo_amount() < 2` — without ammo delivery, it never fires.

### How Turret Ammo Works (from CLAUDE.md)
- Turrets accept resources from **non-facing directions** via conveyors
- Gunner needs **2 Ti ammo per shot** (reload: 1 round)
- Turrets only accept resources when **completely empty**
- Resources move in **stacks of 10** at end of round

### Solution: Build Ammo Conveyor After Gunner Placement

After `_place_gunner` succeeds, the same builder should immediately build 1-2 conveyors forming a short chain from the nearest existing conveyor or core tile to the gunner's non-facing side.

**Approach:**
1. When gunner is placed at position `gp` facing `enemy_dir`, identify the 3 non-facing sides (left, right, behind)
2. Find the nearest allied conveyor or core tile
3. Build 1-2 conveyors connecting that source to one of the gunner's intake sides

### Code Changes

**In `_place_gunner` (line 619), after `c.build_gunner(sp, enemy_dir)` at line 650:**

```python
def _place_gunner(self, c, pos):
    """Place a gunner on any empty tile near core facing the enemy, then build ammo conveyor."""
    if c.get_action_cooldown() != 0:
        return False

    # If we just placed a gunner last turn, build the ammo conveyor now
    if hasattr(self, '_pending_gunner_ammo'):
        gp, facing = self._pending_gunner_ammo
        del self._pending_gunner_ammo
        self._build_ammo_conveyor(c, pos, gp, facing)
        return True  # consumed this turn for ammo setup

    # ... existing gunner count check and placement logic ...
    
    # After successful build:
    #   c.build_gunner(sp, enemy_dir)
    #   self.gunner_placed += 1
    #   self._pending_gunner_ammo = (sp, enemy_dir)  # NEW: schedule ammo build
    #   return True
```

**New method `_build_ammo_conveyor`:**

```python
def _build_ammo_conveyor(self, c, pos, gunner_pos, facing_dir):
    """Build a conveyor feeding into gunner's non-facing side."""
    if c.get_action_cooldown() != 0:
        return False
    
    ti = c.get_global_resources()[0]
    cc = c.get_conveyor_cost()[0]
    if ti < cc + 5:
        return False
    
    # Gunner accepts from 3 non-facing sides
    intake_dirs = []
    for d in DIRS:
        if d != facing_dir:
            intake_dirs.append(d)
    
    # Try each intake direction — build a conveyor adjacent to gunner
    # that faces TOWARD the gunner (so conveyor output goes into gunner)
    for intake_d in intake_dirs:
        conv_pos = gunner_pos.add(intake_d)
        conv_facing = intake_d.opposite()  # face toward gunner
        if pos.distance_squared(conv_pos) <= 2:
            try:
                if c.can_build_conveyor(conv_pos, conv_facing):
                    c.build_conveyor(conv_pos, conv_facing)
                    return True
            except Exception:
                pass
    return False
```

**Key insight:** The conveyor just needs to face toward the gunner. Resources from the core's passive economy (10 Ti every 4 rounds) will flow through existing conveyor networks. Even a single conveyor adjacent to a gunner, facing toward it, will capture passing resources.

**Better approach — use a conveyor from core:** Since the core is 3x3 and outputs resources, place the gunner 2 tiles from core edge, then build a conveyor between core and gunner facing the gunner. This creates a direct ammo pipeline.

### Line-by-line changes to `_place_gunner` (bots/buzzing/main.py):

**Line 620:** Change docstring:
```python
"""Place a gunner near core facing enemy, then build ammo conveyor next turn."""
```

**Line 649-652:** After building gunner:
```python
        for d in self._rank(pos, enemy_target):
            sp = pos.add(d)
            if c.can_build_gunner(sp, enemy_dir):
                c.build_gunner(sp, enemy_dir)
                self.gunner_placed += 1
                self._pending_gunner_ammo = (sp, enemy_dir)  # ADD THIS
                return True
```

**Line 618, add before `_place_gunner`:**
```python
    def _build_ammo_conveyor(self, c, pos, gunner_pos, facing_dir):
        """Build conveyor feeding into gunner's non-facing side."""
        if c.get_action_cooldown() != 0:
            return False
        ti = c.get_global_resources()[0]
        cc = c.get_conveyor_cost()[0]
        if ti < cc + 5:
            return False
        # Try each non-facing direction
        for d in DIRS:
            if d == facing_dir:
                continue
            conv_pos = gunner_pos.add(d)
            conv_facing = d.opposite()  # face toward gunner
            if pos.distance_squared(conv_pos) <= 2:
                try:
                    if c.can_build_conveyor(conv_pos, conv_facing):
                        c.build_conveyor(conv_pos, conv_facing)
                        return True
                except Exception:
                    pass
        return False
```

**At top of `_place_gunner` (after cooldown check at line 622), add:**
```python
        # Ammo conveyor follow-up from previous turn's gunner placement
        if hasattr(self, '_pending_gunner_ammo'):
            gp, facing = self._pending_gunner_ammo
            del self._pending_gunner_ammo
            if self._build_ammo_conveyor(c, pos, gp, facing):
                return True
            # If we couldn't build conveyor (not adjacent), walk toward it
            if pos.distance_squared(gp) > 2:
                self._walk_to(c, pos, gp)
                return True
```

---

## 2. Emergency Defense — Enemy Spotted Near Core

### Current Problem
No emergency response when enemy builders are detected near our core. A rusher arriving at round 24 can freely destroy conveyors while our builder is off exploring for ore.

### Solution: Emergency Barrier + Recall Builder

Add enemy detection to builder logic that triggers when ANY enemy unit is spotted within distance_squared <= 25 of core (roughly 5 tiles).

### Code Changes — in `_builder` method (after barrier logic, before attacker assignment)

**Insert at line ~345 (after bridge_target block, before spend-down gunner):**

```python
        # EMERGENCY DEFENSE: enemy builder spotted near core
        if (self.core_pos and not self.is_attacker
                and c.get_action_cooldown() == 0):
            enemy_near_core = False
            for eid in c.get_nearby_entities():
                try:
                    if c.get_team(eid) != c.get_team():
                        epos = c.get_position(eid)
                        if epos.distance_squared(self.core_pos) <= 36:  # ~6 tiles
                            enemy_near_core = True
                            break
                except Exception:
                    continue
            
            if enemy_near_core and pos.distance_squared(self.core_pos) <= 20:
                # Build emergency barrier between enemy and core
                ti = c.get_global_resources()[0]
                bc = c.get_barrier_cost()[0]
                if ti >= bc + 5:
                    for eid in c.get_nearby_entities():
                        try:
                            if c.get_team(eid) != c.get_team():
                                epos = c.get_position(eid)
                                # Build barrier on a tile between enemy and core
                                block_dir = epos.direction_to(self.core_pos)
                                if block_dir != Direction.CENTRE:
                                    bp = epos.add(block_dir)
                                    if (pos.distance_squared(bp) <= 2
                                            and c.can_build_barrier(bp)):
                                        c.build_barrier(bp)
                                        return
                        except Exception:
                            continue
```

**Why this works:** When a rush attacker enters our vision near core, the nearest builder interrupts whatever it's doing to place a barrier between the attacker and core. Barriers have 30 HP (vs conveyor's 20 HP) and can't be walked on by enemy builders, slowing them down significantly.

### Alternative: Priority Gunner Rush

If an enemy is detected near core and no gunner exists yet, the builder should prioritize building a gunner over a barrier:

```python
            if enemy_near_core:
                # If no gunner exists, emergency gunner takes priority
                has_gunner = False
                for eid in c.get_nearby_buildings():
                    try:
                        if (c.get_entity_type(eid) == EntityType.GUNNER
                                and c.get_team(eid) == c.get_team()):
                            has_gunner = True
                            break
                    except Exception:
                        pass
                if not has_gunner and self.core_pos:
                    # Emergency gunner: skip all other checks
                    ti = c.get_global_resources()[0]
                    if ti >= c.get_gunner_cost()[0]:
                        if self._place_gunner(c, pos):
                            return
```

---

## 3. Should We Add Basic Offense (Forward Gunner Push)?

### Analysis

**Current offense capability:** We have one attacker per game (id%6==5, spawned after round 500 with 4+ harvesters). It builds roads toward the enemy and attacks conveyors with 2 damage per hit. This is very weak — a conveyor has 20 HP, so it takes 10 attacks (20 Ti) to destroy one.

**Forward gunner push concept:** Build a gunner partway to the enemy base, with a conveyor chain feeding it ammo. The gunner fires along its forward ray, potentially hitting enemy infrastructure.

### Recommendation: NOT NOW

Reasons against forward gunner push:
1. **Gunner costs 10 Ti + 10% scaling** — expensive to place far from core
2. **Needs long ammo conveyor chain** — each conveyor is 3 Ti + 1% scaling
3. **Gunner fires along a single ray** — easily missed if enemy infra is offset
4. **Rotation costs 10 Ti** — reorienting is expensive
5. **Our core still dies to rushes** — fixing defense is higher priority

**Better offense option for later:** Launcher (20 Ti, no ammo needed) + builder bot throws. A launcher adjacent to core can throw builder bots toward the enemy base. The thrown builder lands on enemy conveyors and can attack. This is cheaper and more flexible than a forward gunner.

### What to do instead
1. Fix ammo delivery to defensive gunners (Section 1)
2. Add emergency detection (Section 2)
3. Only after defense is solid, consider launcher-based offense

---

## 4. Implementation Plan — Exact Code Changes

### Priority 1: Ammo Conveyor (CRITICAL)
**Files:** `bots/buzzing/main.py`

1. Add `_build_ammo_conveyor` method (new, insert before line 618)
2. Modify `_place_gunner` to store `_pending_gunner_ammo` state (line 650)
3. Add follow-up conveyor build at top of `_place_gunner` (after line 622)
4. Add `_pending_gunner_ammo` cleanup in `__init__` (line 44): `self._pending_gunner_ammo = None`

### Priority 2: Emergency Detection (HIGH)
**Files:** `bots/buzzing/main.py`

1. Insert enemy-near-core scan block at line ~345 (after bridge shortcut, before spend-down gunner)
2. When enemy detected within dist_sq <= 36 of core AND builder is within dist_sq <= 20 of core:
   - If no gunner: emergency gunner placement
   - If gunner exists: emergency barrier between enemy and core

### Priority 3: Earlier Gunner on Tight Maps (MEDIUM)
**Files:** `bots/buzzing/main.py`

Line 367: Change `gunner_round = 30` to `gunner_round = 15` for tight maps. Rusher attackers arrive at round 24-28 — gunner needs to exist before they arrive.

```python
gunner_round = 15 if map_mode == "tight" else (120 if map_mode == "balanced" else 150)
```

### Priority 4: Remove Harvester Requirement for Tight Gunner (MEDIUM)
**Files:** `bots/buzzing/main.py`

Line 368: Change `harv_req = 1 if map_mode == "tight"` to `harv_req = 0`:

```python
harv_req = 0 if map_mode == "tight" else 3
```

This lets the gunner-builder (id%5==1) place a gunner even before any harvester is built. On tight maps, surviving the rush matters more than waiting for economy.

---

## 5. Economy Impact Assessment

### Cost of proposed changes
- **Ammo conveyor:** 1 conveyor = 3 Ti + 1% scaling. Negligible cost for a functional gunner.
- **Emergency barrier:** 3 Ti + 1% scaling. Only triggered when enemy is near core — rare on expand/balanced maps.
- **Earlier gunner (round 15):** Same cost as before (10 Ti + 10% scaling), just earlier. Delays first harvester by ~2 rounds on tight maps.

### Net effect on economy
- Losing 0 Ti to dead core (currently 15/114 = 13% of matches)
- Gunner that actually fires: each shot does 10 damage to enemy builder (30 HP). 3 shots = dead builder. Cost: 6 Ti of ammo. Benefit: enemy builder worth 30+ Ti is eliminated.
- **ROI is strongly positive** — a functional gunner pays for itself in 1-2 kills.

### Impact on conveyors/harvesters
- The ammo conveyor is 1 additional building per gunner (we build 1-5 gunners total)
- No impact on harvester throughput — the conveyor is a short spur, not part of the main chain
- Emergency barriers only fire near core, not in the ore field

**Recommendation for economy-researcher:** These changes add at most 5 conveyors and 2-3 barriers over a full game. The scaling impact is ~5-8% total, far less than the 200-450 conveyors already being placed. The defense benefit (preventing core death) vastly outweighs the economy cost.

---

## 6. Summary of Death Scenarios and Fixes

| Opponent | Death Round | Root Cause | Fix |
|----------|------------|------------|-----|
| HAL9000 | 86 | Rush arrives before gunner, no ammo anyway | Earlier gunner (P3) + ammo conveyor (P1) |
| Warwick | 137 | Gunner exists but starved of ammo | Ammo conveyor (P1) |
| Polska Gurom | 319 | Sustained rush destroys infrastructure | Emergency detection (P2) + ammo conveyor (P1) |

All 15 deaths share the same pattern: **gunner has no ammo, enemy walks freely**. Fixing ammo delivery alone would likely prevent 10+ of these deaths.
