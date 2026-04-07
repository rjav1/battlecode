# V59 Ladder Monitoring

**V59 deployed:** 2026-04-07 ~17:10 UTC  
**V59 = chain-join bridge removed, core-bridge dist 9-25 guard (74% local baseline)**  
**Monitoring started:** 17:10 UTC  
**Current Elo at V59 deploy:** ~1503 (after two V58 losses)

---

## V59 Matches

*(No V59 matches yet — waiting for first matchmaking cycle)*

---

## V58 Matches (for context — played before V59 deployed)

| Result | Score | Opponent | Opp Elo (before) | Elo Delta | Version | Time |
|--------|-------|----------|-----------------|-----------|---------|------|
| LOSS | 1-4 | Stratcom | 1517 | -9.4 | V58 | 17:06 |
| LOSS | 0-5 | MergeConflict | 1521 | -16.4 | V58 | 16:56 |
| WIN | 4-1 | natto warriors | ~1499 | +9.2 | V57 | 16:47 |
| WIN | 5-0 | eidooheerfmaet | ~1507 | +16.2 | V57 | 16:35 |
| LOSS | 2-3 | KCPC-B | ~1499 | -3.6 | V57 | 16:27 |
| WIN | 3-2 | Cenomanum | ~1491 | +2.6 | V57 | 16:16 |

V57/V58 total: 3W-3L (50%), Elo dropped from ~1529 → ~1503

**Strong opponents encountered:** MergeConflict (1521, 1598 matches), Stratcom (1517, 2795 matches) — both experienced. V58 is 0-2 vs these.

---

## Monitoring Log

| Check Time | New Matches | V59 Record | Elo | Notes |
|------------|-------------|------------|-----|-------|
| 17:18 | 0 V59 | 0W-0L | ~1494 | Still playing V58 — nus robot husk LOSS 1-4 (V58, -9.5) |
| 17:10 | 0 V59 | 0W-0L | ~1503 | V59 just deployed |

---

## What V59 Changed

Chain-join leg of bridge shortcut removed. Core-bridge kept with `9 < ore_core_dist <= 25` guard.
- Was breaking conveyor chains on corridors and other maps (no dist guard, bridged to mid-chain conveyors)
- Fix: only bridge ore directly to core tile, only for medium-range ore
- Local baseline: 74% (vs V58's 60-65%)
