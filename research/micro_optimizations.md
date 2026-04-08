# V61 Micro-Optimizations Analysis

## Date: 2026-04-08
## Scope: 1-2 line changes that don't alter architecture. Target: squeeze 1-2% more efficiency.

---

## 1. First Builder Direction (lines 116-131)

### Current behavior:
- Only biases the FIRST builder (`units == 0`)
- Scans ALL ore in core vision (r^2=36) — both Ti AND Ax
- Picks nearest ore tile, spawns builder in that direction
- No distance filter beyond vision range

### Issues found:

**A. Includes Axionite ore in direction bias.**
Line 123: `if c.get_tile_env(tile) in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):`

The first builder should head toward Ti ore, not Ax. Raw Ax delivered to core is destroyed. If the nearest ore is Ax, the first builder walks toward useless ore, delays first Ti harvester.

**Fix:** Filter to Ti only.
```python
if c.get_tile_env(tile) == Environment.ORE_TITANIUM:
```

**Risk:** Very low. On maps with only Ax near core, the builder would use default direction instead of heading toward Ax. But Ax harvesters are already deprioritized (score += 50000), so the builder wouldn't build on it anyway.

**B. Second builder should also be biased.**
Currently only `units == 0` gets the ore direction. The second builder (`units == 1`) spawns in default DIRS order, potentially heading opposite from ore. On maps where ore is concentrated in one direction, the second builder wastes time exploring the wrong direction.

**Fix:** Extend bias to `units <= 1`.
```python
if units <= 1:  # first two builders
```

**Risk:** Low. If ore is in two directions, builder 1 and 2 both head the same way — but marker claiming prevents duplicate targeting.

---

## 2. Marker Claiming Range (lines 385-392)

### Current behavior:
- Places marker on target ore when `pos.distance_squared(self.target) > 2`
- Marker is placed within action radius (r^2=2), which requires being within ~1.4 tiles
- But `can_place_marker(target)` checks if the target is in action radius

Wait — `c.can_place_marker(pos)` requires pos to be within action radius of the builder (r^2=2). So the marker can only be placed when the builder is within ~1.4 tiles of the ore. The `> 2` check prevents placing when adjacent (which would block harvester build).

### Issue: Marker range is fine

The marker is placed when 2 < distance <= 2 (i.e., distance_squared > 2 AND within action radius r^2=2). That means... the marker is placed ONLY when distance_squared is exactly... wait.

`pos.distance_squared(self.target) > 2` means the builder is NOT on the ore tile or diagonally adjacent (distance_squared 1 or 2). But `can_place_marker` requires the target within action radius r^2=2. So the marker would need `distance_squared(target) <= 2` but the check requires `> 2`. **These conditions can never be simultaneously true!**

Actually wait — markers can be placed at any distance? Let me re-check. From CLAUDE.md: "Markers: 1 per round, no cooldown cost." From docs: "Building is completely free and doesn't consume action cooldown." And from _types.py, markers are placed via `c.place_marker(pos, value)` and `c.can_place_marker(pos)`.

Let me check the action radius for markers.

<Actually from the CLAUDE.md: "Markers: 1 per round, no cooldown cost" — but no range restriction mentioned. The `can_place_marker` might check vision range, not action radius.>

Let me check _types.py:

```python
def can_place_marker(self, position: Position) -> bool:
    """Return True if this unit can place a marker at position."""
```

No range specified in the stub. Let me check if markers have a range limit.

From my earlier docs fetch: "A tile containing a single unsigned 32-bit integer that can be read by any allied unit." And "Maximum one marker per round."

**Key question:** What is the marker placement range? If it's vision range (r^2=20 for builders), then the `> 2` check just prevents adjacent placement. If it's action radius (r^2=2), then the `> 2` check makes markers unplaceable.

Let me test empirically.

Actually, re-reading the code: the marker IS being placed successfully (we saw it work in earlier testing — ore claiming functions). So `can_place_marker` must allow placement beyond r^2=2. It's likely vision range.

**Conclusion:** Marker claiming range is fine. The `> 2` check correctly prevents placing markers on adjacent ore (which would block harvester placement). Markers are placed from vision range.

**No change needed.**

---

## 3. Bridge Threshold (line 452)

### Current behavior:
```python
bridge_threshold = bc + 10 if map_mode == "tight" else bc + 20
```
- Tight maps: need bridge_cost + 10 Ti to build a bridge
- Other maps: need bridge_cost + 20 Ti

Bridge base cost is 20 Ti. So:
- Tight: need 30 Ti to build a bridge
- Other: need 40 Ti

### Analysis:
The reserve (10 or 20 Ti) ensures the builder has leftover Ti for conveyors after the bridge. On tight maps, the lower reserve allows more aggressive bridging. On larger maps, the higher reserve prevents overspending on bridges when the builder needs Ti for longer chains.

### Potential optimization:
The bridge is used as a FALLBACK when conveyors and roads fail (stuck at walls). Making it cheaper to trigger would help on wall-heavy maps. But bridge costs 20 Ti + 10% scale — each unnecessary bridge is expensive.

**Issue:** The reserve is AFTER the bridge cost. If Ti = 35 and bridge costs 22 (with 110% scale), then `ti >= 22 + 20 = 42` fails. The builder won't bridge. If we lower to `bc + 10`, it would need 32 Ti — still fails at 35 Ti? No, 22 + 10 = 32 <= 35, so it succeeds.

**Potential fix:** Lower `bc + 20` to `bc + 10` for balanced maps.

**Risk:** Medium. More bridges = more scale inflation (+10% each). But if the builder is stuck at a wall, not bridging means it builds nothing and wastes rounds. A bridge that gets the builder to ore is worth the scale.

**Better fix:** Use `bc + 5` universally. If the builder is stuck (fallback), it's already wasted rounds. Getting it unstuck ASAP is worth the Ti.

---

## 4. Harvester Ti Reserve (line 333)

### Current behavior:
```python
if ti >= c.get_harvester_cost()[0] + 5:
```
Needs harvester cost + 5 Ti to build. The +5 is reserve for the next conveyor.

### Issue:
Harvester base cost is 20 Ti (at 100% scale). With +5 reserve, need 25 Ti. At 200% scale, harvester costs 40 Ti, need 45 Ti.

The reserve should scale with costs. At high scale, 5 Ti isn't enough for the next conveyor (which costs 6 Ti at 200% scale). But conveyors aren't always needed right after harvester — the bridge shortcut (lines 274-326) handles delivery.

**No change needed.** The +5 reserve is minor and the bridge shortcut handles the delivery.

---

## 5. Explore Ti Reserve (lines 523-528)

### Current behavior:
```python
if self._wall_density is not None and self._wall_density > 0.20:
    explore_reserve = 60
elif core_dist_sq > 50:
    explore_reserve = 30
else:
    explore_reserve = 5
```

Then `_nav` is called with this reserve. In conveyor mode, `ti >= cc + ti_reserve` must be true to build a conveyor. With explore_reserve=60, the builder needs 63+ Ti to build an exploration conveyor.

### Issue:
At high Ti (5000+), explore_reserve=60 doesn't suppress exploration conveyors. The builder happily builds conveyors at 63 Ti while hoarding 5000.

**Potential fix:** Scale explore_reserve with total Ti:
```python
if core_dist_sq > 50:
    explore_reserve = max(30, ti // 20)
```
At Ti=1000, reserve=50. At Ti=5000, reserve=250. This makes the builder increasingly reluctant to build exploration conveyors when rich.

**Risk:** Medium. If ore is far from core and the builder needs to explore, high reserve prevents it from building the conveyor chain to reach the ore. The builder gets stuck unable to build conveyors but unable to walk (no conveyors to walk on).

**Better approach:** Don't change reserve. Instead, limit exploration itself when scale is high.

---

## 6. Spawn Direction for Later Builders (lines 130-138)

### Current behavior:
After the first builder, all subsequent builders use default `DIRS` order (N, NE, E, SE, S, SW, W, NW). The spawn position doesn't consider where ore is or where existing builders already went.

### Issue:
Multiple builders spawn in the same direction and compete for the same ore. On maps with ore in 2+ directions, later builders should be sent to different sectors.

**Fix:** Alternate spawn direction by builder count.
```python
if best_ore_dir:
    spawn_dirs = [best_ore_dir] + [d for d in DIRS if d != best_ore_dir]
elif units > 0:
    # Alternate direction for subsequent builders
    spawn_dirs = DIRS[units % len(DIRS):] + DIRS[:units % len(DIRS)]
else:
    spawn_dirs = DIRS
```

**Risk:** Low. Worst case: builder spawns on a different core tile and walks 1 tile further. Best case: builder heads toward unexplored ore immediately.

But actually, the exploration system (sector-based, line 488-501) already sends different builders to different sectors using `mid * 7 + explore_idx * 3`. So even if they spawn in the same direction, they'll explore different sectors. The spawn direction just affects the first 2-3 moves.

**Impact:** Marginal. ~1 round saved per builder at most.

---

## 7. Builder Cap: econ_cap Formula (line 108)

### Current behavior:
```python
econ_cap = max(time_floor, vis_harv * 3 + 4)
```
`vis_harv` is harvesters visible from core (r^2=36). `vis_harv * 3 + 4` means: for each visible harvester, allow 3 more builders (plus 4 base).

### Issue:
With 3 visible harvesters: econ_cap = max(time_floor, 13). This allows 13 builders for 3 harvesters. That's WAY too many. MergeConflict uses 2 builders for 7 harvesters.

The `vis_harv * 3` multiplier is the root of our overbuilding problem. But changing it has been tried and likely failed (it's been tuned many times per the version history).

**Potential fix:** `vis_harv * 2 + 3` instead of `vis_harv * 3 + 4`.
- 0 harvesters: cap 3 (same)
- 3 harvesters: cap 9 (was 13)
- 5 harvesters: cap 13 (was 19)

**Risk:** Medium. On large maps, fewer builders = slower exploration = less ore found. The econ_cap is already gated by the time_floor caps (8 on tight, 12 on balanced, 15 on expand).

---

## Ranked Recommendations

| # | Change | Lines | Risk | Expected Impact |
|---|--------|-------|------|-----------------|
| 1 | Filter first builder to Ti-only ore | 123 | Very low | +0.5% (avoids Ax-direction first builder) |
| 2 | Extend ore bias to second builder | 120 | Low | +0.5% (faster second harvester) |
| 3 | Lower bridge threshold to bc+5 universally | 452 | Low-Medium | +1% (faster wall crossing) |
| 4 | Tighten econ_cap: vis_harv*2+3 | 108 | Medium | +1-2% (fewer wasted builders) |
| 5 | Lower explore_reserve for far builders | 526 | Medium | +0.5% (debatable) |
| 6 | Alternate spawn direction by count | 133 | Very low | +0.2% (marginal) |

**Total potential: +3-5%** if all apply. Enough to push from 74% to 76-78% on local test suite. Whether it translates to ladder improvement is uncertain — local bots are weaker than ladder opponents.

### Safest bundle to test:
Changes 1 + 2 + 3 (3 lines changed, very low risk). Test 50-match to verify >= 66%.
