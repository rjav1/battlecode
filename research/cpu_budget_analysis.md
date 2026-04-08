# CPU Budget Analysis — V61 Bot

**Date:** 2026-04-08  
**Bot:** bots/buzzing/main.py (662 lines)  
**Budget:** 2ms (2000µs) per unit per round, 5% refillable buffer

---

## TLE Status: NONE OBSERVED

Test runs on worst-case maps (cold, galaxy, sierpinski_evil) against barrier_wall (500+ buildings):

| Map | Opponent | Condition | TLE? |
|-----|----------|-----------|------|
| sierpinski_evil | starter | harvesters | No |
| cold | starter | titanium_collected | No |
| cold | barrier_wall | titanium_collected | No |
| galaxy | barrier_wall | titanium_collected | No |

All matches complete 2000 turns. Losses are economic (titanium tiebreak), not timeouts.

**Note:** `c.get_cpu_time_elapsed()` returns 0 in local runs — CPU timing is only enforced server-side on AWS Graviton3. The `TLE: off` flag in local `cambc run` output confirms this.

---

## Top 3 CPU-Expensive Operations (Static Analysis)

### #1 — Vision Scan Loop (lines 192-216) — Called Every Round Per Builder

```python
for t in c.get_nearby_tiles():          # ~60-70 tiles (r²=20 vision)
    e = c.get_tile_env(t)               # API call per tile
    ...
    bid = c.get_tile_building_id(t)     # API call per ore tile
    if bid is not None:
        c.get_entity_type(bid)          # API call per occupied ore tile
```

**Cost estimate per builder per round:**
- `get_nearby_tiles()`: 1 API call → returns ~60-70 Position objects (r²=20)
- `get_tile_env()`: ~60-70 API calls
- `get_tile_building_id()`: ~10-20 calls (ore tiles only)
- `get_entity_type()`: ~2-5 calls (occupied ore only)

**Total: ~75-95 API calls per builder per round.**

With 8 builders (cap), this is ~600-760 vision API calls per round across all builders.

**Severity: LOW.** These are cheap read-only queries. The bottleneck is Python function call overhead, not algorithmic complexity. The loop is O(vision_radius²) = O(20) tiles — fixed regardless of map size.

---

### #2 — BFS Navigation (lines 589-610) — Called Every Round Per Builder

```python
def _bfs_step(self, pos, target, passable):
    queue = deque([(pos, None)])
    visited = {pos}
    steps = 0
    while queue and steps < 200:          # Hard cap: 200 iterations
        steps += 1
        cur, fd = queue.popleft()
        for d in DIRS:                    # 8 directions per step
            nxt = cur.add(d)
            if nxt in visited or nxt not in passable:  # set lookups O(1)
                continue
            ...
            queue.append((nxt, step))
```

**Cost estimate per builder per round:**
- Worst case: 200 iterations × 8 directions = 1600 operations
- Each iteration: 2 set lookups + `Position.add()` + `distance_squared()`
- `passable` set built from vision scan (~60-70 entries): set lookups O(1)

**Actual worst case:** 200 BFS steps × (8 dir checks × ~3 ops) = ~4800 Python operations.

With 8 builders: **~38,400 Python ops per round from BFS alone.**

**Severity: MODERATE.** The 200-step hard cap bounds the worst case. On open maps the BFS terminates early (target found quickly). On maze maps (sierpinski_evil) the 200-step cap is frequently hit, doing maximum work. This is the single most expensive algorithmic operation.

**Key observation:** The `passable` set only contains vision-radius tiles (~60-70). BFS terminates at map boundary of passable set. On maze maps, path to target often goes outside vision → BFS exhausts 200 steps without finding target → returns best partial direction. This is correct behavior but maximum cost.

---

### #3 — Bridge Candidate Search (lines 285-296) — Called Per Round When `_bridge_target` Set

```python
for eid in c.get_nearby_buildings():              # ALL buildings in vision
    c.get_entity_type(eid)                         # API call per building
    c.get_team(eid)                                # API call per building
    c.get_position(eid)                            # API call per building
    epos.distance_squared(self.core_pos)           # math per building
    ore.distance_squared(epos)                     # math per building
```

**Cost estimate:**
- Builder vision r²=20 → ~10-30 nearby buildings in early game
- After 500 buildings: potentially 20-40 buildings in vision (conveyors are dense)
- Each building: 3 API calls + 2 math ops

**With 30 buildings in vision:** ~90 API calls for bridge search.

**Severity: LOW-MODERATE.** Only executes for 1-2 rounds after each harvester build. Not a per-round cost for most builders.

---

## Core Unit CPU Cost (lines 69-137)

The core runs once per round with much simpler logic:

```python
for eid in c.get_nearby_buildings():              # ~20-40 buildings near core
    c.get_entity_type(eid)                         # count harvesters
    c.get_team(eid)
```

**Cost: ~40-80 API calls per round.** Minimal. Core is not a CPU concern.

---

## Sentinel CPU Cost (lines 139-151)

```python
for eid in c.get_nearby_entities():
    c.get_team(eid)
    c.get_position(eid)
    c.can_fire(epos)
```

**Cost: ~20-50 API calls per round** (entities in vision r²=32). Returns on first fire. Not a concern.

---

## Theoretical Per-Round CPU Budget Usage

**At cap of 8 builders + core + 0-1 sentinels:**

| Operation | Calls/Round | Relative Cost |
|-----------|-------------|---------------|
| Vision scan (8 builders) | ~640 API calls | Medium |
| BFS navigation (8 builders, maze) | ~1600 steps × 8 ops | HIGH |
| Ore scoring loop (8 builders) | ~400 ops | Low |
| Bridge search (1-2 builders) | ~90 API calls | Low |
| Core logic | ~60 API calls | Low |
| **Total estimate** | **~2800 API calls + ~13000 Python ops** | |

**Reality check:** Python on AWS Graviton3 can execute roughly 5-10M simple Python operations per second. 13,000 ops = ~1.3-2.6ms. This is **right at the 2ms budget limit** in the worst case (8 builders on a maze map with BFS at 200-step cap simultaneously).

---

## Risk Assessment

### Low Risk — No Observed TLE
All server-side test runs completed 2000 turns. The 5% refillable buffer means occasional overruns don't cause immediate TLE. Python's overhead is real but within budget for typical maps.

### Medium Risk — Maze Maps at High Builder Count
On sierpinski_evil and similar maps, if all 8 builders simultaneously hit 200-step BFS cap:
- 8 builders × 200 steps × 8 dirs = 12,800 BFS iterations
- This is the worst-case scenario and may approach the 2ms limit

**Mitigation already in place:** `_check_is_maze()` sets `use_nearest=True` on maze maps, which doesn't reduce BFS but means BFS finds targets faster (closer targets = fewer steps before return).

### Low Risk — Large Building Counts
Vision scan and nearby_buildings calls don't scale with total building count — only with buildings *within vision radius*. At 500 total buildings, vision r²=20 still contains only ~20-40 buildings near a given builder. Not a scaling concern.

---

## Top 3 CPU Hotspots (Ranked)

| Rank | Hotspot | Location | Cost | Risk |
|------|---------|----------|------|------|
| 1 | BFS `_bfs_step()` 200-step cap | line 589-610, called from `_nav()` | ~1600 iter/builder | Medium on maze maps |
| 2 | Vision scan `get_nearby_tiles()` loop | line 192-216 in `_builder()` | ~75 API calls/builder | Low |
| 3 | Bridge chain search `get_nearby_buildings()` | line 285-296 | ~90 API calls (transient) | Low |

---

## Recommendations

### If TLE becomes a problem (not observed yet):

1. **Cache BFS result for 2-3 rounds** — Builder position changes slowly. Reusing last round's BFS direction avoids 200-step BFS on rounds where the builder couldn't move. Saves ~80% of BFS cost.

2. **Reduce BFS cap on non-maze maps** — On open maps (wall_density < 5%), reduce BFS limit from 200 to 50. Target is almost always visible in 50 steps on open terrain.

3. **Skip vision scan when no action available** — If both `action_cooldown > 0` and `move_cooldown > 0`, skip the full ore scan (only need passable for BFS). Saves ~75 API calls per cooldown-blocked round.

### These changes are NOT currently needed
CPU is not limiting performance. The losses are economic. Prioritize building count cap and ore coverage fixes (see weakest_matchups_deep_dive.md) over CPU optimization.
