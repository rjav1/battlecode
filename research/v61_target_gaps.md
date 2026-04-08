# V61 Target Gaps — What phoenix2 Must Beat

**Date:** 2026-04-08
**Purpose:** Baseline Ti gaps for phoenix2 testing

## Cold

| Matchup | Our Ti mined | Their Ti mined | Gap | Our bldgs | Their bldgs |
|---------|:---:|:---:|:---:|:---:|:---:|
| vs smart_eco | 19,670 | 19,630 | +40 (we lead) | 339 | 275 |
| vs barrier_wall | 15,720 | 18,720 | **-3,000** | 618 | 123 |

## Gaussian

| Matchup | Our Ti mined | Their Ti mined | Gap | Our bldgs | Their bldgs |
|---------|:---:|:---:|:---:|:---:|:---:|
| vs smart_eco | 19,830 | 22,100 | **-2,270** | 221 | 117 |
| vs barrier_wall | 19,830 | 29,730 | **-9,900** | 211 | 101 |

## phoenix2 Pass Criteria

To beat barrier_wall on cold: mine >18,720 Ti (currently 15,720 — need +3,000)
To beat barrier_wall on gaussian: mine >29,730 Ti (currently 19,830 — need +9,900)
To beat smart_eco on gaussian: mine >22,100 Ti (currently 19,830 — need +2,270)

The gaussian/barrier_wall gap (+9,900 Ti) requires ~2 extra harvesters running full game.
This is only achievable by reducing building count from 211→~100, bringing scale from ~3.1× to ~2×.

## barrier_wall Code Pattern (the specific fix)

From reading `bots/barrier_wall/main.py`:
- **3 builders max** (not 7)
- **Explore target: 15 tiles** (not map edge)
- **Explore rotation: every 150 rounds** (not 50)
- **Harvester Ti reserve: 15** (not 5)

These four parameters together explain the entire 50% throughput advantage.
