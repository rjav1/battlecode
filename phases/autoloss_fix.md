# Auto-Loss Fix Analysis: galaxy (0-8), face (0-5), arena (0-4)

## Task 1: Local Reproduction Results

### v30 baseline vs all test opponents:

**arena (25x25, tight, path=8)** — 2W-6L locally
| Opponent | Winner | Buzzing Ti Mined | Opp Ti Mined | Gap |
|----------|--------|-----------------|--------------|-----|
| smart_eco | buzzing | 19,490 | 13,700 | +5,790 |
| smart_defense | smart_defense | 14,650 | 24,270 | -9,620 |
| sentinel_spam | sentinel_spam | 14,620 | 23,910 | -9,290 |
| balanced | balanced | 14,620 | 23,940 | -9,320 |
| rusher | rusher | 1,660 | 4,970 | -3,310 |
| fast_expand | buzzing | 16,820 | 2,850 | +13,970 |
| barrier_wall | barrier_wall | 15,230 | 25,740 | -10,510 |
| adaptive | adaptive | 14,660 | 17,760 | -3,100 |

**face (20x20, tight, path=9)** — 5W-3L locally
| Opponent | Winner | Buzzing Ti Mined | Opp Ti Mined |
|----------|--------|-----------------|--------------|
| smart_eco | smart_eco | 18,490 | 18,920 |
| smart_defense | buzzing | 18,670 | 14,790 |
| sentinel_spam | buzzing | 22,310 | 15,980 |
| balanced | buzzing | 22,460 | 15,820 |
| rusher | rusher | 120 | 9,930 |
| fast_expand | buzzing | 9,660 | 4,980 |
| barrier_wall | buzzing | 23,100 | 14,810 |
| adaptive | adaptive | 2,150 | 9,920 |

**galaxy (40x40, expand, path=34)** — 5W-3L locally
| Opponent | Winner | Buzzing Ti Mined | Opp Ti Mined |
|----------|--------|-----------------|--------------|
| smart_eco | buzzing | 9,940 | 9,930 |
| smart_defense | buzzing | 15,020 | 13,230 |
| sentinel_spam | buzzing | 14,200 | 9,910 |
| balanced | buzzing | 10,660 | 9,920 |
| rusher | rusher | 470 | 4,920 |
| fast_expand | buzzing | 14,200 | 4,970 |
| barrier_wall | barrier_wall | 13,680 | 14,620 |
| launcher_drop | launcher_drop | 13,680 | 13,860 |

## Task 2: Map Properties

| Map | Size | Sym | Ti | Ax | Path 8d/4d | Nearest Ti | Nearest Ax | Classification |
|-----|------|-----|----|----|-----------|------------|------------|----------------|
| arena | 25x25 | rot | 10 | 4 | 8/12 | 6 | 3 | Rush, Scarce |
| face | 20x20 | horiz | 8 | 4 | 9/9 | 5 | 10 | Rush, Scarce |
| galaxy | 40x40 | rot | 16 | 8 | 34/68 | 4 | 15 | Mixed |

## Task 3: Pattern Analysis

### Pattern 1: Close-core maps (face path=9, arena path=8) lack defense
- Tight maps (`area <= 625`) SKIP barriers entirely (`map_mode != "tight"` gate)
- Tight maps SKIP gunners entirely (same gate)
- Enemy builders/rushers reach our core area in 8-9 steps (~rounds 15-20)
- Result: zero defense against rush attacks

### Pattern 2: Rush attacks devastate all 3 maps
- **rusher** bot: mines only 120 Ti on face, 1660 on arena, 470 on galaxy
- **adaptive** bot: mines only 2150 on face, 14660 on arena
- Enemy builders walk on our conveyors and destroy them (2 damage per shot, 10 shots to kill a conveyor at 20 HP)
- By the time we get gunners (round 200), economy is already destroyed

### Pattern 3: Economy gap on arena is fundamental
- We consistently mine ~14,650 Ti while opponents mine ~24,000 Ti
- Arena has only 10 Ti ore tiles — each tile is critical
- Our building count (135-172) is HIGHER than opponents (110-168)
- We build MORE conveyors but mine LESS = broken/inefficient chains
- The d.opposite() conveyor pattern creates bends when builders zigzag
- Bends reduce conveyor chain throughput

### Pattern 4: Galaxy losses are marginal
- barrier_wall: 13,680 vs 14,620 (close loss)
- launcher_drop: 13,680 vs 13,860 (very close)
- rusher: 470 vs 4,920 (economy sabotage)

## Task 4: Root Cause Diagnosis

### face/arena (close cores):
1. **No barriers before round 200+**: Both barriers and gunners gated behind `map_mode != "tight"`
2. **No early gunner**: Skipped entirely on tight maps
3. **Conveyors are walkable by enemies**: Enemy builders walk our conveyor chain and destroy buildings
4. **Economy inefficiency**: On arena, we mine 14,650 vs opponent's 24,000 despite more buildings

### galaxy (far cores):
1. **Gunners too late**: Round 200 threshold means rushers arrive 170 rounds before defense
2. **barrier_wall/launcher_drop**: Marginal losses from slightly lower economy efficiency

### Why fixes are extremely difficult:
Every defensive change tested caused economy regressions:
- Early barriers → builders detour to core, miss ore-seeking window
- Lower harvester requirement for barriers → first builder places barriers instead of harvesting
- Gunners on tight maps → gunner builder mines less ore
- Lower conveyor Ti reserve → builders waste all Ti on exploration conveyors (0 Ti mined!)
- Ax ore penalty → changes ore targeting, can devastate some maps (landscape: 27,130 → 280 Ti mined)

The tight-map economy is a razor's edge: any builder time spent on defense = less mining = losing the economy race.

## Task 5: Implemented Fix

### Change: Earlier gunner on expand maps (v31)
- **File**: `C:\Users\rahil\downloads\battlecode\bots\buzzing\main.py`
- **Change**: `gunner_round = 150 if map_mode == "expand" else 200`
- **Rationale**: Galaxy is 40x40 (expand mode). Earlier gunner provides 50 rounds more defense time.
- **Regression test**: 3W-2L vs buzzing_prev (identical to v30 baseline, losses are position-dependent)
- **Impact**: Minimal — does not solve galaxy's core problems but is the only safe change found.

### Changes attempted and REVERTED (all caused regressions):

1. **Ax ore penalty (+50000 on all maps)**: Improved arena from 14,650→22,340 mining but destroyed landscape (27,130→280 mining). On tight-only, had no effect.

2. **Early barriers on tight maps (round 40, harv_req=0)**: Pulled first builder away from ore. face regressed from 6W-1L to 3W-4L.

3. **Barriers at round 100 on tight (harv_req=2)**: No impact on arena/face mining. Caused barrier_wall regression on face.

4. **4 initial builders on tight maps**: Helped arena vs smart_defense (+4,800 mining) but destroyed face (6W-1L → 3W-4L).

5. **Lower explore_reserve on tight maps (10 vs 30)**: CATASTROPHIC — 0 Ti mined on arena. Builders spent all Ti on exploration conveyors.

6. **Sentinel building**: No measurable impact on any map.

## Recommendations for Future Work

### The real problem: local tests don't match ladder
- We win 5-6/8 locally but go 0/4-8 on ladder
- Real opponents likely use strategies combining rush + economy that our test bots don't model
- The `adaptive` bot (rush on small maps) comes closest to modeling real ladder threats

### What would actually help (but is architecturally complex):

1. **Conveyor chain optimization**: Build straight-line conveyor chains from harvester to core instead of d.opposite() breadcrumbs. smart_eco's chain-building approach (dedicated chain phase after harvester placement) mines significantly more.

2. **Active defense**: Detect enemy builders entering our territory (visible enemy entities) and intercept with our own builders.

3. **Map-specific opening**: Pre-compute optimal first-ore targets for arena/face/galaxy based on symmetry analysis.

4. **Foundry for Ax refinement**: Building foundries to refine axionite would add tiebreaker advantage (refined Ax > Ti delivered in tiebreak).
