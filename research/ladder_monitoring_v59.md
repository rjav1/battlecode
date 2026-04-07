# V59 Ladder Monitoring

**V59 deployed:** 2026-04-07 ~17:10 UTC  
**V59 = chain-join bridge removed, core-bridge dist 9-25 guard (74% local baseline)**  
**Monitoring started:** 17:10 UTC  
**Current Elo at V59 deploy:** ~1503 (after two V58 losses)

---

## V59 Matches

| Result | Score | Opponent | Opp Elo (before) | Elo Delta | Time |
|--------|-------|----------|-----------------|-----------|------|
| WIN | 4-1 | Pray and Deploy | ~1440 | +2 | 19:25 |
| LOSS | 3-2 | Quwaky | ~1460 | -5 | 19:15 |
| WIN | 3-2 | N | ~1450 | +3 | 19:06 |
| WIN | 1-4 | MWLP | ~1455 | +3 | 18:57 |
| LOSS | 3-2 | Code Monkeys | ~1475 | -4 | 18:46 |
| LOSS | 1-4 | binary bros | ~1475 | -8 | 18:35 |
| WIN | 3-2 | Cenomanum | ~1460 | +3 | 18:27 |
| LOSS | 3-2 | oslsnst | ~1460 | -4 | 18:17 |
| WIN | 2-3 | Botz4Lyf | 1455 | +2.6 | 18:06 |
| LOSS | 1-4 | natto warriors | 1477 | -9.6 | 17:57 |
| WIN | 3-2 | O_O | 1477 | +3.3 | 17:47 |
| LOSS | 1-4 | KCPC-B | 1485 | -9.5 | 17:39 |
| LOSS | 1-4 | Chameleon | 1483 | -10.1 | 17:26 |

**V59 total: 6W-7L (46%), current Elo ~1468**

---

## Check-in Update — 18:00

Latest match: **LOSS 1-4 vs natto warriors** (17:57)

V59 record now **1W-4L** since deploy. Elo likely ~1458.

Recent sequence (all V59): LOSS, LOSS, LOSS, WIN, LOSS — poor showing on ladder despite 74% local baseline.

Butterfly investigation result: **butterfly is NOT a bug** — asymmetric map favors player 2; when buzzing plays player 2 on butterfly it mines 51530 Ti vs buzzing_prev's 44400. The 0W-3L result was because test always ran buzzing as player 1.

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
| 19:28 | 7 | 6W-7L | ~1468 | WIN 4-1 Pray+Deploy (19:25), LOSS vs Quwaky (19:15), WIN 3-2 N (19:06), WIN vs MWLP (18:57), LOSS vs Code Monkeys (18:46), LOSS 1-4 binary bros (18:35), WIN 3-2 Cenomanum (18:27) |
| 18:20 | 2 | 2W-5L | ~1461 | LOSS 3-2 oslsnst (18:17), WIN 2-3 Botz4Lyf (18:06, as B scored 3) |
| 18:00 | 1 | 1W-4L | ~1458 | LOSS 1-4 vs natto warriors (17:57) |
| 17:50 | 1 | 1W-3L | ~1468 | WIN 3-2 vs O_O (17:47) — only V59 win so far |
| 17:41 | 1 | 0W-2L | ~1465 | LOSS 1-4 vs KCPC-B (17:39) |
| 17:28 | 1 | 0W-1L | ~1484 | LOSS 1-4 vs Chameleon (1483) — first V59 match |
| 17:18 | 0 | 0W-0L | ~1494 | Still playing V58 — nus robot husk LOSS 1-4 (V58, -9.5) |
| 17:10 | 0 | 0W-0L | ~1503 | V59 just deployed |

---

## What V59 Changed

Chain-join leg of bridge shortcut removed. Core-bridge kept with `9 < ore_core_dist <= 25` guard.
- Was breaking conveyor chains on corridors and other maps (no dist guard, bridged to mid-chain conveyors)
- Fix: only bridge ore directly to core tile, only for medium-range ore
- Local baseline: 74% (vs V58's 60-65%)
