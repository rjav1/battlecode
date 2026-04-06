# v23 Eco Results: Pure Economy on Expand Maps

## Changes Made

1. **Builder cap raised**: expand maps now `3→6→10→15` (was `3→6→9→12`)
2. **Early barriers skipped** on expand maps (added `map_mode != "expand"` guard)
3. **Attacker skipped** on expand maps (added `map_mode != "expand"` guard)
4. **Gunner/barrier** already skipped on tight; now also skip on expand (`map_mode not in ("tight", "expand")`)

settlement = 50x38 = 1900 → expand mode (changes apply)
cold = 37x37 = 1369 → balanced (changes don't apply)
default_medium1 = 30x30 = 900 → balanced (changes don't apply)

---

## Test Results

### Settlement (expand map — changes apply)

| Position | buzzing (v23) | opponent | notes |
|----------|--------------|----------|-------|
| P1: buzzing vs smart_eco | 19,590 mined | 41,880 mined | v22 baseline: 19,590 — **no change** |
| P2: smart_eco vs buzzing | 0 mined | 14,750 mined | v22 also 0 mined — **pre-existing positional issue** |

**Settlement P1 gap: -22,290 Ti (vs -21,550 in v22). No improvement.**

### Cold (balanced map — changes don't apply, control test)

| Position | buzzing (v23) | smart_eco |
|----------|--------------|-----------|
| P1: buzzing vs smart_eco | 8,440 mined | 32,000 mined |
| P2: smart_eco vs buzzing | 14,800 mined | 4,880 mined — **buzzing wins** |

### Default_medium1 (balanced map — changes don't apply, regression test)

| Position | buzzing (v23) | buzzing_prev (v22) |
|----------|--------------|-------------------|
| P1: buzzing vs buzzing_prev | 18,580 mined | 33,930 mined — v22 wins |
| P2: buzzing_prev vs buzzing | 18,580 mined | 33,930 mined — v23 wins |

Numbers are perfectly symmetric — this is positional variance, not a code regression. Both sides win as P2.

---

## Root Cause: Why Settlement Gap Didn't Close

The military skip on expand maps didn't free up meaningful builder time because the real bottleneck is `econ_cap`:

```python
econ_cap = max(6, vis_harv * 3 + 4)
```

On settlement (large map), harvesters are built far from core. `get_nearby_buildings()` has limited range, so the core can't see most harvesters → `vis_harv` stays low → `econ_cap` stays at 6, capping builders at 6 regardless of the 15-unit expand cap.

Smart_eco gets 8 units because it doesn't have this cap. Our bot spawns 6 builders, they all find ore and build harvesters, but the core can't count those harvesters and refuses to spawn more builders.

The 15-unit cap is never reached — `econ_cap` stops us at 6.

---

## Conclusion

**Do NOT deploy v23.** Target of closing settlement gap to -5K not achieved.

The settlement gap remains ~-22K. The econ_cap formula is the fundamental bottleneck on expand maps, not the military overhead. Military overhead is a secondary concern.

### Next experiments to try:
1. **Fix econ_cap on expand maps** — raise the floor from 6 to 10+ on expand, or remove the econ_cap gating entirely on expand (trust the 15-builder cap instead)
2. **Track harvesters_built globally** — `self.harvesters_built` counts what each builder individually built. Use this in the core via a shared counter or just raise the econ_cap floor.
3. **Understand what smart_eco does** — 8 builders, 307 buildings, 41K mined. It clearly doesn't cap itself. Investigate its spawning logic.

---

## Files Modified (v23 changes, not deployed)

- `bots/buzzing/main.py` — military skip on expand maps, builder cap 12→15 on expand
- `bots/buzzing_prev/main.py` — NOT updated (v23 not deployed)
