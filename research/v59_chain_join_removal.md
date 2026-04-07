# V59 Chain-Join Bridge Removal Test

**Date:** 2026-04-06
**Change:** Remove chain-join leg from `_bridge_target` block; keep core-fallback bridge with `9 < dist_sq <= 25` gate (matching buzzing_prev behavior)

---

## Change Made

In `bots/buzzing/main.py`, replaced the full `_bridge_target` block (chain-join + core fallback) with:

```python
# Bridge shortcut: after building harvester, bridge directly to core
# Chain-join removed — bridging to mid-chain conveyors breaks delivery on maze maps
# Only fire when ore is in the sweet spot: close enough to bridge (dist<=25) but
# not so close that the conveyor chain already delivers (dist>9)
if (self._bridge_target and self.core_pos
        and c.get_action_cooldown() == 0):
    ore = self._bridge_target
    if 9 < ore.distance_squared(self.core_pos) <= 25:
        ti = c.get_global_resources()[0]
        bc = c.get_bridge_cost()[0]
        if ti >= bc + 5:
            # Bridge to nearest core tile (no chain-join)
            cx, cy = self.core_pos.x, self.core_pos.y
            core_tiles = [Position(cx + dx, cy + dy)
                          for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
            built = False
            for ct in sorted(core_tiles, key=lambda t: ore.distance_squared(t)):
                for bd in DIRS:
                    bp = ore.add(bd)
                    if c.can_build_bridge(bp, ct):
                        c.build_bridge(bp, ct)
                        built = True
                        break
                if built:
                    break
            self._bridge_target = None
            if built:
                return
    else:
        self._bridge_target = None
```

---

## Single-Map Spot Check (vs smart_eco, seed 1)

| Map | V56 mined | V59 mined | Change |
|-----|-----------|-----------|--------|
| corridors | 5090 | 10060 | +98% |
| default_medium1 | 9100 | 19760 | +117% |
| cold | 19670 | 19670 | 0% |
| face | 16400 | 16400 | 0% |
| settlement | 37870 | 37870 | 0% |
| galaxy | 9950 | 9950 | 0% |

corridors and default_medium1 significantly improved. Other maps unchanged.

---

## 50-Match Baseline

```
Final: 32W-18L-0D (64% win rate)
```

**PASS — above 63% threshold.**

Baseline for comparison: V56 = 65% (80-match), V57 (full removal) = 57%.

V59 at 64% is within CI of V56's 65% while recovering the corridors/default_medium1 3x gap.

### Notable match results:
- sentinel_spam on corridors: LOSS (corridors still loses vs sentinel_spam — map-specific issue)
- smart_eco on gaussian: WIN
- balanced on cold: WIN (×2)
- balanced on default_medium1: WIN
- rusher on dna, gaussian: LOSS (rusher remains a nemesis)
- smart_eco on butterfly, default_large1, shish_kebab: LOSS

---

## Verdict: PASS — Recommend Deploy as V59

64% win rate (32W-18L) meets the ≥63% threshold. The surgical chain-join removal fixes the corridors/default_medium1 3x regression without the broad regression that full bridge removal caused (57%).

Key improvement: chain-join bridge was teleporting resources to mid-chain conveyors that rejected them (wrong input side) — orphaning the upstream chain. Core-only bridge with dist gate is safe and preserves the open-map benefit.
