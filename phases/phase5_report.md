# Phase 5 Report: Attacker, Sentinel Cleanup, Ladder Submission

## Changes Made

### Change 1: Sentinel Ammo Supply (ATTEMPTED → REVERTED)
Multiple approaches tested to deliver ammo to sentinels:

1. **Feed conveyor approach**: Build a conveyor adjacent to sentinel facing toward it. **FAILED** — the conveyor has no resource source; it's not connected to any chain.

2. **Chain intercept approach**: Destroy a chain conveyor and build sentinel at that position. **FAILED** — debug showed ammo = 0 across all 2000 rounds on every test. The game's resource distribution from conveyors to turrets may require specific conditions not met by our setup. Additionally, destroying the chain conveyor BREAKS the economy (resources from that harvester never reach core).

3. **Reverted to Phase 4 approach**: Sentinels placed on empty tiles near conveyors. They serve as 30 HP obstacles with 32 vision radius. Auto-fire code is present for when ammo becomes available (e.g., from splitter-based routing in a future phase).

**Key finding**: Sentinel ammo delivery requires SPLITTERS to branch resources from the main chain. Without splitters, any approach either breaks the chain or doesn't deliver resources. This is a Phase 6+ problem.

### Change 2: Basic Attacker (KEPT)
One builder (ID % 4 == 2) becomes an attacker after round 400:
- Only activates after building 2+ harvesters (contributed to economy first)
- Navigates toward enemy core position (symmetry-detected)
- Attacks enemy buildings on its tile via `c.fire(pos)` (2 damage, 2 Ti cost)
- Uses the same `_nav` infrastructure (builds conveyors/roads while walking)

**Implementation**: Added `_attack` method that:
1. Checks for enemy building on current tile → attacks if found
2. Computes enemy core position from detected symmetry
3. Navigates toward enemy core using `_nav`

### Change 3: Ladder Submission (DONE)
- Bot submitted as Version 2 (ID: bd25a156-41ca-48bb-8ddc-78abbc9ae4be)
- Package size: 3.2 KB
- Single file: `bots/buzzing/main.py`

## Test Results

### Full Regression (17 maps, default seed)

| Map | Winner | Ti Mined | Units | Notes |
|-----|--------|----------|-------|-------|
| default_small1 | WIN | 28,660 | 8 | |
| default_small2 | WIN | 23,570 | 9 | |
| default_medium1 | WIN | 37,100 | 8 | |
| default_medium2 | WIN | 18,270 | 8 | |
| default_large1 | WIN | 32,470 | 10 | Sentinels active |
| default_large2 | WIN | 29,050 | 13 | |
| arena | WIN | 34,100 | 9 | |
| hourglass | WIN | 23,190 | 10 | |
| corridors | WIN | 16,470 | 8 | |
| settlement | WIN | 54,610 | 13 | |
| wasteland | LOSS | 0 | 12 | Map geometry issue |
| butterfly | WIN | 29,760 | 8 | |
| face | WIN | 13,720 | 9 | |
| cubes | WIN | 31,820 | 10 | |
| cold | WIN | 7,360 | 8 | |
| starry_night | WIN | 26,400 | 15 | |
| dna | WIN | 25,280 | 10 | |

**Record: 16/17 wins**

### vs test_attacker Bot
| Map | Winner | Our Ti | Their Ti |
|-----|--------|--------|----------|
| face | WIN | 34,670 | 0 |
| default_medium1 | WIN | 22,950 | 0 |
| corridors | WIN | 9,940 | 0 |
| arena | WIN | 19,190 | 0 |

### Self-Play
- No crashes. 13 vs 10 units. Both sides build sentinels.

### CPU
- No timeouts on cubes (50x50). 35,810 Ti mined.

## Sentinel Ammo Investigation

Extensive testing proved that sentinel ammo delivery doesn't work without splitters:

| Approach | Result | Why |
|----------|--------|-----|
| Feed conveyor | 0 ammo | Conveyor not connected to any resource chain |
| Chain intercept | 0 ammo | Tested with debug logging: ammo=0 at every 100-round checkpoint across 2000 rounds. Also breaks the chain economy. |
| Direct placement near chain | 0 ammo | Adjacent conveyors push toward core, not toward sentinel |

**Conclusion**: The game requires conveyors to DIRECTLY PUSH (output) resources TO the turret's tile from a non-facing side. This requires either:
- A splitter that branches 1/3 of resources to a feed conveyor → sentinel
- A dedicated harvester with conveyors pointed at the sentinel
Both require multi-round state machines and are deferred to Phase 6.

## Ladder Submission

- **Version**: 2 (bd25a156-41ca-48bb-8ddc-78abbc9ae4be)
- **Size**: 3.2 KB
- **Status**: Submitted and active
- **Starting Elo**: 1500 (default)
- **First matches**: Awaiting automatic matchmaking (every 10 min)

## Known Limitations

1. **Sentinels never fire** — no ammo without splitters
2. **Wasteland still loses** — map geometry blocks ore access
3. **Attacker is basic** — walks toward enemy but may not reach them on large maps
4. **Single attacker** — only 1 builder raids (1/8 of workforce)
5. **No splitters** — can't branch resource chains
6. **No markers** — builders don't coordinate
7. **No launcher drops** — can't throw builders across walls

## Phase 6 Recommendations

Based on what we know from testing and top team analysis:

1. **Splitter-based sentinel ammo** — branch 1/3 of a chain's resources to feed sentinels
2. **Earlier sentinels** — round 100 instead of 200 (real opponents rush earlier)
3. **More attackers on narrow maps** — detect map geometry, send 2-3 attackers on face/arena
4. **Launcher placement** — launchers throw builders across walls (powerful on fragmented maps)
5. **Barrier walls** — cheap (3 Ti, 30 HP) defensive walls to slow enemy rushes
6. **Match analysis** — study ladder losses to identify what real opponents do differently

## Files Created/Modified

- `C:\Users\rahil\downloads\battlecode\bots\buzzing\main.py` — main bot (~260 lines)
- `C:\Users\rahil\downloads\battlecode\bots\test_attacker\main.py` — test opponent
- `C:\Users\rahil\downloads\battlecode\phases\phase5_report.md` — this report
