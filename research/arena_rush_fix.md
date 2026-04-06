# Arena Rush Fix Analysis

## Match Results (Seeds 1 & 2 — identical outcome)

| | buzzing | ladder_rush |
|---|---|---|
| Titanium | 3607 | 19291 |
| Mined | 1280 | 19210 |
| Units | 13 | 20 |
| Buildings | 132 | 188 |

**Winner: ladder_rush by Resources tiebreaker (not a rush kill — both cores survive to round 2000)**

## Root Cause: Economy Gap, Not a Defense Problem

The gap is **15x in mining** (1280 vs 19210). This is a pure economy failure. ladder_rush doesn't kill our core — it wins the tiebreaker by mining vastly more titanium.

## Why We Mine So Little

### 1. Builder Cap Too Conservative (PRIMARY CAUSE)

Tight map builder cap:
```python
cap = 3 if rnd <= 20 else (7 if rnd <= 100 else 15)
```

ladder_rush spawns **5 builders by round 15**, then 8 by round 100.
We spawn **3 by round 20**, then 7 by round 100.

On arena (25x25, 10 Ti ore tiles, path=8), ore is RIGHT NEXT to core. With 5 builders, ladder_rush eco builders reach ore and place harvesters by round 10-15. With only 3 builders and 2 trying to do early barriers, we may not get our first harvester until round 20-30.

### 2. Early Barrier Logic Diverts All Early Builders

```python
early_barrier_ok = (
    (map_mode == "tight" and rnd >= 5 and (self.my_id or 0) % 5 != 0)
    or self.harvesters_built >= 1
)
```

On tight maps starting at round 5, builders with `id % 5 != 0` (i.e., builders 1, 2, 3, 4 — ALL of our first 3 non-zero-id builders) try to place barriers BEFORE seeking ore. With only 3 builders:
- Builder 0: May have `id % 5 == 0` → skips barriers, goes to ore ✓
- Builders 1, 2: Both try barriers first → delayed ore mission ✗

This means 2/3 of our builders are barrier-hunting while ladder_rush's 2 eco builders go straight to harvesters.

### 3. Ti Reserve Too Cautious at Spawn

```python
if ti < cost + 5:
    return
```

vs ladder_rush:
```python
if ti < cost + 2:
    return
```

3 Ti difference, but it delays builder spawning by 1-2 rounds per builder. Across 5 builders, that's 5-10 rounds of delay in early game.

## What ladder_rush Does Right

1. **5 builders by round 15** — fast ramp
2. **3 rush + 2 eco split** — eco builders go straight to ore, no barrier diversion
3. **Low Ti reserve**: `cost + 2` — spawn the moment you can afford it
4. **Low conveyor reserve**: `cc + 2` — build conveyors aggressively

## Proposed Minimal Fixes

### Fix 1: Raise tight map early builder cap (HIGH IMPACT)

```python
# Before:
cap = 3 if rnd <= 20 else (7 if rnd <= 100 else 15)

# After:
cap = 5 if rnd <= 20 else (8 if rnd <= 100 else 15)
```

This matches ladder_rush's ramp. 5 builders by round 20 on tight maps.

### Fix 2: Don't divert early builders to barriers before first harvester (HIGH IMPACT)

```python
# Before:
early_barrier_ok = (
    (map_mode == "tight" and rnd >= 5 and (self.my_id or 0) % 5 != 0)
    or self.harvesters_built >= 1
)

# After:
early_barrier_ok = self.harvesters_built >= 1
```

This ensures ALL early builders go straight to ore. Barriers wait until someone has a harvester running. One builder having `harvesters_built >= 1` means the barrier logic activates for that builder only — not all 3 initially.

### Fix 3: Lower builder spawn Ti reserve (LOW-MEDIUM IMPACT)

```python
# Before:
if ti < cost + 5:
    return

# After:
if ti < cost + 2:
    return
```

Matches ladder_rush's spawn aggression.

## Expected Impact

- Fix 1 alone: +2 extra builders by round 20 → potentially 2 more harvesters by round 30-40 → ~5-6x more mining over 2000 rounds
- Fix 2 alone: Prevents builder delay in early rounds
- Together: Should close most of the 15x mining gap

## Risk Assessment

- Fix 1: Could increase builder costs faster (cost scaling). But arena has 10 ore tiles — we NEED more harvesters to cover them.
- Fix 2: Fewer early barriers = more rush vulnerability. But ladder_rush wins via economy, not rush kill. The gunners at round 60 should still deter rushers.
- Fix 3: Minimal risk, small benefit.

## Gunner Ammo Status

Gunners check `ammo >= 2` before firing. Ti stacks flow through conveyors to the gunner. On tight maps, the conveyor chains are short (path=8), so ammo should flow. However, if the gunner builder (id%5==1) builds the gunner facing enemy but no conveyor feeds it Ti, it never fires.

The `_place_gunner` function places a gunner near core facing enemy but does NOT build a dedicated ammo conveyor. It relies on existing conveyor chains passing through the gunner position. This could be an issue if the gunner is placed off the main resource chain.

**However**, this is likely a secondary issue. The primary problem is that we're barely building harvesters at all, so resource flow is negligible regardless.

## Recommended Implementation Order

1. Fix 1 (builder cap) — highest impact, lowest risk
2. Fix 2 (barrier timing) — high impact, slightly riskier on pure rush maps
3. Test: `cambc run buzzing ladder_rush arena --seed 1`
4. If still losing badly, add Fix 3 (spawn reserve)
