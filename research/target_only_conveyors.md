# Target-Only Conveyor Building — Research

Date: 2026-04-06

## The Idea

Only build conveyors when `self.target is not None` (walking toward known ore to place a
harvester). During exploration (`self.target is None`), use roads or nothing — exploration
conveyors connect to nothing and are pure scale inflation.

---

## Current Call Graph

There are exactly **2 call sites** for `_nav`:

```
_builder (line 438):   self._nav(c, pos, self.target, passable)
_explore (line 567):   self._nav(c, pos, far, passable, ti_reserve=explore_reserve)
```

`_explore` is only called when `self.target is None` (line 440):
```python
if self.target:
    self._nav(c, pos, self.target, passable)
else:
    self._explore(c, pos, passable, rnd)   # <-- target is None here
```

This means `_nav` is called from two exclusive paths:
- **Ore-targeted nav:** `self.target` is a known ore tile. Conveyors here build the delivery chain.
- **Exploration nav (via `_explore`):** `self.target` is a synthetic far-edge position. Conveyors here are waste.

The `_nav` signature is:
```python
def _nav(self, c, pos, target, passable, ti_reserve=5, use_roads=False):
```

`use_roads=False` is the default. `_explore` never passes `use_roads=True`. So exploration
always runs in conveyor mode.

---

## What `_explore` Currently Does

`_explore` computes a far-edge target (map edge in the explore direction) and calls:
```python
self._nav(c, pos, far, passable, ti_reserve=explore_reserve)
```

Where `explore_reserve = 30 if core_dist_sq > 50 else 5`.

So when the builder is far from core, `ti_reserve=30` — it won't build a conveyor unless
it has 30+ Ti above the conveyor cost. This already partially limits exploration conveyors
when Ti is scarce. But when Ti is plentiful (e.g., early-game with bank buildup), it happily
builds conveyors along every exploration step.

---

## How Many Conveyors Are Exploration Conveyors?

From the match data (gaussian seed 1, before any fixes):
- buzzing: 238 buildings total, 8 harvesters
- smart_eco: 117 buildings total, 8 harvesters

If buzzing averages 20 conveyors per harvester chain, that's 160 "useful" conveyors +
~78 "exploration" conveyors. smart_eco averages ~14 conveyors per chain = 112 useful,
and 5 exploration = 117 total.

So exploration conveyors are roughly **30-50 of the 238** buildings on gaussian.
Cold is worse: 415 buildings vs 264 for smart_eco. With 8 harvesters × 20 conveyors
= 160 "useful", the remaining ~255 are exploration waste.

Wait — that math doesn't work. 8 harvesters × 20 conveyors = 160, leaving 255 as waste?
That implies exploration waste is the MAJORITY on cold. More likely: conveyor chains
on cold are 30-40 steps long (maze map), so even "useful" conveyors are excessive.
The exploration waste is ~50-80 buildings of the excess.

**Estimate: exploration conveyors = 30-80 buildings per game, worth 90-240 Ti.**

---

## The Fix: Pass `use_roads=True` from `_explore`

The simplest implementation: change the one line in `_explore`:

```python
# Current (line 567):
self._nav(c, pos, far, passable, ti_reserve=explore_reserve)

# Fixed:
self._nav(c, pos, far, passable, ti_reserve=explore_reserve, use_roads=True)
```

`use_roads=True` switches `_nav` to road mode:
```python
if use_roads:
    if c.get_move_cooldown() == 0 and c.can_move(d):
        c.move(d)
        return
    if c.get_action_cooldown() == 0:
        ti = c.get_global_resources()[0]
        rc = c.get_road_cost()[0]
        if ti >= rc + ti_reserve and c.can_build_road(nxt):
            c.build_road(nxt)
            return
```

Road mode: **move first, build road only if blocked** (can't move to unpassable tile).
Roads cost 1 Ti vs 3 Ti for conveyors. Roads don't count toward scale (well, +0.5%/road
vs +1%/conveyor). And crucially, roads still make tiles passable for future builder movement.

---

## Benefits of `use_roads=True` in Explore

### 1. No useless conveyor chains

Exploration conveyors are disconnected chains pointing at map edges. They provide zero
resource delivery. Switching to roads eliminates all exploration conveyor cost.

### 2. Roads are still useful

Roads make tiles passable for builder bots. An exploration road network means future
builders (or the same builder returning) can move freely through explored areas without
rebuilding. This is actually BETTER than exploration conveyors (which only allow movement
in their facing direction).

### 3. Lower Ti cost: 1 vs 3

Roads cost 1 Ti, conveyors cost 3 Ti (at base scale). On a 20-step exploration trip:
- Current: 20 conveyors = 60+ Ti (at scale)
- Fixed: 0-5 roads = 0-5 Ti (only when blocked)

With `explore_reserve=30`, roads are only built when Ti > 31 anyway. Most exploration
moves happen without any building at all — the builder just walks on existing passable tiles
(existing conveyors, roads, or core tiles).

### 4. Lower scale inflation

Conveyors add +1% scale per unit. Roads add +0.5%. Eliminating 30-80 exploration
conveyors per game saves 30-80% scale inflation, making all future buildings cheaper.

---

## Risks

### Risk 1: Explorer gets stranded on unpassable tiles

If a builder is exploring through un-paved area and hits an unpassable tile, road mode
builds a road. But if `ti_reserve=30` and Ti < 31, it can't build a road and can't move —
it would be stuck until Ti accumulates.

However: this situation only occurs when Ti < 31. Early game (rounds 1-50), Ti starts
at 500 and grows. Ti dropping below 31 would mean economy is already in crisis.
In normal play, Ti stays well above the `explore_reserve=30` threshold when builders
are actively harvesting. The stuck detection (12 rounds) catches this case and shifts
explore direction.

**Severity: LOW.** The stuck detection already handles this, and the 30 Ti threshold is
hit rarely in practice.

### Risk 2: Explorer can't return through unpassable tiles

After exploring to the map edge via road, the builder needs to return when it finds ore.
It resets `self.target = ore_tile` and calls `_nav` (conveyor mode) toward the ore.
The return path may not be fully paved.

But: `_nav` in conveyor mode builds conveyors as it moves toward the new target. Conveyors
are passable, so the return trip creates the needed infrastructure. The builder auto-creates
its delivery chain as it walks toward ore, exactly as before.

**Severity: NONE.** Target-nav (conveyor mode) is unaffected by this change.

### Risk 3: Exploration roads create accidental resource delivery paths

Roads are passable but don't carry resources — only conveyors/bridges/splitters do.
A road placed during exploration cannot accidentally route resources. Safe.

### Risk 4: Builder deploys conveyor mid-exploration when `use_roads=True` blocks the bridge fallback

Looking at `_nav` after the conveyor/road loop:
```python
# Bridge fallback (bridges cross walls, roads don't)
if c.get_action_cooldown() == 0:
    ...
    if c.can_build_bridge(bp, bt):
        c.build_bridge(bp, bt)
        return

# Road fallback (for conveyor mode when stuck)
if not use_roads and c.get_action_cooldown() == 0:
    ...  # only runs in conveyor mode
```

With `use_roads=True`, the road fallback at line 512 is SKIPPED (`not use_roads` = False).
The bridge fallback still runs regardless of `use_roads`. This is correct: a bridge during
exploration would also be waste, but bridges are expensive (20 Ti base) and the bridge
threshold (`bc + 20 = 40 Ti`) is high enough that they're rarely built during normal
exploration anyway.

**Mild concern:** In theory a bridge could be built during exploration if the builder is
blocked and has 40+ Ti. But bridge-during-explore is already rare (the bridge fallback
only triggers when all 8 directions fail), and the existing `explore_reserve=30` guard
limits Ti spending. A bridge built during exploration would cost 20 Ti but provide
a shortcut that future builders can use. Net impact: probably neutral to slightly positive.

### Risk 5: Exploration roads destroy conveyor chains?

Road mode does NOT destroy existing conveyors. Only the conveyor build path contains the
road-destroy logic:
```python
# Destroy allied road so we can place conveyor
bid = c.get_tile_building_id(nxt)
if bid is not None:
    if c.get_entity_type(bid) == EntityType.ROAD and ...:
        c.destroy(nxt)
```

With `use_roads=True`, this block is never reached. Road mode simply builds a road on empty
tiles, never destroys anything. If a tile already has a conveyor, `c.can_build_road(nxt)`
returns False (tile occupied), so no road is built there. Existing chains are untouched.

**Severity: NONE.**

---

## Implementation

Single line change in `_explore` (line 567):

```python
# Current:
self._nav(c, pos, far, passable, ti_reserve=explore_reserve)

# New:
self._nav(c, pos, far, passable, ti_reserve=explore_reserve, use_roads=True)
```

No other changes needed. `_nav` already has complete road-mode logic. The `self.target`
check lives in `_builder` — it decides whether to call `_nav` directly or via `_explore`,
so the distinction is already correctly encoded at the call site.

---

## Expected Impact

### Building count reduction

Exploration conveyors eliminated entirely. Estimate 30-80 fewer buildings per game:
- gaussian: 238 → ~190-210 buildings
- cold: 415 → ~350-380 buildings

These are conservative — exploration may account for more on long games.

### Ti saved

30-80 conveyors × 3+ Ti = 90-240 Ti. Plus reduced scale: 30-80 × 1% scale savings
means future buildings are 0.3-0.8 scale% cheaper throughout the game.

### No delivery-chain impact

This change does NOT affect ore-targeted navigation at all. Delivery chains remain exactly
as long as they are today — every step toward ore still builds a conveyor. Only the
exploration-phase building changes.

---

## Comparison With Conveyor Cap Approach

| Approach | Delivery chains | Explore waste | Risk |
|----------|----------------|---------------|------|
| Conveyor cap (tried, reverted) | BREAKS (gaps) | Cuts | HIGH |
| Target-only (`use_roads` in explore) | UNTOUCHED | Eliminates | LOW |

The cap failed because it cut delivery chains. This approach is orthogonal — it leaves
delivery chains completely alone and only changes behavior when `self.target is None`
(which maps exactly to exploration mode, since the call is gated by `else` in `_builder`).

---

## Recommendation

Implement immediately. Single-line change, zero delivery-chain risk, direct elimination
of the explore-conveyor waste category. Should reduce gaussian building count by ~20-30%
and save 90-240 Ti per game across all maps.

Test against:
- `buzzing vs smart_eco gaussian --seed 1` (target: buildings below 200, Ti mined above 19000)
- `buzzing vs buzzing_prev cold --seed 1` (must not regress — cold building count should drop)
- Regression suite (must PASS)
