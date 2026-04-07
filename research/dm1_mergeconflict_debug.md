# default_medium1 vs mergeconflict Debug

**Date:** 2026-04-06

---

## Initial Results

| Test | buzzing mined | mergeconflict mined | Winner |
|------|--------------|---------------------|--------|
| buzzing vs mergeconflict dm1 seed 1 | 1450 | 14310 | mergeconflict |
| buzzing vs mergeconflict dm1 seed 2 | 1450 | 14310 | mergeconflict |
| buzzing vs mergeconflict dm1 seed 99 | 1450 | 14310 | mergeconflict |
| buzzing vs starter dm1 seed 1 | 34780 | 0 | buzzing |

**Identical results across all seeds → structural, not seed-specific.**

---

## Extended Testing

| Test | buzzing/A mined | mergeconflict/B mined | Winner |
|------|----------------|----------------------|--------|
| buzzing(A) vs mergeconflict(B) dm1 | 1450 | 14310 | mergeconflict |
| mergeconflict(A) vs buzzing(B) dm1 | 18630 | 40240 | buzzing |
| buzzing vs mergeconflict default_medium2 | 14920 | 36810 | mergeconflict |
| buzzing vs mergeconflict galaxy | 19050 | 14550 | buzzing |
| buzzing vs mergeconflict gaussian | 27160 | 9550 | buzzing |
| buzzing_prev vs mergeconflict dm1 | 30 | 21900 | mergeconflict |

---

## Root Cause: Side-Dependent Resource Hijacking

The collapse is **side-dependent**:
- buzzing as player A (northwest): 1450 mined — collapse
- buzzing as player B (southeast): 40240 mined — dominant win

When buzzing is player A (northwest core), mergeconflict is player B (southeast core). Both bots build d.opposite() conveyors toward their respective cores. On default_medium1 with its symmetric ore layout, ore tiles near the map center are accessible to both sides.

mergeconflict's builders (from southeast) reach central ore tiles first (or simultaneously) and build conveyors pointing southeast (toward mergeconflict's core). When buzzing's delivery chain reaches these central tiles, buzzing's resources hit mergeconflict's conveyors and are **redirected to mergeconflict's core** instead of buzzing's.

This is the documented game mechanic: "Resources CAN be sent to enemy buildings via misplaced conveyors." mergeconflict accidentally (or not) creates a resource-siphon on default_medium1's central ore.

**Why not galaxy/gaussian?** On those maps, ore clusters are more isolated on each side. Builders reach their own ore without crossing the center. No shared conveyor paths.

**Why buzzing_prev also collapses (30 mined)?** The hijacking affects both bots equally — it's a map layout + spawn-side interaction, not a V59-specific issue.

---

## Is This a Real Ladder Threat?

Yes. Any opponent that:
1. Reaches central ore tiles
2. Builds d.opposite() conveyors pointing toward their own (southeast) core

...will accidentally siphon resources from the northwest player's delivery chain on symmetric medium maps. This is symmetric — if buzzing is southeast, it siphons from the northwest player.

The match outcome depends heavily on **which side you spawn**. On ladder, each match is 5 games with varying sides, so over 5 games the effect averages out. But in a single-game scenario, being on the "wrong" side vs this opponent archetype costs 13x Ti mined.

---

## Potential Fix

The fix would require buzzing to detect when its resources are being hijacked (Ti mined drops sharply while harvesters are working) and either:
1. Destroy the enemy conveyors on its chain (builder attack = 2 Ti, action cooldown)
2. Re-route its chain to avoid enemy-controlled tiles

This is a complex fix. For now, this is a known interaction with no safe simple fix.

**Verdict: Not a V59 regression. Pre-existing map interaction. Monitor but no immediate action.**
