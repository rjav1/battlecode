# v50 Conveyor Cap Implementation Test

Date: 2026-04-06

## Summary

CONVEYOR CAP IMPLEMENTATION WAS REVERTED. The cap caused chain-connectivity failures
that reduced Ti mined on default_medium1 by making harvesters unreachable.

---

## What Was Implemented

4 changes to bots/buzzing/main.py:
1. __init__: self._conveyors_this_trip = 0
2. _nav: cap check before build: conv_cap = max(8, min(w,h)//2), skip if over cap
3. _nav: increment counter after build
4. Reset counter at: harvester built, target change, stuck reset

Cap values tested:
- Formula 1: max(8, min(w,h)//2) -> gaussian=10, cold=18, default_medium1=15
- Formula 2: max(10, min(w,h)*2//3) -> gaussian=13, cold=24, default_medium1=20
- Formula 3: max(12, min(w,h)-10) -> gaussian=12, cold=27, default_medium1=20

---

## Test Results

### Regression suite (formula 1, cap=15 on default_medium1)
PASS verdict (3W-2L) but default_medium1 seed=1 LOST (was WIN before cap).

### buzzing vs balanced -- gaussian (formula 1, cap=10)
Before: 7940 mined, 236 buildings
After:  12330 mined, 160 buildings -- IMPROVED +55% mined, -32% buildings

### buzzing vs smart_eco -- gaussian (formula 1, cap=10)
Before: 14910 mined, 238 buildings
After:  19840 mined, 153 buildings -- IMPROVED +33% mined, -36% buildings

### buzzing vs smart_eco -- default_medium1 (formula 1, cap=15)
Before (no cap):    9820 mined, 251 buildings -- WIN vs smart_eco
After (cap=15):     9100 mined,  87 buildings -- LOSS vs smart_eco

CRITICAL: With cap=15, buzzing built only 87 buildings (was 251).
Buildings halved but Ti mined DROPPED. This means harvesters are orphaned --
chain gaps >3 tiles that bridge shortcut cannot span.
Buzzing stored MORE Ti (10204 vs smart_eco 9865) but lost on total-delivered
tiebreaker -- confirming harvesters producing but not delivering.

### Formulas 2 and 3 (cap=20 on default_medium1)
Same result -- 87 buildings, 9100 mined. The cap still cuts short.
Conclusion: default_medium1 ore requires >20 conveyor steps from core.

---

## Root Cause of Failure

The conveyor cap design assumed the bridge shortcut (range d2<=9, ~3 tiles) would
cover the gap when builders stop building conveyors before reaching ore.

WRONG: Ore on default_medium1 is 20+ steps from core. With cap=15-20, the builder
walks the last 5-10 steps without conveyors. A 5-10 tile gap cannot be bridged (max 3).
The harvester is built but disconnected -- producing Ti with no delivery path.

The "248 buildings -> 87 buildings" collapse confirms this: builders are NOT building
the full chain, leaving harvesters stranded. The Ti accumulates at ore sites.

---

## What Was Reverted

All 4 changes reverted. bots/buzzing/main.py is back to pre-cap state.
Verified: default_medium1 seed=1 = 9100 mined, 117 buildings (matches baseline).

---

## Lessons Learned

1. A simple per-trip conveyor cap does not work when ore is genuinely far (20+ steps).
2. Bridge range (d2<=9=3 tiles) is too short to cover chain gaps from premature cap.
3. The gaussian improvement (cap=10) worked because gaussian ore is 10-15 steps away
   and bridge could cover the 0-5 step gap. But default_medium1 ore is 20+ steps.

## Alternative Approaches to Reduce Conveyor Waste

The conveyor waste problem is real but requires a different solution:

A. REDUCE EXPLORE CONVEYORS: _explore calls _nav with conveyor mode.
   Exploration builds conveyors to nowhere. Switching to use_roads=True in _explore
   would cut explore-phase conveyor waste without breaking delivery chains.
   (These explore conveyors have 0 delivery value.)

B. MAP RECLASSIFICATION: gaussian is classified as "balanced" (area=700) but should
   be "tight" (min dim=20). Tight mode uses simpler exploration that avoids long
   maze detours. This alone could fix gaussian without any conveyor cap.
   Fix: if min(w,h) <= 22, use tight mode regardless of area.

C. DON'T BUILD CONVEYORS ON RETURN TRIPS (fix_chain rebuilds are fine).
   Track whether builder is in "inbound" (going to ore) or "outbound" (exploring).
   Only build conveyors when inbound and have a real ore target.

Recommendation: Implement A (explore road mode) and B (min-dim reclassification)
as the next two fixes. These are lower risk than the cap approach.
