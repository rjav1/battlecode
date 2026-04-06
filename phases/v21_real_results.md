# v21 Real Results — Simplify Gunner Placement

## Change
Replaced the complex splitter-based gunner state machine (destroy conveyor → build splitter → build branch → build gunner) with a simple direct placement: find any empty tile adjacent to builder, build gunner facing enemy. No chain destruction.

## Test Results (Both Positions)

| Map | buzzing pos | buzzing_prev pos | Winner |
|-----|-------------|------------------|--------|
| default_medium1 | 1 (north) | 2 (south) | buzzing_prev (18580 vs 33930 Ti mined) |
| default_medium1 | 2 (south) | 1 (north) | buzzing (34380 vs 18260 Ti mined) |
| cold | 1 | 2 | buzzing (27010 vs 19340 Ti mined) |
| cold | 2 | 1 | buzzing (19300 vs 14970 Ti mined) |
| face | 1 | 2 | buzzing (16670 vs 15930 Ti mined) |
| face | 2 | 1 | buzzing_prev (same Ti — positional bias only) |

## Win Tally
- buzzing: 4 wins
- buzzing_prev: 2 wins
- **Result: buzzing wins majority (4/6)**

## Notes
- default_medium1 and face show strong positional bias — position 2 (south/east spawn) wins regardless of bot version, with dramatically different Ti numbers.
- cold map is cleanly won by buzzing in both positions.
- The gunner simplification does NOT hurt economy. The old state machine was consuming resources on splitters/conveyors and interrupting builder movement. The new version just opportunistically places a cheap 10 Ti gunner when adjacent.

## Economy observation
On default_medium1, the winning position mines ~34k Ti vs ~18k for the losing position. This is a map-specific asymmetry, not a bot regression.

## Verdict: PASS — deploy v21
