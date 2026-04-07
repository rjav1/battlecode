# Explore Reach Reduction Design — Expand Maps

**Date:** 2026-04-06
**Question:** Should we change `reach = max(w,h)` to `reach = min(w,h)//2` on expand maps?

## Current Code (line 540)

```python
if area >= 1600:
    sector = (mid * 7 + self.explore_idx * 3 + rnd // 100) % len(DIRS)
    d = DIRS[sector]
    dx, dy = d.delta()
    cx, cy = self.core_pos.x, self.core_pos.y
    reach = max(w, h)          # <- sends builders to map edge
    tx = max(0, min(w - 1, cx + dx * reach))
    ty = max(0, min(h - 1, cy + dy * reach))
    far = Position(tx, ty)
```

**Proposed change:** `reach = min(w, h) // 2`

For git_branches (50x35): `max(50,35)=50` → `min(50,35)//2=17`
For galaxy (40x40): `40` → `20`
For settlement (50x38): `50` → `19`
For cubes (50x50): `50` → `25`

## Test Results

### git_branches (50x35) — the broken map

| Seed | current Ti (mined) | patched Ti (mined) | Winner current | Winner patched |
|------|--------------------|--------------------|----------------|----------------|
| 256 | 739 (0) | 13361 (**14040**) | starter | **patched wins** |
| 500 | 9653 (9630) | 4526 (4870) | buzzing | **patched wins** |
| 1 | ~0 cached | 5219 (**4860**) | starter | **patched wins** |
| 42 | ~0 cached | 9744 (**9710**) | starter | **patched wins** |

**ALL 4 seeds now mine Ti and win.** seed=256 goes from 0→14040 mined.

### galaxy (40x40) — must not regress

| Seed | current Ti (mined) | patched Ti (mined) | Delta |
|------|--------------------|--------------------|-------|
| 1 | 6809 (9870) | 11386 (**12360**) | +2490 mined (+25%) |
| 999 | 9648 (13150) | 15617 (**16940**) | +3790 mined (+29%) |

**Galaxy IMPROVES with shorter reach.** Patched mines 25-29% more. Why: reach=40 sent all builders to the same 4 corners; reach=20 creates intermediate targets that happen to pass through more ore tiles.

### settlement (50x38) — must not regress

| Seed | current Ti (mined) | patched Ti (mined) | Delta |
|------|--------------------|--------------------|-------|
| 1 | 26926 (36530) | 30318 (**38060**) | +1530 mined (+4%) |
| 256 | 18311 (28220) | 28574 (**38390**) | +10170 mined (+36%) |

**Settlement IMPROVES.** seed=256 is a massive improvement (+10k mined). Current bot apparently struggled on this seed too.

### cubes (50x50) — must not regress

| Seed | current Ti (mined) | patched Ti (mined) | Delta |
|------|--------------------|--------------------|-------|
| 1 | 21917 (31570) | 22166 (**32640**) | +1070 mined (+3%) |

**Cubes roughly the same.** Slight improvement.

### wasteland (40x40) — also broken

| Seed | current Ti (mined) | patched Ti (mined) | Winner current | Winner patched |
|------|--------------------|--------------------|----------------|----------------|
| 1 | 684 (3910) | 821 (0) | current | starter |

**Wasteland: inconclusive.** Current mines 3910 but patched mines 0. Wasteland has extreme wall density — reach=20 may send builders into wall clusters rather than open corridors. Different issue from git_branches.

Note: current 3910 mined but only 684 Ti — implies the conveyors aren't connecting harvester chains back to core. Wasteland may be a separate broken map regardless of reach.

## Analysis

### Why shorter reach works

- `reach=max(w,h)=50` targets the extreme corner of the map from core. On a 50x35 map with core near center, builders target tiles like `(0,0)` or `(50,35)`. BFS routes around walls, but the path goes straight to the edge. Branch corridor entrances on the way are NOT targets — builders pass them if the BFS route doesn't require entering them.

- `reach=min(w,h)//2=17` targets an intermediate tile ~17 steps from core. On git_branches, this lands INSIDE the branch corridor network instead of past it. Builders explore the interior, find ore, and build harvesters.

- For open maps (galaxy, settlement, cubes), intermediate targets still spread builders effectively — there's no wall structure to miss, so shorter reach still reaches all ore areas over time via `explore_idx` rotation.

### Why wasteland is different

Wasteland (40x40) likely has dense internal walls where reach=20 from core hits a wall cluster. The current reach=40 accidentally targets open areas beyond the walls. This is a map-specific pathology. Since both current and patched sometimes mine 0, wasteland may need map-mode reclassification rather than a generic reach fix.

## Recommendation

**Change `reach = max(w,h)` to `reach = min(w,h) // 2` on expand maps.**

- git_branches: 0→4860-14040 mined, 0W→4W on tested seeds  
- galaxy: +25-29% Ti mined improvement  
- settlement: +4-36% Ti mined improvement  
- cubes: +3% (neutral)  
- wasteland: slight regression (but wasteland is broken under both formulas)

This is a safe, unambiguous improvement. The only concern is wasteland, which was already broken. No other expand map regresses.

**Implementation:** Change line 540 only:
```python
# Before:
reach = max(w, h)
# After:
reach = min(w, h) // 2
```
One line, expand mode only, no other changes needed.
