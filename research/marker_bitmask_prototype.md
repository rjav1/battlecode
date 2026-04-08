# Marker Bitmask Prototype — Results

**Date:** 2026-04-08  
**Bot:** bots/buzzing_v3/main.py (copy of V61 + ~25 lines of marker coordination)  
**Hypothesis:** Sector harvest broadcasts via marker bitmask would reduce exploration overlap, improving ore coverage by 15-25% on corridors-type maps.

---

## Implementation

Added to `bots/buzzing_v3/main.py`:

**`__init__`:** `self._last_explore_sector = 0`

**After `build_harvester(ore)`:**
```python
if c.can_place_marker(ore):
    c.place_marker(ore, (1 << self._last_explore_sector) | 0x80000000)
```

**In `_explore()`, before sector selection:**
```python
claimed_sectors = set()
for eid in c.get_nearby_buildings():
    try:
        if (c.get_entity_type(eid) == EntityType.MARKER
                and c.get_team(eid) == c.get_team()):
            val = c.get_marker_value(eid)
            if val & 0x80000000:
                for sec in range(8):
                    if val & (1 << sec):
                        claimed_sectors.add(sec)
    except Exception:
        pass
candidates = [i for i in range(len(DIRS)) if i not in claimed_sectors] or list(range(len(DIRS)))
# All sector formula modulo changed to % len(candidates)
```

**After sector computed:** `self._last_explore_sector = sector`

---

## Results: No Measurable Improvement

### v3 vs V61 self-comparison (corridors, 5 seeds)

| Seed | Winner | v3 mined | v61 mined | v3 bldgs | v61 bldgs |
|------|--------|----------|-----------|---------|---------|
| 1 | buzzing (v61) | 14600 | 14600 | 26 | 26 |
| 2 | buzzing_v3 | 14600 | 14600 | 26 | 26 |
| 3 | buzzing_v3 | 14600 | 14600 | 26 | 26 |
| 4 | buzzing_v3 | 14600 | 14600 | 26 | 26 |
| 5 | buzzing_v3 | 14600 | 14600 | 26 | 26 |

**Identical Ti mined across all seeds.** Winners differ only by tiebreaker (coin-flip equivalent).

### v3 vs sentinel_spam comparison

| Map | v3 mined | sentinel_spam mined | Gap |
|-----|----------|---------------------|-----|
| corridors | 14600 | 19800 | -26% |
| face | 13820 | 15680 | -12% |
| galaxy | 9950 | 9900 | +1% |
| hourglass | 19860 | 24090 | -17% |

**Same as V61 vs sentinel_spam.** The 35% corridors gap is completely unchanged.

### Multi-map comparison (v3 vs V61 vs sentinel_spam, seed 2)

| Map | v3 mined | v61 mined | Difference |
|-----|----------|-----------|------------|
| corridors | 14600 | 14600 | 0 |
| face | 13820 | 13820 | 0 |
| galaxy | 9950 | 9950 | 0 |
| cold | 14060 | 14060 | 0 |

**Zero difference on all maps tested.**

---

## Diagnosis: Wrong Root Cause

The marker bitmask had no effect because **sector overlap between our builders is not the problem on corridors**.

The existing formula `(mid * 7 + explore_idx * 3 + rnd // 100) % 8` with ID primes already spreads builders effectively. They are already going to different sectors. The sector approach was a correct theory but the wrong map.

### What IS the corridors problem

On corridors (seed 1, both seeds):
- Us: 14600 Ti mined, 26 buildings — very lean
- sentinel_spam: 19800 mined, 32 buildings — also lean but 35% more ore

With only 26 buildings (conveyors), we're building very few chains. The mining gap can't be from parallel chains (we don't have enough buildings to have redundant chains).

**The real issue: we're hitting fewer ore tiles on corridors.** Corridors has narrow passable lanes with ore tiles spread across multiple corridors. Our builders reach some corridors and miss others — not because they overlap, but because our BFS navigation fails to route through the narrow corridor entry points.

Evidence: the result is **seed-identical** regardless of marker coordination. If the problem were random exploration overlap, different seeds would show variation. The exact same 14600 mined every time means our bot hits the same ore tiles every time — completely deterministic, constrained by BFS path-finding through corridors.

### What marker coordination would actually help

Marker coordination benefits situations where:
1. Multiple builders are in vision range of each other's markers
2. Ore is abundant enough that there are multiple sectors to choose from
3. The exploration formula actually produces sector collisions

On corridors specifically, the constraint is BFS wall-navigation, not sector selection. On large open maps (cold, galaxy), the constraint is cost-scale overbuilding, not sector selection.

**The hypothesis was valid but the measured maps are wrong.** Marker coordination would help most on large maps with abundant scattered ore (50x50) where multiple builders genuinely do converge on the same region. We don't have a test bot that exercises that specific failure mode at scale.

---

## Salvageable Value

The implementation is correct and low-cost. Even though it produced no measurable improvement on current test maps, it:

1. **Does no harm** — fallback `or list(range(n))` ensures no builder ever gets stuck with no candidates
2. **Is backward compatible** — old claim markers (value=1, high bit=0) are ignored
3. **May help on untested maps** — larger sparse-ore maps not in our test suite

**Recommendation:** Keep the implementation in v3 but don't ship as V62 without evidence of improvement. The corridors gap requires a different fix — likely BFS navigation improvement to route through narrow corridor entry points, or explicit corridor detection.

---

## Action Items

1. **Investigate corridors root cause directly:** Run with BFS debug to see which ore tiles are being found vs missed. Is our BFS failing to navigate through narrow passages?

2. **Test marker coordination on large sparse maps:** Generate a 50x50 test map with ore widely scattered. Marker coordination should show effect there.

3. **Keep `buzzing_v3`** as a branch with the marker code — non-harmful, might show future value.

4. **Don't deploy as V62** — no measured improvement on any current test map.
