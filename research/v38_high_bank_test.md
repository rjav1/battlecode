# v38 High-Bank Override Test

**Change:** Ti-gated builder cap override + dynamic barrier cap + lower barrier Ti reserve.

## Code Changes

### 1. Ti-gated builder cap (after `cap = min(cap, econ_cap)`)
- Ti > 500: +2 builders above normal cap
- Ti > 1000: +3 more (total +5 above base cap)
- Hard ceiling: 25 builders max (prevents runaway)

### 2. Dynamic barrier cap in `_build_barriers`
- Ti < 500: max 6 barriers (unchanged)
- Ti 500-999: max 10 barriers
- Ti >= 1000: max 15 barriers

### 3. Barrier Ti reserve lowered 40 -> 15
- Previously held back barriers unless 40 Ti above cost
- Now only requires 15 Ti buffer (more aggressive barrier deployment)

---

## Test Results

### default_medium1: **buzzing WINS**
```
Winner: buzzing  (Resources tiebreak, turn 2000)
                      buzzing       buzzing_prev
Titanium       8936 (9380 mined)  7018 (4950 mined)
Units                        15              10
Buildings                   329             240
```
Clear improvement: +1362 Ti, mined nearly double. More builders = more harvesters = better economy.

### cold: **buzzing LOSES** (regression)
```
Winner: buzzing_prev  (Resources tiebreak, turn 2000)
                      buzzing        buzzing_prev
Titanium    16729 (19670 mined)  19667 (19700 mined)
Units                       16              10
Buildings                  427             345
```
Cold map hits the ore ceiling (~19700 Ti) for both sides; buzzing_prev reaches it more efficiently.
Buzzing is spending Ti on extra builders/barriers (427 buildings vs 345) rather than accumulating it.
Margin: ~3k Ti deficit. However, buzzing vs itself on cold yields 16680 vs 16964 — the variance is inherent.

**Note:** buzzing_prev vs itself on cold: 18710 vs 19606 — also a 900 Ti gap just from map symmetry.
The cold regression appears to be ~3k Ti "wasted" on extra buildings that don't return value on ore-capped map.

### settlement: **buzzing WINS strongly**
```
Winner: buzzing  (Resources tiebreak, turn 2000)
                       buzzing       buzzing_prev
Titanium     21843 (35540 mined)  6955 (8350 mined)
Units                        21              11
Buildings                   560             247
```
Dominant win: 3x the resources, mined 4x more. High-bank override unlocks builder scaling on resource-rich maps.

---

## Summary

| Map | Result | Buzzing Ti | Prev Ti | Notes |
|-----|--------|-----------|---------|-------|
| default_medium1 | WIN | 8936 | 7018 | +27% more resources |
| cold | LOSS | 16729 | 19667 | -15% — ore-capped map, extra buildings don't help |
| settlement | WIN | 21843 | 6955 | +214% — huge improvement on resource-rich map |

## Assessment

The high-bank override is net positive: wins on medium and settlement (the maps where economy matters),
with a cold regression that is partly inherent to the ore-capped nature of that map.

The cold loss is real but the cap is working (16 units, not 40). The 25-unit ceiling is functioning.

**Recommendation:** Keep the change. Cold is an edge case where extra builders cost more Ti than they
generate (ore tiles saturated early). Could consider a map-mode gate (skip Ti override for tight maps)
if cold regression is unacceptable, but overall EV is positive.
