# Ladder Monitoring — v36 Deploy (Apr 6, 2026)

## Summary

v36 was deployed as "Version 37" on the platform. Monitoring ran from ~10:26 EDT to ~10:49 EDT
(3 check-ins, covering matches from ~14:07 UTC to ~14:47 UTC).

### Elo Trajectory

| Check-in Time | Elo  | Rank   | Matches | Last 10 |
|---------------|------|--------|---------|---------|
| 10:31 EDT     | 1469 | #137   | 74      | 5W 5L   |
| 10:36 EDT     | 1479 | #135   | 75      | 6W 4L   |
| 10:42 EDT     | 1479 | #135   | 75      | 6W 4L   |
| 10:49 EDT     | 1476 | #134   | 76      | 5W 5L   |

**Net change this session: +7 Elo, improved rank from ~#137 to #134**

Pre-v36 baseline: ~1488 Elo, rank ~134/573 (per team lead context)

---

## Match Log (Apr 6, 2026 — Most Recent First)

| Time (UTC) | Result | Opponent       | Score | Notes                    |
|------------|--------|----------------|-------|--------------------------|
| 14:47      | LOSS   | Ash Hit        | 2-3   | 3rd loss to Ash Hit today|
| 14:36      | WIN    | eidooheerfmaet | 4-1   | Strong win               |
| 14:26      | WIN    | Fake Analysis  | 3-2   | Close win                |
| 14:15      | WIN    | EEZ            | 4-1   | Strong win               |
| 14:07      | LOSS   | Pray and Deploy| 0-5   | 5-0 sweep — significant  |
| 13:56      | WIN    | MEOW MEOW x5   | 5-0   | Perfect sweep            |
| 13:45      | LOSS   | double up      | 2-3   | Close loss               |
| 13:36      | LOSS   | Ash Hit        | 2-3   | Ash Hit is a tough matchup|
| 13:27      | WIN    | ah             | 4-1   | Good win                 |
| 13:17      | LOSS   | N              | 1-4   | Decisively beaten        |
| 13:05      | WIN    | Dino           | 3-2   | Close win                |
| 12:54      | LOSS   | andrew_and_friends | 1-4 | Decisively beaten       |
| 12:46      | LOSS   | MEOW MEOW x5   | 2-3   | Close loss               |
| 12:36      | LOSS   | O_O            | 1-4   | Decisively beaten        |
| 12:27      | LOSS   | natto warriors | 2-3   | Close loss               |
| 12:16      | WIN    | Fake Analysis  | 3-2   | Close win (as Team B)    |
| 12:06      | LOSS   | Cenomanum      | 2-3   | Close loss               |
| 11:56      | WIN    | 5goatswalking  | 4-1   | Strong win               |
| 11:46      | LOSS   | oslsnst        | 1-4   | Decisively beaten        |
| 11:35      | LOSS   | eidooheerfmaet | 2-3   | Later beat this opponent 4-1|
| 11:27      | LOSS   | Ash Hit        | 2-3   | Ash Hit recurs often      |
| 11:20      | WIN    | KCPC-B         | 3-2   | Close win (as Team B)    |

**Today's tally (22 matches visible): ~9W 13L = 41% win rate**

---

## Key Observations

### 1. Win Rate Analysis

Over the monitoring window, the last 10 shows 5W 5L (50%), with a peak of 6W 4L briefly.
The overall trend suggests v36 is performing near the 44% baseline — possibly slight improvement
in close matches but not a dramatic shift yet.

### 2. Ash Hit — Recurring Nemesis

Ash Hit appears 3 times in today's history (12:27 loss, 13:36 loss, 14:47 loss). All three
were close 2-3 or 3-2 losses. This team sits at ~Elo 1484 (rank ~131), just above us.
Consistent losses to this specific opponent suggest a strategic matchup weakness.

### 3. "Pray and Deploy" — 0-5 Sweep

The 14:07 match was a complete 0-5 loss to "Pray and Deploy". This is a significant red flag —
a 5-game sweep indicates systematic failure, not random variance. Worth investigating that team's
strategy. They may use rush tactics or have a specific counter to our economy-first approach.

### 4. Strong Wins Available

Multiple 4-1 and 5-0 wins (vs EEZ, eidooheerfmaet, MEOW MEOW, ah, 5goatswalking) show the bot
handles weaker opponents well. The issue is mid-tier (1450-1500) opponents.

### 5. Elo Stability

Elo is holding in the 1469-1479 band. Pre-v36 was reported at ~1488, so we are slightly below
that baseline at the moment. However, with only 74-76 matches played (vs 2000+ for ranked teams),
each match moves Elo more significantly.

### 6. Map-Specific Data (Not Available)

The CLI `match list` output does not show individual game maps — only total score per match.
To check if face/galaxy/arena maps are fixed, would need to either:
- Run `cambc match replay <match_id>` to download and inspect
- Use the visualizer on specific match replays

---

## Ladder Context (Current Top Around Us)

| Rank | Team            | Elo  | Matches |
|------|-----------------|------|---------|
| 129  | O_O             | 1495 | 2635    |
| 130  | Warwick CodeSoc | 1494 | 2635    |
| 131  | Cenomanum       | 1491 | 2635    |
| 132  | One More Time   | 1489 | 2635    |
| 133  | Highly Suspect  | 1480 | 2635    |
| **134** | **buzzing bees** | **1476** | **76** |
| 135  | eidooheerfmaet  | 1476 | 1302    |
| 136  | N               | 1474 | 2230    |
| 137  | Some People     | 1469 | 2636    |

**Key observation:** Teams above us have 2000-2635 matches vs our 76. Our Elo will converge to
its true value much faster once we get more matches — currently we're in high-variance territory.

---

## Target Assessment: 1550+ by Apr 20 Qualifier

- Current: 1476 Elo, #134/574
- Target: 1550+ (to get a competitive rank before qualifier)
- Gap: +74 Elo needed in ~14 days
- At current ~10 matches/day rate: need sustained 60%+ win rate

### Key Issues to Fix:
1. **0-5 sweeps** (Pray and Deploy) — rush defense or early aggression counter needed
2. **Ash Hit matchup** — 0-3 record today, need to understand their strategy
3. **Tight map performance** — v36 enabled gunners at round 60 on tight maps, but unclear if
   that's helping close matches on those specific maps
4. **Only 76 matches played** — Elo is still highly volatile, both up and down risk

---

## Recommendations

1. Download a replay of the Pray and Deploy match (0-5 loss at 14:07) — worst result of the day
2. Download a replay of one Ash Hit match to analyze their strategy
3. Continue monitoring — need more data as v36 propagates (matches queue every ~10 min)
4. Consider that the true v36 impact is still emerging — first few matches may have been queued
   before the new version was active

---

*Monitoring session: 10:26-10:49 EDT, Apr 6, 2026*
*Check-ins: 4 (at 10:31, 10:36, 10:42, 10:49)*
*Total matches observed: 22 (IDs from 11:20 to 14:47 UTC)*
