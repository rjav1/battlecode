# Next Highest-Value Improvement

**Date:** 2026-04-06
**Question:** What's the next safe improvement after the current plateau?

---

## Option Analysis

### Option 1: Debug corridors chain direction

Corridors (31x31 = balanced) mines 5090 Ti with V56 vs smart_eco's 14660 — a 3x gap. V57 (bridge removal) fixed this to 14520 but hurt other maps (57% vs 65% ladder). The root cause is specifically the **chain-join bridge** (bridge to nearest allied conveyor closer to core), not bridges to core.

Key data point: default_medium1 has the SAME pattern — V56 buzzing mines 9100 vs smart_eco's 26320 (3x gap). buzzing_prev mines 4960 there too (bridge wasn't helping). The bridge block (both chain-join AND core fallback) is consistently producing buildings without proportional Ti delivery improvement on maps where smart_eco pulls ahead.

**Targeted fix hypothesis:** Remove only the chain-join bridge leg, keep core-fallback bridge. This would:
- Fix corridors/default_medium1 chain breakage (chain-join is the culprit)
- Keep the core-bridge shortcut for open maps where ore is close to core

Test: replace the `if best_chain:` block with nothing (skip chain-join entirely), keep the "Fallback: bridge to core tile" block.

### Option 2: econ_cap vis_harv undercounting

The `econ_cap = max(time_floor, vis_harv*3+4)` formula is a cap on spawning based on harvesters visible to core (r²=36). On cold/corridors, harvesters placed far away aren't visible → econ_cap stays near time_floor.

Analysis shows: the balanced cap formula (`cap = 3→4→6→8`) is the actual binding constraint, not econ_cap. At round 100, balanced cap=4, econ_cap=max(6,0*3+4)=6 — econ_cap is HIGHER than cap, so it doesn't throttle. Testing the smart_eco cap schedule (4→6→7→8) showed marginal gains (default_medium1 +720 mined, cold -70). Not the primary lever.

**Conclusion: econ_cap is not the bottleneck on most maps. Cap schedule is close to optimal.**

### Option 3: Dead code cleanup (_perp_left/_perp_right)

`_perp_left` and `_perp_right` at lines 36–41 are defined but no longer called (sentinel was removed). Removing them saves ~5 lines but zero runtime impact. Not meaningful.

---

## Recommendation: Option 1 — Remove chain-join bridge, keep core-fallback bridge

### Why this is highest-value

The 80-match test showed V57 (full bridge removal) scored 57% vs V56 (chain-join + core bridges) at 65%. That means bridges help on ~8% of ladder matches. But on corridors and default_medium1, the chain-join bridge produces a 3x Ti mined gap.

**The specific fix:** Remove only the `if best_chain:` block from `_bridge_target`. Keep the "Fallback: bridge to core tile" logic. This should:
- Fix corridors/default_medium1 (chain-join was breaking delivery chains)
- Keep open-map core bridges (beneficial on face, galaxy, etc.)
- Risk: lower than full removal (core bridges worked fine in buzzing_prev)

### Proposed change

Current `_bridge_target` block:
```python
if ti >= bc + 5:
    # First: bridge to nearest allied chain tile closer to core  ← REMOVE THIS
    my_team = c.get_team()
    best_chain = None
    ...
    if best_chain:
        for bd in DIRS:
            bp = ore.add(bd)
            if c.can_build_bridge(bp, best_chain):
                c.build_bridge(bp, best_chain)
                built = True
                break
    # Fallback: bridge to core tile  ← KEEP THIS
    if not built:
        ...bridge to core...
```

Change to: skip chain-join entirely, always go straight to the core-fallback bridge logic. Also restore the `9 < dist <= 25` distance gate from buzzing_prev (don't fire for ore very far from core on maze maps).

### Expected outcome

- corridors: 5090 → ~14000 mined (fix chain breakage from chain-join)
- default_medium1: 9100 → ~14000+ mined (same root cause)  
- face/galaxy/settlement: unchanged or better (core bridge still fires)
- cold: slight improvement (chain-join was breaking some cold chains too)
- Risk: minimal — core-only bridge was buzzing_prev's behavior and was stable

---

## Summary

The chain-join bridge is responsible for the corridors/default_medium1 3x Ti gap. Full bridge removal overcorrects (hurts open maps). Core-only bridge with dist gate is the surgical fix that should recover corridors while keeping the open-map benefit. This is the highest-value next improvement.
