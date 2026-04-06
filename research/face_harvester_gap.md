# Face Map: 83-Round Harvester Gap Investigation

Date: 2026-04-06

## Map Layout

**Dimensions:** 20x20 (area=400) → classified as **tight** mode
**Core1:** (5,7), Core2: (14,7) (symmetric)
**Walls:** 38 tiles forming eyes (rows 2-3), nose (rows 8-11), mouth (rows 13-16)

```
 0: .......T....T.......   <- Ti at (7,0) and (12,0)
 1: .A................A.   <- Ax at (1,1) and (18,1)
 2: ...#####....#####...   <- eye walls
 3: ..#.....#..#.....#..
 4: ....................
 5: ....................
 6: ....................
 7: ....................   <- CORE at (5,7) and (14,7)
 8: .T.......##.......T.   <- Ti at (1,8) and (18,8)
 9: .........##.........   <- nose wall
10: .........##.........
11: ........####........
12: ....................
13: ....#..T....T..#....   <- Ti at (7,13) and (12,13)
14: ....#..........#....
15: .....##......##.....   <- mouth walls
16: .T.....######.....T.   <- Ti at (1,16) and (18,16)
17: ....................
18: .....A........A.....   <- Ax at (5,18) and (14,18)
19: ....................
```

**Ti ore distances from Core1 at (5,7):**
| Tile | d² from Core1 | Notes |
|------|---------------|-------|
| (1,8)  | 17 | Nearest — visible from core (r²=36) |
| (7,13) | 40 | Just outside core vision |
| (7,0)  | 53 | Far — never visible from core |
| (12,13)| 85 | Far |
| (1,16) | 97 | Far |
| (12,0) | 98 | Far |
| (18,8) | 170 | Enemy side |
| (18,16)| 250 | Enemy side |

---

## The 83-Round Gap: Root Cause Analysis

### Phase 1: 1st harvester (fast, rounds 1-~15)

Core spawns builder 1. Core vision (r²=36) sees (1,8) at d²=17. Builder 1 targets (1,8) immediately (visible from spawn area). Reaches it in ~10 steps, places harvester ~round 10-15.

### Phase 2: 2nd harvester (slow, rounds 15-~50)

(7,13) is the next nearest Ti at d²=40 — just **4 tiles outside core vision** (r²=36 = radius 6). Builders spawned at core cannot see it. They enter explore mode immediately.

**Explore directions from core area (5,7) for builders 2,3,4 at rounds 1-99 (rnd//100=0):**
- Builder 2 (id*3=6, idx=6): **WEST** → target (0,7) — passes near (1,8) already mined
- Builder 3 (id*3=9, idx=1): **NORTHEAST** → target (19,0) — passes near (7,0)!
- Builder 4 (id*3=12, idx=4): **SOUTH** → target (5,19) — away from (7,13)

Builder 3 going NE eventually walks into vision range of (7,13) as it travels (7,13) is roughly NE-ish from core). The 2nd harvester gets placed around round 30-50 depending on builder 3's path through the walls at rows 2-3.

### Phase 3: The 83-round gap (rounds ~50-133)

After the 2nd harvester at (7,13) is placed, **the builder at (7,13) cannot see any unclaimed Ti**:

| Tile | d² from (7,13) | In vision (r²=20)? |
|------|----------------|---------------------|
| (12,13) | 25 | NO — just outside (need r²=20, but 25>20) |
| (1,16)  | 45 | NO |
| (7,0)   | 169 | NO |
| (12,0)  | 194 | NO |

Builder vision r²=20 = radius ~4.5 tiles. The next ore tile (12,13) is 5 tiles east — just barely out of vision. The 3rd ore (7,0) is 13 tiles north — far out of vision.

**The builder at (7,13) enters explore mode. Its explore direction:**
```
tight explore: idx = (my_id * 3 + explore_idx + rnd // 100) % 8
```

At round 50, `rnd//100 = 0`, `explore_idx = 0`. Builder (say id=3) gets:
- idx = (3*3 + 0 + 0) % 8 = 1 → **NORTHEAST** → target (19+7, 0+13) = (19, 0)

Going NE from (7,13) — this passes nowhere near (7,0) which is due north.

**The other builders (2,4) explore WEST and SOUTH** — also away from the remaining ore cluster at rows 0 and 13.

### Why the gap lasts until round ~133

**Critical bug: `rnd // 100` changes only at round 100.**

All builders are locked into their `rnd//100=0` explore directions for the entire first 100 rounds. Their ID-based offsets spread them into 4 of 8 directions — and on face, none of those 4 directions efficiently cover the north-row ore at (7,0) from the post-harvester positions.

At round 100, `rnd//100` flips to 1, shifting all explore indices by +1. Builder 2 (which was going WEST) now goes **NW toward (0,0)**, passing near (7,0) in vision. This is when (7,0) gets discovered — approximately round 100-133 depending on when the builder actually traverses into vision range of (7,0).

The stuck detection (`stuck > 12` → `explore_idx += 1`) can also trigger direction changes, but only after the builder is stuck for 12 consecutive rounds. If no wall blocks the explore path, no stuck increment occurs.

---

## Three Contributing Factors

### Factor 1: Builder vision too small for scattered ore layout

Builder r²=20 (radius ~4.5) means a builder must be within 4-5 tiles of ore to target it.
On face, ore tiles are clustered in groups of 2 (symmetric pairs) spread across the map.
After the 2 nearest tiles are claimed, the remaining ore is 5-13 tiles away from any builder.
No builder is ever in vision range until it happens to wander past by chance.

### Factor 2: `rnd // 100` rotation is too slow for early exploration

The explore direction only rotates when `rnd // 100` increments — every 100 rounds.
In a 2000-round game, this gives only 20 direction changes. In the critical early-game
window (rounds 1-100), the direction is completely static per builder. If the initial
ID-based directions don't cover the map quadrant with remaining ore, no rotation occurs
until round 100 minimum.

**Compare with balanced explore:** `rnd // 50` rotates every 50 rounds — 2x faster.
Tight maps use 100 to avoid over-rotation, but this is too slow for face's scattered ore.

### Factor 3: Explore target is from BUILDER POSITION (not core)

In tight mode:
```python
far = Position(pos.x + dx * reach, pos.y + dy * reach)
```

As the builder moves, the explore target shifts with it. This creates a moving target
that stays 20 tiles ahead in the explore direction — so the builder never actually
reaches "the edge" of the map. It just keeps walking in a straight line.

However, this also means explore doesn't radiate from a fixed point. Two builders going
NORTHWEST and NORTHEAST can both be exploring "toward row 0" but from different x positions,
giving good coverage of the top of the map. The problem is which builders are assigned
these directions — and on face, the ID-based hashing sends too many builders south/east.

### Factor 4: `(12,13)` barely outside vision — near-miss

The ore at (12,13) is d²=25 from (7,13), needing r²=25 to see. Builder vision is r²=20.
A single-tile difference (r²=25 vs 20) means this ore is invisible from the adjacent
harvester site. If builder vision were r²=25 (not changeable), or if (12,13) were 1 tile
closer, it would be discovered immediately. This near-miss is a map-specific unlucky case.

---

## Quantifying the Gap

- 2nd harvester placed: ~round 30-50 (estimate)
- 3rd harvester placed: ~round 83+ after 2nd (as stated)
- Implicit 3rd harvester round: ~113-133

This represents ~83 rounds where 4+ builders are moving but finding no new ore.
At 10 Ti/4 rounds per harvester, a 83-round delay = ~208 Ti lost from the 3rd harvester.
With 8 harvesters total, each round of delay compounds.

---

## Potential Fixes

### Fix A: Faster explore rotation on tight maps (low risk)

Change tight explore rotation from `rnd // 100` to `rnd // 50`:
```python
# Current:
idx = (mid * 3 + self.explore_idx + rnd // 100) % len(DIRS)
# Fixed:
idx = (mid * 3 + self.explore_idx + rnd // 50) % len(DIRS)
```

This halves the direction-lock period. At round 50, builders would already rotate to
new directions, discovering the north-row ore ~50 rounds sooner.

**Risk:** May cause over-rotation on other tight maps where builders are already
efficiently covering the map. Need to test on cold, default_medium1.

### Fix B: Stuck threshold triggers faster rotation

Current stuck threshold: 12 rounds. If reduced to 6-8 rounds, builders that are
genuinely stuck in a direction would rotate to a new explore direction sooner.

**Risk:** Builders navigating long paths through walls will trigger stuck detection
prematurely and abandon working paths.

### Fix C: After placing harvester, explicitly scan wider for next ore

After `c.build_harvester(ore)`, the builder could immediately call `c.get_nearby_tiles()`
with a larger radius search by walking a few steps. But builder vision is fixed at r²=20 —
cannot be increased.

### Fix D: Core places markers on inferred ore positions (symmetry exploitation)

Face is symmetric. Core knows its own ore at (1,8). Symmetric counterpart would be
around (18,8) — enemy territory. But the other ore at (7,13) is 40 tiles from core
and known to exist (maps are guaranteed symmetric). 

The core could place markers on likely-ore positions derived from symmetry of already-
discovered ore. However, the core only has 1 marker per round and doesn't know the full
map layout — it only sees within r²=36.

### Fix E: Builder re-explores toward core after placing harvester (best fix)

When a builder places a harvester and has no visible ore, instead of exploring in a
fixed-hash direction, it should walk TOWARD CORE first. Walking toward core means it
passes through regions that OTHER builders haven't covered, and the core's vision r²=36
might reveal ore that the builder couldn't see from the harvester site.

```python
# After harvester build, if no ore in vision:
# Walk toward core until core is in vision, then pick nearest unvisited direction
if not ore_tiles and self.core_pos and pos.distance_squared(self.core_pos) > 36:
    self._nav(c, pos, self.core_pos, passable, use_roads=True)
    return
```

This would bring the builder back through the explored conveyor chain (already passable),
letting it scan the area between the harvester and the core, then re-dispatch.

---

## Summary

The 83-round gap on face has 4 compounding causes:

1. **Builder vision (r²=20) is too small** — next ore is 5+ tiles away at every point
2. **`rnd//100` rotate period is 100 rounds** — too slow for early-game on tight maps  
3. **ID-based hash distributes explorers AWAY from the remaining ore quadrant** — face's
   ore layout and builder ID assignment happen to point 3/4 builders south/east/west
4. **Ore at (12,13) d²=25 from (7,13)** — 1 tile outside builder vision radius

**Best fix:** Change tight explore rotation from `rnd//100` to `rnd//50` (Fix A).
Halves the lock-in period, costs nothing, likely applies to other tight maps too.
Secondary: consider a post-harvester "return to core" step (Fix E) for faster redispatch.
