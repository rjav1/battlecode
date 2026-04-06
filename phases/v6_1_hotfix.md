# v6.1 Hotfix — April 6, 2026

## Bugs Fixed

### Bug 1: `_build_barriers` AttributeError — ALREADY FIXED BY ANOTHER AGENT
The `_build_barriers` method was missing in v6 but has been added in the current v7 code (lines 383-436). No action needed from this hotfix.

### Bug 2: Position out of bounds — FIXED
Three locations in the code called `c.get_tile_building_id()`, `c.can_build_road()`, or similar on positions that could be out of map bounds (when a unit is near a map edge and tries to check tiles beyond the boundary).

**Locations fixed:**

1. **`_nav()` road fallback (line ~226)**: `pos.add(d)` passed to `can_build_road` without bounds check.
   - Fix: Added `rp.x < 0 or rp.x >= w or rp.y < 0 or rp.y >= h` guard with `continue`.

2. **`_attack()` adjacent enemy scan (line ~453)**: `pos.add(d)` passed to `get_tile_building_id` without bounds check.
   - Fix: Added bounds check with `continue`. Also fetches `w, h` at top of loop.

3. **`_walk_to()` road building (line ~483)**: `pos.add(try_d)` passed to `can_build_road` without bounds check.
   - Fix: Added bounds check with `continue`. Also fetches `w, h` before the loop.

## Test Results

| Map | Errors | Ti Mined | Winner |
|-----|--------|----------|--------|
| default_medium1 | **0** | 13,510 | buzzing |
| face | **0** | 9,660 | buzzing |
| arena | **0** | -- | buzzing |
| settlement | **0** | -- | buzzing |

All 4 maps that previously showed errors now run clean. Zero `AttributeError`, zero `GameError: Position out of bounds`.

## Status

- [x] Bug 1 (`_build_barriers`): Already fixed in v7
- [x] Bug 2 (out of bounds): Fixed in 3 locations
- [x] Tested on default_medium1: no errors, 13,510 Ti mined
- [x] Tested on face: no errors, 9,660 Ti mined
- [x] Tested on arena: no errors
- [x] Tested on settlement: no errors
- [ ] Submit and git commit (awaiting team lead approval -- not a git repo currently)
