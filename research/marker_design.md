# Marker-Based Ore Claiming: Design Document

## Problem

Builders operate in isolated Python instances with no shared state. On maps with scattered ore (galaxy, arena, butterfly), two or more builders frequently target the same ore tile, wasting one builder's entire trip. The only inter-unit communication channel is markers.

## 1. Encoding Scheme

**Simple approach: `CLAIMED = 1`**

Any non-zero marker on an ore tile means "claimed." No need for builder ID, round number, or bitpacking. Rationale:

- We only need to answer one question: "is another builder already heading here?"
- Markers are fragile (1 HP) and easily destroyed by enemies, so stale-claim recovery via round encoding is unreliable anyway.
- Simpler encoding = fewer bugs, less CPU time parsing.

```python
CLAIM_VALUE = 1  # Any non-zero u32 value = "this ore is claimed"
```

**Why not encode builder ID or round?**
- Builder ID: useless because we can't cancel our own claim (marker might be out of vision/action range by then).
- Round number: staleness detection sounds nice but adds complexity. A simpler approach handles staleness: if we arrive at the ore and it already has a building, the claim is irrelevant.

## 2. Integration Points in main.py

### 2a. Claiming: after choosing a target ore tile

Location: `_builder()` method, after the ore scoring loop (line ~315 in current code).

```python
# After selecting self.target from ore_tiles:
if self.target and self.target != old_target:
    # Place claim marker on the target ore tile if within action range
    if c.can_place_marker(self.target):
        c.place_marker(self.target, CLAIM_VALUE)
        self._claimed_pos = self.target
```

**Constraint:** `can_place_marker(pos)` requires the position to be within the builder's action radius (distance_squared <= 2). The builder is usually NOT adjacent to its target when it first picks it. So the marker must be placed **when the builder arrives near the tile**, not when it first picks the target.

Revised approach — place the marker as the builder approaches:

```python
# In _builder(), after navigation, each round:
if (self.target
        and not getattr(self, '_marker_placed', False)
        and c.can_place_marker(self.target)):
    c.place_marker(self.target, CLAIM_VALUE)
    self._marker_placed = True
```

Reset `_marker_placed = False` whenever `self.target` changes.

### 2b. Respecting claims: when scanning ore tiles

Location: `_builder()` method, inside the ore-scanning loop (line ~178).

```python
# When building ore_tiles list, skip tiles that have a claim marker:
if c.get_tile_building_id(t) is None:
    # Check for existing claim marker
    marker_id = c.get_tile_building_id(t)  # markers ARE buildings (EntityType.MARKER)
    # Wait -- markers occupy a tile like buildings. So get_tile_building_id()
    # returns the marker's ID if a marker is on the tile.
    # But if a marker is on the tile, can_build_harvester() would fail anyway
    # since the tile isn't empty.
```

**Critical discovery: markers ARE buildings.** From the API:
- `EntityType.MARKER` is in the building types
- Markers have 1 HP, are placed on tiles
- `get_tile_building_id(pos)` returns marker IDs

This means: **if we place a marker on an ore tile, we CANNOT build a harvester there** until the marker is destroyed/removed.

**This changes the design fundamentally.** We cannot place markers directly ON ore tiles because:
1. A marker on the ore tile blocks harvester construction
2. The builder would need to `destroy()` its own marker before building the harvester
3. `destroy()` works on allied buildings within action radius -- so this IS possible, but adds a step

Revised protocol with destroy step:

```python
# When arriving at ore tile to build harvester:
# 1. Check if our claim marker is on the tile
# 2. Destroy the marker
# 3. Build the harvester

# In _best_adj_ore or before building:
for d in DIRS:
    p = pos.add(d)
    bid = c.get_tile_building_id(p)
    if bid is not None:
        try:
            if (c.get_entity_type(bid) == EntityType.MARKER
                    and c.get_team(bid) == c.get_team()):
                c.destroy(p)  # No cooldown cost!
                # Now can_build_harvester should work
        except Exception:
            pass
    if c.can_build_harvester(p):
        # ... build it
```

`destroy()` does NOT cost action cooldown, so destroying a marker then building a harvester in the same turn is legal.

### 2c. Filtering claimed tiles from ore selection

```python
# In the ore-scanning loop:
for t in c.get_nearby_tiles():
    e = c.get_tile_env(t)
    if e in (Environment.ORE_TITANIUM, Environment.ORE_AXIONITE):
        total_ore_count += 1
        bid = c.get_tile_building_id(t)
        if bid is None:
            ore_tiles.append(t)
        else:
            # Check if it's just our own claim marker (still available to US)
            try:
                if (c.get_entity_type(bid) == EntityType.MARKER
                        and c.get_team(bid) == c.get_team()):
                    # Claimed by ally -- skip UNLESS it's our own claim
                    if t == getattr(self, '_claimed_pos', None):
                        ore_tiles.append(t)  # We claimed it, still our target
                    # else: skip, another builder claimed it
                elif c.get_entity_type(bid) == EntityType.MARKER:
                    pass  # Enemy marker -- can't read, treat as blocked
                # else: has a real building (harvester etc.) -- skip
            except Exception:
                pass  # Can't read enemy entities, skip
```

**Problem:** We can't distinguish our own marker from another allied builder's marker. `get_marker_value(id)` returns the u32 value, but we set CLAIM_VALUE=1 for everyone. We could encode builder_id to distinguish, but we can't easily tell "is this MY marker or another builder's?"

**Solution: track `_claimed_pos` locally.** Each builder remembers which tile it claimed. If the marker is on that tile, it's ours. If we see an allied marker on a tile we didn't claim, another builder claimed it.

```python
# Filtering logic:
if bid is not None:
    try:
        et = c.get_entity_type(bid)
        tm = c.get_team(bid)
        if et == EntityType.MARKER and tm == c.get_team():
            if t != getattr(self, '_claimed_pos', None):
                continue  # Another builder's claim -- skip
            # else: our own claim, keep in ore_tiles
        else:
            continue  # Real building or enemy -- skip
    except Exception:
        continue
```

## 3. Complete Method Changes

### New instance variables in `__init__`:
```python
self._claimed_pos = None    # Position of our placed claim marker
self._marker_placed = False # Whether we've placed the marker yet
```

### Modified ore scanning (in `_builder`):
Replace the current ore tile check:
```python
# OLD:
if c.get_tile_building_id(t) is None:
    ore_tiles.append(t)

# NEW:
bid = c.get_tile_building_id(t)
if bid is None:
    ore_tiles.append(t)
elif self._is_own_claim(c, bid, t):
    ore_tiles.append(t)
# else: has building or another builder's claim marker -- skip
```

### New helper method:
```python
def _is_own_claim(self, c, building_id, tile_pos):
    """Check if building on tile is our own claim marker."""
    try:
        return (c.get_entity_type(building_id) == EntityType.MARKER
                and c.get_team(building_id) == c.get_team()
                and tile_pos == self._claimed_pos)
    except Exception:
        return False
```

### Marker placement (each round in `_builder`, before navigation):
```python
# Place claim marker when close enough to target
if (self.target
        and not self._marker_placed
        and c.can_place_marker(self.target)):
    c.place_marker(self.target, CLAIM_VALUE)
    self._marker_placed = True
    self._claimed_pos = self.target
```

### Marker cleanup before harvester build:
```python
# In the harvester build section, before c.build_harvester(ore):
bid = c.get_tile_building_id(ore)
if bid is not None:
    try:
        if (c.get_entity_type(bid) == EntityType.MARKER
                and c.get_team(bid) == c.get_team()):
            c.destroy(ore)  # Free, no cooldown
    except Exception:
        pass
if c.can_build_harvester(ore):
    c.build_harvester(ore)
    self._claimed_pos = None
    self._marker_placed = False
```

### Reset on target change:
```python
# Whenever self.target changes:
if best != self.target:
    self.fix_path = []
    self._marker_placed = False
    # Note: we can't remove old marker (may be out of range)
    # It will be destroyed by enemy or become irrelevant
self.target = best
```

## 4. Edge Cases

| Case | Handling |
|------|----------|
| Two builders claim same tile same round | First in spawn order places marker; second sees tile has a building (the marker) and skips it. **This works.** |
| Builder dies en route | Marker persists (1 HP). Other builders won't target that tile. The marker will eventually be destroyed by enemies or ignored (ore becomes less relevant over time). Acceptable waste. |
| Enemy destroys claim marker | Another builder may then target the same ore. This is fine -- enemy action disrupting coordination is a fair game mechanic. |
| Builder changes target | Old marker stays (can't destroy from distance). Tile appears claimed to others until marker dies. Minor waste, acceptable for simplicity. |
| Ore tile already has enemy marker | `can_place_marker()` returns false (can't overwrite enemy markers). Builder treats tile as available (enemy marker doesn't block `can_build_harvester` -- wait, it DOES block it since marker is a building). So enemy markers on ore tiles effectively deny that ore. Interesting defensive play by opponents. |
| Marker on ore tile but builder wants to build | `destroy()` the marker first (0 cooldown cost), then `build_harvester()`. Both in same turn. |
| can_place_marker range vs target distance | Builder can only place marker when within action radius (dist_sq <= 2) of target. Marker is placed as builder approaches, not when target is first selected. |
| Multiple markers per builder per round | Only 1 marker per round per unit. If builder changes target mid-round, it can't re-mark. This is fine -- the old mark persists. |

## 5. Expected Impact

### Maps that benefit most:
- **galaxy**: Scattered ore clusters, 2+ builders routinely compete for the same pocket. High impact.
- **arena**: Sparse ore in open areas, builders often converge. High impact.
- **butterfly**: Fragmented regions with ore pockets separated by walls. Medium impact (builders often can't see each other's targets anyway due to walls).
- **default_medium1, cold**: Ore close to core, builders naturally spread. Low impact (rarely competing).

### Quantitative estimate:
- On galaxy/arena, ~20-30% of builder trips are wasted due to duplicate targeting (rough estimate from replays).
- Eliminating this waste = ~15-20% more harvesters placed in the same number of rounds.
- Net resource gain: +10-15% total Ti harvested on affected maps.
- On maps where builders rarely compete: 0% impact (no regression).

### Performance cost:
- 1 extra `can_place_marker()` check per builder per round: negligible
- 1 extra `get_tile_building_id()` + `get_entity_type()` per ore tile in vision: negligible (already iterating tiles)
- No BFS, no encoding/decoding, no complex state: well within 2ms budget

## 6. Implementation Complexity

**Estimated effort: Low (30-50 lines of code changes)**

Changes:
1. Add 2 instance variables to `__init__` (+2 lines)
2. Modify ore-scanning filter (+8 lines)
3. Add marker placement in `_builder` main loop (+5 lines)
4. Add marker destroy before harvester build (+8 lines)
5. Add `_is_own_claim` helper (+6 lines)
6. Reset tracking vars on target change (+2 lines)
7. Add `CLAIM_VALUE = 1` constant (+1 line)

Total: ~32 lines added/modified. No new imports. No architectural changes.

## 7. Testing Plan

1. **A/B test on galaxy**: Run `cambc run buzzing_markers buzzing galaxy` (with and without markers). Compare total harvesters built and final Ti score.
2. **A/B test on arena**: Same comparison.
3. **Regression on cold/default_medium1**: Verify no score decrease.
4. **Edge case replay**: Watch a galaxy replay to confirm builders visibly avoid each other's claimed tiles.

## 8. Future Extensions (NOT for v1)

- **Encode ore type in marker value**: bit 0 = Ti vs Ax claim. Useful if we want to prioritize Ax ore.
- **Stale claim timeout**: encode round number, ignore claims older than N rounds. Handles dead-builder case.
- **Core-placed markers**: core could mark strategic positions for builders to target. Requires core to have vision of those tiles.
- **Defensive markers**: mark enemy approach directions for turret placement coordination.
