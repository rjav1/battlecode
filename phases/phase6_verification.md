# Phase 6 Economy Fix - Verification Report

## Critic Claim C1: Chain self-terminates after 1-2 conveyors because builder finds its own conveyor
Verdict: **CONFIRMED**
Evidence: Traced through the code step-by-step starting at `main.py:127-174`.

1. Round N: Builder at tile X, builds harvester at adjacent tile Y (line 119). Sets `chain_target = core_pos` (line 123). Returns.
2. Round N+1: Builder still at X. Action cooldown > 0 from harvester build. Falls to movement at line 159. Moves toward core. `chain_steps=1`.
3. Round N+2: Builder at tile X'. Action cooldown now 0. Checks `get_tile_building_id(X')` at line 136 -- tile is empty (or has a road). If empty, builds conveyor at X' facing toward core (line 155). `chain_steps=2`. Returns WITHOUT moving.
4. Round N+3: Builder STILL at X' (it returned after building, never moved). Line 136: `get_tile_building_id(X')` finds the conveyor it just built. Line 139: type is CONVEYOR. Line 143: `existing_dir == d_to_core` is TRUE (it just built it that way). Sets `chain_target = None`. **Chain abandoned after 1 conveyor.**

This is a real, critical bug. The builder interprets its own freshly-built conveyor as an "existing chain" and stops. Every chain will be exactly 1 conveyor long (or 0 if the first tile had a road).

Action needed: **Yes -- the builder must either (a) move off the tile after building before re-entering the chain logic, or (b) track which tile it last built on and skip the existing-conveyor check for that tile.**

---

## Critic Claim C2: Chain direction is backwards (conveyors should face away from core)
Verdict: **FALSE ALARM (critic self-corrected)**
Evidence: The critic initially raised this as a concern, then re-analyzed and retracted it. The code at line 149 computes `d_to_core = pos.direction_to(self.core_pos)` and builds the conveyor facing that direction. Per CLAUDE.md: "Conveyor outputs in facing direction, accepts from 3 non-output sides." A conveyor facing toward core outputs toward core and accepts from the harvester side (behind). This IS the correct direction for resource flow from harvester to core.

The critic correctly identified this is NOT a bug. Verified.

Action needed: **No.**

---

## Critic Claim C3: Chain is only 1-2 conveyors long (confirming C1)
Verdict: **CONFIRMED (same root cause as C1)**
Evidence: This is the same bug as C1. The critic's step-by-step trace is slightly off in some details (e.g., the critic says "chain_steps=1" after just moving in round N+1, and then the conveyor is built in round N+2 making chain_steps=2 before termination in N+3), but the conclusion is correct: the chain terminates prematurely because the builder checks `get_tile_building_id(pos)` on a tile where it just built a conveyor.

The critic's suggested fix (add `last_built_pos` variable) is reasonable.

Action needed: **Yes -- same fix as C1.**

---

## Critic Claim H1: Builder alternates build/move, wasting a round each cycle
Verdict: **PARTIALLY CORRECT**
Evidence: Looking at the code flow at lines 147-174: after `c.build_conveyor(pos, d_to_core)` at line 155, the builder `return`s at line 157. Next round, action cooldown > 0, so it can't build. It falls to the move section at line 159. If move cooldown is 0, it moves. This is a 2-round cycle per conveyor tile (build, then move). However, this is inherent to the game mechanics -- building uses action cooldown, and you can only do one action per turn. The builder COULD potentially build and move in the same turn if action and move cooldowns are independent, but the code does `return` after building (line 157), which prevents trying to move in the same turn.

Looking more carefully: `c.get_action_cooldown()` and `c.get_move_cooldown()` are separate. The code returns after building (line 157) even though it might still be able to move (move cooldown could be 0). This IS wasteful -- the builder could build the conveyor AND move toward core in the same turn.

However, this is a secondary concern since C1/C3 prevents chains from being built at all. The build/move interleaving would only matter once the chain termination bug is fixed.

Action needed: **Yes, but low priority -- after fixing C1/C3, remove the early `return` after building a conveyor and fall through to the move section.**

---

## Critic Claim H2: `_best_adj_ore` prefers ore closest to core (suboptimal heuristic)
Verdict: **PARTIALLY CORRECT (design choice, not a bug)**
Evidence: Code at lines 358-366 iterates all `Direction` values (including CENTRE), picks the adjacent ore tile with minimum `distance_squared(self.core_pos)`. The critic notes:

1. Ore closest to core might not be best. TRUE but this is a heuristic, not a bug. Shorter chains are cheaper.
2. `Direction.CENTRE` is iterated, so `pos.add(Direction.CENTRE)` = `pos` itself. The critic says `can_build_harvester(pos)` should reject this since the builder is on the tile. Looking at the API: `can_build_harvester(pos)` checks if the tile is valid for a harvester. A builder bot is a unit, not a building. Per game rules, the check is for ore tile + no existing building. The builder bot being on the tile might not prevent building -- but `can_build_harvester` likely checks `is_tile_empty(pos)` which per the API means "No building and not wall." Since the builder is a unit, not a building, `is_tile_empty` could return True. However, building a harvester on the tile the builder is standing on would trap the builder (harvester is not walkable). In practice, `can_build_harvester` almost certainly prevents this (the engine would check), but it's an edge case worth noting.

Action needed: **No -- the heuristic is reasonable. The CENTRE iteration is wasteful but harmless since the engine's `can_build_harvester` handles it.**

---

## Critic Claim H3: Roads block conveyor chain building (chain has gaps)
Verdict: **CONFIRMED**
Evidence: At line 154, `c.can_build_conveyor(pos, d_to_core)` returns False if the tile already has a building (road is a building). The builder would skip the build and fall through to the move section at line 159. The chain would have a gap where the road exists. Resources cannot flow through roads -- only through conveyors. The builder does NOT call `c.destroy(pos)` to remove the road before placing a conveyor.

Per CLAUDE.md, `c.destroy(pos)` removes an allied building within action radius with no cooldown cost. The builder COULD destroy the road and build a conveyor in its place, but the code doesn't do this.

However, I need to check: does `c.destroy` use action cooldown? CLAUDE.md says "Remove allied building within action radius (no cooldown cost, repeatable)." So `destroy` has NO cooldown cost. But `build_conveyor` DOES use action cooldown. So the builder could destroy the road (free) and build a conveyor (uses action) in the same turn, if action cooldown is 0.

But wait -- there's a subtlety. After building, the builder returns (line 157). Next turn, it's on a tile with its new conveyor, and C1 kicks in (terminates the chain). So H3 is real but secondary to C1.

Also note: the builder only builds roads during `_nav` (exploration). When in chain-building mode (lines 127-174), the builder does NOT call `_nav`. It moves directly via `_bfs_step` or `direction_to`. So roads would only exist on tiles the builder previously explored -- which is actually the path it would take back toward core, since it explored outward from core. This makes H3 quite likely to occur.

Action needed: **Yes -- add `c.destroy(pos)` before building a conveyor when the tile has a road. But this fix only matters after C1/C3 is fixed.**

---

## Critic Claim H4: First conveyor's input side might not face the harvester
Verdict: **PARTIALLY CORRECT**
Evidence: After building the harvester at `ore` (an adjacent tile), the builder is at `pos`. The first conveyor is built at the builder's position facing toward core. For the harvester's output to reach this conveyor, the harvester must be on one of the conveyor's 3 input sides (any side except the output side, which faces toward core).

The output side of the first conveyor faces toward core. The harvester is adjacent to the builder (one tile away). The question is: is the harvester on the core-facing side of the builder? If so, the harvester would be on the output side, and resources couldn't flow in.

`_best_adj_ore` picks the ore tile closest to core. So the harvester tends to be placed BETWEEN the builder and core. In that case, the first conveyor (at the builder's position, facing toward core) has its output side facing toward core -- and the harvester is on that same side. The conveyor would NOT accept from the harvester because the harvester is on the output side.

Wait -- but the harvester is on a tile adjacent to the builder. The conveyor's output direction points toward core. If the harvester is on the core-side of the builder, the harvester IS on the output side. Conveyors only accept from the 3 NON-output sides. So resources from the harvester would NOT enter the conveyor.

However, `_best_adj_ore` picks the ore closest to core, but that doesn't mean the ore is between the builder and core. The ore could be closest to core but to the side. It depends on the geometry. But in many cases, the ore closest to core IS in the core direction from the builder, making this a real issue.

Counterpoint: harvesters don't output in a specific direction -- per CLAUDE.md, harvesters just "output 1 stack every 4 rounds." The output goes... where? The CLAUDE.md doesn't specify a direction for harvesters. Looking at the API: `c.build_harvester(pos)` has no direction parameter. So harvesters might output to all adjacent tiles, or to any adjacent conveyor. If harvesters output to any adjacent conveyor regardless of direction, then this isn't a bug -- the conveyor just needs to be adjacent.

Actually, looking at the transport rules more carefully: the resource distribution happens "at end of round" and resources move in stacks. The game engine likely handles harvester output by finding adjacent buildings that can accept resources. A conveyor accepts from 3 non-output sides. So the question is: does the engine check if the harvester is on an input side of the conveyor? Almost certainly yes -- the conveyor only accepts from its 3 non-output sides.

Verdict: This is a real concern but depends on the specific geometry. When the ore is in the direction of core (which `_best_adj_ore` favors), the first conveyor's output side faces the harvester, blocking resource intake. When the ore is to the side, it works fine.

Action needed: **Yes, but complex. After building a harvester, the builder should position itself so the first conveyor's input side faces the harvester. Or, the first conveyor should face AWAY from the harvester (toward core on the opposite side).**

---

## Critic Claim H5: Deferred military timing (sentinel 300, attacker 700) may be too late
Verdict: **PARTIALLY CORRECT**
Evidence: The test results show 4-4 record. On maps where buzzing loses (cold, corridors, settlement, arena), starter builds significantly more buildings. But the build results analysis says "0 mined" for ALL games -- neither bot mines successfully. The wins/losses are determined by remaining Ti, not military outcomes.

Looking at the test results more carefully:
- `settlement`: starter has 217 Ti vs buzzing 2790 Ti, but starter wins with 1014 buildings. This suggests starter won on a tiebreaker (delivered resources? harvester count?) despite having less remaining Ti.
- The tiebreaker order per CLAUDE.md: refined Ax delivered -> Ti delivered -> living harvesters -> stored Ax -> stored Ti.

Since neither bot delivers resources successfully (0 mined), the tiebreak goes to living harvesters. Starter's 1014 buildings likely include more harvesters. Buzzing's 422 buildings include fewer. So starter wins the harvester count tiebreak.

The military timing isn't the issue here -- the losses are due to the harvester/conveyor chain not working (C1/C3 bug), not lack of defense. However, once the chain is fixed, military timing may become important.

Action needed: **No immediate action. Revisit after fixing C1/C3.**

---

## Critic Claim M1: BFS limited to vision radius
Verdict: **FALSE ALARM**
Evidence: The critic acknowledges this is "not a bug, just a limitation" and notes the `direction_to` fallback handles beyond-vision navigation. The BFS at lines 368-387 uses the `passable` set from `get_nearby_tiles()` which is vision-limited. This is standard and expected behavior. The fallback at line 166 (`pos.direction_to(self.core_pos)`) handles long-distance navigation.

Action needed: **No.**

---

## Critic Claim M2: Roads have only 5 HP, fragile against enemy attack
Verdict: **FALSE ALARM (acceptable tradeoff)**
Evidence: The critic acknowledges this is "acceptable tradeoff for economy." Roads cost 1 Ti vs conveyors at 3 Ti. Roads are used for exploration paths, not critical infrastructure. The cost savings (+0.5% scale vs +1%) are significant when building many tiles during exploration. Enemy builders attacking roads is a theoretical concern but unlikely to be the primary issue.

Action needed: **No.**

---

## Critic Claim M3: Builder doesn't check position relative to harvester when starting chain
Verdict: **FALSE ALARM**
Evidence: The critic notes this is "LOW" severity and says "Edge case that doesn't actually occur given current code flow." I agree -- `_best_adj_ore` returns an adjacent tile (not the builder's own tile), so the builder is never on the harvester tile when starting the chain.

Action needed: **No.**

---

## Critic Claim M4: `_nav` builds roads on NEXT tile, taking 2 turns per tile
Verdict: **FALSE ALARM (not a bug)**
Evidence: At lines 307-318, the builder builds a road on `nxt` (the tile it wants to move to) and returns. The critic says this takes 2 turns, but looking more carefully: the builder builds the road (line 314, uses action cooldown) and returns. Next turn, action cooldown > 0 but MOVE cooldown could be 0. At line 316, it checks `c.get_move_cooldown() == 0 and c.can_move(d)`. If the road was built on `nxt`, `can_move(d)` should now return True (road is walkable). So it moves in 1 turn.

Wait -- the code does `return` at line 315 after building the road. Next turn, it re-enters `_nav`, iterates `dirs` again, and at line 316 tries to move. This should work -- 2 turns total (build road, then move) is correct and unavoidable since building uses the action turn.

However, there IS an optimization: the code could try to move AFTER building the road in the same turn (action and move cooldowns are separate). But the code returns after building. This wastes the move opportunity. The critic correctly identifies the 2-turn pattern but marks it MEDIUM, which is fair.

Action needed: **No immediate action -- minor optimization, not a bug.**

---

## Critic Claim L1: `chain_steps` counts both build and move actions
Verdict: **CONFIRMED (but low impact)**
Evidence: Lines 156 and 163 both increment `chain_steps`. The 20-step limit means at most ~10 conveyors (alternating build/move). But given C1/C3, chains never exceed 1-2 steps anyway. Once C1/C3 is fixed, this could limit chain length unnecessarily on large maps.

Action needed: **Low priority -- consider only counting build actions toward the limit, or increasing the limit.**

---

## Critic Claim L2: `_attack` uses fragile mirror selection
Verdict: **PARTIALLY CORRECT**
Evidence: At lines 282-297, `_attack` recomputes mirror positions and matches them against `enemy_dir` using `direction_to`. The `direction_to` function returns the nearest 45-degree direction, which could be imprecise for cores near the center of the map. However, `_get_enemy_direction` at lines 230-259 already detects symmetry correctly and caches the result. The attack method's re-matching is redundant but generally correct. Edge cases exist (e.g., perfectly centered map where direction_to returns CENTRE), but the fallback to `mirrors[0]` (rotational) handles this.

Action needed: **No immediate action.**

---

## Critic Claim L3: Explore index collision between builders
Verdict: **FALSE ALARM**
Evidence: The critic notes `my_id * 3` could cause collisions. But `my_id` values are sequential integers assigned by the game engine. The explore index is `(id * 3 + explore_idx + round // 200) % 8`. For sequential IDs, this provides reasonable spread. Not a real concern.

Action needed: **No.**

---

## Critic's Test Results Analysis
Verdict: **MOSTLY CORRECT**
Evidence: The "0 mined" observation across all games is the most important finding and is directly explained by C1/C3 -- chains are 1 conveyor long, so resources never reach the core. The wins are purely from conserving Ti (building fewer structures). The losses are from tiebreakers on harvester count.

The critic's recommendation order (fix C1/C3 first, then H3, then H4) is sound.

---

## Summary

| Claim | Verdict | Action |
|-------|---------|--------|
| C1: Chain self-terminates (builder finds own conveyor) | **CONFIRMED** | **FIX IMMEDIATELY** |
| C2: Chain direction backwards | **FALSE ALARM** (critic self-corrected) | No |
| C3: Chain only 1-2 conveyors (same as C1) | **CONFIRMED** | Same fix as C1 |
| H1: Build/move alternation wastes rounds | **PARTIALLY CORRECT** | Low priority optimization |
| H2: `_best_adj_ore` heuristic suboptimal | **PARTIALLY CORRECT** (design choice) | No |
| H3: Roads block conveyor placement in chain | **CONFIRMED** | Fix after C1 |
| H4: First conveyor input may not face harvester | **PARTIALLY CORRECT** | Fix after C1 |
| H5: Deferred military too late | **PARTIALLY CORRECT** | Revisit after C1 fix |
| M1: BFS limited to vision | **FALSE ALARM** | No |
| M2: Roads fragile (5 HP) | **FALSE ALARM** (acceptable tradeoff) | No |
| M3: Builder position check at chain start | **FALSE ALARM** | No |
| M4: `_nav` 2-turn-per-tile pattern | **FALSE ALARM** (not a bug) | No |
| L1: chain_steps double-counts | **CONFIRMED** (low impact) | Low priority |
| L2: Attack mirror selection fragile | **PARTIALLY CORRECT** | No |
| L3: Explore index collisions | **FALSE ALARM** | No |

## Priority Fix List

1. **C1/C3 (CRITICAL):** After building a conveyor, the builder must move before re-checking for existing conveyors. Simplest fix: after `c.build_conveyor()` at line 155, fall through to the move section instead of returning. Or add a `last_built_pos` variable and skip the existing-conveyor check (lines 136-146) when `pos == last_built_pos`.

2. **H3 (HIGH):** Before building a conveyor at line 154, check if the tile has a road. If so, `c.destroy(pos)` first (free, no cooldown), then build the conveyor.

3. **H4 (HIGH):** After building a harvester, ensure the first conveyor's input side faces the harvester. Consider: instead of `_best_adj_ore` picking ore closest to core, pick ore that is NOT in the `direction_to(core)` from the builder, so the harvester is on an input side of the first conveyor.

4. **L1 (LOW):** Only count build actions toward `chain_steps`, not move actions.
