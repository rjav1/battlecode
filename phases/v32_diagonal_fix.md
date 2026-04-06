# v32 Diagonal Chain Gap Fix — Experiment Results

## Summary

**All three approaches to fix diagonal chain gaps FAILED to improve performance.** The diagonal gap bug is real but the cure is worse than the disease. Code reverted to v31.

## The Bug (Confirmed)

Conveyors can only face cardinal directions (N/S/E/W) and only transfer resources to/from cardinal neighbors. When the builder walks diagonally:
- `d.opposite()` produces a diagonal direction (e.g., SOUTHWEST)
- `can_build_conveyor(nxt, Direction.SOUTHWEST)` returns False
- No conveyor placed at diagonal tile = gap in chain

## Three Approaches Tested

### Approach A: Decompose diagonal into two cardinal steps
Replace each diagonal step with two cardinal steps (NE -> N then E).

| Map | v31 Mined | v32a Mined | Change |
|-----|-----------|-----------|--------|
| cold | 18,800 | 17,710 | -5.8% |
| shish_kebab | 14,730 | 13,220 | -10.2% |
| galaxy | 13,650 | 7,890 | **-42.2%** |
| arena | 9,880 | 4,950 | **-49.9%** |
| default_medium1 | 30,320 | 17,990 | **-40.7%** |

**Verdict: CATASTROPHIC.** Builder moves 2x slower, reaches ore much later, builds fewer harvesters.

### Approach B: Cardinal-only BFS
BFS uses only cardinal directions (N/S/E/W), diagonals as fallback.

| Map | v31 Mined | v32b Mined | Change |
|-----|-----------|-----------|--------|
| cold | 18,800 | 19,040 | +1.3% |
| shish_kebab | 14,730 | 4,940 | **-66.5%** |
| galaxy | 13,650 | 9,940 | -27.2% |
| default_medium1 | 30,320 | 4,910 | **-83.8%** |

**Verdict: CATASTROPHIC.** Cardinal-only BFS makes paths ~1.4x longer on open maps.

### Approach C: Build cardinal bridge + move diagonally (same turn)
When moving diagonally, place a conveyor on a cardinal neighbor AND move diagonally using separate cooldowns.

| Map | v31 Mined | v32c Mined | Change |
|-----|-----------|-----------|--------|
| cold | 18,800 | 22,200 | +18.1% (but high variance) |
| shish_kebab | 14,730 | 9,830 | -33.3% (tight map) |
| galaxy | 13,650 | 13,670 | +0.1% |
| default_medium1 | 30,320 | 30,980 | +2.2% |

Restricted to expand-only maps: cold/arena/default_medium1 unchanged, galaxy neutral (extra conveyors don't connect to useful chains). shish_kebab variance confirmed with multi-seed test.

**Verdict: NEUTRAL at best.** Extra conveyors don't reliably connect chains and waste Ti/scale.

## Why the Fix Doesn't Work

The fundamental tradeoff is:
- **Diagonal speed advantage (~1.4x)** > **Chain gap cost**
- Each diagonal gap loses at most 1 harvester's worth of throughput at that point
- But slowing builder movement delays ALL future harvesters by many rounds
- The compounding effect of slower exploration vastly exceeds the chain gap cost

On constrained maps (corridors), walls force cardinal movement anyway -- no diagonal gaps to fix. On open maps, diagonal paths are short and gaps are few. The chain-fix mechanism already handles winding paths.

## Key Insight

**The diagonal gap bug is real but not the primary competitive bottleneck.** The bot already mines 14-30K Ti on most maps. The competitive gap against top bots is likely elsewhere:
- Number of builders/harvesters spawned
- Military timing and placement
- Resource banking (spending Ti instead of hoarding)
- Connected chains through multiple harvesters sharing conveyors

## Code Status

Code reverted to v31 (identical). No changes deployed.
