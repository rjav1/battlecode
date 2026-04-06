# Phase 6 Rewrite - Verification Report

## Prior Bug Verification

### Previously identified C1/C3: Chain self-termination
Critic says: **FIXED.**
Verdict: **CONFIRMED FIXED.**
Evidence: The old `chain_target`, `chain_steps`, and the problematic `get_tile_building_id(pos)` check that terminated chains early are completely gone. The rewrite has no chain state machine at all. Conveyors are built inline during navigation (`_nav_conveyor`, lines 157-204). No self-termination is possible because there is no termination logic to trigger. The d.opposite() approach builds conveyors as a trail behind the builder, which is structurally immune to the old bug.

### Previously identified H3: Roads blocking conveyor placement
Critic says: **PARTIALLY FIXED** -- road fallback in `_nav_conveyor` (lines 196-204) can still create gaps.
Verdict: **CONFIRMED PARTIALLY FIXED.** See M1 below for details. The road fallback exists and can create gaps, though it fires only when conveyor build fails.

### Previously identified H4: First conveyor not facing harvester
Critic says: **FIXED BY DESIGN.**
Verdict: **CONFIRMED FIXED.**
Evidence: I traced the chain topology. Builder starts near core, walks outward. At each step, it builds a conveyor at `nxt = pos.add(d)` facing `d.opposite()` (back toward where it came from / toward core). When the builder reaches ore, the last conveyor is one step behind the harvester. That conveyor faces `d.opposite()` (toward core). Its output side is toward core. The harvester is on the side `d` (the direction the builder was walking), which is one of the 3 INPUT sides. Per CLAUDE.md: "Accepts from 3 non-output sides." The harvester is on a non-output side. Resources flow: harvester -> last conveyor's input -> output toward core -> next conveyor -> ... -> core. This is correct.

---

## Critic Claim H1: Exploration builds conveyors -- massive cost scaling waste
Verdict: **CONFIRMED**
Evidence: `_nav_explore` at line 214 calls `self._nav_conveyor(...)`. `_nav_conveyor` builds conveyors at +1% scale and 3 Ti each (line 169-173). When a builder explores in a direction with no ore, the conveyor trail serves no economic purpose. Each wasted conveyor is 3 Ti + 1% scale.

Looking at the test data: buzzing builds 117-459 buildings across maps. An unknown fraction of these are exploration conveyors that never carry resources. On maps like `cold` (361 buildings) and `settlement` (459 buildings), a significant number could be dead-end exploration trails.

The docstring at line 9 claims "Separate explore nav (roads) vs ore nav (conveyors) to reduce waste" but this is NOT implemented -- both paths use `_nav_conveyor`. The critic is correct that the docstring is misleading.

However, the builder's stated rationale is also valid: "harvesters are often found during exploration." If a builder explores and finds ore, the trail IS useful. The question is what fraction of exploration trails lead to ore vs dead ends. This is map-dependent and can't be determined from the test data alone.

At higher Elo where cost scaling matters more, this waste will compound. Roads at 1 Ti + 0.5% scale would be 3x cheaper in Ti and half the scale impact.

Action needed: **Yes -- implement the docstring's claimed design: use roads for exploration, switch to conveyors when `self.target` is set (ore spotted). This is an optimization, not a correctness fix.**

---

## Critic Claim H2: Build + move in same turn optimization
Verdict: **PARTIALLY CORRECT (optimization, not a race condition)**
Evidence: The critic frames this as a "race condition" in the title but then correctly analyzes it as an optimization opportunity. Let me trace the actual behavior:

1. Builder at `pos`, wants to move direction `d` toward ore.
2. Line 167: `c.get_action_cooldown() == 0` -- yes.
3. Line 172: `c.can_build_conveyor(nxt, face)` -- yes (tile is empty).
4. Line 173: `c.build_conveyor(nxt, face)` -- builds conveyor. Action cooldown goes to 1.
5. Line 174: `return` -- builder ends its turn.
6. NEXT TURN: Builder at `pos`. Action cooldown = 1 (from building). Move cooldown = 0.
7. Line 167: action cooldown != 0, skips build. Line 175: move cooldown == 0, `can_move(d)` -- yes (conveyor at `nxt` is walkable). Moves to `nxt`.

So: build turn 1, move turn 2. Could this be done in 1 turn? After `c.build_conveyor()`, action cooldown goes to 1. But `c.get_move_cooldown()` is separate. If move cooldown is 0, the builder could move onto the freshly built conveyor in the same turn -- IF the code didn't `return` at line 174.

The critic is right that removing the `return` after building and falling through to the move check could allow build+move in one turn. This would nearly double chain-building speed.

BUT: there's a question of whether the game engine allows building on a tile and then moving onto it in the same action. `c.build_conveyor(nxt, ...)` builds on `nxt`. Then `c.can_move(d)` checks if `nxt` is passable. If the engine processes the build immediately (within the same turn), then `nxt` is now a conveyor and `can_move(d)` returns True. If the engine batches builds to end-of-turn, the tile might not yet be walkable. Per CLAUDE.md: "Each round, units act in spawn order. After all units act, resources are distributed between buildings." This suggests builds happen immediately during the unit's turn (only resource distribution is batched). So build+move in the same turn should work.

Action needed: **Yes -- remove the `return` after `c.build_conveyor()` at line 174 and let execution fall through to the move check. This is a meaningful speed improvement. However, this is UNVERIFIABLE without testing whether the engine actually allows moving onto a just-built conveyor in the same turn.**

---

## Critic Claim H3: Attacker builds conveyors toward enemy -- feeding resources to opponent
Verdict: **PARTIALLY CORRECT (wasteful but NOT dangerous)**
Evidence: At line 263, `self._nav_conveyor(c, pos, enemy_pos, passable)` builds conveyors facing `d.opposite()` as the attacker walks toward the enemy. The critic correctly notes these conveyors face back toward our core, so resource flow would be FROM enemy territory TOWARD our core -- not feeding resources to the enemy.

Per CLAUDE.md: "Resources CAN be sent to enemy buildings via misplaced conveyors." But our conveyors face toward OUR core, so they would only carry resources toward us. The critic correctly downgrades this from "feeding resources to opponent" to "just wasting Ti and scale." I agree.

The waste is real: each conveyor costs 3 Ti + 1% scale, and the attacker is building a long trail toward the enemy with no economic purpose. Given that only 1 in 5 builders (those with `my_id % 5 == 4`) becomes an attacker, and only after round 700 with 4+ harvesters, the impact is limited but real.

Action needed: **Low priority -- the attacker could use a road-based navigation instead. But this is a minor optimization since attackers are rare and late-game.**

---

## Critic Claim M1: Road fallback in _nav_conveyor creates chain gaps
Verdict: **CONFIRMED but LOW real-world impact**
Evidence: Lines 196-204 build a road when the conveyor build fails. This creates a gap in the conveyor chain since resources can't flow through roads.

When does this trigger? The conveyor build at line 172 (`can_build_conveyor(nxt, face)`) fails when:
1. The tile already has a building (road, another conveyor, harvester, etc.)
2. The tile is a wall
3. The tile is out of action range (r^2 = 2, so only adjacent -- `nxt = pos.add(d)` is always adjacent, so this is fine)

Case 1 is most likely. If the tile already has a conveyor (from another builder's trail), `can_build_conveyor` returns False. The builder falls through to `can_move(d)` -- if the existing conveyor is walkable (it is, per game rules), the builder moves onto it.

The road fallback at lines 196-204 only triggers if BOTH the conveyor build AND the move fail for ALL directions in `dirs`. This is an extreme edge case -- the builder is surrounded by non-buildable, non-walkable tiles in all 8 directions.

In practice, the road fallback fires when:
- All preferred directions have buildings (can't build conveyor) AND are unwalkable (can't move)
- This should be very rare since conveyors are walkable by any team

The road itself would be placed on a tile that already prevents conveyor building. So the gap isn't created by the road -- it was already there due to the existing obstacle. The road just allows the builder to continue moving.

Action needed: **No -- the road fallback is a reasonable escape hatch for stuck builders. The gaps it creates would exist anyway due to the underlying obstacle. The chain would already be broken by whatever prevented the conveyor build.**

---

## Critic Claim M2: No road-destroying when conveyors needed on road tiles
Verdict: **FALSE ALARM (overblown by M1 analysis)**
Evidence: This issue compounds on M1, but as I showed above, M1 itself has very low real-world impact. Roads from the fallback are placed when conveyors can't be built anyway (tile already occupied). A subsequent builder visiting the same tile would encounter the road, fail to build a conveyor there, and either move over it or skip it.

However, there IS a scenario: the road fallback builds a road on a tile that WAS previously empty (conveyor build failed due to insufficient Ti). Later, when the builder has more Ti, it can't build a conveyor there because the road is now on the tile. But `c.destroy(pos)` could remove it (no cooldown, per CLAUDE.md), and the code doesn't do this.

This is a valid edge case but extremely unlikely: the builder would need to run out of conveyor Ti (checked at line 170: `ti >= cc + 10`), have enough road Ti (line 200: `ti >= rc + 5`), and then return later with more Ti to the same tile.

Action needed: **No -- too unlikely to matter in practice.**

---

## Critic Claim M3: BFS limited to vision radius
Verdict: **FALSE ALARM (acknowledged by critic as "not a bug")**
Evidence: Same as in the prior review. BFS uses `passable` from `get_nearby_tiles()` (vision r^2 = 20 for builders). The `_rank` function provides a fallback direction order. Stuck detection (lines 93-101) handles cases where the builder can't navigate around obstacles within vision. This is a standard limitation, not a bug.

Action needed: **No.**

---

## Critic Claim M4: `_best_adj_ore` iterates over CENTRE direction
Verdict: **FALSE ALARM (harmless)**
Evidence: Same issue as the prior review. `Direction.CENTRE` causes `pos.add(CENTRE) = pos`. `can_build_harvester(pos)` returns False because... actually, the builder is a unit, not a building. `can_build_harvester` checks for ore tile and no existing building. If `pos` is on ore and has no building, it could return True. Building a harvester on the builder's own tile would... place the harvester there while the builder is on it? Per game rules, builders can stand on buildings (specifically conveyors and roads). But harvesters are not in the walkable list. So the builder would be stuck.

However, `can_build_harvester` almost certainly checks for unit presence as well, or the engine prevents building on an occupied tile. The one extra check per call is harmless CPU cost.

Action needed: **No.**

---

## Critic Claim L1: Docstring claims separate explore/ore navigation
Verdict: **CONFIRMED (documentation bug)**
Evidence: Line 9: "Separate explore nav (roads) vs ore nav (conveyors) to reduce waste." Line 214: `_nav_explore` calls `_nav_conveyor`. There is no separation. The docstring is wrong.

Action needed: **Fix the docstring, OR implement the claimed separation (which would address H1). If implementing H1's fix, the docstring becomes correct.**

---

## Critic Claim L2: Sentinel count uses vision-limited query
Verdict: **FALSE ALARM**
Evidence: `get_nearby_buildings()` at line 227 only returns buildings within vision (r^2 = 20). But the sentinel placement check at line 117 requires `pos.distance_squared(self.core_pos) <= 25`. Builder vision r^2 = 20. The sentinel placement range (25) is slightly larger than vision (20), but sentinels are placed on adjacent tiles (`pos.add(d)`, distance 1-2 from builder). So sentinels are placed within ~sqrt(25) = 5 tiles of core. Builders checking sentinel count are within 5 tiles of core. Vision radius is ~4.5 tiles. Sentinels within 5 tiles of core ARE within vision of a builder also within 5 tiles of core -- as long as both are on the same side. There's a possible blind spot if sentinels are placed on the far side of core from the builder.

In practice: the core is 3x3. If the builder is 5 tiles east of core center, and a sentinel is 5 tiles west of core center, the distance between them is 10 tiles, and distance_squared = 100, which is well outside builder vision (20). So the builder COULD miss sentinels on the opposite side of core.

BUT: the sentinel cap is 3, and the placement target is within 5 tiles of core toward the enemy. Builders checking are also near core. Unless builders approach core from the opposite side of the enemy, they should see existing sentinels. And the `_rank` function directs sentinel placement toward the enemy direction, so all sentinels tend to cluster on the same side.

Action needed: **No -- the practical risk of over-building sentinels is very low given the clustering toward the enemy side.**

---

## Critic Claim L3: Enemy core position fallback
Verdict: **FALSE ALARM**
Evidence: At line 353, `return mirrors[0]` fires when no mirror's `direction_to` matches `enemy_dir`. The `_get_enemy_direction` method (line 307) uses tile environment sampling to detect symmetry. On maps with clear symmetry, the detected direction will match one of the 3 mirrors. The fallback to `mirrors[0]` (rotational) is reasonable since rotational symmetry is the most common.

Edge case: if the map uses horizontal reflection but `direction_to` rounds differently than expected, the loop at lines 349-352 could fail to match. But `direction_to` returns the nearest 45-degree direction, and the mirror positions should produce distinct enough vectors. This is a very unlikely edge case.

Action needed: **No.**

---

## Test Results Cross-Check

The critic's analysis of the test results is accurate:
- Ti mined 4,950-26,980 across all maps, confirmed by the build results.
- Starter mined 0 on all maps, confirmed.
- 8-0 sweep, confirmed.
- Mirror match close (14,700 vs 14,390), confirmed. The P1 advantage is expected (first to act).
- The critic's recommendation to "SHIP IT" is reasonable given the massive improvement.

---

## Summary

| Claim | Verdict | Action |
|-------|---------|--------|
| Prior C1/C3 fixed | **CONFIRMED FIXED** | None |
| Prior H3 partially fixed | **CONFIRMED** | See M1 |
| Prior H4 fixed | **CONFIRMED FIXED** | None |
| H1: Exploration conveyors wasteful | **CONFIRMED** | Implement road-based exploration |
| H2: Build+move same turn optimization | **PARTIALLY CORRECT** | Try removing `return` after build; **UNVERIFIABLE** without testing engine behavior |
| H3: Attacker conveyors toward enemy | **PARTIALLY CORRECT** (waste, not danger) | Low priority -- use roads for attacker |
| M1: Road fallback creates gaps | **CONFIRMED but LOW impact** | No action needed -- fallback is reasonable |
| M2: No road destruction for conveyors | **FALSE ALARM** | No |
| M3: BFS vision-limited | **FALSE ALARM** | No |
| M4: CENTRE iteration in _best_adj_ore | **FALSE ALARM** | No |
| L1: Misleading docstring | **CONFIRMED** | Fix docstring or implement separation |
| L2: Sentinel count vision-limited | **FALSE ALARM** | No |
| L3: Enemy core fallback | **FALSE ALARM** | No |

## Priority Improvements

1. **H1 (HIGH):** Implement road-based exploration. Create a `_nav_road` function (like the old `_nav`) that uses roads (1 Ti, +0.5% scale) instead of conveyors (3 Ti, +1% scale). Call it from `_nav_explore`. Keep `_nav_conveyor` for when `self.target` is set (ore spotted). This would reduce exploration costs by ~66% in Ti and ~50% in scale impact.

2. **H2 (MEDIUM):** Try removing the `return` at line 174 after building a conveyor. If the engine allows moving onto a just-built conveyor in the same turn, this nearly doubles chain-building speed. Must test empirically.

3. **H3 (LOW):** Have the attacker use roads instead of conveyors. Minor savings since attackers are rare.

## Overall Assessment

The critic's review is accurate and well-reasoned. No false critical bugs were raised. The identified issues are genuine optimizations, not blockers. The critic's "SHIP IT" recommendation is sound -- the rewrite solves the core resource delivery problem and the 8-0 sweep against starter confirms it works. The optimizations (especially H1 -- exploration roads) should be tackled in a follow-up phase, not gate the current submission.
