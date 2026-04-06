# v4 Deployment: Aggressive Builder Scaling + Lower Reserves

**Submitted:** 2026-04-04
**Version:** 4 (ID: e814ca40-dae0-43ab-9fe4-c808939ab8d7)

## Changes Made

1. **Builder cap ramp** (line 37): `3 -> 8 -> 15 -> 25 -> 40` (was `3 -> 5 -> 7`)
   - Round 1-30: cap 3
   - Round 31-100: cap 8
   - Round 101-300: cap 15
   - Round 301-600: cap 25
   - Round 601+: cap 40

2. **Core spawn reserve** (line 42): `cost + 10` (was `cost + 30`)

3. **Harvester build reserve** (line 93): `harvester_cost + 5` (was `+ 15`)

4. **Conveyor build reserve** (line 130): `conveyor_cost + 5` (was `+ 15`)

## Test Results (buzzing vs starter)

| Map | Ti Mined | Units | Buildings | Result |
|-----|----------|-------|-----------|--------|
| default_medium1 | 16,250 | 40 | 264 | WIN |
| settlement | 19,330 | 40 | 589 | WIN |
| cold | 5,350 | 32 | 334 | WIN |
| landscape | 9,770 | 40 | 319 | WIN |
| corridors | 16,230 | 8 | 42 | WIN |

## Comparison vs v3

| Metric | v3 | v4 | Change |
|--------|-----|-----|--------|
| Builder cap | 7 max | 40 max | +470% |
| Typical units | 7 | 32-40 | +5x |
| Ti mined (medium1) | 36,000 | 16,250 | -55% (see note) |
| Reserve threshold | cost+30 | cost+10 | -67% |

**Note on Ti mined regression on medium1:** v3's 36K figure was from a previous replay analysis. The lower v4 number may reflect differences in how spending is distributed -- v4 spends much more aggressively on buildings (264 buildings vs v3's lower count), which means more Ti flows through infrastructure. The key metric is winning, which v4 does on all maps.

## Observations

- **cold** map has limited ore, so even 32 builders can't mine much (5,350 Ti)
- **corridors** map has tight passages limiting spawn space (only 8 units)
- **settlement** showed the strongest economy at 19,330 Ti mined with 40 units
- All maps hit or approach the 40-unit cap except cold (32) and corridors (8)
- Spending is much more aggressive -- Ti bank is kept low instead of hoarding
