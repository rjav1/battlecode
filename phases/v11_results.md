# v11 Results: Gunners Replace Sentinels

**Date:** 2026-04-04
**Change:** Replaced sentinel building with gunner building in the splitter-based turret placement system.

## Changes Made

- `bots/buzzing/main.py`: docstring updated to v11
- `run()`: Added `elif t == EntityType.GUNNER: self._gunner(c)` handler
- Added `_gunner(self, c)` method — fires every round when ammo >= 2
- `_build_sentinel_infra()`: now counts GUNNER (not SENTINEL), builds gunner in step 4
- Cost checks lowered: resource threshold 150→80 Ti, step reserves reduced to match gunner cost (10 Ti base)
- `_sentinel()` kept for compatibility with any old sentinel entities
- `bots/buzzing_prev/main.py`: snapshot of pre-v11 bot

## Regression Tests (5/5 wins)

| Map            | Result | Buzzing Ti mined | Prev Ti mined |
|----------------|--------|-----------------|---------------|
| default_medium1| WIN    | 23530            | 7070          |
| hourglass      | WIN    | 23720            | 19590         |
| settlement     | WIN    | 19660            | 17910         |
| corridors      | WIN    | 9930             | 9930          |
| face           | WIN    | 18890            | 12080         |

## Self-play Test

- Map: default_medium1 — no crash
- Ti mined: 23530 (>10K threshold)

## Key Observations

- Gunner bot mines significantly more Ti on most maps (lower scale = cheaper economy buildings)
- Corridors was a tie on Ti mined but buzzing still won tiebreaker
- Buildings count much higher in new version (lower scale cost = more buildings affordable)
- The resource threshold for starting gunner placement was lowered from 150 to 80 Ti since gunners cost only 10 Ti vs 30 Ti for sentinels

## Conclusion

All DEPLOY_CHECKLIST.md requirements passed. Bot submitted.
