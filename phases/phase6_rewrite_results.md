# Phase 6 Rewrite Results - Economy Bot with d.opposite() Conveyor Chains

## Key Discovery

The `d.opposite()` conveyor pattern is the ONLY approach that successfully delivers resources.

**Why it works:** Builders walk outward FROM core. At each step, they build a conveyor facing BACK (d.opposite() = toward core). When a harvester is built at the end of the trail, resources flow backward along the conveyor chain to core.

**Why forward chains failed:** Building conveyors FROM harvester TOWARD core requires the builder to walk the entire route, and any interruption (road on tile, wall, existing building) breaks the chain. The d.opposite() approach builds the chain AS the builder explores, so the trail is inherently connected.

## Architecture

Single file, ~310 lines. Key design decisions:

1. **Conveyors for ALL navigation** (not just ore-targeting). Exploration also lays conveyors because harvesters are often found during exploration. Without a conveyor trail back, the harvester output has nowhere to go.

2. **Sentinel defense** after round 300 (1 in 5 builders, capped at 3 sentinels). Placed toward enemy using symmetry detection.

3. **Attacker role** after round 700 (1 in 5 builders, requires 4+ harvesters). Walks toward enemy core, attacks enemy buildings.

4. **Aggressive spawning**: 3 builders by round 20, 5 by round 100, 7 by round 300, 8 max.

## Test Results: buzzing vs starter (8-0 SWEEP)

| Map | Winner | buzzing Ti (mined) | starter Ti (mined) | buzzing Bldgs | starter Bldgs |
|-----|--------|-------------------|-------------------|--------------|--------------|
| default_medium1 | **buzzing** | 29,041 (26,980) | 3,475 (0) | 218 | 568 |
| landscape | **buzzing** | 16,173 (14,550) | 2,771 (0) | 174 | 546 |
| cold | **buzzing** | 8,035 (8,030) | 836 (0) | 361 | 832 |
| settlement | **buzzing** | 13,382 (14,760) | 1,055 (0) | 459 | 924 |
| corridors | **buzzing** | 23,153 (20,260) | 2,734 (0) | 145 | 502 |
| battlebot | **buzzing** | 7,896 (4,950) | 4,334 (0) | 132 | 291 |
| arena | **buzzing** | 17,972 (14,650) | 4,280 (0) | 170 | 383 |
| face | **buzzing** | 22,993 (19,430) | 4,971 (0) | 135 | 211 |

## Mirror Match

| Map | Winner | P1 Ti (mined) | P2 Ti (mined) | P1 Bldgs | P2 Bldgs |
|-----|--------|--------------|--------------|---------|---------|
| default_medium1 | P1 | 18,301 (14,700) | 17,034 (14,390) | 139 | 226 |

## Comparison: Before vs After

| Metric | Phase 6 Fix (roads+chains) | Phase 6 Rewrite (d.opposite) |
|--------|---------------------------|------------------------------|
| vs starter record | 4-4 | **8-0** |
| Ti mined (any map) | 0 (all maps) | **4,950 - 26,980** |
| Avg Ti mined | 0 | **15,451** |
| Best Ti mined | 0 | 26,980 (default_medium1) |

## Improvement: 0 Ti mined -> 15,451 avg Ti mined. Infinite improvement.

The rewrite went from ZERO resource delivery to consistent 5,000-27,000 Ti mined per game. This is the single largest improvement in the bot's history.

## File

`C:\Users\rahil\downloads\battlecode\bots\buzzing\main.py` (~310 lines)
