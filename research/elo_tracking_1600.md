# V61 Ladder Monitoring — 1600 Elo Push

**Goal:** Reach 1600 Elo (Emerald tier) from ~1480  
**Bot:** V61 (662 lines, 68% win rate verified locally)  
**Monitoring started:** 2026-04-08 ~04:50 UTC  
**Starting Elo at monitor start:** ~1480 (after first V61 win)

---

## Current Status

| Metric | Value |
|--------|-------|
| **Estimated Elo** | ~1509 |
| **Target** | 1600 |
| **Gap** | ~91 Elo |
| **V61 Total Record** | 13W-12L (52.0%) |
| **Last 10 matches** | 3W-7L (30%) — steep decline |
| **Nemesis** | nibbly-fi (0-2), no_friend (1-2), nus robot husk (0-2), O_O (0-1) |

---

## All V61 Matches (Chronological)

| Time (local) | Result | Score | Opponent | Notes |
|-------------|--------|-------|----------|-------|
| ~19:56 | WIN | 4-1 | Taro Noodle House | First V61 match, strong start |
| 01:37 | WIN | 3-2 | Pray and Deploy | |
| 01:48 | WIN | 3-2 | Highly Suspect | We were Team B |
| 01:55 | WIN | 4-1 | What team name yall want | We were Team B |
| 02:06 | WIN | 4-1 | no_friend | We were Team B |
| 02:16 | WIN | 4-1 | Cenomanum | We were Team B |
| 02:27 | WIN | 3-2 | Chameleon | We were Team B |
| 02:36 | WIN | 3-2 | One More Time | We were Team B |
| 02:46 | LOSS | 2-3 | oslsnst | We were Team B (3-2 their favor) |
| 02:57 | WIN | 4-1 | New Jabees | |
| 03:07 | LOSS | 2-3 | nibbly-fi | We were Team B |
| 03:16 | LOSS | 2-3 | nus robot husk | |
| 03:26 | WIN | 4-1 | Vibecoders | We were Team B |
| 03:36 | WIN | 3-2 | MergeConflict | We were Team B |
| 03:48 | LOSS | 1-4 | KCPC-B | We were Team B |
| 03:56 | LOSS | 1-4 | Ash Hit | |
| 04:06 | LOSS | 2-3 | Stratcom | |
| 04:16 | LOSS | 2-3 | eidooheers | |
| 04:27 | LOSS | 2-3 | no_friend | 2nd loss to no_friend |
| 04:36 | WIN | 3-2 | N | |
| 04:45 | LOSS | 2-3 | nibbly-fi | 2nd loss to nibbly-fi |
| 04:57 | WIN | 3-2 | The Defect | We were Team B |
| 05:07 | LOSS | 1-4 | nus robot husk | We were Team B; 2nd loss to nus robot |
| 05:16 | LOSS | 2-3 | One More Time | Reversal — beat them 3-2 at 02:36 |
| 05:26 | LOSS | 1-4 | O_O | New nemesis; 3rd straight loss |

---

## Elo Estimate Trajectory

Starting at ~1480 (post-first V61 win):
- After 7-match win streak (~01:37-02:36): ~1514
- Losses at 02:46-03:16: ~1502
- Recovery wins 03:26-03:36: ~1512
- Loss streak 03:48-04:27: ~1488
- Recovery 04:36: ~1494
- Final loss 04:45: ~1490

**Current estimated Elo: ~1490-1509**

Note: Actual Elo depends on opponent ratings. Wins against higher-rated teams = more points. The late loss streak (Ash Hit, Stratcom, eidooheers, no_friend) may have dragged us below 1500.

---

## Nemesis Teams

| Opponent | Record vs Us | Notes |
|----------|-------------|-------|
| nibbly-fi | 0W-2L | Lost 2-3 both times |
| no_friend | 1W-1L | Win early (4-1), loss later (2-3) |
| oslsnst | 0W-1L | 2-3 |
| KCPC-B | 0W-1L | 1-4, tough opponent |
| Ash Hit | 0W-1L | 1-4, dangerous |
| Stratcom | 0W-1L | 2-3 |

---

## Win Rate Analysis

| Window | W-L | Rate |
|--------|-----|------|
| All V61 | 12W-9L | 57.1% |
| Last 10 | 6W-4L | 60% |
| Last 20 | 11W-9L | 55% |

---

## Monitoring Log

| Check Time | New Matches | V61 Record | Elo Est | Notes |
|------------|-------------|------------|---------|-------|
| 12:35 | 1 new | 13W-12L | ~1475-1485 | LOSS 1-4 vs O_O — matchmaker confirmed stopped after 05:26 |
| 05:55 | 0 new | 13W-11L | ~1480-1495 | No matches in 40 min — matchmaker quiet (off-peak) |
| 05:20 | 2 new | 13W-11L | ~1480-1495 | Two losses (nus robot husk 1-4, One More Time 2-3) |
| 04:50 | 20 new | 12W-9L | ~1490-1509 | Late loss streak concerning |
| 19:58 prev | 1 V61 | 1W-0L | ~1480 | V61 first match WIN |

---

## Path to 1600

At 55-57% win rate vs ~1500 avg opponents:
- Each win: ~+5 Elo
- Each loss: ~-5 Elo  
- Net per match: +0.5 Elo average
- Matches needed at this rate: ~180+ matches

**To actually reach 1600, need:**
- Win rate closer to 70%+ vs current field
- OR bot improvement to beat higher-rated teams consistently

**Recommendation:** Bot needs improvement. V61 is hitting a ceiling at ~1490-1510.
