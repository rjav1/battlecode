# Rush Bot vs v6 Buzzing — April 6, 2026

## Context

The rush bot reportedly beat buzzing 8-3, but that may have been against the broken v4. This tests against the current v6 buzzing (with economy fix applied).

**IMPORTANT: Two bugs found in v6 buzzing during these tests:**
1. `AttributeError: 'Player' object has no attribute '_build_barriers'` — on default_medium1, settlement, arena
2. `GameError: Position out of bounds` — on face (both sides)

These bugs crash individual units but don't forfeit the game. However, they likely degrade buzzing's performance significantly.

## Results: Rusher as Team A

| Map | Rusher Ti (mined) | Buzzing Ti (mined) | Winner | Buzzing Error? | Notes |
|-----|-------------------|-------------------|--------|----------------|-------|
| face | 10,743 (9,850) | 25 (710) | **rusher** | Position out of bounds | Buzzing down to 1 unit |
| corridors | 9,764 (4,990) | 15,038 (9,930) | **buzzing** | None | Clean win |
| default_medium1 | 15 (4,920) | 53 (14,810) | **buzzing** | _build_barriers | Both near 0 final Ti |
| settlement | 10 (0) | 38 (10,090) | **buzzing** | _build_barriers | Rusher mines 0 |
| arena | 10 (0) | 87 (8,420) | **buzzing** | _build_barriers | Rusher mines 0 |

**Rusher as A: 1 win, 4 losses**

## Results: Buzzing as Team A (Side Swap)

| Map | Buzzing Ti (mined) | Rusher Ti (mined) | Winner | Buzzing Error? |
|-----|-------------------|-------------------|--------|----------------|
| face | 43 (410) | 10,660 (9,930) | **rusher** | Position out of bounds |
| default_medium1 | 16 (1,570) | 11 (0) | **buzzing** | Position out of bounds |

**Buzzing as A on face: loses. Buzzing as A on default_medium1: wins.**

## Overall Score: Rusher 2 — Buzzing 5

| Map | Rusher=A | Buzzing=A | Map Winner |
|-----|---------|-----------|------------|
| face | **rusher** | **rusher** | **RUSHER** (both sides) |
| corridors | **buzzing** | -- | **BUZZING** |
| default_medium1 | **buzzing** | **buzzing** | **BUZZING** (both sides) |
| settlement | **buzzing** | -- | **BUZZING** |
| arena | **buzzing** | -- | **BUZZING** |

## Key Findings

### 1. Face is a definitive rusher win
Rusher wins on face from BOTH sides. This is the only map where rusher dominates. face is a 20x20 map with path=9 (shortest in the game) and only 8 Ti ore. The rush arrives before buzzing can establish economy. Rusher mines 9,850-9,930 Ti while buzzing mines only 410-710.

**Why rusher wins on face:**
- Path to enemy is only 9 steps -- attackers arrive by round ~15
- 4 builders spawned by R8, 2 become attackers immediately
- Attackers destroy buzzing's conveyors before resources flow
- Buzzing has a `Position out of bounds` bug on face that crashes units

### 2. Buzzing v6 wins everywhere else
On corridors (path=46), default_medium1 (path=18), settlement (path=45), arena (path=12): buzzing's economy + sentinels outperform rusher. Even on arena (path=12, a rush map), buzzing wins because it mines 8,420 vs rusher's 0.

### 3. Buzzing v6 has critical bugs

**Bug 1: `_build_barriers` AttributeError**
Occurs on default_medium1, settlement, arena. The code calls `self._build_barriers()` but the method doesn't exist. This crashes the builder that triggers it but other units continue. The bug fires on 3/5 maps -- needs immediate fix.

**Bug 2: `Position out of bounds` GameError**
Occurs on face (both sides). The code accesses `c.get_tile_building_id(nxt)` with an out-of-bounds position. This crashes the affected unit. On face (20x20), units hit map edges frequently.

### 4. Rusher's economy is fatally weak
Rusher mines 0 Ti on settlement and arena. On default_medium1, it mines 4,920 vs buzzing's 14,810. Only 2 builders do economy (the rest attack). When ore is far from core, 2 builders can't find it.

### 5. The 8-3 result was likely against broken v4
The broken v4 buzzing mined 0 Ti on every map. Against that, rusher's 4,980 Ti from 2 economy builders would win easily. Against v6 which mines 8,000-15,000 Ti, rusher can only win on face.

## Rusher Attack Effectiveness

| Map | Path | Rusher Disruption | Outcome |
|-----|------|-------------------|---------|
| face | 9 | High -- arrives fast, destroys chains | Wins |
| arena | 12 | Low -- buzzing already established | Loses |
| default_medium1 | 18 | Low -- too far, buzzing mines 3x more | Loses |
| corridors | 46 | None -- maze prevents reach | Loses |
| settlement | 45 | None -- too far | Loses |

**Rush attack only works when path <= 9.** On path 12+ maps, the attacker arrives too late or can't navigate walls.

## Recommendations

1. **Fix `_build_barriers` bug immediately** -- crashes on 3/5 maps tested
2. **Fix `Position out of bounds` bug** -- add bounds checking in nav code
3. **Don't worry about rush defense on most maps** -- rusher only wins on face (path=9). Our sentinels + economy are enough.
4. **Consider rush defense for path <= 12 maps** -- face (9), arena (12), starry_night (9). Early sentinel placement or barrier walls could block rush.
5. **Incorporate rusher's fast spawn** -- 4 builders by R8 is faster than buzzing's ramp. More early builders = faster economy.
