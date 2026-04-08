# Sentinel Auto-Split Prototype Results

## Date: 2026-04-08
## Prototype: bots/buzzing_v4/main.py

---

## Mechanic Confirmed

Harvesters "prioritise outputting in directions used least recently." Two adjacent conveyors = auto-split ~50/50. The harvester does the splitting for free.

## Implementation

After a builder builds a harvester (gated by various conditions):
1. Set `_sentinel_harv` = harvester position
2. Builder stays near harvester (returns instead of finding next ore)
3. Step 0: Build conveyor adjacent to harvester, facing perpendicular to enemy
4. Step 1: Build sentinel 1 tile beyond conveyor, facing enemy
5. Result: harvester auto-splits between existing chain conveyor and new sentinel-feeding conveyor

## Testing Results

### v4 vs buzzing (seed 1, 10 maps)

| Trigger | v4 Wins | Maps Won |
|---------|---------|----------|
| 3+ harvesters, round >= 300 | 4/10 | medium1, arena, hooks, butterfly |
| 2+ harvesters, round >= 200 | 4/10 | medium1, arena, hooks, butterfly |
| 2+ harvesters, any round, Ti >= sentinel+30 | 3/10 | medium1, arena, butterfly |
| Any harvester, round >= 500, Ti >= 500 | 4/10 | medium1, arena, hooks, butterfly |

**Baseline buzzing wins 6-7/10 across all variants.**

### Root Cause: Builder Time is the Scarcest Resource

The sentinel feature costs the builder 2-3 rounds:
- Round N: Build harvester (action cooldown consumed)
- Round N+1: Wait for cooldown or build conveyor
- Round N+2: Build sentinel

During those 2-3 rounds, the builder is NOT finding new ore or building more harvesters. On economy-focused games (which is ALL games at our Elo), this delay costs more than the sentinel provides.

**Evidence:** On maps where we lose (default_small1, default_large1, cold, wasteland_oasis), the gap is enormous (often 2-3x Ti mined). The sentinel doesn't help because:
1. There's no enemy attacking at our Elo -- games are decided by economy
2. The 2-3 round delay per sentinel compounds across multiple builders
3. Each sentinel costs 30 Ti + 20% scale + the opportunity cost of delayed harvesters

### When Sentinels DO Help

On maps where it's close (default_medium1, hooks), the sentinel can swing the result. But this only matters when the opponent is attacking our harvesters or core -- which doesn't happen in most resource-victory games.

---

## Key Discovery: The Real Blocker

**The prototype reveals that the problem isn't sentinel ammo delivery -- it's that sentinels aren't worth building at our Elo.**

At 1480 Elo, games are decided by resource accumulation, not military. Building a sentinel (30 Ti + 20% scale) is -50 Ti of effective cost for a unit that never fires because no one is attacking. The top teams that build sentinels (Polska Gurom at 1487) are doing so for HIGHER Elo opponents who use military.

**The sentinel auto-split MECHANIC works.** The harvester DOES split output between two adjacent conveyors. But the VALUE of a sentinel at our Elo is net negative.

---

## What This Means for 1600 Elo

1. **Sentinel ammo delivery is solved** -- harvester auto-split works, ~20 lines of code.
2. **But sentinels aren't the breakthrough to 1600** -- they're defense against military that doesn't exist at our Elo tier.
3. **The 1600 breakthrough must be economic** -- fewer conveyors per harvester, shorter chains, better ore targeting.
4. **Sentinels become valuable at 1600+** where opponents use military. Save this feature for after we reach 1600 via economy.

---

## Files

- Prototype: `bots/buzzing_v4/main.py` (modified copy of buzzing)
- Key code: lines 332-375 (sentinel auto-split) + line 393-397 (trigger)
