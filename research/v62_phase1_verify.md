# V62 Phase 1 Ore Proximity Fix — Verification Sample

**Date:** 2026-04-08
**Bot:** buzzing (V62 with Phase 1 ore proximity fix)
**Sample:** Second 50-match run (first was 64%, this is verification)

## This Sample: 29W-21L = 58% win rate

## Combined with First Sample
- First 50: 32W-18L = 64%
- Second 50: 29W-21L = 58%
- **Combined 100: 61W-39L = 61%**

## Assessment

The second sample (58%) is below the first (64%), and the combined 61% is **below V61's established 66% baseline**. This suggests Phase 1 did not improve performance and may have slightly regressed it.

**Verdict: Phase 1 ore proximity fix does NOT clear 64% consistently. Combined result is 61%, below V61's 66%.**

---

## Per-Opponent This Sample

| Opponent | W | L | Win% |
|----------|---|---|------|
| adaptive | 2 | 1 | 67% |
| balanced | 0 | 1 | 0% |
| barrier_wall | 2 | 1 | 67% |
| fast_expand | 2 | 1 | 67% |
| ladder_eco | 3 | 2 | 60% |
| ladder_fast_rush | 3 | 0 | 100% |
| ladder_hybrid_defense | 1 | 4 | 20% |
| ladder_mergeconflict | 2 | 2 | 50% |
| ladder_rush | 1 | 0 | 100% |
| rusher | 2 | 2 | 50% |
| sentinel_spam | 2 | 1 | 67% |
| smart_defense | 2 | 1 | 67% |
| smart_eco | 3 | 4 | 43% |
| turtle | 4 | 1 | 80% |

Notable: ladder_hybrid_defense went 1-4 (20%) — consistent problem from V61 baseline.

---

## Per-Map This Sample (notable results)

**Losses:**
- hourglass: 0W-2L (appeared twice, lost both — unplayed in V61 baseline)
- face: 0W-3L (lost all 3 appearances)
- minimaze: 0W-2L
- wasteland_oasis: 1W-3L (50% -> dragged down)

**Wins:**
- wasteland: 3W-0L
- default_medium1: 2W-0L
- default_large1/2: solid

---

## Conclusion

Phase 1 ore proximity fix does not show a reliable improvement over V61's 66% baseline. The combined 100-match result (61%) is 5 points below V61. Recommend either:
1. Revert Phase 1 and keep V61 as the baseline
2. Investigate why `face`, `hourglass`, `minimaze`, and `ladder_hybrid_defense` are regressing before deploying
