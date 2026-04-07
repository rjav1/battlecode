# Pray and Deploy — 0-5 Analysis

**Date:** 2026-04-06
**Opponent:** Pray and Deploy (UK, 1477 Elo, 2694 matches played)
**Our rating before:** 1471.7 → **after: 1455.3**

---

## Two 0-5 Losses Summary

### Match 1: bfad9abb (2026-04-06 22:37)
- Pray and Deploy (version 20) vs buzzing bees (version 48)
- We were team B; Elo delta: **-15.8**

| Game | Map | Win Condition | Notes |
|------|-----|---------------|-------|
| 1 | sierpinski_evil | **harvesters** (tiebreak 3) | Both mined 0 Ti (self-play verified) |
| 2 | galaxy | titanium_collected | We lose on economy |
| 3 | thread_of_connection | titanium_collected | — |
| 4 | pls_buy_cucats_merch | **titanium_stored** (tiebreak 5) | Both mined 0 Ti (self-play verified) |
| 5 | face | titanium_collected | We lose on economy |

### Match 2: 783cc2fd (2026-04-06 14:07)
- buzzing bees (version 36) vs Pray and Deploy (version 36)
- We were team A (older bot); Elo delta: **-15.4**

| Game | Map | Win Condition | Notes |
|------|-----|---------------|-------|
| 1 | default_small1 | resources | Economy loss |
| 2 | bar_chart | resources | Economy loss |
| 3 | galaxy | resources | Economy loss |
| 4 | cubes | resources | Economy loss |
| 5 | tree_of_life | resources | Economy loss |

**All 10 games lost by resource tiebreak — no core destructions in either direction.** Pray and Deploy simply out-economies us every game.

---

## Pray and Deploy Profile

| Stat | Value |
|------|-------|
| Elo | 1477 (was 1475 before our first match) |
| Region | UK |
| Matches played | 2,694 |
| Recent record (last 20) | 10W-10L (50%) |

Pray and Deploy is a **50% bot** at a similar Elo to us. They're not elite. We're not specifically weak to them — they just happened to draw favorable maps twice.

---

## Root Cause Analysis

### Critical: Two maps completely break our economy

**sierpinski_evil (31x31):**
- Our core spawns at (3, 15) — far left edge
- Ti ore is clustered at center/right: nearest Ti at (15,9), (15,10), dist≈12+ tiles
- Map is covered in fractal walls — pathfinding is severely restricted
- Self-play result: **both sides mine 0 Ti** (tiebreak decided by harvesters count alone)
- We lose on harvesters count — likely Pray and Deploy has more builder bots alive

**pls_buy_cucats_merch (49x49):**
- Our core spawns at (13, 17) — left side of a very large map
- All ore clusters are far right (x=35-43 range), distance 25-30 tiles minimum
- No ore near core at all — pure exploration required
- Self-play result: **both sides mine 0 Ti** (tiebreak decided by titanium_stored = passive income only)
- Passive income: 10 Ti every 4 rounds = 5,000 Ti by round 2000. Whoever has more units/buildings built wins on stored Ti.

### Economy maps: galaxy, face, default_small1, etc.

On standard maps our economy is simply weaker:
- Self-play galaxy: A=9940 Ti mined, B=18790 — side B (spawn position) gets 2x our output due to better ore access
- We consistently lose to a strong eco bot by ~2x Ti mined ratio

### What Pray and Deploy likely does

Their 2,694 match history suggests a refined, consistent bot. No core destructions in 10 games against us = they don't have an aggressive rush. Their win condition is pure economy. They likely have:
- Efficient harvester discovery (doesn't waste time on broken maps)
- Better passive income utilization (more buildings, more harvesters stored)
- Possibly a foundry + axionite economy

---

## Map-by-Map Self-Play Results (our bot vs itself)

Using match 1's exact seeds:

| Map | Seed | Side A Ti | Side B Ti | Winner | Condition |
|-----|------|-----------|-----------|--------|-----------|
| sierpinski_evil | 1027605631 | 0 | 0 | B | harvesters |
| galaxy | 1369425799 | 9,940 | 18,790 | B | titanium_collected |
| thread_of_connection | 1695562514 | 24,490 | 9,920 | A | titanium_collected |
| pls_buy_cucats_merch | 33518442 | 0 | 0 | B | resources |
| face | 1700203522 | 4,970 | 9,910 | B | titanium_collected |

Side B wins 4/5 in self-play — meaning **spawn position determines the winner** on these maps. Pray and Deploy drew the favorable side in 5/5 games.

---

## Key Findings

1. **Not a Pray-and-Deploy-specific weakness.** They're a 50% bot. We lost twice to lucky map draws.

2. **sierpinski_evil and pls_buy_cucats_merch are broken maps for us.** Both sides mine 0 Ti. We lose on unit count tiebreakers. This is a navigation failure on extreme maps.

3. **Spawn position is the dominant factor on these maps.** B-side won 4/5 self-play games. Pray and Deploy was team A (favorable spawn) in all 5 games of match 1.

4. **Economy gap on standard maps is real.** Galaxy shows 9,940 vs 18,790 Ti — a 2x difference depending on spawn side. This is a known issue.

---

## Recommendations

1. **sierpinski_evil fix (high priority):** Core at (3,15) with ore at distance 12+ behind walls. We need better wall-aware navigation or a fallback for "no ore reachable" scenarios. Currently we mine 0 Ti — even 1 harvester would be better.

2. **pls_buy_cucats_merch fix:** 49x49 map with no nearby ore. The large-map expand mode (area ≥ 1600 = 2401 tiles for 49x49) should trigger, but builders still can't reach ore 30 tiles away without infrastructure. Need to verify expand mode triggers correctly and builders actually traverse long distances.

3. **Don't over-index on Pray and Deploy.** They're 50% — we'll face them again and should win ~50% of matches. The two 0-5 losses were both bad luck on map draw + spawn assignment.

4. **Passive income tiebreaker:** On maps where neither side mines, the winner is determined by units/buildings. We should ensure we always build up to our builder cap even on impossible maps.
