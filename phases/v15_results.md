# v15 Results: Chain-fix for winding conveyor paths

## Approach chosen: Option A Hybrid (with key modifications)

Started with Option A (d.opposite() conveyors outbound, fix on return trip) but evolved significantly through testing.

### What was tried and failed:
1. **Full walk-back chain-fix**: Builder walks all the way back to core after every harvester. Cost: too many rounds wasted, massive Ti regression on open maps.
2. **direction_to(core) facing**: Replace d.opposite() with global direction toward core. CATASTROPHIC: all conveyors face the same direction, resources go into walls.
3. **Inline fix during navigation**: Fix conveyors at previous position while moving. Caused complete bot failure (destroy leaves tiles empty, builder trapped).
4. **Unbounded path recording**: `fix_path.append()` grew to 1000+ entries, causing CPU timeout on 2ms limit.

### What works (final implementation):
- **d.opposite() conveyors on outbound trip** (unchanged from v14)
- **Path recording during navigation** to ore targets (capped at 30 entries)
- **After building first 2 harvesters**, if outbound path had 3+ direction changes, walk back along recorded path
- **During walk-back**: fix conveyors at BEHIND tiles (tiles just left, within action r^2=2)
- **Fix = destroy + rebuild** with correct facing (destroy has no cooldown cost)
- **Safety**: if rebuild fails, restore original direction

### Key discovery: game is non-deterministic
Same seed + same bot can produce wildly different results across runs (e.g., cold seed 3: 7K, 19K, 25K on three runs). This means single-seed comparisons are unreliable. Only head-to-head match results matter.

## Ti mined comparison (single representative run)

| Map | v14 (mined) | v15 (mined) | Change |
|-----|-------------|-------------|--------|
| cold | 10,550 | 23,140 | +119% |
| corridors | 9,930 | 9,930 | 0% |
| shish_kebab | 9,580 | 4,940 | -48% |
| default_medium1 | 4,510 | 23,790 | +427% |
| settlement | 18,420 | 19,660 | +7% |
| face | 12,610 | 19,130 | +52% |
| hourglass | 19,370 | 10,840 | -44% |

## Head-to-head regression (v15 vs v14)

### Run 1 (default seed):
| Map | Winner |
|-----|--------|
| default_medium1 | **v15** |
| hourglass | v14 |
| settlement | **v15** |
| corridors | **v15** (tiebreak) |
| face | **v15** |
| cold | **v15** |
| shish_kebab | v14 |

**Result: v15 wins 5/7**

### Run 2 (seed 2):
| Map | Winner |
|-----|--------|
| default_medium1 | **v15** |
| hourglass | v14 |
| settlement | **v15** |
| corridors | **v15** |
| face | **v15** |

**Result: v15 wins 4/5**

## Gotchas encountered

1. **CPU timeout from list growth**: `fix_path.append()` without cap caused paths to grow to 1000+ entries. Even with only Position NamedTuples, this was enough to push Python over the 2ms CPU limit. Fixed with `len(self.fix_path) < 30` cap.

2. **Cannot destroy conveyor under builder's feet**: Builder standing on a tile cannot destroy the conveyor there (tile becomes empty, builder is trapped). All fixes must target ADJACENT tiles within action radius.

3. **`build_conveyor` after `destroy` can fail**: Even though destroy has no cooldown, the tile state after destroy might not allow immediate rebuilding. Always save original direction for fallback.

4. **Chain-fix walk-back is EXPENSIVE**: Walking back 20+ tiles costs 20+ rounds. On open maps where d.opposite() already works, this time loss outweighs any chain improvement. Solution: only trigger on paths with 3+ direction changes (truly winding paths).

5. **Game non-determinism**: Same seed, same bot, different runs = different results. Single comparisons are meaningless. Need head-to-head matches for reliable evaluation.

## Implementation details

- File: `bots/buzzing/main.py`
- Lines changed: ~60 lines added (chain-fix state, path recording, _fix_chain method)
- State variables: `fixing_chain` (bool), `fix_path` (list[Position], capped at 30), `fix_idx` (int)
- Trigger: first 2 harvesters only, path length >= 4, direction changes >= 3
