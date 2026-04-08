# Elo Grind Status Report

## Date: 2026-04-08
## Current Status: Rating 1463 (Silver), Rank #144 of 578, 318 matches played

---

## Last 30 Ladder Matches (most recent first)

| # | Opponent | Score | We Are | Result |
|---|----------|-------|--------|--------|
| 1 | What team name yall want | 3-2 | A (us first) | **WIN** |
| 2 | Polska Gurom | 3-2 | A | **WIN** |
| 3 | oslsnst | 3-2 | B (them first) | **LOSS** |
| 4 | Highly Suspect | 5-0 | B | **LOSS** |
| 5 | andrew_a | 2-3 | B | **WIN** |
| 6 | Some People | 1-4 | A | **LOSS** |
| 7 | The Defect | 3-2 | B | **LOSS** |
| 8 | Pray and Deploy | 2-3 | A | **LOSS** |
| 9 | Warwick CodeSoc | 1-4 | B | **WIN** |
| 10 | Atomic | 1-4 | B | **WIN** |
| 11 | O_O | 1-4 | A | **LOSS** |
| 12 | One More Time | 2-3 | A | **LOSS** |
| 13 | nus robot husk | 4-1 | B | **LOSS** |
| 14 | The Defect | 2-3 | B | **WIN** |
| 15 | nibbly-fi | 2-3 | A | **LOSS** |
| 16 | N | 3-2 | A | **WIN** |
| 17 | no_friends | 2-3 | A | **LOSS** |
| 18 | eidooheer | 2-3 | A | **LOSS** |
| 19 | Stratcom | 2-3 | A | **LOSS** |
| 20 | Ash Hit | 1-4 | A | **LOSS** |
| 21 | KCPC-B | 4-1 | B | **LOSS** |
| 22 | MergeConflict | 2-3 | B | **WIN** |
| 23 | Vibecode | 1-4 | B | **WIN** |
| 24 | nus robot husk | 2-3 | A | **LOSS** |
| 25 | nibbly-fi | 3-2 | B | **LOSS** |
| 26 | New Jabees | 4-1 | A | **WIN** |
| 27 | oslsnst | 3-2 | B | **LOSS** |
| 28 | One More Time | 2-3 | B | **WIN** |
| 29 | Chameleon | 2-3 | B | **WIN** |
| 30 | Cenomanum | 1-4 | B | **WIN** |

## Win Rate: 13W-17L = 43%

At 43% win rate, we are LOSING Elo. We need 50%+ to maintain, 60%+ to climb.

---

## Elo Breakdown

- **Current rating:** 1463 (Silver, need 1500 for Gold)
- **Rank:** #144 of 578 (top 25%)
- **Last 10:** 5W-5L (50% — stable, not climbing)
- **Last 30:** 13W-17L (43% — declining)
- **Active bot:** v61

## Repeat Opponents

| Opponent | Record | Notes |
|----------|--------|-------|
| oslsnst | 0-2 | Consistently losing |
| The Defect | 1-1 | Split |
| nibbly-fi | 0-2 | Consistently losing |
| One More Time | 1-1 | Split |
| nus robot husk | 0-2 | Consistently losing — 4-1 and 2-3 losses |

---

## Unrated Match Capability

**YES — we can challenge specific opponents for unrated matches.**

Command: `cambc match unrated <OPPONENT_TEAM_ID>`

To find a team's ID: `cambc team search <name>`

**Unrated matches do NOT affect Elo.** They're practice only.

**Limitation:** Cannot grind Elo via unrated matches — they don't count toward rating. Only ladder matches (auto-matched every ~10 minutes) affect Elo.

**Use case:** Test our bot against specific opponents to understand weaknesses, then tune. But since V61 is final, this is mainly for scouting.

---

## Path to 1500 (Gold)

Need: +37 Elo (1463 -> 1500)
At ~3.5 Elo per match, need ~11 net wins.
At current 43% rate over 30 matches: -4 net wins. **Going backwards.**

**To stabilize:** Need 50%+ win rate. V61 is 74% vs local test bots but 43-50% on ladder. The ladder opponents are stronger than our test suite.

**To climb to Gold (1500):**
- Need consistent 55%+ win rate on ladder
- Or a version upgrade that improves win rate by 10%+ (which has proven impossible — V61 IS our ceiling)

---

## Strategic Options

1. **Submit and wait** — V61 at 50% (last 10) may stabilize near 1463. Not climbing but not falling fast.

2. **Scout specific opponents** — Use unrated matches against our 0-2 opponents (oslsnst, nibbly-fi, nus robot husk) to understand their strategies. Won't improve Elo but could inform future tuning.

3. **Accept 1463 as the V61 ceiling** — Focus on competition strategy (map bans, tournament format) rather than Elo grinding.
