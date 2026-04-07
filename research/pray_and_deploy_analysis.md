# Pray and Deploy — 0-5 Sweep Analysis

**Date:** 2026-04-06  
**Opponent:** Pray and Deploy (1517 Elo)  
**Our record vs P&D:** 0-10 (two 0-5 sweeps)  
**Elo impact:** -15.8 and -15.4 per match

---

## Match Data (from ladder API)

### Match 1 — `bfad9abb` (P&D as Team A, buzzing as Team B)
P&D won 5-0. P&D gained +15.8 Elo, we lost -15.8.

| Game | Map | Winner | Win Condition | Turns |
|------|-----|--------|--------------|-------|
| 1 | sierpinski_evil | P&D | **harvesters** | 2000 |
| 2 | galaxy | P&D | titanium_collected | 2000 |
| 3 | thread_of_connection | P&D | titanium_collected | 2000 |
| 4 | pls_buy_cucats_merch | P&D | titanium_stored | 2000 |
| 5 | face | P&D | titanium_collected | 2000 |

### Match 2 — `783cc2fd` (buzzing as Team A, P&D as Team B)
P&D won 5-0. We lost -15.4 Elo.

| Game | Map | Winner | Win Condition | Turns |
|------|-----|--------|--------------|-------|
| 1 | default_small1 | P&D | resources | 2000 |
| 2 | bar_chart | P&D | resources | 2000 |
| 3 | galaxy | P&D | resources | 2000 |
| 4 | cubes | P&D | resources | 2000 |
| 5 | tree_of_life | P&D | resources | 2000 |

No core kills in either match. All 10 games went to round 2000 — P&D wins on resources/tiebreakers, not aggression.

---

## Map Analysis

| Map | Dimensions | Area | Ti ore | Ax ore | Walls | Ore density | Our Ti (mined) | vs smart_defense |
|-----|-----------|------|--------|--------|-------|-------------|----------------|-----------------|
| sierpinski_evil | 31x31 | 961 | 21 | 9 | 273 | 3.1% | **0 mined** | Lost (harvester count) |
| galaxy | 40x40 | 1600 | — | — | — | — | 15010 mined | **Won** vs smart_defense |
| thread_of_connection | 20x20 | 400 | 34 | 10 | 54 | 11% | 24600 mined | Lost (close, 24600 vs 24840) |
| pls_buy_cucats_merch | 49x49 | 2401 | 60 | 20 | 240 | 3.3% | **0 mined** | Lost (titanium_stored) |
| face | 20x20 | 400 | — | — | — | — | 4960 mined | Lost (18630 vs face = 3.75x gap) |
| default_small1 | — | — | — | — | — | — | 18130 mined | Close loss |
| bar_chart | 35x40 | 1400 | 20 | 8 | 340 | 2.0% | 14210 mined | **Won** vs smart_defense |
| cubes | 50x50 | 2500 | 134 | 40 | 382 | 7.0% | 34810 mined | **Won** vs smart_defense |
| tree_of_life | — | — | — | — | — | — | 23020 mined | **Won** vs smart_defense |

---

## Root Cause Analysis

### 1. Harvester tiebreaker loss (sierpinski_evil, game 1)
Win condition: **harvesters** — not resources. This is tiebreaker #3 in game rules (after titanium delivered and titanium current). Both sides mined **0 Ti** (passive income only — ore is there but neither team connected harvesters to core effectively). P&D won because they had **more living harvesters** at round 2000.

- sierpinski_evil: 31x31, 273 walls (28% wall density), 21 Ti ore tiles. The fractal wall pattern creates deep maze corridors. Our BFS nav traverses these mazes correctly, but we likely wasted builders navigating dead ends and failed to establish harvester chains before the game ended.
- **Our bot prioritizes building conveyors over getting harvesters operational.** On maze maps where the chain must route around many walls, we run out of Ti building conveyors before ever connecting a harvester.

### 2. Sparse-ore catastrophe (bar_chart, pls_buy_cucats_merch)
Both maps have **2-3.3% ore density** — our confirmed weakness from the gaussian investigation. We overbuild infrastructure Ti while opponents build fewer, better-placed conveyors.

- `bar_chart` (2.0% ore density): locally we won 14210 vs 13300 mined against smart_defense, but P&D's more efficient infrastructure extracts more Ti from sparse ore.
- `pls_buy_cucats_merch` (3.3% density, 49x49): our local test showed **0 Ti mined** for both sides with smart_defense — the map is so large and sparse that neither side connects harvesters in time. P&D wins on **titanium_stored** (starting Ti), meaning they spent less Ti building dead-end infrastructure.

### 3. Face harvester pathing failure (game 5, match 1)
Confirmed from weak matchup analysis: face is a persistent 0W-2L map. We mine 3-4x less Ti than opponents. P&D would exploit this the same way.

### 4. Galaxy inconsistency (appears in both matches)
In Match 1, P&D beat us on galaxy. But locally we beat smart_defense on galaxy 15010 vs 13230. This suggests P&D's strategy is specifically better than smart_defense on expand maps, OR the galaxy seed used in the ladder match was unfavorable (our expand performance is seed-sensitive).

### 5. Thread_of_connection (very close loss)
20x20, 11% ore density — a small, ore-rich map. Local sim: 24600 vs 24840 mined — we lost by only 240 Ti. This is a razor-thin margin that better harvester timing could flip. P&D may be slightly faster at establishing their first harvester chain.

---

## Pattern: Why P&D Sweeps Us

P&D appears to play a clean **resource-focused economy** without aggressive attacks. Their strategy:
1. Fewer, more efficiently-placed buildings (fewer wasted conveyors)
2. Faster harvester establishment — they connect harvesters to core before us on sparse/maze maps
3. Better harvester count management (winning the harvester tiebreaker on sierpinski_evil)

Our bot's weaknesses that P&D exploits:
- **Conveyor overbuilding on sparse maps** (bar_chart, pls_buy_cucats_merch, gaussian)
- **Maze map navigation failure** (sierpinski_evil — 273 walls create dead-end corridors)
- **Face pathing failure** (consistent 3-4x mining deficit)
- **Explorer builders don't prioritize connecting harvesters** — they lay conveyors then move on, leaving incomplete chains

---

## Maps We'd Beat P&D On (based on local data)

Maps where we beat smart_defense (a similar-style opponent):
- cubes (7% ore, 50x50) — we mine 34810 vs 14400: dominant
- tree_of_life — we mine 23020 vs 9640: dominant  
- default_small1 — close but competitive
- galaxy (mixed — seed-dependent)

P&D got lucky with map draws: 4/10 games were on our weak maps (face, sierpinski_evil, bar_chart, pls_buy_cucats_merch/sparse). If map pool shifted to cubes/tree_of_life/hourglass, we'd likely win.

---

## Recommended Fixes

### High priority (directly caused losses)
1. **Maze map detection**: Count wall density. If walls > 20% of tiles, switch to conservative conveyor mode — only build a chain if you can trace a complete path from ore to core within N steps.
2. **Harvester floor on maze maps**: Ensure at least 1 harvester is connected and delivering before spending Ti on exploration infrastructure.
3. **Face pathing fix**: The first builder goes the wrong direction on face. This is a known 0-3 map — investigate what the `best_ore_dir` heuristic returns on face seed 1.

### Medium priority
4. **Sparse-ore chain cap**: Refuse to extend a conveyor chain > 12 tiles on maps with ore density < 4%.
5. **Harvester count awareness for tiebreaker**: In late game (round 1800+), prioritize building harvesters over conveyors even if the chain isn't complete — the harvester count tiebreaker matters.

---

## Conclusion

P&D at 1517 Elo is a competitive but not exceptional opponent. We're losing because of 3 structural bugs: face pathing failure, maze map wall-navigation that wastes builders, and sparse-ore conveyor overbuilding. These are the same issues identified in the gaussian investigation and v49 weak matchup analysis. Fixing these three issues would likely flip 6-7 of the 10 P&D games.
