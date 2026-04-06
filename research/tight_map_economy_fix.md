# Tight Map Economy Fix — Arena Deep Analysis

## Match Data (arena, seed 1)

```
                         buzzing            ladder_dual  
  Titanium     4339 (1470 mined)    17018 (14650 mined)  
  Buildings                  153                    136
```

## Root Causes (3 compounding problems)

### 1. CRITICAL: 2 of 3 harvesters are on AXIONITE ore — resources destroyed at core

Arena ore layout (buzzing's side, core at (8,10)):
- Ax ore @ (8,13) dist²=9   ← CLOSEST, buzzing builds HERE first (R3)
- Ti ore @ (4,8)  dist²=20
- Ax ore @ (12,7) dist²=25  ← buzzing builds HERE second (R11)
- Ti ore @ (5,15) dist²=34

**Buzzing's `_best_adj_ore` only sorts by distance to core — no resource type preference.**
It builds on whichever ore is closest. On arena, the 2 closest ore tiles are AXIONITE.
Raw axionite delivered to core is DESTROYED (game rule). So 2/3 harvesters produce nothing.

Ladder_dual has the same issue on their side (first harvester is Ax) but they build 4+ harvesters quickly, getting 2-3 on Ti ore.

### 2. Builder cap too restrictive — only 3 builders for first 20 rounds

Buzzing tight cap timeline:
```
R0-20:  cap=3 (min of base=3 and econ_cap=6)
R21-100: cap=5 (min of base=5 and econ_cap=13)
R101+:  cap=8
```

Ladder_dual tight cap:
```
R0-15:  cap=5  ← 67% more builders early
R16-100: cap=8  ← 60% more
R101+:  cap=12
```

With only 3 builders, buzzing can't cover enough ore tiles. Ladder_dual has 5 builders by R5, covering more ground.

### 3. Rush destruction of conveyor chains — no defense

Ladder_dual assigns 2/5 builders as rushers (id%5 < 2). They build roads/conveyors toward buzzing's core and attack enemy buildings.

Buzzing conveyor count over time:
```
R150: 32 conveyors (peak)
R300: 18 conveyors (rushers destroying them)
R500: 7 conveyors  (supply chains severed)
R900: 8 conveyors  (stabilized but damage done)
```

Ladder_dual conveyors: 29-30 stable (buzzing has no rushers, no threat to their chains).

**Result: buzzing's Ti harvester at (4,8) can't deliver resources to core.** Mining rate drops from theoretical ~10 Ti/4 rounds to near-zero. Buzzing's total income is almost entirely passive (10 Ti per 4 rounds = 2.5/round).

Income comparison R500-R900:
- buzzing: ~1.9 Ti/round (≈ passive only)
- ladder_dual: ~9.75 Ti/round (passive + 2-3 Ti harvesters delivering)

### 4. Early barriers waste Ti and builder turns (minor)

Buzzing builds 2 barriers by R6 (tight: id%5!=0 builds barrier starting R5). This:
- Costs ~6-8 Ti directly
- Costs 1 builder action turn (1 turn wasted not building conveyors/harvesters)
- Doesn't actually stop rushers (barriers are placed 2-3 tiles from core, rushers walk around)

Ladder_dual builds ZERO barriers, spending all resources on economy.

## Proposed Fixes

### Fix 1: Prefer Titanium ore over Axionite in `_best_adj_ore` (HIGHEST IMPACT)

**File:** `bots/buzzing/main.py`, `_best_adj_ore` method (line ~1266)

Current code:
```python
def _best_adj_ore(self, c, pos):
    best, bd = None, 10**9
    for d in DIRS:
        p = pos.add(d)
        if c.can_build_harvester(p):
            dist = p.distance_squared(self.core_pos) if self.core_pos else 0
            if dist < bd:
                best, bd = p, dist
    return best
```

**Proposed:**
```python
def _best_adj_ore(self, c, pos):
    ti_best, ti_bd = None, 10**9
    ax_best, ax_bd = None, 10**9
    for d in DIRS:
        p = pos.add(d)
        if c.can_build_harvester(p):
            env = c.get_tile_env(p)
            dist = p.distance_squared(self.core_pos) if self.core_pos else 0
            if env == Environment.ORE_TITANIUM and dist < ti_bd:
                ti_best, ti_bd = p, dist
            elif env == Environment.ORE_AXIONITE and dist < ax_bd:
                ax_best, ax_bd = p, dist
    return ti_best if ti_best is not None else ax_best
```

This ensures Ti ore is always preferred. Ax is only built as fallback (still useful for tiebreaker TB#1).

### Fix 2: Also prefer Ti in ore targeting logic (line ~444-468)

Current ore scoring doesn't differentiate Ti vs Ax. When a builder picks a target to walk toward, it should prefer Ti ore tiles over Ax:

```python
# In the ore_tiles scoring section (~line 444):
if use_nearest:
    score = builder_dist
else:
    core_dist = t.distance_squared(self.core_pos) if self.core_pos else 0
    score = builder_dist + core_dist * 2
# ADD: Penalize Ax ore to prefer Ti targets
if c.get_tile_env(t) == Environment.ORE_AXIONITE:
    score += 500  # strong preference for Ti, but still target Ax if no Ti available
```

### Fix 3: Raise tight builder cap to match ladder_dual (line ~99)

Current:
```python
if self.map_mode == "tight":
    cap = 3 if rnd <= 20 else (5 if rnd <= 100 else 8)
```

**Proposed:**
```python
if self.map_mode == "tight":
    cap = 5 if rnd <= 15 else (8 if rnd <= 100 else 12)
```

This gives 5 builders immediately (matching ladder_dual), allowing faster ore coverage on tight maps.

### Fix 4: Remove econ_cap ceiling for tight maps (line ~119-121)

The `econ_cap` formula (`vis_harv * 3 + 4` with time_floor `6 + rnd//200`) was designed for open maps. On tight maps where all ore is in core vision, it's not a problem, but the cap min logic at line 121 (`cap = min(cap, econ_cap)`) can suppress builder production.

**Proposed: Skip econ_cap on tight maps entirely, or raise time_floor:**
```python
if self.map_mode == "tight":
    time_floor = min(8 + rnd // 100, 12)  # faster ramp on tight
```

### Fix 5: Delay barriers on tight maps (line ~246-288)

Current: barriers start at R5 for tight maps (id%5!=0).
**Proposed: Remove early barriers entirely on tight maps**, or delay to R50+.

```python
early_barrier_ok = (
    (map_mode == "tight" and rnd >= 50 and (self.my_id or 0) % 5 != 0)
    or self.harvesters_built >= 1
)
```

Every turn spent building barriers early is a turn NOT building conveyors toward ore.

### Fix 6: Consider adding 1-2 defensive builders on tight maps (longer term)

Ladder_dual's rushers destroy 25+ of buzzing's conveyors. Possible defenses:
- Build a gunner earlier (currently R30 for tight, but requires 1+ harvester)
- Assign one builder as "repair" role to rebuild broken chains
- Build barriers specifically blocking the approach from enemy core (not generic placement)

## Priority Order

1. **Fix 1** (Ti preference in _best_adj_ore) — Immediately doubles effective harvesting
2. **Fix 3** (raise tight cap) — More builders = faster ore coverage
3. **Fix 5** (delay tight barriers) — Stop wasting early turns on useless barriers
4. **Fix 2** (Ti preference in targeting) — Builders walk to Ti ore first
5. **Fix 4** (econ_cap for tight) — Minor cap relief
6. **Fix 6** (defense) — Longer-term anti-rush measures

## Expected Impact

On arena specifically:
- Fix 1 alone: buzzing would mine ~3x more Ti (3 Ti harvesters instead of 1)
- Fixes 1+3: would match ladder_dual's early harvester count (4+)
- All fixes: should close the 4x mining gap to near-parity or advantage

Note: ladder_dual has 4 harvesters by R21 vs buzzing's 3 by R17 (and buzzing's 3rd is also on Ti). The real killer is the Ax waste + chain destruction, not harvester count.
