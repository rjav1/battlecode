# Ladder Results — Latest Check

**Date:** 2026-04-07 ~16:00
**Version submitted:** V55 (explore reach fix)

## Current Elo: ~1347 (down from ~1567, -220 over last 50 matches)

---

## Last 50 Matches Summary

**Record: 23W-27L (46.0%)**

| Metric | Value |
|--------|-------|
| Wins | 23 |
| Losses | 27 |
| Win rate | 46.0% |
| Elo start (50 matches ago) | ~1567 |
| Elo current | ~1347 |
| Elo change | -220 |

---

## Recent 20 Matches (newest first)

| Result | Score | Opponent | Opp Elo | Elo Delta | Time |
|--------|-------|----------|---------|-----------|------|
| LOSS | 2-3 | Bit by Bit | ~1898 | -2.0 | 15:58 |
| LOSS | 2-3 | Three Bolts One Bug | ~1358 | -2.8 | 15:57 |
| LOSS | 2-3 | Yellow Dragon | ~1999 | -2.3 | 15:57 |
| LOSS | 1-4 | Signal | ~1989 | -9.2 | 15:57 |
| WIN | 3-2 | O_O | ~1473 | +3.0 | 15:57 |
| WIN | 3-2 | natto warriors | ~1515 | +3.3 | 15:57 |
| WIN | 3-2 | Highly Suspect | ~1471 | +3.7 | 15:57 |
| LOSS | 2-3 | ah | ~1422 | -3.5 | 15:57 |
| LOSS | 1-4 | Tylenol Enthusiasts | ~1542 | -8.7 | 15:57 |
| WIN | 4-1 | bot123 | ~1595 | +9.1 | 15:57 |
| WIN | 3-2 | Aggressive Toasters | ~1564 | +2.9 | 15:56 |
| LOSS | 1-4 | Psyduck Hold | ~1109 | -4.8 | 15:56 |
| WIN | 3-2 | Manny and his Minions | ~1159 | +2.4 | 15:56 |
| WIN | 4-1 | Axionite Inc | ~1852 | +9.6 | 15:56 |
| LOSS | 2-3 | Dear jump Give me a job | ~2381 | -1.9 | 15:56 |
| WIN | 4-1 | dzwiek spadajacej metalu | ~1899 | +8.7 | 15:56 |
| WIN | 3-2 | Por Favor | ~2234 | +3.5 | 15:56 |
| LOSS | 2-3 | ken-is-goated | ~1346 | -2.8 | 15:56 |
| WIN | 3-2 | - | ~1554 | +3.6 | 15:56 |
| LOSS | 0-5 | vedi-veci-fatalerror | ~1550 | -16.8 | 15:56 |

---

## Notable Heavy Losses (1-4 or 0-5)

| Opponent | Their Elo | Our Score | Elo Cost |
|----------|-----------|-----------|----------|
| Signal | ~1989 | 1-4 | -9.2 |
| Tylenol Enthusiasts | ~1542 | 1-4 | -8.7 |
| Psyduck Hold | **~1109** | 1-4 | **-4.8** |
| vedi-veci-fatalerror | ~1550 | 0-5 | -16.8 |
| Mind of Metal and Wheels | ~1690 | 1-4 | -8.4 |
| KAIZEN | ~1622 | 1-4 | -8.7 |
| TheWarriors | **~1163** | 1-4 | **-10.5** |
| sauce_destroyer | **~952** | 0-5 | **-9.3** |

3 losses to opponents rated under 1200 — upsets indicating genuine bot weakness.

---

## Analysis

### Win patterns
- Wins tend to be 3-2 or 4-1 vs ~1400-1600 Elo opponents
- Big wins: 5-0 vs Patata (~1385, +14.8), 5-0 vs drop table (~2086, +12.7)

### Alarm signals
1. **3 losses to sub-1200 opponents** (Psyduck Hold ~1109, TheWarriors ~1163, sauce_destroyer ~952) — teams we should beat reliably. Indicates exploitable weakness or map-specific bugs.
2. **Two 0-5 sweeps** (vedi-veci-fatalerror, sauce_destroyer) — being swept 0-5 means we lost all 5 map games, likely triggering the enemy-road BFS bug or bridge regression on specific map sets.
3. **Elo collapse -220 over 50 matches** — severe regression since V52/V55 deploys.

### Connection to identified bugs
- **Enemy road BFS bug** (0 Ti mined on default_medium1 vs ladder_road-style opponents): any opponent using roads on open maps causes near-zero economy. Sweep losses likely involve this.
- **Bridge regression on close-range ore** (corridors: 5090 vs 14850 Ti): maps where ore is close to core suffer 3x economy loss.
- **Neither bug is fixed in V55** — V55 only added explore reach fix.

### Priority before April 11 snapshot
1. Bridge distance guard fix (1-line, researched in corridors_chain_regression.md)
2. Enemy-road BFS exclusion fix (researched in default_medium1_collapse.md)
Both fixes identified and documented — eco-debugger implementing.
