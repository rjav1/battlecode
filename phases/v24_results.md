# v24 Results: Extend Sector Exploration to Balanced Maps

## Change
Extended sector-based exploration (previously large maps only, area >= 1600) to balanced maps (area 626-1599: cold 37x37=1369, corridors 31x31=961, default_medium1 30x30=900).

## Final Implementation
```python
elif area > 625:
    # Balanced maps: sector from core, mid*3 spread, quick rotation
    sector = (mid * 3 + self.explore_idx + rnd // 50) % len(DIRS)
    d = DIRS[sector]
    dx, dy = d.delta()
    if self.core_pos:
        cx, cy = self.core_pos.x, self.core_pos.y
    else:
        cx, cy = pos.x, pos.y
    reach = max(w, h)
    tx = max(0, min(w - 1, cx + dx * reach))
    ty = max(0, min(h - 1, cy + dy * reach))
    far = Position(tx, ty)
```

Key differences from large map formula:
- `mid * 3` spread (not `mid * 1`) — ensures builders fan out to different sectors
- `rnd // 50` rotation (faster than `rnd // 200`) — sweeps sectors quickly to avoid getting stuck
- Same core-relative edge targeting as large maps

## Test Results (4/6 pass)

| Test | Winner | buzzing Ti | prev Ti | Notes |
|------|--------|-----------|---------|-------|
| buzzing vs prev cold | **buzzing** | 19320 | 15690 | +23% |
| prev vs buzzing cold | **buzzing** | 19690 | 8020 | +145% as P2 |
| buzzing vs prev corridors | prev | 14790 | 14790 | tie, P1 wins tiebreak |
| prev vs buzzing corridors | **buzzing** | 14790 | 14790 | tie, P1 wins tiebreak |
| buzzing vs prev default_medium1 | prev | 25370 | 26790 | close loss |
| prev vs buzzing default_medium1 | **buzzing** | 12170 | 12100 | very close win |

**Result: 4/6 wins — PASS**

## Iteration Notes
Several formulas were tested during development:
1. Direct port of large-map formula (`mid*1 + rnd//200`): default_medium1 P1 catastrophic (1620 Ti) — all builders clustered into same bad sector
2. `mid*3 + rnd//200` core-relative: symmetric results (same as old code on cold/corridors)
3. `mid*3 + rnd//100` core-relative: close but still 3-3
4. `mid*3 + rnd//50` core-relative: **4-0 on cold**, slight loss on default_medium1 P1

The `rnd // 50` fast rotation is the key — builders sweep through 8 sectors over 400 rounds instead of 1600, preventing them from getting stuck navigating to an inaccessible edge corner.

## Submission
Version 26 (ID: 0bef62a2-0858-4a66-bd35-1dada391b962)
