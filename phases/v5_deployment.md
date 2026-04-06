# v5 Deployment: Definitive Merge

**Submitted:** 2026-04-04
**Version:** 8 (ID: 0166566e-b267-469e-93aa-8d3ea9ec017a)
**File:** `bots/buzzing/main.py` (578 lines, 13 methods)

## Changes from Previous Versions

### From phase6-builder (economy base):
- d.opposite() conveyors for ALL navigation (proven to deliver Ti)
- BFS pathfinding within vision
- Build harvesters on Ti ore, conveyors trail behind builder
- Symmetry detection for enemy direction
- Sentinel placement via splitter pattern
- Attacker raider after round 500

### New in v5 (merged improvements):
1. **Moderate builder scaling** (was 3/5/7 or 3/8/15/25/40):
   - Round 1-20: cap 3
   - Round 21-100: cap 6
   - Round 101-300: cap 10
   - Round 301-600: cap 15
   - Round 601+: cap 20
   - Economy cap: min(round_cap, visible_harvesters * 2 + 3)

2. **Lower reserves** (spend more aggressively):
   - Core spawn: cost + 10 (was +30)
   - Harvester: cost + 5 (was +15)
   - Conveyor: cost + 5 (was +15)
   - Sentinel infra: cost + 30 (was +50)

3. **Road-destroy fix** (from critic review):
   - When building conveyor at nxt and allied road exists, destroy road first then build conveyor
   - Prevents chain gaps where roads block conveyor placement

4. **Bridge fallback threshold**: cost + 50 (was +200, too stingy)

5. **Earlier sentinels**: round 200 (was 1000), cap 3 (was 2)

6. **Enhanced attacker**: moves onto adjacent enemy buildings to attack them

7. **Barrier walls**: 6 barriers on enemy-facing side of core after round 80

8. **Bounds check**: prevents "Position out of bounds" error in nav

9. **Enemy core caching**: avoids recomputing symmetry every tick

## Test Results (buzzing vs starter, 10-0 SWEEP)

| Map | Ti Mined | Units | Buildings | Result |
|-----|----------|-------|-----------|--------|
| default_small1 | 24,430 | 7 | 95 | WIN |
| default_medium1 | 14,640 | 5 | 185 | WIN |
| default_large1 | 13,810 | 9 | 343 | WIN |
| settlement | 19,660 | 3 | 427 | WIN |
| cold | 7,490 | 3 | 137 | WIN |
| landscape | 19,310 | 3 | 92 | WIN |
| corridors | 15,730 | 17 | 226 | WIN |
| face | 9,880 | 5 | 82 | WIN |
| arena | 19,410 | 5 | 133 | WIN |
| cubes | 19,590 | 3 | 69 | WIN |

**Average Ti mined: 16,395**
**Min: 7,490 (cold -- limited ore)**
**Max: 24,430 (default_small1)**

### Self-play:
| Map | P1 Ti (mined) | P2 Ti (mined) | P1 Buildings | P2 Buildings |
|-----|---------------|---------------|-------------|-------------|
| default_medium1 | 25,690 (21,370) | 20,981 (16,790) | 83 | 120 |

No crashes in self-play.

## Comparison vs Previous Versions

| Metric | v3 (eco) | v4 (40-cap) | v5 (merged) |
|--------|----------|-------------|-------------|
| Builder cap | 7 max | 40 max | 20 max (econ-limited) |
| Avg Ti mined | ~15K | ~13K | **16,395** |
| Bridge threshold | +200 | +200 | +50 |
| Harvester reserve | +15 | +5 | +5 |
| Sentinel timing | round 600 | round 1000 | **round 200** |
| Sentinel cap | 2 | 2 | **3** |
| Road-destroy | No | No | **Yes** |
| Barriers | No | No | **Yes (6 max)** |
| Attacker | Basic | Basic | **Enhanced (adjacent)** |
| Win rate vs starter | 8/8 | 5/5 | **10/10** |

## Features Included

- [x] d.opposite() conveyor economy
- [x] BFS pathfinding
- [x] Moderate builder scaling (cap 20, econ-limited)
- [x] Lower reserves for aggressive spending
- [x] Road-destroy fix for conveyor placement
- [x] Bridge fallback across walls
- [x] Splitter-based sentinel placement (cap 3)
- [x] Barrier walls near core (cap 6)
- [x] Attacker raider with adjacent-building targeting
- [x] Symmetry detection + enemy core caching
- [x] Bounds checking in nav

## Features NOT Included (for future iterations)

- [ ] Sentinel ammo delivery (splitters placed but no dedicated ammo chain yet)
- [ ] Launcher drops
- [ ] Marker-based builder coordination
- [ ] Axionite/foundry economy
- [ ] Scale awareness (stop building when scale > 300%)
- [ ] Map-specific adaptation

## Known Limitations

1. Sentinels are placed but won't have ammo (no dedicated ammo chain from harvesters)
2. Barriers are placed reactively when builders happen to be near core
3. Builder count still driven by round curve primarily (econ cap helps but core can only see nearby harvesters)
4. No coordination between builders -- may duplicate harvester coverage
5. Some "Position out of bounds" errors still possible in bridge fallback (non-fatal, caught by exception)
