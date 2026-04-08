# Chain Audit: Diagonal Decomposition Fix

**Date:** 2026-04-08
**Hypothesis (from strategic_gap_final.md):** Our 19% delivery rate vs MergeConflict's 49% is caused by broken chains from diagonal BFS steps that place no conveyor.
**Fix tested:** In `_nav()` conveyor mode, decompose diagonal directions into two cardinal steps, each placing a conveyor.

---

## Result: 32W-18L = 64% — FAILS the 66% threshold (-2pp from V61)

---

## What the Fix Did

In `_nav()`, replaced the single diagonal step logic with:

```python
diag = d in (NORTHEAST, SOUTHEAST, SOUTHWEST, NORTHWEST)
if diag:
    dx, dy = d.delta()
    horiz = EAST if dx > 0 else WEST
    vert  = SOUTH if dy > 0 else NORTH
    card_dirs = [horiz, vert]
else:
    card_dirs = [d]
# then try building conveyor on each cd in card_dirs
```

This ensures diagonal moves still place a conveyor on a cardinal adjacent tile before moving.

---

## Per-Map Impact (vs starter, seed 1)

| Map | V61 Ti mined | V62 Ti mined | Delta |
|-----|:---:|:---:|:---:|
| gaussian | 19,830 | **23,180** | **+3,350 (+17%)** |
| galaxy | 9,950 | **14,160** | **+4,210 (+42%)** |
| cold | 19,670 | 19,630 | ~flat |
| default_medium1 | 14,500 | 4,960 | **-9,540 (-66%)** |

Galaxy and gaussian improved significantly. But default_medium1 collapsed by 66%.

---

## Why It Regressed on default_medium1

The cardinal decomposition places a conveyor on a cardinal tile adjacent to the diagonal target. This tile might be a different cell than where the builder was actually heading — it's a "side step" that builds an extra conveyor the builder doesn't move to. These side-step conveyors:

1. **Add +1% scale each** — extra conveyors inflate cost scaling
2. **May interfere with later builders** — a conveyor placed on a side-step tile can block another builder's path or misdirect resources
3. **Don't help on already-cardinal maps** — default_medium1 has few diagonal shortcuts, so the fix adds extra buildings without improving chains

The building count on default_medium1 went from 316 (V61) to 316 (same) but Ti mined collapsed — suggesting the extra side-step conveyors are misdirecting resource flow on that map's specific layout.

---

## Root Cause Analysis

The fix prevents diagonal chain gaps, but:
- The gain (better chains on galaxy/gaussian) is outweighed by the cost (extra buildings + scale inflation + possible flow misdirection)
- V61's 66% already accounts for chains that *sometimes* work even with diagonal steps — many paths are predominantly cardinal anyway
- The 19% delivery rate has multiple causes, not just diagonal gaps

From prior research (`v61_barrier_chainfix_removal.md`): the old `_fix_chain()` system was removed in V61 because it wasted 60-120 builder turns and the scale savings from removing it gained +4pp. This diagonal fix is a lighter version but still adds more buildings net.

---

## Conclusion

Diagonal decomposition: **FAILED. Reverted to V61.**

The chain audit / repair approach has now been tried in two forms:
1. **Old chain-fix (backtrack + rebuild):** Removed in V61, gained +4pp from removal
2. **Diagonal decomposition (place side-step conveyors):** -2pp, reverted

The 19% delivery rate problem cannot be solved by chain repair alone without a fundamental architectural change (planned chains from scratch rather than walk-path emergent chains). All repair approaches add building cost that exceeds the delivery benefit.

**V61 at 66% remains the ceiling for the current architecture.**
