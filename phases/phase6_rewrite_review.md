# Phase 6 Rewrite - Critic Review

## Summary Verdict

The rewrite is a **massive improvement**. The d.opposite() conveyor pattern fundamentally solves the chain-building problem. Ti mined went from 0 to 4,950-26,980 per game. The 8-0 sweep against starter is real -- resources are flowing. The code is cleaner, shorter (~310 lines vs ~400), and eliminates the broken chain state machine from the prior version.

That said, there are several issues that will hurt performance at higher Elo, plus one potential correctness bug.

---

## Verification of Prior Critical Bugs

### Previously identified: Chain self-termination (C1/C3 from prior review)
**STATUS: FIXED.** There is no chain state machine at all. No `chain_target`, no `chain_steps`, no early termination. The d.opposite() approach builds conveyors as the builder walks, so the chain is the trail itself. No self-termination possible.

### Previously identified: Roads blocking conveyor placement (H3)
**STATUS: PARTIALLY FIXED.** Roads are no longer built during ore-targeting navigation (`_nav_conveyor` builds conveyors, not roads). However, `_nav_conveyor` has a road fallback at lines 196-204 which COULD build roads when conveyors fail (e.g., tile already has a building). These roads are in the middle of a conveyor trail, creating gaps. See M1 below.

More importantly, `_nav_explore` now calls `_nav_conveyor` (line 214), so exploration ALSO builds conveyors. The docstring at line 9 says "Separate explore nav (roads) vs ore nav (conveyors)" but this is misleading -- both use `_nav_conveyor`. There is no separate road-only exploration path.

### Previously identified: First conveyor not facing harvester (H4)
**STATUS: FIXED BY DESIGN.** The d.opposite() pattern means the conveyor trail leads FROM core TO harvester. The last conveyor placed before the harvester is the one adjacent to the harvester. Its direction is `d.opposite()` where `d` was the direction the builder moved from that tile to the harvester's tile. So it faces back toward core, and the harvester is on the output side... wait.

Let me trace this carefully. The conveyor's direction is its OUTPUT direction. If the builder moves EAST (toward ore), it builds a conveyor at the next tile facing WEST (d.opposite()). This conveyor outputs WEST (toward core) and accepts from EAST, NORTH, SOUTH. The harvester is EAST of this conveyor -- but the OUTPUT side is WEST. EAST is one of the three input sides. 

Actually no -- the conveyor is built at `nxt = pos.add(d)` (line 166), facing `d.opposite()`. The builder is at `pos`, moving toward `nxt` in direction `d`. The conveyor at `nxt` faces `d.opposite()` (back toward `pos`). The harvester will be built later, BEYOND `nxt`, further along direction `d`. So the harvester is on the side `d` of the conveyor, which is the OPPOSITE of the output direction (`d.opposite()`). The output is toward `d.opposite()` (back toward core). The input sides are the other 3, which includes direction `d` (where the harvester is). **This is correct -- the harvester feeds into the input side.**

But wait -- the conveyor is built BEFORE the harvester. The builder builds a conveyor at `nxt`, then next turn moves onto `nxt`, then walks further. When the builder reaches ore and builds a harvester at the adjacent tile, the conveyor it built one step back will accept from the harvester's direction (input side). BUT -- there may be additional tiles between the last conveyor and the harvester. The builder walks: build conveyor at step N, move to step N, build conveyor at step N+1, move to step N+1, ..., find ore at step N+K, build harvester. The chain of conveyors from core to harvester should be continuous if the builder built a conveyor at every step.

**But the builder builds at `nxt` (ahead of it), then returns without moving.** Next turn, it tries to move. But the conveyor at `nxt` is walkable, so `can_move(d)` should return True. It moves there. Then next turn, it builds another conveyor at the next `nxt`. This means: build, move, build, move -- alternating. The chain should be continuous with a conveyor every tile.

**STATUS: CORRECT.** Chain topology is: Core <- conv <- conv <- conv <- ... <- conv <- harvester. Each conveyor outputs toward core. Harvester feeds into the last conveyor's input side.

### Ti mined > 0
**STATUS: CONFIRMED.** All 8 maps show 4,950-26,980 Ti mined. Resources are flowing.

---

## Issues Found

### CRITICAL Issues

None found. The core logic is correct.

### HIGH Issues

#### H1: Exploration also builds conveyors -- massive cost scaling waste

**Lines 207-214:**
```python
def _nav_explore(self, c, pos, passable):
    """Explore outward, laying conveyors to maintain trail back to core."""
    idx = ((self.my_id or 0) * 3 + self.explore_idx
           + c.get_current_round() // 150) % len(DIRS)
    d = DIRS[idx]
    dx, dy = d.delta()
    target = Position(pos.x + dx * 20, pos.y + dy * 20)
    self._nav_conveyor(c, pos, target, passable)
```

Exploration calls `_nav_conveyor`, which builds conveyors at +1% scale each. When a builder explores in a direction with no ore, it leaves a long conveyor trail to nowhere. This is wasteful because:
1. Each conveyor costs 3 Ti + 1% scale increase
2. Building counts: 117-459 buildings across test maps, many of which are exploration conveyors that never carry resources
3. Scale increases make ALL future buildings more expensive

The docstring (line 9) claims "Separate explore nav (roads) vs ore nav (conveyors)" but the code doesn't actually do this. Both use `_nav_conveyor`.

**Counter-argument:** The builder noted this is intentional because "harvesters are often found during exploration." If a builder explores in a random direction and finds ore, the trail IS useful. But many trails lead nowhere.

**Severity: HIGH** -- At higher Elo where cost scaling matters more, the excess conveyors will hurt. Consider using roads for exploration (much cheaper at 1 Ti, +0.5% scale) and only switching to conveyors when ore is spotted. The original design doc mentioned this separation.

#### H2: Conveyors built AHEAD of builder create a move-then-build race condition

**Lines 165-177:**
```python
for d in dirs:
    nxt = pos.add(d)
    if c.get_action_cooldown() == 0:
        ti = c.get_global_resources()[0]
        cc = c.get_conveyor_cost()[0]
        if ti >= cc + 10:
            face = d.opposite()
            if c.can_build_conveyor(nxt, face):
                c.build_conveyor(nxt, face)
                return
    if c.get_move_cooldown() == 0 and c.can_move(d):
        c.move(d)
        return
```

The builder tries to build a conveyor at `nxt` first. If it can't (tile occupied, no resources), it tries to move instead. If it moves onto a tile that has NO conveyor/road, the chain has a gap.

But `can_move(d)` requires the target tile to be passable (conveyor, road, or allied core). So if the tile ahead has no walkable surface, the builder can't move there either. The builder is stuck.

In practice, this means the builder builds a conveyor, returns, then moves onto it next turn. The alternating build/move pattern means each tile costs 2 turns. This is inherent to the design and not a bug, but it's worth noting for optimization: the builder could try to build AND move in the same turn if both cooldowns allow.

Actually, after `c.build_conveyor(nxt, ...)`, the action cooldown goes to 1, so the builder can't do another action. But `c.get_move_cooldown()` might still be 0. The builder could move after building if it doesn't return. Currently it returns immediately after building (line 174).

**Severity: HIGH** -- Could potentially double the chain-building speed by doing build + move in the same turn (if move cooldown allows after a build action).

#### H3: Attacker builds conveyors toward enemy -- feeding resources to opponent

**Lines 250-263:**
```python
def _attack(self, c, pos, passable):
    ...
    enemy_pos = self._get_enemy_core_pos(c)
    if enemy_pos:
        self._nav_conveyor(c, pos, enemy_pos, passable)
```

The attacker navigates toward the enemy core using `_nav_conveyor`, which builds conveyors facing `d.opposite()` (back toward our core). This creates a conveyor trail from our base toward the enemy. From CLAUDE.md: "Resources CAN be sent to enemy buildings via misplaced conveyors."

Actually, the conveyors face back toward our core (d.opposite()), so they would carry resources FROM the enemy direction TOWARD our core. The risk is if enemy harvesters or conveyors connect to our trail. But more practically, this is just wasting Ti and scale on conveyors that serve no economic purpose.

**Severity: MEDIUM** -- Not actively dangerous (direction is toward our core, not enemy), but wasteful. Attackers should use roads, not conveyors.

### MEDIUM Issues

#### M1: Road fallback in _nav_conveyor creates chain gaps

**Lines 196-204:**
```python
# Road fallback
if c.get_action_cooldown() == 0:
    ti = c.get_global_resources()[0]
    rc = c.get_road_cost()[0]
    if ti >= rc + 5:
        for d in dirs:
            if c.can_build_road(pos.add(d)):
                c.build_road(pos.add(d))
                return
```

When the conveyor build fails (tile occupied, insufficient Ti for conveyor, etc.) but road is affordable, the builder builds a road instead. This creates a gap in the conveyor chain -- resources can't flow through roads.

In practice, this likely happens rarely since conveyor build failure usually means the tile already has a building. But when it does happen, the chain is broken.

**Severity: MEDIUM** -- Rare but can silently break chains.

#### M2: No road-destroying when conveyors are needed on road tiles

The old code had roads during exploration. The new code builds conveyors everywhere (no separate exploration road mode). But the road fallback (M1) can still place roads. If a builder later needs a conveyor on that tile, `can_build_conveyor` returns False because the road occupies it. The builder can't destroy the road either -- `destroy` requires the builder to be within action radius (r^2 = 2), which is adjacent.

The builder COULD destroy the road if it's on the tile or adjacent. But there's no code to check for and destroy roads before placing conveyors.

**Severity: MEDIUM** -- Edge case from M1 compounding.

#### M3: BFS explores only visible tiles (vision r^2 = 20)

**Lines 286-305:** The `_bfs_step` function searches `passable`, which is built from `c.get_nearby_tiles()` (vision radius). For builders, vision r^2 = 20, so BFS only explores ~4.5 tiles in any direction. Beyond that, BFS returns the best local direction and falls back to `direction_to` (line 162-163 rank order).

This means on maps with walls that require detours beyond vision range, the builder will try to walk straight into the wall, get stuck (stuck counter reaches 15), and change explore direction. This works eventually but is slow.

**Severity: MEDIUM** -- Inherent limitation, not a bug. The stuck detection handles it.

#### M4: `_best_adj_ore` iterates over all `Direction` including CENTRE

**Line 268:**
```python
for d in Direction:
```

This includes `Direction.CENTRE`, which checks `pos.add(Direction.CENTRE)` = `pos` itself. `can_build_harvester(pos)` would return False (builder is on the tile). Harmless but wasteful.

**Severity: LOW**

### LOW Issues

#### L1: Docstring claims separate explore/ore navigation but code doesn't implement it

**Line 9:** "Separate explore nav (roads) vs ore nav (conveyors) to reduce waste"

But `_nav_explore` (line 214) calls `_nav_conveyor`. There is no road-only exploration path. The docstring is misleading.

**Severity: LOW** -- Documentation issue, not a code bug.

#### L2: Sentinel count check uses `get_nearby_buildings` which only sees within vision

**Lines 227-233:**
```python
for eid in c.get_nearby_buildings():
    try:
        if (c.get_entity_type(eid) == EntityType.SENTINEL
                and c.get_team(eid) == c.get_team()):
            sent_count += 1
```

This counts sentinels within vision (r^2 = 20 for builders). If sentinels are placed outside vision range, the builder won't count them and may build more than 3 total. The cap is local, not global.

**Severity: LOW** -- Sentinels are placed near core (distance_squared <= 25 check at line 117), so they should be visible to builders near core. Unlikely to exceed 3 in practice.

#### L3: Enemy core position fallback uses mirrors[0] without validation

**Line 353:**
```python
return mirrors[0]
```

If no mirror direction matches `enemy_dir`, it falls back to rotational symmetry. This could be wrong if the map uses horizontal/vertical reflection. However, `_get_enemy_direction` caches a specific direction, and if none of the mirror positions produce that exact direction (due to floating-point rounding in `direction_to`), the fallback fires. This is unlikely but possible on maps where the core is near the center.

**Severity: LOW**

---

## Test Results Analysis

### Resource Flow Confirmed
- Ti mined ranges from 4,950 (battlebot) to 26,980 (default_medium1)
- Starter mined 0 on ALL maps -- our bot has a decisive economic advantage
- Average 15,451 Ti mined vs 0 for starter

### Building Count Analysis
- buzzing: 117-459 buildings
- starter: 211-924 buildings
- buzzing builds fewer structures despite also building conveyors
- The d.opposite() pattern is more efficient than starter's random conveyors

### Map-by-Map Notes
- **default_medium1**: Best performance (26,980 mined, 29,041 total Ti). Open map favors long conveyor trails.
- **battlebot**: Lowest mining (4,950). Likely has walls that disrupt chains.
- **cold**: 8,030 mined despite 361 buildings. Cold has many walls -- chains may be fragmented.
- **settlement**: 14,760 mined, 459 buildings. Previously lost to starter. Now wins decisively.

### Mirror Match
- P1 wins with 14,700 vs 14,390 mined. Very close -- P1 advantage from acting first.
- Both players mine effectively, confirming the pattern works from either spawn.

---

## Recommended Improvements (Priority Order)

1. **Separate exploration roads from ore conveyors (H1):** Change `_nav_explore` to use a road-based navigation function. Only switch to `_nav_conveyor` when ore is visible (`self.target` is set). This would roughly halve building costs during exploration.

2. **Build + move in same turn (H2):** After building a conveyor, check if `get_move_cooldown() == 0` and try to move onto it in the same turn. This would nearly double chain-building speed.

3. **Use roads for attacker navigation (H3):** The attacker doesn't need conveyors toward the enemy. Use a road-based nav function.

4. **Remove road fallback in _nav_conveyor (M1):** If a conveyor can't be built, don't build a road -- just move. Or destroy the road and replace with a conveyor on the next visit.

5. **Fix docstring (L1):** Either implement the separation or update the docstring.

---

## Overall Assessment

**SHIP IT.** The rewrite solves the fundamental resource delivery problem. Going from 0 Ti mined to 15,000+ avg is transformative. The 8-0 sweep confirms this works across all map types. The identified issues (H1-H3, M1-M4) are optimizations for higher Elo, not blockers.

The d.opposite() insight -- building conveyors as you walk rather than retracing a path -- is elegant and robust. It avoids all the state-machine complexity and edge cases that broke the previous chain-building approach.
