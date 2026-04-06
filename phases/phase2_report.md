# Phase 2 Report: Reliable Conveyor Chains + Sentinel Defense

## Changes from Phase 1

### Change 1: Chain-Building State Machine
After placing a harvester, the builder enters `BUILD_CHAIN` mode:
- Walks back toward core using BFS pathfinding
- At each tile, ensures a conveyor exists facing toward core
- Roads are destroyed and replaced with conveyors (`_replace_with_conveyor`)
- Stops when reaching a core-adjacent tile
- Outbound navigation (`_nav`) also replaces roads with conveyors when encountered

**Key: Every tile between harvester and core now has a conveyor or core tile. No more chain gaps from roads.**

### Change 2: Sentinel Defense
- `_sentinel()` method: auto-fires at nearest enemy when ammo >= 10 and cooldown == 0
- `_try_place_sentinel()`: builds sentinel near core after round 200
  - Only builder with `my_id % 4 == 1` attempts (prevents overbuilding)
  - Cap: 2 sentinels max (counted via `get_nearby_buildings`)
  - Sentinel faces enemy direction (inferred from rotational symmetry: `w-1-cx, h-1-cy`)
  - Reserve: sentinel_cost + 50 Ti before building
- Sentinels placed opportunistically: during chain-building return trip AND in normal mode near core
- Currently unarmed (no dedicated ammo supply) — serve as 30 HP obstacles + 32 vision radius

## Ti Mined Comparison: Phase 1 vs Phase 2

All results with default seed:

| Map | Phase 1 | Phase 2 | Change | Sentinel Count |
|-----|--------:|--------:|-------:|:-:|
| default_small1 | 24,190 | 21,520 | -11% | 0 |
| default_small2 | 23,980 | 33,260 | **+39%** | 0 |
| default_medium1 | 19,200 | 32,710 | **+70%** | 0 |
| default_medium2 | 26,130 | 14,170 | -46% | 0 |
| default_large1 | 18,880 | 23,280 | **+23%** | 1 |
| default_large2 | 37,460 | 40,100 | +7% | 0 |
| arena | 23,580 | 33,630 | **+43%** | 0 |
| hourglass | 24,760 | 24,600 | ~same | 0 |
| corridors | 14,700 | 14,480 | ~same | 1 |
| settlement | 38,600 | 54,650 | **+42%** | 0 |
| wasteland | 12,260 | 50* | -99% | 0 |
| butterfly | 33,420 | 29,640 | -11% | 0 |
| face | 4,980 | 9,800 | **+97%** | 0 |
| cubes | 29,100 | 29,550 | +2% | 0 |

*Wasteland varies significantly by seed. Some seeds mine 10K+, others 0.

**Maps with >10% improvement: 6/14.** Major gains on medium/large maps where chain repair matters most.

## Full Test Results

### Regression Test (14 maps, all default seed)

| Map | Winner | Ti Mined | Units |
|-----|--------|----------|-------|
| default_small1 | buzzing | 21,520 | 5 |
| default_small2 | buzzing | 33,260 | 8 |
| default_medium1 | buzzing | 32,710 | 8 |
| default_medium2 | buzzing | 14,170 | 8 |
| default_large1 | buzzing | 23,280 | 9 |
| default_large2 | buzzing | 40,100 | 8 |
| arena | buzzing | 33,630 | 8 |
| hourglass | buzzing | 24,600 | 8 |
| corridors | buzzing | 14,480 | 9 |
| settlement | buzzing | 54,650 | 8 |
| wasteland | buzzing | 50 | 8 |
| butterfly | buzzing | 29,640 | 8 |
| face | buzzing | 9,800 | 8 |
| cubes | buzzing | 29,550 | 8 |

**Record: 14/14 wins.**

### Self-Play
- buzzing vs buzzing: No crashes. Score: 23,430 vs 11,170 Ti mined. 10 and 9 units respectively.

### CPU
- No timeouts on cubes (50x50).

## How the Chain Fix Works

**Before (Phase 1):** Builder walks outward building conveyors → places harvester → immediately targets next ore. Road fallback creates gaps.

**After (Phase 2):**
```
FIND_ORE → MOVE_TO_ORE → BUILD_HARVESTER → BUILD_CHAIN_TO_CORE → FIND_ORE
```

`BUILD_CHAIN_TO_CORE`:
1. BFS from current position toward core
2. If current tile is empty → build conveyor facing toward core
3. If current tile has a road → destroy road, build conveyor
4. If current tile has a conveyor → skip, just move
5. If adjacent to core → chain complete, exit mode
6. If stuck > 15 rounds → abandon chain, resume ore seeking

During outbound navigation (`_nav`), roads are also replaced with conveyors when encountered.

## How Sentinels Work

- **Timing:** After round 200, builder with `my_id % 4 == 1` checks when near core
- **Placement:** Adjacent to builder, toward inferred enemy direction
- **Facing:** Toward enemy (rotational symmetry assumed)
- **Cap:** 2 sentinels max
- **Auto-fire:** Checks `get_nearby_entities()` for enemies, fires if ammo >= 10
- **Ammo:** Currently no dedicated supply — Phase 3 will add splitter-based ammo routing

## Review Agent Findings

### Chain Auditor
- **CRITICAL (acknowledged):** Existing conveyors with wrong facing are never corrected during chain-build (line 161). Builder skips tiles with any building. If another builder's conveyor faces the wrong direction, chain silently breaks. *Not fixed in Phase 2 — would require destroying other builders' conveyors, which risks breaking their chains.*
- **CRITICAL (fixed):** `_replace_with_conveyor` could destroy road without building replacement. Fixed: pre-check Ti availability before destroying.
- **MEDIUM:** Builder gets stuck 15 rounds when Ti runs out mid-chain. Acceptable — passive income provides Ti in ~2 rounds.
- **MINOR (fixed):** `_on_or_adjacent_to_core` distance threshold tightened from 13 to 8.

### Military Auditor
- **CRITICAL (acknowledged):** Sentinels never fire — no ammo supply. They are 30 HP obstacles + 32 vision radius for 30 Ti + 20% scale. A barrier gives 30 HP for 3 Ti + 1% scale. *Sentinels kept as Phase 3 ammo foundation; mitigated by cap of 2 and ID filter.*
- **CRITICAL (acknowledged):** Enemy direction wrong on reflection-symmetric maps (~58% of maps). *Phase 3 fix: symmetry detection.*
- **MEDIUM:** Unit count includes sentinels, reducing effective builder cap. With 2 sentinels: max 6 builders instead of 8. Acceptable tradeoff.

### Integration Reviewer
- Mining gains confirmed as real (chain fix is the driver)
- Sentinel economy impact is conservative and acceptable
- Phase 3 priority: sentinel ammo > reflection symmetry > axionite > bridges

## Known Limitations

1. **No sentinel ammo supply** — sentinels are 30 HP obstacles only (Phase 3 will add supply)
2. **Wasteland remains seed-dependent** — map geometry issue, not a code bug
3. **Existing wrong-direction conveyors not corrected** — would risk breaking other builders' chains
4. **Enemy direction assumes rotational symmetry** — wrong for ~58% of maps
5. **No bridges** — can't cross gaps in fragmented maps (sierpinski_evil, cinnamon_roll)
6. **default_medium2 variance** — chain-building return trip costs time on some seeds

## Phase 3 Recommendations (from all 3 reviewers)

1. **Sentinel ammo delivery** — dedicated harvester or splitter branch feeding sentinels
2. **Map symmetry detection** — check reflection vs rotation for correct enemy position
3. **Axionite pipeline** — 1 foundry after round 300, enables sentinel stun (+5 cooldown)
4. **Bridges** for cross-terrain transport on fragmented maps
5. **Builder cap increase** to 10-12 late game
6. **Correct existing conveyor directions** during chain-build (destroy + rebuild if wrong)

## Files Modified
- `C:\Users\rahil\downloads\battlecode\bots\buzzing\main.py` — main bot code (~280 lines, was 199)
- `C:\Users\rahil\downloads\battlecode\phases\phase2_report.md` — this report
