# V61 Weakness Map — Cold & Gaussian Economy Gaps

**Date:** 2026-04-08
**Test:** buzzing (V61) vs worst opponents, seed 1

## Match Results

| Opponent | Map | Winner | Our Ti mined | Their Ti mined | Our bldgs | Their bldgs |
|----------|-----|--------|:---:|:---:|:---:|:---:|
| barrier_wall | cold | **barrier_wall** | 15,720 | 18,720 | 618 | 123 |
| sentinel_spam | cold | **sentinel_spam** | 18,930 | 27,520 | 133 | 203 |
| smart_eco | cold | **buzzing** | 19,670 | 19,630 | 339 | 275 |
| barrier_wall | gaussian | **barrier_wall** | 19,830 | 29,730 | 211 | 101 |
| smart_eco | gaussian | **smart_eco** | 19,830 | 22,100 | 221 | 117 |

## Target Gaps (what phoenix2 / future bot must beat)

| Opponent | Map | Ti gap to close | Building gap to reduce |
|----------|-----|:-:|:-:|
| barrier_wall | cold | +3,000 Ti (19% more needed) | 618 → <200 |
| sentinel_spam | cold | +8,590 Ti (45% more needed) | - |
| barrier_wall | gaussian | +9,900 Ti (50% more needed) | 211 → <120 |
| smart_eco | gaussian | +2,270 Ti (11% more needed) | 221 → <120 |

## barrier_wall Efficiency Analysis

Reading `bots/barrier_wall/main.py`:

**Why barrier_wall mines 50% more Ti with fewer buildings:**

1. **Hard 3-builder cap** — spawns exactly 3 builders and stops. Our bot spawns 7+ on expand maps.

2. **Tight explore target** — `_explore()` only looks 15 tiles out (`pos + dx*15`). Ours looks to the map edge (`max(w,h)` tiles). This limits chain length dramatically.

3. **Ti reserve of 15** for harvester builds (vs our 5) — holds back spending until it has more buffer, avoiding cost-scaling traps.

4. **No BFS, no bridge fallback, no barrier logic** — simpler code means fewer decisions, fewer accidental buildings.

5. **One role-based builder becomes a wall builder at round 60** — stops mining, builds barriers, then reverts to miner. This caps exploration conveyors from that builder entirely.

6. **Explore rotation every 150 rounds** — much slower than our 50-round rotation, so builders stay in productive zones longer.

**Net effect:** barrier_wall's 3 builders each lay ~40 conveyors total (120 total) vs our 7 builders each laying 80+ (560+). Scale stays at ~2.2× vs our 6.5×. Harvesters cost ~44 Ti instead of 130 Ti. They can afford 3× more harvesters at same Ti budget.

## Key Insight

smart_eco on cold is essentially a tie (19,670 vs 19,630 Ti) and we WIN. The problem is only vs barrier_wall (lean 3-builder) and sentinel_spam (higher absolute throughput). 

The Ti gap to close vs barrier_wall on gaussian is 9,900 Ti — that requires either:
- 2 additional harvesters running the full 2000 rounds (2 × 5,000 = 10,000 Ti), OR  
- Dramatically lower cost scale to afford more harvesters earlier

The building bloat fix (reduce from 618→150 on cold) is the only path to closing this gap without a complete architectural rewrite.
