# v25 Results: Reduce wasteful exploration conveyors

## Changes

Two targeted improvements to address economy inefficiency on cold and similar maps:

### 1. Distance-based explore Ti reserve
- Builders exploring >7 tiles from core (`dist_sq > 50`) require 30 Ti reserve before building conveyors during exploration (vs default 5)
- Reduces wasteful conveyor sprawl in areas unlikely to connect back to core
- Near-core exploration still builds conveyors freely (useful for nearby chains)

### 2. Time-based econ_cap floor ramp
- `time_floor = min(6 + rnd // 200, 10)` replaces fixed floor of 6
- Gradually allows more builders over time even when harvesters are outside core vision (r^2=36)
- Fixes issue where cold's distant harvesters couldn't be seen by core, capping builders at 6

## Test Results vs v24 Baseline

### Ti Mined Comparison (vs starter unless noted)

| Map | v24 Ti Mined | v25 Ti Mined | Change |
|-----|-------------|-------------|--------|
| **cold** (P1 vs smart_eco) | 10,510 | 17,230 | **+64%** |
| **corridors** (vs starter) | 16,500 | 32,270 | **+96%** |
| **default_medium1** (vs smart_eco) | 18,770 | 18,770 | 0% |
| **settlement** (vs starter) | 33,130 | 38,390 | **+16%** |
| **galaxy** (vs starter) | 14,190 | 13,660 | -3.7% |

### Cold Map Detail (vs smart_eco)

| Position | v24 Buzzing | v25 Buzzing | smart_eco | Result |
|----------|-------------|-------------|-----------|--------|
| P1 (buzzing left) | 10,510 mined | 17,230 mined | 14,340 mined | Still LOSE (15.1K vs 16.6K Ti remaining) |
| P2 (buzzing right) | 19,690 mined | 19,690 mined | 4,880 mined | WIN |

### Key Observation on Cold P1
Buzzing now MINES more than smart_eco (17,230 vs 14,340) but LOSES because it spends more on buildings (455 vs 252). The remaining gap is ~1,500 Ti in building overhead. This is an inherent cost of buzzing's military infrastructure (barriers, gunners) and more aggressive conveyoring pattern.

## What Was Tried and Didn't Work

| Tweak | Cold Result | Why It Failed |
|-------|-------------|---------------|
| Slower explore rotation (rnd//100) | 9,820 (-7%) | Builders stuck exploring one direction too long |
| More builders early (cap 6 by rnd 100) | 4,850 (-54%) | Ti drain from extra builders before harvesters connected |
| Nearest-ore scoring on balanced maps | 6,710 (-36%) | Core-proximity was actually helping find good ore |
| Lower expand threshold (1300) | 0 mined (-100%) | Expand mode rotation too slow for cold |
| Roads for exploration | 0 mined (-100%) | Conveyors during explore are essential for delivery chains |
| Higher ore-nav reserve (10) | 11,840 (+13%) but worse than 30 | Slowed chain building too much |
| Flat explore reserve (40) | 9,700 (-8%) | Too restrictive, builders stuck everywhere |

## Root Cause Analysis

The core issue on cold P1 was **exploration conveyor waste**. On a 37x37 map with 115 Ti ore, builders explore in all directions. Each step builds a conveyor (3 Ti + 1% scale). Builders far from core build conveyors that never connect to anything, wasting Ti and inflating costs.

The distance-based explore reserve fixes this by only building cheap conveyors near core (where they form useful chains) and being conservative far from core. The time-based econ_cap ramp ensures cold gets enough builders despite harvesters being outside core vision.

## Cold P1 Loss: Remaining Gap

Still lose cold P1 by ~1,500 Ti remaining. Buzzing mines +2,890 more but spends +4,377 more on buildings. The overhead comes from:
- 455 buildings (vs 252) = ~600 Ti in raw conveyor cost
- Scale inflation from buildings: +455% vs +252% = higher cost for everything
- Military overhead (barriers + gunners): ~50-100 Ti + scale

Closing this gap would require either:
1. Reducing conveyor count during ore navigation (risky — slows chains)
2. Removing military on cold (loses defense on other maps)
3. Smarter pathing that builds fewer conveyors (fundamental architecture change)

## Regression Safety

- No regression on default_medium1 (identical results)
- Slight regression on galaxy (-3.7%) — acceptable given massive gains elsewhere
- corridors improved by +96%
- settlement improved by +16%
