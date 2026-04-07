# V57 Ladder Monitoring

**V57 deployed:** 2026-04-07 16:03 UTC  
**V57 = API version 57 (active submission)**  
**Monitoring started:** ~16:10 UTC  
**Current Elo at V57 deploy:** ~1504 (recovered from ~1347 low)

---

## V57 Matches

| Result | Score | Opponent | Opp Elo | Elo Delta | Time |
|--------|-------|----------|---------|-----------|------|
| LOSS | 0-5 | MergeConflict | 1521 | -16.4 | 16:56 |
| WIN | 4-1 | natto warriors | ~1499 | +9.2 | 16:47 |
| WIN | 5-0 | eidooheerfmaet | ~1507 | +16.2 | 16:35 |
| LOSS | 2-3 | KCPC-B | ~1499 | -3.6 | 16:27 |
| WIN | 3-2 | Cenomanum | ~1491 | +2.6 | 16:16 |

**V57/V58 total: 3W-2L (60%), current Elo ~1513**

*** SWEEP LOSS: 0-5 vs MergeConflict (1521 Elo, 1598 matches played) — strong opponent ***

---

## V56 Matches (for baseline comparison)

| Result | Score | Opponent | Opp Elo | Elo Delta | Time |
|--------|-------|----------|---------|-----------|------|
| WIN | 3-2 | chicken tikka masala | ~1496 | +3.0 | 16:08 |
| LOSS | 2-3 | eidooheerfmaet2 | ~1502 | -3.3 | 15:55 |

V56: 1W-1L (50%)

---

## V55 Matches

| Result | Score | Opponent | Opp Elo | Elo Delta | Time |
|--------|-------|----------|---------|-----------|------|
| LOSS | 2-3 | Chameleon | ~1510 | -3.1 | 15:47 |

V55: 0W-1L (sample too small)

---

## V54 Matches (large sample)

| Result | Score | Opponent | Opp Elo | Elo Delta | Time |
|--------|-------|----------|---------|-----------|------|
| LOSS | 0-5 | nus robot husk | ~1543 | -15.1 | 15:37 |
| WIN | 3-2 | eidooheerfmaet | ~1523 | +3.4 | 15:26 |
| WIN | 4-1 | KCPC-B | ~1501 | +9.2 | 15:18 |
| WIN | 3-2 | - | ~1532 | +4.4 | 15:05 |
| WIN | 4-1 | New Jabees | ~1510 | +10.3 | 14:57 |
| WIN | 5-0 | old but bronze | ~1484 | +16.2 | 14:44 |
| WIN | 4-1 | DODO | ~1476 | +9.9 | 14:37 |
| WIN | 3-2 | Fake Analysis | ~1449 | +2.3 | 14:28 |
| LOSS | 2-3 | nibbly-finger | ~1483 | -2.6 | 14:16 |
| LOSS | 1-4 | Polska Gurom | ~1478 | -9.7 | 14:07 |
| LOSS | 1-4 | Solo Gambling | ~1505 | -8.9 | 13:55 |
| LOSS | 1-4 | The Defect | ~1507 | -9.2 | 13:47 |
| WIN | 4-1 | Chameleon | ~1488 | +9.6 | 13:37 |
| LOSS | 2-3 | natto warriors | ~1508 | -2.4 | 13:27 |
| WIN | 4-1 | DODO | ~1475 | +9.3 | 13:17 |
| WIN | 3-2 | N | ~1472 | +2.9 | 13:07 |
| WIN | 3-2 | no_friends_to_make_a_t | ~1478 | +3.3 | 12:56 |

V54: 11W-6L (65%) — strong performance during V54 era

---

## Elo Trajectory

| Version | Elo (approx) | Notes |
|---------|-------------|-------|
| V54 start | ~1500 | Strong baseline |
| V54 end | ~1530 | Good run |
| V55 | dropped | 0-5 sweep by nus robot husk |
| V56 | ~1504 | Partial recovery |
| V57 start | ~1504 | Just deployed |

---

## Monitoring Log

| Check Time | New Matches | V57 Record | Notes |
|------------|-------------|------------|-------|
| 16:10 | 0 V57 matches | 0W-0L | Just deployed, waiting |

---

## What V57 Changed

V57 is the bridge distance guard fix + enemy-road BFS exclusion fix:
- **Bridge fix**: restored `ore_core_dist > 9` guard — prevents bridge shortcut from firing on close-range ore (was causing corridors 5090→14850 Ti regression)
- **Enemy-road fix**: excludes enemy road tiles from BFS passable set — prevents 80 Ti economy collapse on default_medium1 vs road-heavy opponents

Expected impact:
- Corridors and similar close-range ore maps: +~9760 Ti per game
- Maps vs road-heavy opponents (ladder_road style): +massive (was 80, now ~normal)
- No regressions expected on current test maps (bridge still works for medium-range ore)

Local baseline: 57% win rate (up from 46% V55 baseline)
