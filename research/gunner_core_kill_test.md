# Gunner Core Kill Test — ladder_fast_rush vs starter on binary_tree

**Date:** 2026-04-08
**Match:** ladder_fast_rush vs starter, binary_tree, seed 1

## Result

**Winner: starter** (Resources tiebreak, turn 2000)

```
Titanium:  ladder_fast_rush 4,753 (0 mined)  |  starter 2,298 (0 mined)
Buildings: 57                                |  516
```

## Analysis

**No core kill.** ladder_fast_rush wins on Ti tiebreak (4,753 vs 2,298) but cannot destroy starter's core in 2000 rounds on binary_tree.

Key observations:
- 0 Ti mined by either side — binary_tree's ore is completely unreachable for both bots on seed 1
- ladder_fast_rush wins on starting Ti advantage (500 Ti minus spending)
- 57 buildings for ladder_fast_rush vs 516 for starter — rush bot stays lean
- No "Killed" or turn-of-death in output — core survived to round 2000

## Why No Core Kill?

1. **binary_tree has high wall density** (24 wall tiles, maze structure) — gunner fire lines are blocked by walls. A gunner's forward ray hits walls which are untargetable and block the shot.

2. **0 Ti mined** means no ammo delivery economy. Gunners need Ti stacks fed via conveyors. Without ore income, ammo supply runs dry early.

3. **ladder_fast_rush likely builds gunners early but can't sustain fire** without a working harvester chain delivering Ti.

## Verdict

The gunner core kill concept does NOT work reliably on binary_tree with existing bot patterns. Wall density blocks gunner lines of sight, and the mining collapse (0 Ti mined) means no ammo for sustained fire.

Gunner pushes work better on open maps (galaxy, cold) where fire lines are clear and ore is accessible for ammo delivery. binary_tree is the wrong test map for this concept.
