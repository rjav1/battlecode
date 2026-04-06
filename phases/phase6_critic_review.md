# Phase 6 Economy Fix - Critic Review

## Summary Verdict

The fix correctly addresses the original problem (wasteful conveyor spam during exploration) by switching to roads. However, the conveyor chain-building logic has a **fatal flaw** that explains the "0 mined" results: **conveyors are built ON the builder's tile, not AHEAD of it**, meaning the builder is standing on the conveyor it just built and immediately returns (action used), but the chain never actually connects because the builder builds where it IS, not where it's GOING. More critically, there is a fundamental directionality problem.

---

## CRITICAL Issues

### C1: Conveyor chain builds on the builder's current tile -- but the builder is STANDING there

**Lines 148-157** (chain-building logic):
```python
# Build conveyor at current pos facing toward core, then move toward core
d_to_core = pos.direction_to(self.core_pos)
if d_to_core != Direction.CENTRE and c.get_action_cooldown() == 0:
    ti = c.get_global_resources()[0]
    cc = c.get_conveyor_cost()[0]
    if ti >= cc + 10:
        if c.can_build_conveyor(pos, d_to_core):
            c.build_conveyor(pos, d_to_core)
            self.chain_steps += 1
            return
```

The builder tries to build a conveyor at `pos` (its own tile). But `can_build_conveyor(pos, ...)` requires the tile to be empty (no existing building). The builder bot is a **unit**, not a building -- so the tile might be empty of buildings. However, there's a subtlety: the builder just built a harvester on the adjacent ore tile, so its current tile may or may not have a building.

The real problem: after building the conveyor at `pos`, the builder `return`s. Next round, when the builder runs again, it's still on the same tile (it didn't move). It enters the chain logic again, checks `get_tile_building_id(pos)` at line 137, finds its own conveyor, checks if it faces toward core (it does, since it just built it that way), and **sets `self.chain_target = None`** (line 143), abandoning the chain after placing just ONE conveyor.

**Severity: CRITICAL** -- This means every chain is exactly 1 conveyor long. It will never reach the core. This directly explains the "0 mined" result.

### C2: Chain direction is BACKWARDS -- conveyors should face AWAY from core, not toward it

**Lines 149, 154:**
```python
d_to_core = pos.direction_to(self.core_pos)
...
c.build_conveyor(pos, d_to_core)
```

The conveyor direction is its **output direction** (per CLAUDE.md: "outputs in facing direction"). The builder walks FROM the harvester TOWARD the core, placing conveyors facing toward core. This means each conveyor outputs toward core -- which IS correct for resource flow.

Wait -- actually, let me re-examine. The harvester outputs resources. The harvester has no explicit direction -- it "outputs 1 stack every 4 rounds." The docs say harvesters output, and conveyors accept from 3 non-output sides.

For a chain: Harvester -> Conveyor A -> Conveyor B -> Core

- Conveyor A must accept from the harvester's side and output toward Conveyor B / Core
- Conveyor A facing toward core: output side = toward core, accept sides = other 3 sides including the harvester side

Actually, this direction IS correct. If the builder is between the harvester and core, placing a conveyor facing toward core, that conveyor will accept resources from the harvester side (behind it) and output toward core. **The direction logic is actually correct.**

**Revised severity: NOT A BUG** -- The direction is correct. Conveyors facing toward core will chain resources from harvester to core properly IF the chain is complete.

### C3: The chain IS only 1 conveyor long due to premature termination (confirming C1)

Let me trace step-by-step:

1. Round N: Builder at tile X, adjacent to ore tile Y. Builds harvester at Y. Sets `chain_target = core_pos`, `chain_steps = 0`. Returns.
2. Round N+1: Builder still at tile X (didn't move, action cooldown > 0 from harvester build). Enters chain logic at line 128. `chain_steps=0 < 20`, `distance_squared(pos, core) > 2` (probably). Checks `get_tile_building_id(pos)` -- tile X has no building (the harvester is at Y, not X). Reaches line 147-154. Action cooldown is likely still > 0 from the harvester build. Falls to movement at line 159. Moves toward core. `chain_steps=1`. Returns.
3. Round N+2: Builder at tile X+1 (moved one step toward core). Enters chain logic. Checks `get_tile_building_id(pos)` -- this tile might have a road (from earlier exploration) or be empty. If empty: tries to build conveyor. If action cooldown is 0, builds conveyor facing toward core. `chain_steps=2`. Returns.
4. Round N+3: Builder still at tile X+1 (returned after building). Enters chain logic. Checks `get_tile_building_id(pos)` -- finds the conveyor it just built. Checks direction: `existing_dir == d_to_core`? Yes. **Sets `chain_target = None`**. Chain abandoned after 2 steps.

**Severity: CRITICAL** -- The chain will always be 1-2 conveyors long because the builder checks its OWN conveyor and thinks it found an existing chain. The fix: after building a conveyor, the builder should move FIRST before checking for existing conveyors, or skip the existing-conveyor check on the tile it just built.

---

## HIGH Issues

### H1: Builder builds conveyor on its own tile, then can't move off it next turn

After building a conveyor at `pos` (line 155), the builder returns. Next turn, it has action cooldown > 0. It enters chain logic, tries to move (line 159-170), which is fine since conveyors are walkable. But the issue is that the build-then-return pattern wastes a round each time. The builder alternates: build conveyor (return), move (return), build conveyor (return), move (return). This means chains build at half speed.

But given C3, the chain never gets past 2 steps anyway.

**Severity: HIGH** -- Even if C3 is fixed, the alternating build/move pattern doubles the time to build a chain.

### H2: `_best_adj_ore` prefers ore CLOSEST to core, which may not be optimal

**Lines 358-366:**
```python
def _best_adj_ore(self, c, pos):
    best, bd = None, 10 ** 9
    for d in Direction:
        p = pos.add(d)
        if c.can_build_harvester(p):
            dist = p.distance_squared(self.core_pos) if self.core_pos else 0
            if dist < bd:
                best, bd = p, dist
    return best
```

This picks the adjacent ore tile closest to core. But ore tiles far from core might be more valuable if they're in a cluster. Also, picking the closest-to-core ore means the chain is short but may miss better deposits.

More importantly: `Direction` includes `CENTRE`. `pos.add(Direction.CENTRE)` returns `pos` itself. If the builder is standing on an ore tile, it would try to build a harvester on its own tile. `can_build_harvester` should reject this (builder bot is on the tile), but it's worth noting.

**Severity: MEDIUM** -- Not a bug per se, but the heuristic could be improved. The CENTRE iteration is wasteful but harmless since `can_build_harvester` would return False.

### H3: Chain doesn't check if tiles already have buildings (non-conveyor)

**Line 154:**
```python
if c.can_build_conveyor(pos, d_to_core):
```

This check should handle it -- `can_build_conveyor` returns False if the tile already has a building. But what if the tile has a road? The builder walked there on a road from exploration. `can_build_conveyor` would return False because the road is already there.

In this case, the builder would skip the build and just move. But the chain would have a gap -- a road tile instead of a conveyor. Resources can't flow through roads, only through conveyors.

**Severity: HIGH** -- On paths where the builder previously built roads during exploration, the chain will have gaps where roads exist. The builder should `destroy` the road first, then build a conveyor. Currently it doesn't do this.

### H4: No conveyor chain from harvester to first conveyor

The chain starts at the builder's position after building the harvester. The harvester is adjacent to the builder. But the first conveyor in the chain is at the builder's current position -- which is 1 tile away from the harvester. How does the harvester's output reach the first conveyor?

Harvesters output resources. The docs say conveyors "accept from 3 non-output sides." For the first conveyor (facing toward core), one of its 3 input sides needs to be adjacent to the harvester. If the builder was between the harvester and the core, then the harvester is on the opposite-to-core side of the first conveyor, which IS one of the 3 input sides. So this works.

But if the builder was NOT between the harvester and core (e.g., the builder approached the ore from the side), the harvester might not be on an input side of the first conveyor.

**Severity: HIGH** -- The chain assumes the builder is between the harvester and core, but the builder could be anywhere relative to both. The first conveyor's input side might not face the harvester.

### H5: Deferred military timing may be too late

Sentinel timing pushed from 200 to 300, attacker activation from 400 to 700. On maps where enemies rush, this leaves the bot defenseless for 100+ extra rounds.

Test results show losses on `settlement` (starter builds 1014 buildings!) and `arena`. These maps may have shorter distances where enemy aggression arrives early.

**Severity: HIGH** -- The economy-first strategy works on large maps but may lose to rushes on small/medium maps.

---

## MEDIUM Issues

### M1: BFS in chain-building uses `passable` set which only includes visible tiles

**Line 160:**
```python
step_dir = self._bfs_step(pos, self.core_pos, passable)
```

The `passable` set is computed from `c.get_nearby_tiles()` which only returns tiles within vision radius (r^2 = 20, so ~4.5 tiles). If the core is far away, BFS will only explore locally and return the best local direction. This is fine for navigation but means the chain path may be suboptimal.

**Severity: MEDIUM** -- Not a bug, just a limitation. The fallback `direction_to` handles the beyond-vision case.

### M2: Roads have only 5 HP -- enemy builders can easily destroy road networks

Roads (5 HP) vs builder attack (2 damage, costs 2 Ti) means an enemy builder destroys a road in 3 attacks (6 Ti). If enemies send an attacker builder, the road network is fragile.

But conveyors (20 HP) would take 10 attacks. This is a tradeoff: roads are cheaper to build (1 Ti vs 3 Ti) but more fragile.

**Severity: MEDIUM** -- Acceptable tradeoff for economy, but worth noting for future defensive considerations.

### M3: Builder doesn't check if it's ON the harvester tile when starting chain

**Lines 122-124:**
```python
if self.core_pos:
    self.chain_target = self.core_pos
    self.chain_steps = 0
```

This sets chain_target regardless of the builder's position relative to the harvester. If the builder is ON the ore tile (built harvester at `pos.add(Direction.CENTRE)` -- unlikely since CENTRE is included but `can_build_harvester` checks for empty tile), the chain would start from the harvester tile. But `can_build_conveyor(pos, ...)` would fail because the harvester occupies the tile.

Actually, the builder builds the harvester at `ore` (an adjacent tile from `_best_adj_ore`), not at `pos`. So the builder is NOT on the harvester tile. But the builder's `pos` might not be between the harvester and core.

**Severity: LOW** -- Edge case that doesn't actually occur given current code flow.

### M4: `_nav` builds roads on the NEXT tile, not the current tile

**Lines 307-315:**
```python
for d in dirs:
    nxt = pos.add(d)
    if c.get_action_cooldown() == 0:
        ti = c.get_global_resources()[0]
        rc = c.get_road_cost()[0]
        if ti >= rc + 10:
            if c.can_build_road(nxt):
                c.build_road(nxt)
                return
```

The builder builds a road on `nxt` (the tile it wants to move to) and returns. Next turn, it can move onto the road. This is correct behavior but means each movement step takes 2 turns (build road, then move). This was the same pattern as before with conveyors -- the fix just made it cheaper.

**Severity: MEDIUM** -- Not a bug, but the 2-turn-per-tile exploration speed is inherently slow.

---

## LOW Issues

### L1: `chain_steps` counts both build and move actions

**Lines 156-157 and 163-164:**
```python
self.chain_steps += 1  # After building
...
self.chain_steps += 1  # After moving
```

The 20-step limit counts both building conveyors and moving as steps. So the effective chain length is at most 10 conveyors (alternating build/move). In practice, with C3, this never matters.

**Severity: LOW**

### L2: Unused `_enemy_dir` recomputation in `_attack`

**Lines 282-297:** The `_attack` method recomputes the mirror positions to find `enemy_pos`, but it already has `enemy_dir` from `_get_enemy_direction`. The mirror selection logic using direction comparison is fragile -- `direction_to` might not match exactly when the core is near map center.

**Severity: LOW** -- Could cause the attacker to go to the wrong position on near-center maps, but the attacker role is secondary.

### L3: Explore index wraps differently per builder

**Line 350-352:**
```python
idx = ((self.my_id or 0) * 3 + self.explore_idx
       + c.get_current_round() // 200) % len(DIRS)
```

Using `my_id * 3` means builders with IDs that differ by multiples of 8/3 might explore the same direction. Not a real issue since IDs are sequential integers.

**Severity: LOW**

---

## Test Results Analysis

### Wins (4): landscape, battlebot, default_medium1, face
- buzzing builds fewer structures (117-338 vs 229-525 for starter)
- Wins by having MORE remaining Ti (spending less on buildings)
- NOT winning by mining -- still "0 mined"

### Losses (4): cold, corridors, settlement, arena
- starter builds MORE buildings (385-1014) 
- On `settlement`, starter has only 217 Ti remaining vs buzzing's 2790, but starter has 1014 buildings. Starter likely won by tiebreaker on delivered resources (even if shown as 0) or harvester count
- The losses suggest starter's brute-force conveyor approach accidentally creates functional chains on some maps

### Key insight from results:
The "0 mined" across ALL games is damning. Neither bot successfully mines resources. The wins/losses are entirely determined by remaining Ti (who spent less on buildings) plus tiebreakers. This means the conveyor chain feature is completely non-functional for both bots.

---

## Recommendations (Priority Order)

1. **Fix C1/C3 FIRST**: The chain self-terminates after 1-2 conveyors. The builder must NOT check for existing conveyors on a tile it just built. Add a `last_built_pos` variable and skip the existing-conveyor check for that tile.

2. **Fix H3**: Destroy roads before building conveyors during chain-building. Add `c.destroy(pos)` before `c.build_conveyor(pos, ...)` when a road exists on the tile.

3. **Fix H4**: Ensure the first conveyor in the chain is positioned so its input side faces the harvester. After building the harvester, the builder should move to the tile between the harvester and core before starting the chain.

4. **Verify conveyor chain connectivity**: Add debug indicators (`draw_indicator_line`) to visualize the chain in replays. This would quickly confirm whether chains actually connect.

5. **Consider making chain-building smarter**: Instead of `direction_to(core)` for each conveyor, use BFS to find a complete path from harvester to core first, THEN build conveyors along that path. This avoids chains that run into walls.
