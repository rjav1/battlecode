# Conveyor Chain Length Cap — Design Research

Date: 2026-04-06

## Problem Statement

Buzzing builds 2-4x more buildings than opponents (238 vs 117 on gaussian, 415 vs 264 on cold).
The root cause: `_nav` builds a conveyor on every step toward ore, regardless of trip length.
A 15-step maze path produces 15 conveyors (45 Ti) instead of 5-8 for a straight path (15-24 Ti).
This Ti drain delays harvesters and builder spawns.

---

## Code Analysis

### Where conveyors are built in `_nav` (lines 466–484)

The conveyor build happens unconditionally on every nav step:

```python
if ti >= cc + ti_reserve:
    face = d.opposite()
    # ... road-destroy logic ...
    if c.can_build_conveyor(nxt, face):
        c.build_conveyor(nxt, face)   # NO cap check
        return
if c.get_move_cooldown() == 0 and c.can_move(d):
    if self.target is not None and len(self.fix_path) < 30:
        self.fix_path.append(pos)     # step recorded here
    c.move(d)
    return
```

`_nav` is called each round from `_builder`. It has no memory of how many conveyors were
built on the current trip — each call is stateless with respect to trip history.

### Existing trip state: `fix_path`

`fix_path` (list of positions visited) already approximates trip length.
Reset when: target changes (line 413), harvester built (line 378/380), chain-fix completes (line 729).
Populated in `_nav` at line 486: appends on MOVE, not on build.
`len(fix_path)` ≈ steps taken ≈ conveyors built (one per step). Capped at 30 internally.

---

## Tracking Conveyors-Built-This-Trip

### Option A: Use `len(self.fix_path)` as proxy (no new variable)

`fix_path` already tracks steps. Since the builder typically builds one conveyor per step,
`len(fix_path)` is a reliable upper bound.

Downside: not exact — if builder spends multiple rounds stuck trying to build without Ti,
`fix_path` grows without conveyors actually built, triggering premature cap.

### Option B: Add `self._conveyors_this_trip = 0` (precise)

Add to `__init__`:
```python
self._conveyors_this_trip = 0
```

Increment in `_nav` immediately after each `c.build_conveyor(...)`:
```python
c.build_conveyor(nxt, face)
self._conveyors_this_trip += 1
return
```

Reset at same points as `fix_path` (target change, harvester built, stuck reset).

**Recommendation: Option B** — exact count, one int overhead. Option A drift risk is real.

---

## Where to Add the Cap Check in `_nav`

Insert before the conveyor build at line ~470:

```python
if c.get_action_cooldown() == 0:
    ti = c.get_global_resources()[0]
    cc = c.get_conveyor_cost()[0]
    conv_cap = getattr(self, "_conv_cap", 12)
    under_cap = self._conveyors_this_trip < conv_cap
    if under_cap and ti >= cc + ti_reserve:
        face = d.opposite()
        # ... existing road-destroy + build_conveyor logic ...
        if c.can_build_conveyor(nxt, face):
            c.build_conveyor(nxt, face)
            self._conveyors_this_trip += 1
            return
# move-only path (already present):
if c.get_move_cooldown() == 0 and c.can_move(d):
    c.move(d)
    return
```

When over cap, code falls through to move-only. The road fallback (lines 510–521) then
handles building a road if the next tile is not passable.

### Compute `_conv_cap` once per builder

In the `_builder` init block (alongside `map_mode` detection at line ~189):

```python
if not hasattr(self, "_conv_cap"):
    w, h = c.get_map_width(), c.get_map_height()
    self._conv_cap = max(8, min(w, h) // 2)
```

---

## Cap Value Recommendation

### Observed path lengths

| Map          | Buzzing bldgs | Opponent bldgs | Est. steps/harvester |
|--------------|---------------|----------------|----------------------|
| gaussian     | 238           | 117            | 15–20 (maze)         |
| cold         | 415           | 264            | 20–30 (maze)         |
| default_med1 | 251           | 149            | 10–15 (moderate)     |

Straight-line ore distance from core: 3–8 tiles typical. Maze detour multiplier: 1.5–3x.

### Cap analysis

**Cap = 8 (aggressive):** Matches smart_eco near-zero conveyor waste on open maps.
Risk: cold/butterfly ore is genuinely 12+ steps away — builder stops short, orphans harvester.

**Cap = 12 (moderate):** Covers ore within ~10 straight-line tiles. Cuts maze detours of 15–20.
Risk: low for most maps.

**Cap = 15 (conservative):** Covers ~13 straight-line tiles. Still cuts worst paths (20–30). Very safe.

**Recommended: `cap = max(8, min(w, h) // 2)`**

| Map              | min(w,h) | Cap | Effect                        |
|------------------|----------|-----|-------------------------------|
| gaussian 35×20   | 20       | 10  | Cuts 15–20 step paths to 10   |
| cold 37×37       | 37       | 18  | Covers cold maze paths safely |
| default_med1 30× | 30       | 15  | Appropriate for moderate paths|
| tight 20×20      | 20       | 10  | Short enough for dense maps   |

Adaptive: larger maps get higher caps because ore is genuinely farther away.

---

## Risk: Does Capping Break Resource Chains for Far Ore?

### Scenario 1: Ore genuinely beyond cap steps

Example: cold, ore 20 steps away, cap=18. Builder lays 18 conveyors, walks last 2 steps
without conveyors. Harvester is built but has a 2-tile gap in its chain.

**Mitigation:** The bridge-shortcut logic (`_bridge_target`, lines 288–340) already attempts
to bridge orphaned harvesters to the nearest allied conveyor or core tile after placement.
Bridge range = d² ≤ 9 = up to 3 tiles. Gaps ≤ 3 tiles are covered automatically.

For gaps > 3 tiles (ore 15+ steps beyond a cap=12 map): harvester produces Ti that cannot
reach core — wasted. This case is rare with the adaptive formula since cap scales with map.

### Scenario 2: Reset correctness

`_conveyors_this_trip` must reset at ALL target-change sites:
- Line ~413: `if best != self.target` — add reset here
- Line ~361: after `c.build_harvester()` — add reset here
- Line ~200: stuck reset (`self.target = None`) — add reset here

If any reset is missed, the cap carries over between trips and prematurely stops a new trip.

### Scenario 3: `_fix_chain` interaction

`_fix_chain` calls `c.build_conveyor()` directly, NOT through `_nav`. The cap counter is
never incremented by fix_chain rebuilds. These are replacement conveyors (reorienting),
not new chain links. No interaction issue — fix_chain is cap-agnostic by design.

### Scenario 4: Explore-mode conveyors

`_explore` calls `_nav` without `use_roads=True`, so exploration builds conveyors to nowhere.
The cap bounds this waste to `conv_cap` tiles per explore trip.

Once a builder hits the cap in explore mode, it moves without conveyors. The road fallback
(lines 510–521) kicks in, building 1 Ti roads instead. This is correct behavior.

**Better fix (separate from this task):** Call `_nav` with `use_roads=True` from `_explore`.
Exploration should use roads, not conveyors. This removes explore conveyor waste entirely.

### Scenario 5: Two builders approaching same ore cluster

Marker claiming (lines 427–434) ensures each builder targets a different ore tile.
They build independent chains that may converge near core. The cap applies per-builder,
so both stop at their respective cap. No interaction between their chains.

---

## Summary Design

### 4 changes required

**1. `__init__` (line ~64):**
```python
self._conveyors_this_trip = 0
```

**2. `_builder` init block (line ~189, alongside `map_mode` detection):**
```python
if not hasattr(self, "_conv_cap"):
    w, h = c.get_map_width(), c.get_map_height()
    self._conv_cap = max(8, min(w, h) // 2)
```

**3. `_nav` (line ~470), replace conveyor build block:**
```python
conv_cap = getattr(self, "_conv_cap", 12)
if self._conveyors_this_trip < conv_cap and ti >= cc + ti_reserve:
    face = d.opposite()
    # ... existing road-destroy logic unchanged ...
    if c.can_build_conveyor(nxt, face):
        c.build_conveyor(nxt, face)
        self._conveyors_this_trip += 1
        return
```

**4. Three target-reset sites — add `self._conveyors_this_trip = 0`:**
- Line ~413: `if best != self.target` block
- Line ~361: after `c.build_harvester()`
- Line ~200: stuck reset block

### Expected impact

| Map          | Cap | Before bldgs | Projected bldgs | Ti saved |
|--------------|-----|--------------|-----------------|----------|
| gaussian     | 10  | 238          | 120–140         | 250–350  |
| cold         | 18  | 415          | 280–320         | 280–400  |
| default_med1 | 15  | 251          | 160–190         | 180–270  |

Ti saved → fewer scale inflations → cheaper future buildings → more harvesters.
Each saved harvester ≈ +500 Ti income over the game (10 Ti/4 rounds × 200 rounds).

### Risk level: LOW

Primary failure mode (orphaned harvester from far-ore gap) is mitigated by:
- Bridge shortcut covers gaps ≤ 3 tiles automatically
- Adaptive cap scales with map size (larger maps get higher cap)
- Road fallback keeps builders mobile past the cap
- `_fix_chain` bypasses cap entirely (replacements, not new links)
- Marker system prevents duplicate targeting
