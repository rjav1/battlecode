# Chain Connectivity Truth: d.opposite() Analysis

## Executive Summary

**Three key findings:**

1. **Cardinal turns ARE connected.** When a builder walks E then N (or any cardinal-to-cardinal turn that isn't a 180-degree reversal), the d.opposite() conveyors connect correctly. The prior analysis in `constrained_maps_analysis.md` was wrong about this.

2. **Diagonal steps create gaps.** Conveyors can ONLY face cardinal directions (N/S/E/W) and ONLY transfer resources to/from cardinal neighbors. When the builder walks diagonally (NE, SE, SW, NW), `d.opposite()` produces a diagonal facing, `can_build_conveyor()` returns False, and NO conveyor is placed. This creates a gap in the chain.

3. **The prior "9,930 Ti on corridors" claim is outdated.** Current buzzing gets 14,790-18,410 Ti mined on corridors, not 9,930.

---

## Finding 1: Cardinal Turns Connect Perfectly

### Conveyor rules (from official docs):
- Conveyors face CARDINAL directions only (N, S, E, W)
- A conveyor OUTPUTS to its cardinal-facing neighbor
- A conveyor ACCEPTS from the 3 other cardinal neighbors
- Diagonal neighbors are NOT involved in resource transfer

### Proof that cardinal turns work:

When builder walks D1 (cardinal), placing D1.opposite()-facing conveyor at tile A, then walks D2 (cardinal, D2 != D1.opposite()), placing D2.opposite()-facing conveyor at tile B:

1. B = A.add(D2), so A = B.add(D2.opposite())
2. Conveyor at B outputs D2.opposite() -> reaches tile A (cardinal neighbor)
3. Conveyor at A accepts from {N,S,E,W} minus {D1.opposite()} = 3 directions including D2
4. Since D2 != D1.opposite(), tile A accepts the input. **CONNECTED.**

### Worked example: E->N->E->S corridor zigzag

```
(12,10) N-facing     (12,9) W-facing
    |                    ^
    v                    |
(11,10) W-facing <-- (11,9) S-facing
    ^
    |
  [from harvester or further chain]
```

- (12,10) faces N, outputs NORTH to (12,9). (12,9) faces W, accepts from N,E,S -- accepts from S. CONNECTED.
- (12,9) faces W, outputs WEST to (11,9). (11,9) faces S, accepts from N,E,W -- accepts from E. CONNECTED.
- (11,9) faces S, outputs SOUTH to (11,10). (11,10) faces W, accepts from N,E,S -- accepts from N. CONNECTED.

Every 90-degree cardinal turn works. The only break: 180-degree reversal (E then W), where the accepting conveyor's facing matches the incoming direction.

### Correction to constrained_maps_analysis.md

Line 59 claims: "The S-facing conveyor outputs SOUTH, but the next conveyor in the path is to the EAST. Complete disconnect."

This confuses builder walk order with resource flow direction. The S-facing conveyor outputs SOUTH to the tile below it, which contains the W-facing conveyor that accepts from N. **Connected.**

---

## Finding 2: Diagonal Steps Create Gaps (The REAL Bug)

### The mechanism:

1. Builder walks NORTHEAST (diagonal step)
2. `d.opposite()` = SOUTHWEST (a diagonal direction)
3. `can_build_conveyor(nxt, Direction.SOUTHWEST)` returns **False** (conveyors only face cardinal)
4. Builder moves diagonally but places NO conveyor
5. **Gap in chain** -- the diagonal tile has no conveyor

### Why this matters:

BFS pathfinding uses all 8 directions. On maps where diagonal shortcuts exist (most maps), BFS frequently chooses diagonal steps. Each diagonal step = a gap. A path with 3 diagonal steps out of 10 has 3 gaps -- resources can't flow through.

### Which maps are affected:

- **Open maps (arena, galaxy):** BFS finds mostly straight/diagonal paths. Diagonal steps are common but paths are short, so gaps may be few.
- **Corridor maps (corridors):** Walls force cardinal movement through corridors. Fewer diagonal steps. Chains connect better. This explains why corridors performance is actually decent (14K-18K Ti).
- **Diagonal-gap maps (shish_kebab):** Regions connected only by diagonal gaps. Builder MUST walk diagonally to cross. Every region crossing = a gap.
- **Cold:** Mixed paths. Some diagonal shortcuts around wall clusters create gaps.

### What happens at gaps:

At a gap (tile with no conveyor), the upstream conveyor outputs into empty space. Resources are lost. The chain is severed at every diagonal step.

---

## Finding 3: Current Performance Data

### corridors (31x31):

| Seed | Ti Mined | Total Ti | Buildings |
|------|----------|----------|-----------|
| default | 18,410 | 20,194 | 182 |
| 2 | 14,790 | 19,289 | 31 |
| 3 | 14,790 | 19,065 | 55 |

Much better than the old "9,930" claim. Corridors forces cardinal movement, so chains connect.

### cold (37x37):

| Seed | Ti Mined | Total Ti | Buildings |
|------|----------|----------|-----------|
| default | 17,820 | 12,914 | 583 |

17,820 Ti mined but only 12,914 total (some spent on buildings). High building count (583) suggests lots of conveyors placed.

### shish_kebab (20x20):

| Seed | Ti Mined | Total Ti | Buildings |
|------|----------|----------|-----------|
| default | 14,470 | 18,915 | 79 |

---

## The Real Bottlenecks (Ranked)

### 1. Diagonal step gaps (HIGH impact on diagonal-heavy maps)
Every diagonal BFS step = no conveyor placed = chain gap. Fix: decompose diagonal steps into two cardinal steps (NE -> N then E), or use roads for diagonal movement and only build conveyor chains on cardinal paths.

### 2. Scale inflation from long conveyor chains (MEDIUM impact)
Each conveyor adds +1% scale. A 30-conveyor chain adds +30% to all future costs. On corridors with 46-step paths, this is severe. Fix: use roads (0.5% scale) for exploration, conveyors only for harvester-to-core pipelines.

### 3. Builder time spent navigating (LOW-MEDIUM impact)
Each step takes 1-2 rounds (build + move). 30-step path = 30-60 rounds per harvester. With 2000 total rounds, this limits total harvesters.

### 4. 180-degree reversals (LOW impact, rare)
BFS never produces these. Only happens on target changes or stuck resets.

---

## Recommended Fix for Diagonal Gaps

In `_nav()`, when `d` is diagonal, decompose into two cardinal steps:

```python
if d in (Direction.NORTHEAST, Direction.SOUTHEAST, Direction.SOUTHWEST, Direction.NORTHWEST):
    # Decompose: try horizontal first, then vertical
    dx, dy = d.delta()
    horiz = Direction.EAST if dx > 0 else Direction.WEST
    vert = Direction.SOUTH if dy > 0 else Direction.NORTH
    # Try building conveyor on horizontal step first
    # Then on next round, build on vertical step
```

This doubles the steps (2 cardinal instead of 1 diagonal) but ensures every step gets a conveyor. Trade-off: slower movement but connected chains.

Alternative: Keep diagonal movement for speed but don't rely on the trail for resource delivery. Build dedicated cardinal-only conveyor chains after harvester placement.
