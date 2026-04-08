# Sentinel Auto-Split — Face Regression Diagnostic

**Date:** 2026-04-08

## Test: V62 sentinel (harvesters>=3, no walk-back) — 50-match baseline

**Result: 31W-19L = 62%** — FAILS the 66% threshold.

This is -4pp from V61's 66% baseline. The sentinel auto-split at harvesters>=3 with no walk-back still regresses performance.

## Face Diagnostic

The face regression was specifically about `buzzing vs rusher face --seed 1`:

- V61 result: Winner=rusher, Ti mined: 340 (us) vs 9,940 (them), Buildings: 28 vs 268
- With sentinel>=3, no walk-back: same result — face mines only 340 Ti regardless

**Conclusion: The trigger timing and walk-back are NOT the face issue.**

Face is a unique map where we mine almost zero Ti (340 vs 9,940). This is a fundamental ore proximity / pathfinding issue on that specific map geometry — the sentinel feature doesn't affect it at all. The 340 Ti figure means our harvesters barely fire; we never reach 3 harvesters_built to trigger the sentinel anyway.

## Why 62% vs 66%?

The sentinel auto-split adds a sentinel (~30 Ti + 20% scale) and a conveyor (+1% scale) once per builder after the 3rd harvester. With 7 builders that's up to 7 sentinels — massive scale increase. Even with the no-walk-back guard, the cost of building 7 sentinels at later-game scale prices hurts economy enough to drop ~4pp.

The sentinel itself rarely fires (needs ammo delivered via conveyors) and the scale cost outweighs any defensive benefit.

## Verdict

Sentinel auto-split in any form (v4: trigger>=2, walk-back; refined: trigger>=3, no walk-back) does not improve on V61. The feature should be abandoned.

The face regression is a separate issue — it's a map-specific ore unreachability problem unrelated to sentinels.
