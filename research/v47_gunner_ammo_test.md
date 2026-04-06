# V47 Gunner Ammo Delivery Test

**Date:** 2026-04-06
**Question:** Does V47's gunner ammo delivery work — do gunners fire?

---

## Match Results

### Test 1: buzzing vs rusher, face, seed 1
- **Winner:** rusher (Resources tiebreak, round 2000)
- buzzing: 2348 Ti (510 mined), 8 units, 32 buildings
- rusher: 7438 Ti (9930 mined), 10 units, 225 buildings
- No core destruction (survived to 2000)

### Test 2: buzzing vs rusher, arena, seed 1
- **Winner:** rusher (Resources tiebreak, round 2000)
- buzzing: 3007 Ti (1170 mined), 8 units, 27 buildings
- rusher: 3419 Ti (4970 mined), 10 units, 344 buildings
- No core destruction (survived to 2000)

### Test 3: buzzing vs ladder_rush, face, seed 1
- **Winner:** buzzing (Resources tiebreak, round 2000)
- buzzing: 17388 Ti (13780 mined), 8 units, 100 buildings
- ladder_rush: 6570 Ti (4980 mined), 20 units, 148 buildings
- No core destruction (survived to 2000)

### Test 4: buzzing vs ladder_rush, shish_kebab, seed 1
- **Winner:** buzzing (Resources tiebreak, round 2000)
- buzzing: 10176 Ti (7160 mined), 8 units, 71 buildings
- ladder_rush: 781 Ti (0 mined), 20 units, 148 buildings
- No core destruction (survived to 2000)

---

## Code Analysis

### _pending_gunner_ammo logic (main.py:65, 595–613, 643)

The gunner placement is a 2-turn sequence handled by `_place_gunner`:

**Turn N:** Builder builds gunner facing enemy direction, stores `(gunner_pos, facing_dir)` in `self._pending_gunner_ammo`.

**Turn N+1:** Builder detects `_pending_gunner_ammo != None`, tries to build a conveyor on an adjacent tile of the gunner (any non-facing side), with the conveyor facing toward the gunner (`d.opposite()`). Condition: builder must be within `distance_sq <= 2` of the chosen conveyor tile.

### Critical Issues Found

**Issue 1: Conveyor direction is wrong — won't feed ammo.**
The code builds a conveyor at `gp.add(d)` facing `d.opposite()` (toward the gunner). According to the game rules, a conveyor "outputs in its facing direction." So this conveyor would output INTO the gunner's tile — this part is correct.

However, the conveyor needs to *receive* Ti from somewhere. There is no second conveyor connecting this to the Ti supply chain. The lone ammo conveyor is isolated — it can only hold what's on it already, which is nothing. The gunner will never receive ammo.

**Issue 2: The conveyor is not connected to the resource chain.**
Building one conveyor adjacent to the gunner does nothing unless that conveyor is connected to a Ti source (another conveyor carrying Ti, or the core). In practice the builder places one orphan conveyor on a random adjacent tile with no upstream supply.

**Issue 3: `_pending_gunner_ammo` cleared even on failure.**
At line 598, `self._pending_gunner_ammo = None` is set before attempting to build. If all attempts fail (no buildable tile within range), the state is cleared and no retry happens next turn.

**Issue 4: Ammo detection is absent.**
`_gunner` at line 160 checks `c.get_ammo_amount() < 2` correctly, but since no ammo ever arrives, the check always fails and the gunner never fires.

### Verification: Do Gunners Actually Fire?

**Almost certainly not.** The ammo conveyor placed by `_place_gunner` is:
1. Orphaned (not connected to any Ti supply)
2. Only one tile deep (can hold one stack, but never receives one)

The gunner logic at lines 161–165 requires `ammo_amount >= 2` before firing. Since no Ti reaches the gunner, `ammo_amount` stays 0. Gunners are built but never fire.

This is confirmed indirectly by the match stats: in tests vs rusher (a strong economy bot), buzzing achieves only 510–1170 Ti mined despite surviving to round 2000 — no gunner damage is contributing to defense or forcing resource denial.

---

## Conclusion

**Gunners do NOT fire in V47.** The ammo delivery code places a single isolated conveyor adjacent to the gunner with no upstream supply. The fix requires connecting the ammo conveyor to the existing Ti conveyor chain (e.g., routing a branch from the nearest production conveyor to the gunner's input side). Until then, the `_place_gunner` feature costs Ti (10 Ti per gunner) and scale without any combat benefit.

**Recommendation:** Either fix ammo delivery to route from a known Ti source, or remove the gunner placement code entirely to save Ti and scale for the economy.
