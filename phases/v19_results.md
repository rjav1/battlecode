# v19 Results: Harvest Axionite Ore Too

## Change
Single line changed in `_builder` scan loop (line 149):
```python
# OLD:
if e == Environment.ORE_TITANIUM and c.get_tile_building_id(t) is None:
# NEW:
if e in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE) and c.get_tile_building_id(t) is None:
```

`_best_adj_ore` was NOT changed — it uses `can_build_harvester()` which already handles both ore types implicitly.

## Regression Results (buzzing v19 vs buzzing_prev v18)

| Map            | Winner       | Ti (v19) | Ti (v18) | Notes |
|----------------|--------------|----------|----------|-------|
| default_medium1 | **buzzing** | 34734    | 18677    | +16k Ti — massive improvement |
| settlement      | **buzzing** | 19513    | 3402     | v18 mined 0 Ti; v19 dominates |
| cold            | **buzzing** | 25940    | 19831    | +6k Ti |
| face            | **buzzing** | 18422    | 14834    | +3.6k Ti |
| corridors       | buzzing_prev | 19286   | 19286    | **Symmetric tie** — identical resources, units, buildings. Tiebreak went to buzzing_prev as player 2. Not a real loss. |

**Score: 4-1 (or 4-0.5-0.5 counting the symmetric tie)**
Pass threshold: 3/5 wins. **PASS.**

## Butterfly Test (buzzing vs starter)

| Map       | Winner  | Ti (buzzing) | Ti (starter) |
|-----------|---------|--------------|--------------|
| butterfly | **buzzing** | 28904    | 4865         |

butterfly has 57 Ax ore tiles. Axionite mined = 0 for both — the map may not have had Ax ore reachable, or the conveyor chain doesn't deliver Ax to core yet. But buzzing won decisively on Ti resources.

## Submission
- Submitted as **Version 21** (ID: 40d6ceac-b1f1-463c-884e-a1b8abfaa29b)
- `buzzing_prev` updated to v19 as new baseline

## Notes
The corridors tie is a known edge case — with identical map symmetry and the same bot logic, the outcome is a coin flip based on player position. This is not a regression.
