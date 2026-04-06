# Pray and Deploy Investigation — 0-5 Sweep Analysis

**Date:** 2026-04-06  
**Match ID:** 783cc2fd-8a7d-4b11-af5d-fdebc22cf8d1  
**Our bot:** buzzing bees v36  
**Their bot:** Pray and Deploy v20

---

## Match Summary

We lost 0-5 (all 5 games). Every game went to round 2000 and was decided by **resources tiebreaker** — not a core kill. Pray and Deploy simply out-economed us on every map.

| Game | Map | Win Condition | Turns |
|------|-----|---------------|-------|
| 1 | default_small1 | resources | 2000 |
| 2 | bar_chart | resources | 2000 |
| 3 | galaxy | resources | 2000 |
| 4 | cubes | resources | 2000 |
| 5 | tree_of_life | resources | 2000 |

**No game ended early.** This is not a rush strategy. They did not destroy our core. They out-farmed us across 5 different maps with different geometries.

---

## Elo Context

| | Before Match | After Match |
|--|---|---|
| buzzing bees | 1472 | 1479 (+7) |
| Pray and Deploy | 1484 | 1517 (+15) |

- P&D was rated ~12 Elo higher than us going in — close to equal
- The expected score was roughly 50/50 — a 0-5 sweep is a major upset
- **P&D is NOT a highly-rated team.** They are Silver tier (~1517 Elo) with 2637 matches played
- They have been playing since 2026-03-16 (3 weeks) and are a 4-person UK team

---

## Pray and Deploy Performance Analysis

From their last 50 matches (as of 2026-04-06 ~15:05):

- **Win rate: 42%** (21 wins, 29 losses out of 50)
- **5-0 sweeps won:** 2 (us, and one other)
- **0-5 sweeps lost:** 2 (nus robot husk, Comp Practical Analysis Enjoyers)
- Their rating fluctuates around 1484–1517 — they are a mid-tier bot

### Teams that beat P&D (sample):
Blue Dragon, bot123, The Blades, sixseven, the_best_team, sacred stack of njtz, Comp Practical Analysis Enjoyers, nus robot husk, Highly Suspect, SPAARK, JDK: More like IDK, Bumchit, Vibecode, ert, AspiringGMs, DODO

### Teams P&D beats:
food, Goobie Woobies, Axionite Inc, natto warriors, One More Time, The Edge Case, Por Favor, object Object, Lorem Ipsum, Tylenol Enthusiasts, MWLP, BFS Enjoyers (us), Some People

**Pattern:** P&D loses regularly to teams rated 1500+ and even several below 1500. This was not a dominant opponent — we should be able to beat them.

---

## What Probably Happened

### Critical finding: ALL 5 games decided by resources at round 2000

This rules out:
- Rush strategy (would end early via core kill)
- Aggressive military (would end before round 2000)
- TLE/crash (would show error condition)

The only way P&D wins all 5 by resources is **superior economy**. They delivered more titanium + axionite to their core over 2000 rounds.

### Possible causes of our loss:

1. **Economy gap** — Their v20 may have a more efficient harvester placement or conveyor network that scales better by round 2000. We were on v36 which has been our working build, but something in the pure economy tiebreaker is being lost.

2. **Axionite tiebreaker** — Tiebreaker #1 is **total refined axionite delivered**. If they refine axionite and we don't, they win even with equal titanium. Our v36 may not be delivering refined Ax to core, or not enough.

3. **Map adaptation** — 5 different maps (default_small1, bar_chart, galaxy, cubes, tree_of_life). We lost all 5. This suggests a systematic disadvantage, not a map-specific issue.

4. **Late-game scaling** — Our unit count cap or econ formula may be cutting off harvester growth too early, while P&D continues expanding past round ~500.

---

## Comparison with Our Other 0-5 Losses

From all 77+ matches played:

| Opponent | Their Elo | Win Condition | Notes |
|----------|-----------|---------------|-------|
| I dont know | 1833 | ? | Higher rated — expected loss |
| brumbaclarts | 976 | ? | LOWER rated — major upset |
| AI | 757 | ? | Very low rated — bot crash? |
| Comp Practical Analysis Enjoyers | 1905 | ? | Higher rated — expected loss |
| **Pray and Deploy** | **1517** | **resources** | **Near-equal — explained here** |
| ert | 1331 | ? | Lower rated — concerning |
| Mysticmage45 | 1351 | ? | Lower rated |
| Postmodern Prosperos | 2268 | ? | Very high — expected |
| KAIZEN | 1645 | ? | Higher — plausible |
| Peanut | 1742 | ? | Higher — plausible |
| Enter team name | 1170 | ? | Lower rated — concerning |
| wandering_supernova | 827 | ? | Very low — early bot era |

**Note:** Several 0-5 losses are against lower-rated teams, which is a real problem. The Pray and Deploy match is not uniquely bad — we have a pattern of losing economically even to weak bots.

---

## Replay Available

Game 1 replay downloaded to:
`/C/Users/rahil/downloads/battlecode/783cc2fd-8a7d-4b11-af5d-fdebc22cf8d1_game_1.replay26`

View with: `cambc watch 783cc2fd-8a7d-4b11-af5d-fdebc22cf8d1_game_1.replay26`

All 5 game replays available via: `cambc match replay 783cc2fd-8a7d-4b11-af5d-fdebc22cf8d1`

---

## Recommended Actions

### High Priority
1. **Watch game 1 replay** — Compare resource totals at round 2000 between us and P&D. Look for: do they have foundry + refined Ax delivery? How many harvesters do they have? Do they use splitters for efficiency?

2. **Verify Ax tiebreaker delivery** — TB#1 is refined Ax delivered to core. If P&D has even 1 foundry delivering refined Ax and we have zero, they win every close game. Our current bot may not be building foundries at all.

3. **Test v36 vs starter on tiebreaker** — Run a local match specifically looking at round 2000 resource scores. Use `print()` or `draw_indicator_dot` to see how much refined Ax each team has delivered.

### Medium Priority
4. **Check econ_cap formula** — Our unit cap may be capping harvesters at a suboptimal count. If P&D builds more harvesters by late game, they pull ahead on titanium delivery.

5. **Run local match buzzing vs starter to get baseline** — If we can't beat the starter bot by resources, we have a fundamental economy problem.

---

## Bottom Line

The P&D 0-5 sweep was decided by economy, specifically the **resources tiebreaker**, across 5 different maps. This is not a map-specific or military exploit — it is a pure economy problem. P&D's bot (v20) outfarmed our bot (v36) by round 2000 on every map. Given that P&D is only 1517 Elo (Silver, 42% win rate), this is a fixable gap. The most likely culprit is axionite refinement — if they deliver refined Ax and we don't, we lose tiebreaker #1 every time.
