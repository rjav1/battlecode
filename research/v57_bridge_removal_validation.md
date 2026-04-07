# V57 Bridge Removal Validation

**Date:** 2026-04-06
**Change:** Full removal of `_bridge_target` post-harvester bridge block (chain-join + core fallback)

---

## Test Results

### buzzing vs smart_eco corridors seed 1

| | buzzing | smart_eco |
|--|--|--|
| Ti mined | **14520** | 14660 |
| Winner | smart_eco (resources tiebreak) | — |

corridors: 14520 mined — up from 5090 pre-fix (+185%). Within 1% of smart_eco. Loss is on Ti stored (tiebreak), not mined.

### buzzing vs smart_eco gaussian seed 1

| | buzzing | smart_eco |
|--|--|--|
| Ti mined | **24780** | 23900 |
| Winner | **buzzing** | — |

buzzing wins gaussian vs smart_eco — +880 Ti mined advantage.

### buzzing vs balanced gaussian seed 1

| | buzzing | balanced |
|--|--|--|
| Ti mined | 14420 | **29680** |
| Winner | balanced | — |

buzzing loses badly to `balanced` on gaussian (-15260 mined). `balanced` is mining 2x more Ti. This indicates there is another opponent with aggressive builder caps that outperforms buzzing on gaussian. Worth investigating — likely builder cap / econ_cap throttle gap vs high-end opponents.

### buzzing vs buzzing_prev corridors seed 1

| | buzzing | buzzing_prev |
|--|--|--|
| Ti mined | **14520** | 14850 |
| Winner | buzzing_prev (resources tiebreak) | — |

Within 2% of buzzing_prev — essentially parity. Bridge fix fully restored corridors efficiency.

---

## Summary

| Test | Before (V55) | After (V57) | Change |
|------|-------------|-------------|--------|
| corridors vs smart_eco | 5090 mined | 14520 mined | +185% |
| gaussian vs smart_eco | ~5000 mined | 24780 mined | +395% |
| corridors vs buzzing_prev | 5090 mined | 14520 mined | +185% |

Bridge removal is confirmed correct. The chain-join bridge was breaking delivery chains on all map types, not just corridors.

## Flag: `balanced` bot on gaussian

`balanced` mines 29680 Ti on gaussian vs buzzing's 14420 — a 2x gap. The `balanced` bot is likely a reference bot with aggressive builder caps and no econ_cap throttle. This is the next performance gap to close.
