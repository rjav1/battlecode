# Core-Facing Conveyors: Would It Work?

## Date: 2026-04-08
## Idea: Build conveyors facing `direction_to(core)` instead of `d.opposite()`

---

## Current System: d.opposite()

Builder walks direction `d`, builds conveyor facing `d.opposite()`. Each conveyor points BACK to the tile the builder came from. Chain looks like:

```
Core at (10,10). Builder walks N then E (BFS around wall).
(10,9): conv facing S [d=N, opp=S] → outputs to (10,10)=core
(11,9): conv facing W [d=E, opp=W] → outputs to (10,9)=prev conv
```

Resources flow: (11,9) → (10,9) → core. Chain BENDS correctly. Each conveyor outputs to the previous one. Always connected.

## Proposed: direction_to(core)

All conveyors face toward core regardless of walk direction:

```
Core at (10,10). Builder walks N then E.
(10,9): conv facing S [dir_to_core=S] → outputs to (10,10)=core ✓
(11,9): conv facing S [dir_to_core=S] → outputs to (11,10)=EMPTY ✗
```

**CHAIN BREAKS.** The conveyor at (11,9) outputs SOUTH to (11,10), which is an empty tile. It doesn't connect to the conveyor at (10,9) or to core. Resources go nowhere.

## Why d.opposite() Is Correct

d.opposite() creates a LINKED LIST — each conveyor points to the previous one. The chain topology follows the builder's exact path. No matter how winding the BFS path, every conveyor outputs to a tile that has another conveyor (or core).

Core-facing creates PARALLEL LINES — all conveyors output in the same direction. Only conveyors in a straight line toward core connect. Any deviation from the straight line breaks the chain.

## What About Hybrid?

Use core-direction when it matches d.opposite() (straight line), and d.opposite() when the path turns.

```python
core_dir = pos.direction_to(self.core_pos)
face = core_dir if core_dir == d.opposite() else d.opposite()
```

This is literally: "use d.opposite() always, but call it core_dir when they happen to match." It produces identical behavior to d.opposite() in ALL cases. The hybrid adds complexity without changing any output.

## What About Always Facing One Cardinal Direction?

E.g., all conveyors face SOUTH on maps where core is south. This creates a grid of south-flowing conveyors. Any ore north of core feeds naturally.

Problem: builder walks on these conveyors (they're walkable). The builder walks NORTH (against resource flow). After building a harvester, the builder continues north. The conveyors below are already south-facing. Resources from the harvester flow south through them. **This actually works for straight-line paths.**

But: on maps where ore is EAST of core, south-facing conveyors don't deliver east-side resources to core. You'd need a mix of south and west conveyors, which is back to the direction problem.

## The Real Issue (Confirmed Again)

The chain direction (d.opposite()) is NOT the problem. Chains work correctly — resources flow from harvester to core through bending chains. The problem is:

1. **Too many exploration conveyors** — conveyors built when walking without an ore target
2. **Parallel chains** — multiple builders walking to the same area
3. **Too many builders** — each laying their own chain

These are QUANTITY problems, not DIRECTION problems. Changing the facing direction of conveyors doesn't reduce the number of conveyors built.

## Conclusion

**Core-facing conveyors would BREAK chains at every BFS turn.** d.opposite() is the correct algorithm — it creates connected chains regardless of path shape. No change needed.

The d.opposite() coupling (conveyors are both walkways AND chains) is not the bottleneck. The bottleneck is building conveyors during exploration when no ore target exists. We've tried suppressing these (ti_reserve) and hit the ceiling.

**d.opposite() is mathematically optimal for 1-pass chain building.** No alternative facing scheme can produce connected chains with fewer conveyors in a single pass.
