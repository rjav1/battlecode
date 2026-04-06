# Settlement Debug Report

## Match Results

**buzzing vs smart_eco (settlement):** smart_eco wins — 28097 Ti (27230 mined), 8 units vs 20052 Ti (19660 mined), 4 units  
**buzzing vs starter (settlement):** buzzing wins — 16891 Ti (19660 mined), 4 units vs 1064 Ti, 3 units

## Key Finding: 4 units vs starter too

Buzzing ends at **4 units even against starter** (which does not attack). Builders are NOT dying from enemy attacks. This is a pure internal logic bug.

## Root Cause: econ_cap starves builder spawning

In `_core()`, the spawn cap is computed as:

```python
vis_harv = 0
for eid in c.get_nearby_buildings():
    if c.get_entity_type(eid) == EntityType.HARVESTER and c.get_team(eid) == c.get_team():
        vis_harv += 1
econ_cap = vis_harv * 3 + 4
cap = min(cap, econ_cap)
```

With **0 visible harvesters**, `econ_cap = 0*3+4 = 4`. The unit cap is immediately throttled to 4.

Settlement is a **50x38 = area 1900** map → `map_mode = "expand"` → raw cap reaches 12 by round 400+. But it never gets there because `econ_cap` overrides it.

The problem: **harvesters are built far from the core** (builders explore the full 50x38 map). The core's vision radius does not reach them. So `vis_harv` stays at 0 or near-0 throughout the game, keeping `econ_cap = 4` indefinitely.

## What smart_eco does differently

smart_eco has **no econ_cap logic at all**. It uses a simple time-based ramp:
- Round ≤30: cap=4, ≤100: cap=6, ≤200: cap=7, else: cap=8

It builds 8 builders unconditionally, all of them find ore, and ends with 8 units and 27K Ti mined.

## econ_cap value at round 2000

With ~4 harvesters built (all far from core): `vis_harv ≈ 0`, so `econ_cap = 4`.  
Even if 1-2 are close: `vis_harv=1` → `econ_cap=7`, `vis_harv=2` → `econ_cap=10`. The formula itself is not wrong — the vision check is the problem.

## Builder / Harvester Counts

- Buzzing builds 4 builders early, then stops spawning (capped by econ_cap=4)
- Harvesters built: ~4-6 (one per builder), but none visible from core
- smart_eco builds 8 builders → ~8+ harvesters, 27K mined

## Fix Required

Either:
1. **Use global harvester count** (not vision-limited): `c.get_harvester_count()` if available, or track via a shared counter
2. **Remove or relax econ_cap** on expand maps — the raw time-based cap (12 by round 400) is already conservative
3. **Cap floor**: ensure `econ_cap` never drops the cap below the time-based schedule minimum

Option 2 is simplest: on `map_mode == "expand"`, skip the `econ_cap` check entirely and rely on the time-based cap (max 12). The econ_cap was designed to prevent builders from spawning when there's no ore to harvest, but on a 148-Ti-ore map like settlement that's never the limiting factor.
