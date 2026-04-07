# Ladder Monitoring — V51

**Monitoring started:** 2026-04-07T00:48 UTC  
**Version live:** V51 (chain-fix improvements + wall-density guard)  
**Previous baseline:** V49=65% local, V51=55% local

---

## Baseline (last 10 matches at monitor start)

| Result | Score | Opponent | Time |
|--------|-------|----------|------|
| W | 4-1 | natto warriors | 00:48 |
| W | 3-2 | Code Monkeys | 00:36 |
| W | 3-2 | O_O | 00:26 |
| L | 2-3 | MWLP | 00:16 |
| W | 4-1 | Atomic | 00:06 |
| L | 1-4 | Chameleon | 23:57 |
| W | 3-2 | Botz4Lyf | 23:45 |
| W | 4-1 | 5goatswalkintoabarbut1dies | 23:34 |
| L | 2-3 | Dino | 23:26 |
| L | 0-5 | N | 23:16 |

**Pre-monitor snapshot: 6W-4L (60%) across last 10**  
Latest match ID at start: `531a9d7e-bb45-47ee-9a5a-be6b665df9e2`

---

## Poll Log

| Time (UTC) | New Matches | Running W-L | Notes |
|------------|-------------|-------------|-------|
| 00:48 | — | 6W-4L baseline | Monitor started |
| 00:58 | 1 | 7W-4L | W 3-2 vs oslsnst |
| 01:08 | 1 | 8W-4L | W 4-1 vs MEOW MEOW MEOW MEOW MEOW |
| 01:11 | 0 | 8W-4L | No new matches |
| 01:14 | 0 | 8W-4L | No new matches |
| 01:17 | 0 | 8W-4L | No new matches — ladder quiet |
| 01:20 | 1 | 8W-5L | L 1-4 vs Pray and Deploy (cbf9cff6) |
| 01:23 | 0 | 8W-5L | No new matches |
| 01:26 | 0 | 8W-5L | No new matches |
| 01:29 | 1 | 8W-6L | L 2-3 vs MWLP |
| 01:32 | 0 | 8W-6L | No new matches |
| 01:35 | 0 | 8W-6L | No new matches |
| 01:38 | 0 | 8W-6L | No new matches |
| 01:41 | 1 | 9W-6L | W 4-1 vs O_O |
| 01:44 | 0 | 9W-6L | No new matches |
| 01:47 | 0 | 9W-6L | No new matches |
| 01:50 | 1 | 9W-7L | L 2-3 vs ah |
| 01:53 | 0 | 9W-7L | No new matches |
| 01:56 | 0 | 9W-7L | No new matches |
| 01:59 | 1 | 9W-8L | L 1-4 vs Cenomanum |
| 02:02 | 0 | 9W-8L | No new matches |
| 02:05 | 0 | 9W-8L | No new matches |
| 02:08 | 0 | 9W-8L | No new matches |
| 02:12 | 1 | 10W-8L | W 4-1 vs KCPC-B |
| 02:15 | 0 | 10W-8L | No new matches |
| 02:18 | 0 | 10W-8L | No new matches |
| 02:19 | 1 | 11W-8L | W 3-2 vs double up — monitor session complete |

---

## Session Summary

**Monitor window:** 2026-04-07T00:48 → 02:19 UTC (~90 minutes)  
**Session record (new matches only):** 5W-4L (56%)  
**Cumulative (baseline + session):** 11W-8L (58%)

### All matches during session
| Time | Result | Score | Opponent |
|------|--------|-------|----------|
| 00:56 | W | 3-2 | oslsnst |
| 01:05 | W | 4-1 | MEOW MEOW MEOW MEOW MEOW |
| 01:16 | L | 1-4 | Pray and Deploy |
| 01:26 | L | 2-3 | MWLP |
| 01:37 | W | 4-1 | O_O |
| 01:46 | L | 2-3 | ah |
| 01:55 | L | 1-4 | Cenomanum |
| 02:09 | W | 4-1 | KCPC-B |
| 02:16 | W | 3-2 | double up |

### Observations
- **P&D loss (1-4):** Third time meeting them, third 0-5 style loss. Maps: hourglass, default_small1, git_branches, arena (all losses) + cold (win). Same pattern as previous analysis — sparse/maze maps + tight maps hurt us.
- **Win rate holding ~55-60% on ladder** — consistent with V51's 55% local baseline.
- **4-1 wins vs MEOW MEOW and KCPC-B** — healthy wins against weaker opponents.
- **2-3 close losses vs ah and MWLP** — competitive games, slightly below par.
- Ladder matchmaking is slow (~1 match per 10 min during this window).

### Verdict
V51 is performing at approximately 55-58% on the live ladder, matching the local 55% baseline. No evidence of improvement over V49 (65% local). The chain-fix improvements are not yet showing measurable effect at the macro level — P&D continues to dominate on the same map types identified in prior analysis.

---

## Match Detail Log

### L 1-4 vs Pray and Deploy — 2026-04-07T01:16 (cbf9cff6)
| G | Map | Result | Condition | Turns |
|---|-----|--------|-----------|-------|
| 1 | hourglass | L | resources | 2000 |
| 2 | default_small1 | L | resources | 2000 |
| 3 | git_branches | L | resources | 2000 |
| 4 | arena | L | resources | 2000 |
| 5 | cold | **W** | resources | 2000 |

1-4 loss. All games to round 2000 (resource tiebreakers). We won only cold. Hourglass, default_small1, arena are known weak maps. git_branches is new — likely another maze/sparse map. Pattern consistent with previous P&D analysis.
