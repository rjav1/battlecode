# Spend-Down Policy Analysis — buzzing v36

## Problem Statement

Our bot routinely banks 3-18K Ti while top competitors keep reserves below 300 Ti.
Every 30 Ti sitting idle is a missed builder (cost ~30 Ti base). Delivered Ti (tiebreaker #2)
vastly outweighs stored Ti (tiebreaker #5), so hoarding hurts on both axes.

---

## Current Spending Thresholds (as of v36)

### 1. Core: builder spawn (`_core`, line 95)
```python
if ti < cost + 5:
    return
```
- **Reserve kept: 5 Ti** (cost + 5 before spawning a builder)
- Builder base cost ~30 Ti at scale 1.0, so effective minimum is ~35 Ti.
- This is already aggressive. The core rarely hoards here — hoard builds up *after*
  builders stop spawning (due to `cap`), not because of this threshold.

### 2. Builder: harvester build (`_builder`, line 299)
```python
if ti >= c.get_harvester_cost()[0] + 5:
```
- **Reserve kept: 5 Ti** after harvester cost (~20 Ti base → effectively 25 Ti min)
- Already near-zero reserve. Not the source of hoarding.

### 3. Builder navigation — conveyor build (`_nav`, line 394)
```python
if ti >= cc + ti_reserve:  # ti_reserve default=5
```
- **Reserve kept: 5 Ti** (default for normal navigation toward ore)
- During exploration **far from core**: `explore_reserve = 30` (line 496)
- During exploration **near core or maze maps**: `explore_reserve = 5`
- **The 30 Ti explore reserve is fine** — distant conveyors are wasteful, so being
  selective here is correct.

### 4. Builder navigation — road fallback (`_nav`, line 439)
```python
if ti >= rc + 5:  # road cost ~1 Ti
```
- **Reserve kept: 5 Ti** — already minimal.

### 5. Builder navigation — bridge fallback (`_nav`, lines 421-422)
```python
bridge_threshold = bc + 10 if map_mode == "tight" else bc + 20
if ti >= bridge_threshold:
```
- **Reserve kept: 10-20 Ti** on top of bridge cost (~20 Ti base → 30-40 Ti minimum)
- Reasonable — bridges are expensive and bridges far from ore are low ROI.

### 6. Early barriers (`_builder`, lines 230-231)
```python
barrier_reserve = 5 if map_mode == "tight" else 20
if ti >= bc + barrier_reserve:
```
- **Reserve kept: 5 Ti (tight) or 20 Ti (other)** on top of barrier cost (~3 Ti base)
- The `20 Ti` reserve on non-tight maps is mildly conservative but negligible.

### 7. Mid-game barriers (`_build_barriers`, line 562)
```python
if ti < c.get_barrier_cost()[0] + 40:
    return False
```
- **Reserve kept: 40 Ti** — this is the largest gating threshold in the bot.
- Barriers cost ~3 Ti (scale 1.0), so builder won't place a barrier unless bank >= ~43 Ti.
- This is intended to avoid starving economy for a 3 Ti building, but 40 Ti is large.

### 8. Gunner placement (`_place_gunner`, line 518)
```python
if ti < c.get_gunner_cost()[0] + 10:
    return False
```
- **Reserve kept: 10 Ti** on top of gunner cost (~10 Ti base → 20 Ti minimum)
- Fine — gunners are investments that pay off.

### 9. Walk-to road building (`_walk_to`, line 724)
```python
if ti >= rc + 5:
```
- **Reserve kept: 5 Ti** — minimal, fine.

---

## Root Cause of Hoarding

The bot does NOT hoard because of high spending thresholds on individual actions.
The true cause is:

**The builder cap (`cap` / `econ_cap` in `_core`) limits how many builders exist,
and the remaining Ti accumulates faster than the capped builders can spend it.**

On expand maps after round 400, cap = 12. On balanced maps after round 300, cap = 10.
With 10-12 builders each needing roads/conveyors costing 1-3 Ti per step, and the
economy generating 10 Ti every 4 rounds + harvester income, the bank fills up because
there is nothing left to build — not because thresholds are too high.

Secondary contributors:
- No spending outlet once all ore is claimed and all conveyors are laid.
- No mechanism to build additional roads, extra barriers, or turrets with excess Ti.

---

## Where Thresholds Could Be Lowered

These are the only meaningful changes:

| Location | Current Reserve | Suggested Reserve | Rationale |
|---|---|---|---|
| `_build_barriers` line 562 | `bc + 40` | `bc + 10` | 40 Ti gate is unnecessarily conservative; barriers cost ~3 Ti |
| Early barrier non-tight (line 230) | `bc + 20` | `bc + 5` | Same logic — 20 Ti buffer for a 3 Ti barrier |
| Bridge fallback non-tight (line 421) | `bc + 20` | `bc + 10` | Minor — saves ~10 Ti of hesitation |

All other thresholds are already at +5 Ti (near-zero) and do not contribute to hoarding.

---

## Recommended New Thresholds

```python
# _build_barriers, line 562 — change 40 -> 10
if ti < c.get_barrier_cost()[0] + 10:
    return False

# Early barrier non-tight, line 230 — change 20 -> 5
barrier_reserve = 5  # same for all map modes

# Bridge fallback, line 421 — change bc+20 -> bc+10
bridge_threshold = bc + 10  # same for all map modes
```

These changes would reduce the minimum bank during active construction phases
from ~43 Ti to ~13 Ti for barriers, freeing ~30 Ti per barrier opportunity.

---

## What Actually Fixes Hoarding

Lowering thresholds above will marginally reduce hoarding but the real fix requires
one of:

1. **Spend excess Ti on more builders beyond the cap** — already addressed by v36's
   econ_cap fix (raises cap and expands time_floor). This is the highest-leverage change.

2. **Build more turrets/sentinels when bank exceeds threshold** — e.g., if `ti > 200`,
   place an additional gunner or sentinel. Top bots spend on defense continuously.

3. **Build extra roads proactively** — cheap (1 Ti each) and useful for builder mobility.
   A builder could pave its entire exploration path when bank > 100 Ti.

4. **Convert excess Ti to infrastructure** — the game allows converting refined Ax to Ti,
   but not the reverse. If we have excess Ti, accelerate foundry investment.

---

## Risk of Overspending

Over-aggression is a real risk in **early game (rounds 1-50)**:
- Need at least ~60 Ti liquid to spawn a builder (cost ~30) AND build first conveyor (~3)
  AND build first harvester (~20) in the same sequence.
- If Ti drops to 0 before first harvester, economy stalls.
- Current +5 reserve on core spawn and harvester build is the right call for early game.

**Do not lower the core spawn threshold (line 95)** or the harvester build threshold (line 299).
These are already minimal and protect the early economy.

Mid/late game hoarding risk is essentially zero — there is nothing to accidentally
buy that would harm the bot.

---

## Summary

The hoard problem is **not threshold-driven** — it is **cap-driven**. The econ_cap
fix (v36) is the right primary lever. The only threshold worth changing is the
`_build_barriers` gate (40 → 10), which will spend ~30 extra Ti per barrier cycle
but won't materially reduce a 3-18K Ti hoard. For that, the answer is more builders.
