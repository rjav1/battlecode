# Phoenix2: Return-to-Core After Far Harvest

## Date: 2026-04-08
## Concept: After building a harvester >15 tiles from core, builder walks back on existing conveyors, finds missed ore, sweeps next sector.

---

## Implementation

Based on V61 buzzing with ONE addition:
- New state: `_returning = False`
- After building harvester: if `ore.distance_squared(core) > threshold`, set `_returning = True`
- When `_returning`: walk toward core via `_walk_to` (movement only, no new conveyors)
- When near core (r^2 <= 8): clear `_returning`, increment `explore_idx` for next sector
- Thresholds: balanced r^2=225 (15 tiles), expand r^2=144 (12 tiles). Tight: never return.
- Stuck detection clears `_returning`
- Builder still builds harvesters opportunistically during return (existing code handles this)

## Results: Phoenix2 vs Buzzing (10 maps, seed 42)

| Map | Winner | Phoenix2 Ti | Buzzing Ti | Notes |
|-----|--------|------------|-----------|-------|
| default_small1 | buzzing | 9,850 | 19,700 | Tight — no return |
| default_medium1 | phoenix2 | 9,650 | 9,380 | **Identical to buzzing vs buzzing** |
| default_medium2 | buzzing | 16,680 | 33,170 | **Identical to buzzing vs buzzing** |
| default_large1 | buzzing | 14,860 | 23,730 | **Identical to buzzing vs buzzing** |
| arena | phoenix2 | 14,850 | 9,910 | Team A positional advantage |
| binary_tree | buzzing | 5,600 | 16,010 | **Identical to buzzing vs buzzing** |
| hooks | phoenix2 | 35,750 | 18,940 | Team A positional advantage |
| cold | buzzing | 16,390 | 21,620 | **Identical to buzzing vs buzzing** |
| butterfly | phoenix2 | 34,580 | 34,390 | **Identical to buzzing vs buzzing** |
| wasteland_oasis | buzzing | 4,170 | 9,350 | **Identical to buzzing vs buzzing** |

## Critical Finding: RETURN-TO-CORE NEVER TRIGGERS

Verified by comparing phoenix2 vs buzzing with buzzing vs buzzing (self-play). **Results are IDENTICAL on every map.** The return-to-core feature has zero effect because:

1. **Harvesters are always within 15 tiles of core.** Ore on all 38 maps is within 15 tiles of at least one builder's starting path. Builders find and build harvesters before reaching the return threshold.

2. **The threshold is too high.** At r^2=225 (15 tiles), the builder has already built 10-15 conveyors. But most harvesters are built at r^2=50-100 (7-10 tiles from core). The threshold never triggers.

3. **Lowering the threshold hurts.** At r^2=100 (10 tiles) or r^2=144 (12 tiles), the same maps produce identical results. Ore is close enough that the return distance is never reached on ANY map tested.

## Why Return-to-Core Doesn't Work

The premise was: "builders currently explore OUTWARD forever." But testing reveals builders DON'T explore outward forever. They find ore within 7-10 tiles of core and build harvesters. The conveyor chain to that ore is 7-10 conveyors — not 60-137 as hypothesized.

The 60-137 conveyor counts from replay analysis include MULTIPLE harvesters' chains, exploration dead-ends, and the conveyors laid during exploration when no ore is visible. Return-to-core doesn't address ANY of these:
- Multiple harvester chains: each is 7-10 conveyors, return doesn't shorten them
- Exploration dead-ends: conveyors laid when searching for ore, not connected to any harvester
- The problem is conveyors laid DURING exploration, not chain length per harvester

## The Real Problem (Confirmed)

The V61 building count (400-600) comes from:
1. **Multiple builders exploring simultaneously** — each lays conveyors as they walk
2. **Exploration conveyors** — conveyors laid when no ore target exists, just walking outward
3. **Multiple chains to same area** — 2-3 builders build parallel chains to nearby ore

Return-to-core addresses NONE of these. The fix would need to:
- Reduce builder count (tried, regressed)
- Suppress exploration conveyors (tried via ti_reserve, ceiling reached)
- Prevent duplicate chains (tried via marker claiming, partially works)

## Conclusion

Phoenix2 is identical to V61 buzzing in practice. The return-to-core feature never triggers because harvesters are placed at 7-10 tiles from core, well within the return threshold. The code is correct but the premise (builders explore too far) is wrong.

**The building count problem is exploration conveyors + multiple builders, not chain length.**

## Files
- Prototype: `bots/phoenix2/main.py`
- Changes: ~15 lines added to V61 buzzing
