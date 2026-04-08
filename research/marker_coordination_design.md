# Marker-Based Builder Coordination Design

**Date:** 2026-04-08  
**Context:** V61 has 13W-12L ladder record. Weakest matchups analysis identified "ore coverage gap" as root cause #2 — on corridors vs sentinel_spam we mine 35% less despite similar building counts. Builders walk the same sectors and build redundant parallel chains.

---

## Current Marker Usage

Markers are used for exactly one purpose: **ore tile claiming**.

```python
# Place claim when targeting ore tile (line 389-392)
c.place_marker(self.target, 1)   # value always = 1
self._claimed_pos = self.target
self._marker_placed = True

# Read claim when scoring ore tiles (line 364-366)
if (c.get_entity_type(bid) == EntityType.MARKER
        and c.get_team(bid) == c.get_team()):
    score += 10000  # heavy penalty — this ore is claimed
```

**What's NOT read:** `get_marker_value()` is never called. All markers have value=1. The u32 payload is completely unused.

**Placement rules (from game docs):**
- 1 marker per round, no action cooldown cost
- Any unit can place on any tile in vision
- Marker persists until replaced or the tile is in vision of an enemy that destroys it (no — markers are permanent until overwritten)
- Builder vision r²=20 (~4.5 tile radius)

**Current limitation:** A builder places a marker on its *target ore tile* when still far away. This prevents a second builder from targeting the same ore. But:
1. It only covers the *current target*. A builder that has already built a harvester places no "I'm done here, sector claimed" marker.
2. It gives zero sector-level information — just "this specific ore is taken."
3. The explore direction (sector) is determined purely by `(my_id * 7 + explore_idx * 3 + rnd // 100) % 8` — a local formula, no coordination.

---

## The Coordination Problem

On corridors (35% ore gap vs sentinel_spam), the exploration formula spreads builders by ID. With IDs like 3, 5, 9, 80:
- `(3*7) % 8 = 21 % 8 = 5` → DIRS[5] = SOUTHWEST
- `(5*7) % 8 = 35 % 8 = 3` → DIRS[3] = SOUTHEAST  
- `(9*7) % 8 = 63 % 8 = 7` → DIRS[7] = NORTHWEST
- `(80*7) % 8 = 560 % 8 = 0` → DIRS[0] = NORTH

This looks spread — 4 different sectors. But IDs are assigned sequentially by spawn order, and we only spawn 3-8 builders total. The formula isn't truly uniform. Worse: when a builder finds ore and builds a harvester, it resets `target = None` and `explore_idx` doesn't change. The next builder spawned with a nearby ID will pick the same sector.

**Result:** Builders cluster in 2-3 sectors, leaving other sectors unexplored. Especially problematic on corridors where ore is in narrow bands — missing one band is a large mining loss.

---

## Proposed Encoding

### Scheme: Sector Harvest Broadcast

**Core idea:** When a builder successfully builds a harvester, it places a marker on the harvested ore tile with an encoded value indicating "sector X is harvested, round Y." Other builders read this in their vision scan and exclude that sector from exploration.

### Encoding Format (u32)

```
bits [31:28]  = type tag (4 bits)
  0x1 = ore claim (existing, value=1 compatible)
  0x2 = sector harvest complete
  0x3 = sector congested (builder gave up after stuck)

bits [27:24]  = sector index (4 bits, 0-7 for 8 DIRS)
bits [23:16]  = round placed (8 bits, round % 256 — for staleness)
bits [15:0]   = builder_id % 65536 (16 bits — for debugging)
```

**Encoding helper:**
```python
def _encode_harvest_marker(sector_idx, rnd, builder_id):
    tag = 0x2
    return (tag << 28) | ((sector_idx & 0xF) << 24) | ((rnd & 0xFF) << 16) | (builder_id & 0xFFFF)

def _decode_marker(value):
    tag = (value >> 28) & 0xF
    sector = (value >> 24) & 0xF
    rnd_placed = (value >> 16) & 0xFF
    builder_id = value & 0xFFFF
    return tag, sector, rnd_placed, builder_id
```

**Backward compatibility:** Existing claim markers have value=1. `(1 >> 28) & 0xF = 0` — tag 0 = legacy claim. The new reader treats tag=0 as old-style claim (existing behavior preserved exactly).

---

## Implementation Plan

### Step 1: Broadcast on Harvester Build

In `_builder()`, after `c.build_harvester(ore)` succeeds:

```python
# After build_harvester (line 334-339)
c.build_harvester(ore)
self.harvesters_built += 1
self.target = None
self._claimed_pos = None
self._marker_placed = False
self._bridge_target = ore

# NEW: broadcast sector completion
sector_idx = DIRS.index(self._last_explore_sector) if hasattr(self, '_last_explore_sector') else 0
val = _encode_harvest_marker(sector_idx, rnd, self.my_id or 0)
if c.can_place_marker(ore):
    c.place_marker(ore, val)   # overwrites any existing claim on the ore tile
```

Requires tracking `self._last_explore_sector` — set in `_explore()` each time a sector is chosen.

### Step 2: Read Sector Markers in Explore

In `_explore()`, before computing `sector`:

```python
# Scan nearby markers for claimed sectors
claimed_sectors = set()
for eid in c.get_nearby_buildings():
    try:
        if c.get_entity_type(eid) == EntityType.MARKER and c.get_team(eid) == c.get_team():
            val = c.get_marker_value(eid)
            tag, sec, rnd_placed, _ = _decode_marker(val)
            if tag == 0x2:  # harvest complete broadcast
                age = (rnd - rnd_placed) % 256
                if age < 200:  # marker is fresh (< 200 rounds old)
                    claimed_sectors.add(sec)
    except Exception:
        pass

# Now pick sector excluding claimed ones
sector_candidates = [i for i in range(len(DIRS)) if i not in claimed_sectors]
if not sector_candidates:
    sector_candidates = list(range(len(DIRS)))  # fallback: all sectors
sector = sector_candidates[(mid * 7 + self.explore_idx) % len(sector_candidates)]
```

### Step 3: Track Last Explore Sector

In `_explore()`, after computing `sector`:
```python
self._last_explore_sector = DIRS[sector]
```

---

## Constraints and Edge Cases

### Constraint: 1 marker per round, no cooldown cost
This is the key constraint. If a builder places a harvest broadcast marker, it uses its marker allowance for that round. Currently the only other marker use is the ore claim (also 1/round). We need to decide priority:

**Resolution:** Harvest broadcast takes priority over ore claim on the round a harvester is built. The ore is now occupied by the harvester — the claim marker is no longer needed. Replace it with the broadcast.

### Constraint: Marker placement requires can_place_marker(pos)
Markers can be placed anywhere in vision. The ore tile is adjacent (action range), so always in vision. No issue.

### Constraint: Marker persistence
Markers are permanent until overwritten. A harvest broadcast on ore tile X stays there until another builder overwrites it (unlikely — ore tiles don't get revisited). The 200-round age limit in the reader handles stale data gracefully even if it doesn't expire physically.

### Edge Case: Sector index stability
DIRS is a module-level constant `[d for d in Direction if d != Direction.CENTRE]`. Its order is deterministic (Python enum iteration order is insertion order). All Player instances will have the same DIRS ordering. Sector index 0-7 is stable across all builders. ✓

### Edge Case: Marker vision range vs exploration range
A builder reads markers within r²=20 (~4.5 tiles). Harvest markers are placed on ore tiles — which can be far from core. If another builder is still near core, it won't see a marker placed at an ore 10 tiles away. 

**Fix:** After building a harvester, also place a broadcast marker near the core (on a core-adjacent tile visible to newly-spawned builders):

```python
# Place second marker near core for new builders to see
if self.core_pos:
    for d in DIRS:
        cp = self.core_pos.add(d)
        if c.is_in_vision(cp) and c.can_place_marker(cp):
            c.place_marker(cp, val)
            break
```

But this costs the marker for the round. Since harvest is rare (once per ore tile ever), this is acceptable. Alternatively: use the ore tile marker (visible to any builder that gets close to that sector) and rely on the explore logic to rotate naturally anyway.

**Simpler approach:** Just use the ore tile. New builders near core won't see it until they explore toward that sector — which is fine because by that point they need the info.

### Edge Case: Map has 8+ ore tiles, all sectors claimed
The fallback `sector_candidates = list(range(len(DIRS)))` handles this — fall back to original formula. No deadlock.

### Edge Case: Enemy markers
`c.get_team(eid) == c.get_team()` check already in the read loop. Enemy markers are ignored. ✓

---

## API Call Cost

Additional per-round cost in `_explore()`:

```python
for eid in c.get_nearby_buildings():   # already iterating for bridge search
    c.get_entity_type(eid)             # already called in vision scan
    c.get_team(eid)                    # ~1 call per marker found
    c.get_marker_value(eid)            # ~1 call per allied marker
```

In practice, there are typically 0-3 allied markers in vision at any time (ore claims are placed far from builder, and harvest markers are on ore tiles which may be out of range). The additional cost is **< 10 API calls per explorer round** — negligible given the CPU analysis showed we're well within budget.

---

## Expected Impact

### Direct benefit: Sector separation on corridors
On corridors (our worst sentinel_spam map, 35% ore gap):
- 4 builders exploring 4 different sectors → each claims distinct corridor branches
- vs. current: 2-3 builders converging on same corridor
- Expected mining improvement: +15-25% on corridor-type maps

### Indirect benefit: Fewer redundant conveyors
When builders don't overlap sectors, parallel conveyor chains don't form. Fewer chains = lower cost scale = cheaper future conveyors/harvesters. This directly attacks the overbuilding root cause identified in weakest_matchups_deep_dive.md.

### Downside risk
- **Staleness:** If a builder builds a harvester on a small ore tile that gets exhausted (no — ore tiles don't deplete in this game), others avoid that sector unnecessarily. **Not a real risk** — ore is permanent.
- **Sector granularity:** 8 sectors may be too coarse for maps with 20+ ore tiles. But 8 sectors for 8 builders is the right granularity — 1 sector per builder is the target.
- **Implementation complexity:** Low. ~30 lines of new code, no structural changes.

---

## Alternative Simpler Encoding: Just the Sector Bits

If the full u32 scheme feels over-engineered, a simpler version:

```python
# Encode: just set bit corresponding to sector index (bit 0-7 of u32)
# Multiple builders can OR their claims into a single tile's marker value
# value = 0b00000101 means sectors 0 and 2 are taken

# On harvest:
c.place_marker(ore, 1 << sector_idx)  # single bit

# On read:
val = c.get_marker_value(eid)
for sec in range(8):
    if val & (1 << sec):
        claimed_sectors.add(sec)
```

**Advantage:** No age tracking needed — sector stays claimed permanently (which is correct — a harvested ore tile is permanently taken). **16x simpler.**

**Disadvantage:** Can't tell which builder placed it or distinguish claim types. But we don't need that.

**Recommendation: Use the simple bitmask scheme.** The age-based approach adds complexity for no real gain since ore is permanent and sectors should stay claimed.

---

## Recommended Implementation (Final)

```python
# Module level
def _sector_for_dir(d):
    return DIRS.index(d)

# In _explore(): track chosen sector
self._last_explore_sector = DIRS[sector]

# After build_harvester() succeeds:
if hasattr(self, '_last_explore_sector') and c.can_place_marker(ore):
    sec_bit = 1 << _sector_for_dir(self._last_explore_sector)
    c.place_marker(ore, sec_bit | 0x80000000)  # high bit = harvest type
    
# In _explore(), read claimed sectors:
claimed_sectors = set()
for eid in c.get_nearby_buildings():
    try:
        if (c.get_entity_type(eid) == EntityType.MARKER
                and c.get_team(eid) == c.get_team()):
            val = c.get_marker_value(eid)
            if val & 0x80000000:  # harvest broadcast
                for sec in range(8):
                    if val & (1 << sec):
                        claimed_sectors.add(sec)
    except Exception:
        pass
# Exclude claimed sectors from candidate list
candidates = [i for i in range(len(DIRS)) if i not in claimed_sectors] or list(range(len(DIRS)))
sector = candidates[(mid * 7 + self.explore_idx) % len(candidates)]
```

**Total new code: ~20 lines.** Backward compatible with existing claim markers (value=1 has high bit 0 → not a harvest broadcast → ignored by sector reader).

---

## Verdict

This is a **low-cost, high-value** improvement. The encoding is simple, backward-compatible, uses ~20 new lines, and directly addresses the ore coverage gap that caused the corridors loss. It also has secondary benefits for overbuilding reduction.

**Recommended to implement as V62 change.**
