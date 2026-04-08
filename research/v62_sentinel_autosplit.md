# V62 Sentinel Auto-Split: 50-Match Results

## Date: 2026-04-08

---

## Test Configuration

- 50-match varied test (random opponents, maps, seeds)
- Opponents: ladder_eco, ladder_rush, smart_eco, smart_defense, balanced, sentinel_spam, rusher, fast_expand, adaptive, barrier_wall, turtle, ladder_mergeconflict, ladder_fast_rush, ladder_hybrid_defense
- Maps: all 38 maps
- Seeds: random

## Results

| Version | Win Rate | Record |
|---------|----------|--------|
| V61 baseline (no sentinel) | **74%** | **37W-13L** |
| V61 + sentinel auto-split | **62%** | **31W-19L** |

**Delta: -12 percentage points. REGRESSION. Do not ship.**

## What Changed

The sentinel auto-split adds:
1. `_sentinel_harv` / `_sentinel_step` instance vars
2. After 3rd harvester built by a single builder (with Ti >= sentinel_cost + 30):
   - Set `_sentinel_harv` = harvester position
   - Next round: if still adjacent, build conveyor perpendicular to enemy direction
   - Next round: build sentinel beyond the conveyor
3. No walk-back (cancels if builder moves away from harvester)
4. Max 1 sentinel per builder (`_sentinel_done`)
5. Skips bridge shortcut when sentinel is pending

## Why It Regresses

Despite "no walk-back," the sentinel still costs:
1. **1-2 rounds of action cooldown** -- the builder waits near the harvester instead of finding ore
2. **Bridge shortcut skipped** -- when `_sentinel_harv` is set, bridge code is skipped. This means the harvester's delivery chain may be worse (no bridge to core)
3. **30 Ti + 20% scale** -- sentinel cost is high relative to the economy value it provides against test bots
4. **Extra conveyor** -- 3 Ti + 1% scale for the branch conveyor, which also splits harvester output 50/50, reducing Ti delivery to core

The net effect: economy regresses more than defense helps. Test bots don't attack aggressively enough for sentinels to fire and compensate.

## Recommendation

**Revert buzzing/main.py to V61 baseline.** The sentinel auto-split is confirmed as a regression.

The sentinel mechanic (harvester auto-split) is valid and can be re-added when:
1. We face opponents with military (1600+ Elo)
2. We can gate it on round 800+ when economy is established
3. We DON'T skip the bridge shortcut

Keep the prototype at bots/buzzing_v4/main.py for future reference.
