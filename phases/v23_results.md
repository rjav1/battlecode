# v23 Results: Roads-First Nav + Deliberate Conveyor Chains

## Outcome: PARTIAL — roads-first chain building FAILED, attacker removal SHIPPED

The roads-first approach was attempted but the deliberate chain-building system could not be made to work reliably. Three chain-building strategies were tried and all produced 0 Ti mined on most maps:

1. **Build conveyor at NEXT tile (ahead of builder, toward core):** Failed because `can_build_conveyor(nxt, step)` succeeds but the conveyor facing was wrong — creating loops and disconnected chains.

2. **Build conveyor at PREVIOUS tile (behind builder):** Builder moved first, then built conveyor behind. But the builder couldn't move because the next tile had no road/conveyor. The chain-build logic consumed the action cooldown placing the conveyor behind, leaving no action to build a road ahead.

3. **Follow recorded outbound path backward:** The `fix_path` only captured 2-4 positions (not the full path from core) because road-building turns don't reach the `c.move()` code that records positions.

4. **Walk on roads toward core, replace with conveyors behind:** Builder oscillated between tiles because the conveyors it placed created walkable loops that the direction-to-core logic couldn't escape.

### Root Cause Analysis

The fundamental problem: **builders can't build conveyors under themselves** (occupied tile), so they must build at adjacent tiles. But the chain needs a continuous path of conveyors from harvester to core. During the return trip, the builder creates conveyors one step behind as it walks — but the return path through vision-limited BFS doesn't follow the exact outbound road trail, creating disconnected or looping conveyor chains.

The v15 approach (d.opposite() conveyors outbound + chain-fix on return) worked because the conveyor trail was built during the outbound trip and naturally followed the builder's path. Any approach that tries to build conveyors on the return trip inherently faces the path-tracking and tile-occupancy problems.

## What Was Shipped: Attacker Mode Removal

The only change that could be validated: removing the attacker mode (id%6==5 after round 500 with 4+ harvesters). This saves one builder from wasteful attack runs (2 damage/action vs 500 HP core, plus laying expensive conveyors along the attack path).

### vs Starter Results (all maps mine Ti > 0)

| Map | v23 mined | v22 mined | Change |
|-----|-----------|-----------|--------|
| default_medium1 | 30,110 | 13,230 | **+127%** |
| cold | 8,460 | 19,420 | **-56%** |
| corridors | 14,770 | ~15,000 | ~same |
| settlement | 19,650 | 17,540 | **+12%** |
| face | 24,220 | N/A | new map |

### Head-to-Head Regression (v23 vs v22, both positions)

| Map | v23 mined | v22 mined | Winner |
|-----|-----------|-----------|--------|
| default_medium1 | 18,580 | 33,930 | v22 |
| cold | 24,730 | 14,800 | v23 |
| corridors | 14,790 | 14,790 | Tie |
| settlement | 19,590 | 0 | v23 |
| face | 13,710 | 17,140 | v22 |
| hourglass | 10,830 | 19,380 | v22 |

**Score: v22 wins 3, v23 wins 2, 1 tie.** Does NOT meet the 4/6 requirement.

### Analysis

The attacker removal helps on maps where the extra economic builder is valuable (cold, settlement) but hurts on maps where it increases conveyor scale inflation (default_medium1, hourglass, face). Net effect is approximately neutral.

## Recommendation

Do NOT deploy v23 yet — it fails the regression requirement. The roads-first architecture change needs a fundamentally different approach to chain building. Possible alternatives:

1. **Marker-based coordination:** Use markers to signal harvester positions, then a dedicated chain-builder follows markers from core outward.
2. **Two-pass system:** First pass explores/finds ore using roads. Second pass builds a planned conveyor chain from core to each harvester using BFS pathfinding.
3. **Keep current architecture (conveyors everywhere) and optimize elsewhere:** The current d.opposite() conveyor approach works. Focus on other improvements like marker coordination, smarter builder caps, or bridge optimization.

## Files Modified

- `bots/buzzing/main.py` — attacker mode removed, dead code cleaned up
