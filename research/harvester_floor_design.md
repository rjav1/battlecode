# Harvester Floor + Maze Chain-Fix Design

**Date:** 2026-04-06  
**Context:** On sierpinski_evil (31x31, 28% wall density), we mine 0 Ti in 2000 rounds. Harvesters are built but chains from harvester → core are broken by the fractal maze. Chain-fix exists but isn't triggering. Can a "harvester floor" check fix this?

---

## Q1: Is chain-fix triggered automatically, or only manually?

**Only manually — triggered only when a harvester is built.**

From `main.py` line 366-381 (`_builder`):

```python
# Chain-fix for first 2 harvesters if path is winding
if (self.core_pos and len(self.fix_path) >= 4
        and self.harvesters_built <= 2):
    changes = 0
    for i in range(1, len(self.fix_path) - 1):
        d1 = self.fix_path[i-1].direction_to(self.fix_path[i])
        d2 = self.fix_path[i].direction_to(self.fix_path[i+1])
        if d1 != d2:
            changes += 1
    if changes >= 3:
        self.fixing_chain = True
        self.fix_idx = len(self.fix_path) - 1
```

**Conditions for chain-fix to trigger:**
1. Just built a harvester
2. `self.fix_path` has ≥ 4 recorded positions
3. `harvesters_built <= 2` (only for first 2 harvesters)
4. Path has ≥ 3 direction changes (winding)

**Critical problem:** `fix_path` is populated in `_nav`/`_explore` only while the builder is moving toward a target (line 487-488). On sierpinski_evil, if the builder loses its target, resets stuck counter, or reaches ore via a short path, `fix_path` may be empty or too short. Additionally, once `harvesters_built > 2`, chain-fix **never triggers**, even if chains are broken.

There is no external signal, no periodic re-trigger, and no global awareness of chain health. Chain-fix is entirely local to each builder's memory of its own path.

---

## Q2: Does vis_harv in _core tell us if harvesters are connected?

**Imperfectly — it counts visible harvesters, not connected ones.**

From `_core` (lines 98-103):
```python
vis_harv = 0
for eid in c.get_nearby_buildings():
    try:
        if (c.get_entity_type(eid) == EntityType.HARVESTER
                and c.get_team(eid) == c.get_team()):
            vis_harv += 1
    except Exception:
        pass
```

Core has vision r²=36, which covers approximately 6 tiles in any direction from the core center. `vis_harv` counts harvesters **physically near the core**, not harvesters connected via conveyor chain.

**What vis_harv tells us:**
- `vis_harv == 0`: No harvesters near core — either none built yet, or all are far away
- `vis_harv >= 1`: At least one harvester is nearby, but its chain may still be broken

**What vis_harv does NOT tell us:**
- Whether harvesters are actually delivering Ti
- Whether harvester chains are complete and functional
- Whether harvesters are far from core (outside vision r²=36) with working chains

On sierpinski_evil, harvesters built in the fractal maze may be well outside core vision. `vis_harv` would be 0 even if 3 harvesters exist, just far away. The current code uses `vis_harv` only for `econ_cap = max(time_floor, vis_harv * 3 + 4)` — the spawning rate. It does not use it to detect disconnection.

**Verdict: vis_harv is not a reliable disconnection signal.** A better proxy would be whether Ti income exceeds passive income (10 Ti per 4 rounds = 2.5/round).

---

## Q3: Could core track "Ti collected this game" to signal chain repair?

**Yes, but requires a workaround — there is no direct API for cumulative Ti mined.**

The only resource API is `get_global_resources() → (ti, ax)` which returns **current stored Ti**, not total collected. Starting Ti is 500. Passive income is 10 Ti every 4 rounds (2.5/round). Spending reduces the pool.

**Workaround — Ti income tracking in core:**

```python
# In _core, per-round tracking:
if not hasattr(self, '_last_ti'):
    self._last_ti = 500
    self._ti_income_samples = []

ti_now = c.get_global_resources()[0]
rnd = c.get_current_round()
# Income estimate: current - last + estimated spend this round
# Spend is hard to track (buildings + bots cost Ti)
# Simpler: track whether Ti is growing at all above passive rate
```

The problem: tracking spend requires knowing exactly what was built each round, which builders don't communicate to core. Alternatively, core can check if current Ti is meaningfully less than `500 + passive_rounds * 2.5` — if Ti is much lower than expected from passive alone, spending happened (good). If Ti ≈ `500 + passive_income - spend_on_builders` and barely growing, harvesters may not be connected.

**Simpler signal: absolute Ti comparison at round 200**

At round 200:
- Passive income: 500 + (200 / 4) * 10 = 500 + 500 = ~1000 Ti (before any spending)
- If harvesters are connected and mining: Ti should be much higher
- Builder spawn costs: ~8 builders × 30 Ti = 240 Ti spent
- Infrastructure: ~50 conveyors × 3 Ti = 150 Ti spent  
- Expected Ti with 2 working harvesters at round 200: ~800-1200 Ti
- Expected Ti with 0 working harvesters at round 200: ~600 Ti (500 + passive - spend)

The signal `ti < 650 at round 200` (when harvesters_built >= 2) would indicate broken chains.

**However, this signal is noisy:**
- High building activity legitimately depletes Ti
- Elo doesn't track Ti income, only current pool
- Signal fires ~round 200 — by then 2 harvesters are already misplaced in a maze

---

## Design: Harvester Floor with Marker-Based Signal

### The core problem
Chain-fix is builder-local and only triggers at harvester placement. On maze maps:
1. Builder A reaches ore via winding path, records fix_path
2. Builds harvester, chain-fix triggers — builder A walks back fixing conveyors
3. Chain-fix completes or gets stuck — builder marks itself "done"
4. **But**: fix_path doesn't account for walls that force conveyors off-axis. The `d.opposite()` conveyor assumption (conveyors face toward core along the path) breaks when the actual chain direction is diagonal or perpendicular to avoid walls.

### Proposed: Core-side Ti income check + marker signal

**Core logic (add to `_core` after round 150):**
```python
# Harvester floor check: detect disconnected chains
if not hasattr(self, '_floor_checked'):
    self._floor_checked = False
if rnd == 150 and not self._floor_checked:
    self._floor_checked = True
    ti_now = c.get_global_resources()[0]
    # If we have builders but Ti is still near starting (≤ 600), 
    # and harvesters should be built, chains are likely broken
    # Signal builders via marker on core tile
    if ti_now <= 600 and units >= 3:
        # Place a marker value=1 on core tile = "fix chains" signal
        core_center = c.get_position()
        if c.can_place_marker(core_center):
            c.place_marker(core_center, 1)
```

**Builder logic (check for core signal):**
```python
# Check for core "fix chains" signal
if self.core_pos and rnd > 150 and not self.fixing_chain:
    core_building_id = c.get_tile_building_id(self.core_pos)
    # Core itself is on the center tile — check adjacent for marker
    # Or: check if a marker on core_pos has value=1
    # Actually: core marker is placed on a core tile (9 tiles)
    # Need to check visible markers near core
    ...
```

**Problems with this approach:**
1. Markers last until overwritten — core can only place 1 per round, and it's already used for ore claiming
2. Builders need to be within vision of core to read the marker — if they're deep in a maze, they can't see it
3. Core's `can_place_marker` may be blocked if a builder is standing on the target tile
4. The marker value scheme conflicts with existing ore-claim markers

---

## Better Design: Per-Builder Ti-Delta Inference

Instead of global signaling, each builder can infer chain health locally:

**Builder self-check at round 150 (if harvesters_built >= 1):**
```python
if rnd == 150 and self.harvesters_built >= 1 and not self.fixing_chain:
    ti = c.get_global_resources()[0]
    # Rough check: if Ti is very low, we've been spending but not earning
    # Passive income by round 150: ~375 Ti
    # Builder + infra spend: ~400-600 Ti  
    # If Ti < 400, we're net-spending → chains likely broken
    # This is a very rough heuristic
    if ti < 350:
        # Re-trigger chain fix if we have a recorded path
        if len(self.fix_path) >= 2:
            self.fixing_chain = True
            self.fix_idx = len(self.fix_path) - 1
```

**Problems:** Ti is global — all builders share the same `get_global_resources()`. A builder that spent 200 Ti on infrastructure but has working harvesters would also see Ti < 350 at round 150. False positives are high.

---

## Most Viable Design: vis_harv + Ti Threshold in Core

**The cleanest signal available:**

```python
# In _core, check at round 200:
if rnd == 200 and vis_harv == 0 and units >= 4:
    ti = c.get_global_resources()[0]
    # vis_harv==0 means no harvesters near core
    # Could be: (a) none built yet, (b) all built but far/maze
    # Ti < 550 means we've spent on builders but passive income only
    # Ti > 550 means some mining happened (harvesters working somewhere)
    if ti < 550:
        # Place "SOS" marker for builders to find
        # Use value=99 to distinguish from ore-claim markers (value=builder_id)
        ...
```

**Why this is still fragile:**
- `vis_harv == 0` at round 200 is common even on working maps (harvesters built far from core)
- Ti threshold is map-dependent — on tight maps with fewer builders, Ti depletes slower
- Marker placement from core limited to 1/round and may conflict

---

## Recommended Approach: Fix chain-fix trigger condition, not add new signal

The root cause is that chain-fix only fires at harvester placement with `harvesters_built <= 2` and `len(fix_path) >= 4`. On maze maps, fix_path is often too short (builder took a short path via a lucky corridor) or chain-fix runs but terminates early because the builder gets stuck in the maze walls.

**Simpler fix with higher confidence:**

1. **Raise harvesters_built threshold**: Change `harvesters_built <= 2` to `harvesters_built <= 4` — fix chains for more harvesters, not just the first two.

2. **Lower fix_path direction-change threshold**: Change `changes >= 3` to `changes >= 2` — trigger fix on less-winding paths too. A 2-turn path through a maze corridor is still broken.

3. **Periodic re-trigger**: In `_builder`, if `harvesters_built >= 1` and `rnd % 100 == 0` and `rnd < 500` and not `fixing_chain` and `len(fix_path) >= 2`: re-trigger chain-fix. This catches cases where the initial fix was incomplete.

4. **Wall-density guard on exploration**: If `_wall_density > 0.20` (maze map), reduce `explore_reserve` aggressively — this limits how far builders go before running out of Ti, keeping them closer to core where chains are shorter.

---

## Summary: Answering the Three Questions

| Question | Answer |
|----------|--------|
| Is chain-fix triggered automatically? | No — only at harvester placement, only for harvesters 1-2, only if path has ≥4 steps and ≥3 turns |
| Does vis_harv in _core detect disconnection? | Imperfectly — counts nearby harvesters, not connected ones. Far harvesters (outside r²=36) are invisible |
| Can core track "Ti collected" to signal? | No direct API. Workaround: track `get_global_resources()` delta over rounds. Noisy but possible. ti < 550 at round 200 with vis_harv==0 is the best signal available |

**Bottom line:** The proposed harvester floor is sound in concept but the implementation is constrained by API limitations (no Ti-mined query, marker conflicts, builder vision limits in maze). The most robust fix is improving the existing chain-fix trigger (lower threshold, periodic re-trigger, wall-density guard) rather than adding a new global signal system. The global signal approach requires marker bandwidth that's already used for ore claiming.
