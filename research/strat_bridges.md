# Bridge-First Expansion Strategy Research

**Date:** 2026-04-04
**Bot:** `bridge_expand` (v3) — d.opposite() conveyors + aggressive bridge shortcuts
**Theory:** Bridges every 3 tiles shortcut conveyor chains, reducing latency and enabling expansion to distant/fragmented ore patches.

## Design

- 4 builders, d.opposite() conveyors for chain integrity
- After building a harvester >25 dist^2 from core, enter "chain-back" mode
- Chain-back: walk toward core, place bridge every 3 conveyors passed
- Bridge targets: furthest reachable tile toward core (dist^2 <= 9, up to 3 tiles)
- Fallback bridges for wall traversal during exploration
- Target: 5-10 bridges per game

## Results vs Starter

| Map | Winner | bridge_expand Ti (mined) | starter Ti (mined) | Notes |
|-----|--------|-------------------------|-------------------|-------|
| wasteland | starter | 4388 (0) | 1965 (0) | No ore on map; starter wins by spending less |
| butterfly | **bridge_expand** | 42787 (38400) | 4869 (0) | Dominant win |
| settlement | **bridge_expand** | 16196 (18970) | 85 (0) | Strong win on wall-heavy map |
| default_medium1 | **bridge_expand** | 18809 (18050) | 3515 (0) | Solid win |

**Record vs starter: 3-1** (loss only on ore-less map)

## Results vs Buzzing (our current best bot)

| Map | Winner | bridge_expand Ti (mined) | buzzing Ti (mined) | Notes |
|-----|--------|-------------------------|-------------------|-------|
| wasteland | buzzing | 5167 (0) | 5278 (0) | No ore; buzzing barely wins on passive Ti |
| default_medium1 | buzzing | 20371 (18320) | 26236 (22280) | Buzzing mines 22% more |
| butterfly | buzzing | 42787 (38400) | 42286 (38430) | Near-identical mining; buzzing wins on units (12 vs 10) |
| settlement | **bridge_expand** | 31578 (30530) | 19559 (17910) | Bridge_expand mines 70% more! |
| corridors | buzzing | 14916 (9910) | 15039 (9930) | Near-identical (20 Ti diff in mining) |
| arena | buzzing | 17428 (14800) | 23164 (19750) | Buzzing mines 33% more |

**Record vs buzzing: 1-5** (win only on settlement)

## Analysis

### Where bridges help
- **Settlement (wall-heavy):** Bridge_expand's biggest win. 30530 vs 17910 mined Ti — a 70% advantage. Bridges clearly enable reaching and connecting distant ore patches across walls.
- Maps with fragmented terrain and long chain distances benefit most from bridge shortcuts.

### Where bridges hurt
- **Open maps (arena, default_medium1):** Buzzing outperforms by 22-33%. The 20 Ti + 10% scale cost of each bridge is a significant economic drag when conveyors (3 Ti, 1% scale) would suffice.
- **Bridge cost is expensive:** At 20 Ti + 10% scale per bridge, 5 bridges = 100 Ti + 50% cumulative scale. vs 5 conveyors = 15 Ti + 5% scale. Bridges cost ~6.7x more Ti and 10x more scale.
- **Chain-back mode pauses exploration:** While a builder walks back to place bridges, it's not finding new ore. Buzzing builders immediately resume exploring.

### Key insight
- Bridges are **situationally powerful** on fragmented/wall-heavy maps but **economically costly** on open maps.
- The 10% scale increase per bridge compounds: 5 bridges = +50% to global scale, making everything more expensive.
- On maps like butterfly where both bots mine identical amounts (38400 vs 38430), the bridge bot has fewer units (10 vs 12) because scale inflation limits spawning.

## Recommendations

1. **Don't make bridges the primary strategy.** The cost/scale penalty is too high for general use.
2. **Use bridges as tactical tools** for specific situations:
   - Crossing walls when conveyors can't route around
   - Connecting distant ore patches (>8 tiles from existing chain) where a long conveyor chain would be even more expensive
   - Late-game when scale is already high and 10% more doesn't matter as much
3. **Budget bridges carefully:** Max 2-3 per game (like buzzing's current fallback approach), not 5-10.
4. **Map detection:** If the bot could detect wall density early, it could switch between bridge-heavy (settlement-style maps) and conveyor-only (open maps) modes.
5. **The real lesson from Blue Dragon's 33 bridges:** They likely have superior bridge-to-conveyor connection logic and/or use bridges offensively (crossing enemy territory). Raw bridge count without smart placement is wasteful.

## Verdict

**Bridge-first expansion is NOT a winning general strategy.** It beats starter easily but underperforms buzzing on 5 of 6 maps. The one map where it dominates (settlement, +70%) suggests bridges should be a **conditional tool** activated by map analysis, not the default building approach.

The optimal approach: keep buzzing's conveyor-first economy with its 0-2 bridge fallback, but add a map-awareness heuristic that increases bridge usage on fragmented/wall-heavy maps.
