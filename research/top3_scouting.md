# Cambridge Battlecode 2026 -- TOP 3 SCOUTING REPORT
## Compiled April 5, 2026

---

## EXECUTIVE SUMMARY

The top 3 teams in Cambridge Battlecode 2026 share one fundamental trait: **economic dominance wins games**. The overwhelming majority of games at the top level are decided by Resource Victory at the 2000-turn limit, not by Core Destroyed. All three teams prioritize building extensive conveyor networks, maximizing harvester count, and leveraging Sentinels as their primary turret of choice. Blue Dragon separates itself from the pack through sheer economic efficiency -- routinely out-collecting opponents by 10x or more. Kessoku Band provides the closest competition but still loses to Blue Dragon more often than not. "something else" has the most volatile results but can occasionally upset either top team.

---

## TEAM 1: BLUE DRAGON

**Rating:** ~2790-2797 (fluctuates) | **Peak Rating:** 2797 | **Peak Rank:** #1
**Matches Played:** 2511+
**Category:** MAIN | **Region:** International
**Members:** Benjamin Kovacs (owner), SamH
**Team ID:** 023ce802

### OVERVIEW
Blue Dragon is the undisputed #1 team. They hold rank #1 with a rating approximately 90 points above #2 Kessoku Band and 270 points above #3 "something else". Their win rate against every team in the top 10 is extremely high, with the only consistent challenge coming from Kessoku Band and occasional upsets from "something else" or MFF1.

### RECENT RECORD (from 50 most recent matches)
- vs Kessoku Band: Multiple 4-1 wins, but KB did take a 3-2 off them recently
- vs something else: Mostly 5-0 and 4-1 wins; one 3-2 loss (close match)
- vs MFF1: Mostly 5-0 and 3-2 wins; MFF1 is the only lower team to occasionally steal games
- vs Oxford, bwaaa, food, Dear jump, Lorem Ipsum, Operation Marvin: Consistently 5-0 or 4-1
- Overall estimated win rate in recent 50: ~90%+

### ECONOMY -- THE DEFINING STRENGTH

Blue Dragon's economy is their absolute superpower. In every replay analyzed, their resource collection dwarfs their opponents:

**Match: BD vs MFF1 on wasteland (ade2dd2e, Game 1)**
- Round 442: BD 3,360 Ti collected vs MFF1 220 Ti collected (15:1 ratio)
- Round 1896: BD 30,460 Ti collected vs MFF1 230 Ti collected (132:1 ratio!)
- Final: BD wins by Resource Victory at 2000 turns

Key economic observations from replays:
- **Harvester count:** By round 442, BD had 7 harvesters vs MFF1's 4. By round 1896, BD had 22 harvesters vs MFF1's 7.
- **Conveyor network:** BD builds MASSIVE conveyor networks. At round 442: 84 conveyors. By round 1896: 308 conveyors. This is 10-18x the opponent.
- **Bridge usage:** BD builds many bridges (10 by round 442, 33 by round 1896) -- far more than opponents (1 bridge). Bridges appear to be key for crossing terrain and establishing long conveyor chains.
- **Splitters:** BD uses splitters (4 by end game) to distribute resources across multiple paths.
- **No Foundries:** Zero foundries observed in any game. BD does not use the foundry mechanic.
- **No Axionite:** Zero axionite collected in all observed games. BD appears to focus exclusively on Titanium.
- **Starting capital spent efficiently:** From 500 starting Ti, BD rapidly invests into infrastructure, getting harvesters and conveyors running before opponents.

**Match: BD vs KB on face (b5115d14, Game 2)**
- Round 558: BD (Silver) 5,870 Ti collected vs KB (Gold) 570 Ti collected (10:1)
- BD had 7 harvesters vs KB's 1, 44 conveyors vs KB's 0
- BD built 158 roads vs KB's 33
- This was a match between the top 2 teams, and BD still dominated economically 10:1

**Match: BD vs Oxford (54d77330) -- 5-0 sweep**
- All 5 games were Resource Victory at 2000 turns except one Core Destroyed at 328 turns
- Maps: arena, wasteland_oasis, pls_buy_cucats_merch, face, shish_kebab
- BD dominates on virtually every map type

### MILITARY -- SENTINEL-HEAVY DEFENSE

Blue Dragon's military strategy is heavily defensive with Sentinels as the primary turret:

**Turret preferences (from replays):**
- **Sentinels:** The overwhelming favorite. In the wasteland game, BD had 3 Sentinels at round 442 and 20 by round 1896. In the hourglass game, 6 Sentinels by round 130. In the face game, 4 Sentinels at round 558.
- **Gunners:** Rarely built. 1 Gunner observed at round 1896 (wasteland) and 1 at round 558 (face). Appears to be supplementary.
- **Launchers:** Sparingly used. 1-3 launchers observed. Used for offense on narrow maps.
- **Breaches:** Zero observed across all replays.
- **Barriers:** Used defensively, 1-4 observed per game. Fewer than opponents typically build.

**Turret timing:**
- First Sentinels appear around round 100-200 based on the hourglass game data (6 sentinels by turn 130).
- BD builds turrets AFTER establishing economic infrastructure, not before.

**Turret positioning:**
- Sentinels appear to be placed along the path toward the enemy, protecting the expanding conveyor network.
- On narrow maps like hourglass, Sentinels are placed at choke points.
- Ammo supply appears to come through the conveyor network itself, as conveyors reach turret positions.

### OFFENSE

Blue Dragon's offense is opportunistic rather than aggressive:

**Core Destroyed wins observed:**
- vs MFF1 on hourglass: 235 turns (fast kill on narrow map)
- vs MFF1 on landscape: 164 turns (very fast kill)
- vs MFF1 on cubes: 626 turns (medium speed)
- vs Oxford on pls_buy_cucats_merch: 328 turns
- vs something else on corridors: 749 turns
- vs something else on chemistry_class: 569 turns

**Pattern:** BD achieves Core Destroyed primarily on NARROW/SMALL maps (hourglass, landscape, corridors, chemistry_class). On OPEN/LARGE maps (wasteland, wasteland_oasis, face, arena, galaxy, default_large1, shish_kebab), BD wins by Resource Victory.

**Offensive units:** BD appears to use builders that walk toward the enemy core on narrow maps where the path is short. On hourglass (a corridor map), the 6 Sentinels at round 130 provide cover fire while builders approach.

### ADAPTATION

BD appears to run a consistent strategy regardless of opponent but adapts to map geometry:
- **Open maps:** Pure economy, win by Resource Victory. Build massive conveyor/harvester networks.
- **Narrow maps:** Still build economy but also push with Sentinels toward enemy core for early-mid game Core Destroyed.
- **No observed reactive changes to opponent behavior** -- BD plays "their game" regardless.

### WIN CONDITION ANALYSIS

From all BD matches analyzed:
- **Resource Victory (2000 turns):** The dominant win condition. ~60-70% of individual game wins.
- **Core Destroyed:** ~30-40% of game wins, almost exclusively on narrow/corridor maps.
- **Typical game-ending turn for Core Destroyed:** 164-749 turns (wide range depending on map).
- **Losses:** BD loses some games on maps where the opponent gets a lucky Core Destroyed rush (MFF1 destroyed BD's core on cubes at 626t and landscape at 164t in the ade2dd2e match).

### DISTINGUISHING FEATURES -- WHAT MAKES BD #1

1. **Unmatched economic efficiency:** 10x-130x resource collection advantage is absurd. Their conveyor network topology is clearly optimized far beyond other teams.
2. **Bridge-heavy expansion:** 33 bridges vs 1 for opponent -- BD uses bridges aggressively to cross terrain and establish resource pathways.
3. **Pure Titanium focus:** Zero axionite collected in all observed games. They don't split focus.
4. **Sentinel spam:** 20 Sentinels in late game creates an impenetrable defensive wall while economy runs.
5. **Road infrastructure:** 174 roads built (wasteland late game). They invest heavily in roads to speed up builder movement.
6. **Bot count:** 15+ bots active at once, vs 2-7 for opponents. More builders = faster construction.
7. **Two-person team efficiency:** With only 2 members, their code is likely very cohesive.

### WEAKNESSES

1. **Narrow maps can force losses:** When MFF1 got Core Destroyed wins on cubes and landscape (164 turns!), it suggests BD can be vulnerable to very aggressive early rushes on maps where the cores are close.
2. **Kessoku Band can compete economically:** KB's 3-2 win shows that on certain maps, KB can match BD's economy (KB won on minimaze via Resource Victory).
3. **"something else" stole 2 games:** SE won on wasteland and wasteland_oasis in a 2-3 loss, suggesting open wasteland-type maps are slightly less dominant for BD against the very best.

---

## TEAM 2: KESSOKU BAND

**Rating:** ~2702-2720 (fluctuates) | **Peak Rating:** 2747 | **Peak Rank:** #1
**Matches Played:** 2506+
**Category:** MAIN | **Region:** International
**Members:** gura (owner), Varity, jzhc, Hallooz
**Team ID:** a2b913f3
**Team Description:** "lmao"

### OVERVIEW
Kessoku Band is the clear #2 team, approximately 90 points behind Blue Dragon. They have briefly held the #1 rank (peak rating 2747). They dominate every team except Blue Dragon, against whom they have a negative record but can occasionally win. Their 4-person team (the max allowed) suggests diverse contributions to the codebase.

### RECENT RECORD (from 50 most recent matches)
- vs Blue Dragon: Mostly 1-4 and 0-5 losses, but managed a 3-2 win (rated) and 3-2 win (unrated)
- vs something else: Mostly 4-1 and 5-0 wins; lost once 0-5 in a major upset
- vs MFF1: Consistently 5-0 and 4-1 wins; MFF1 did manage a 2-3 win once
- vs lower teams: Dominant 5-0 sweeps against bwaaa, Dear jump, Oxford, food, Lorem Ipsum, Operation Marvin
- vs WindRunners: Lost 2-3 (lower team upset)
- Overall estimated win rate: ~80-85%

### ECONOMY

KB runs a strong economy, second only to Blue Dragon:

**Match: KB vs MFF1 on gaussian (53cb1fb8, Game 5)**
- Round 148: KB 1,720 Ti collected vs MFF1 780 Ti collected (2.2:1 ratio)
- KB had 6 harvesters vs MFF1's 6 (matched), but 20 conveyors vs MFF1's 0
- KB had 40 roads vs MFF1's 27

**Match: KB vs BD on face (b5115d14, Game 2)**
- Round 558: KB (Gold) 570 Ti collected vs BD (Silver) 5,870 Ti collected
- KB only had 1 harvester vs BD's 7, 0 conveyors vs BD's 44
- This shows KB's economy is significantly weaker than BD's, even though KB is the #2 team

**Key economic observations:**
- KB builds solid conveyor networks but not as extensive as BD (20 conveyors vs BD's 300+)
- Fewer bridges than BD (1-2 typical vs BD's 10-33)
- KB does use splitters (0-1 observed)
- No foundries observed
- No axionite collected (same pure Titanium focus as BD)
- Harvester count: 6-7 typical, lower than BD's 7-22

### MILITARY -- SENTINEL FOCUS (EVEN MORE AGGRESSIVE THAN BD)

**Turret preferences:**
- **Sentinels:** KB's absolute go-to. In the gaussian game, KB had 10 Sentinels by round 148 (!) -- that's extraordinarily early and numerous. This is even more aggressive Sentinel building than BD.
- **Gunners:** Zero observed in the gaussian game.
- **Launchers:** Zero observed (KB relies on Sentinels entirely for combat).
- **Breaches:** Zero observed.
- **Barriers:** Zero observed. KB doesn't build barriers.

**Key difference from BD:** KB appears to build Sentinels EVEN FASTER than BD, potentially at the cost of economic infrastructure. By round 148 on gaussian, KB had 10 Sentinels which is remarkable.

### OFFENSE

KB achieves Core Destroyed wins on certain maps:

**Core Destroyed wins observed:**
- vs MFF1 on default_medium2: 241 turns
- vs MFF1 on gaussian: 337 turns

**Pattern:** Like BD, KB's Core Destroyed wins happen on smaller/narrower maps. On larger maps, KB wins by Resource Victory.

### ADAPTATION

**Map-dependent strategy:**
- KB dominates on minimaze (won Resource Victory vs BD on this map!)
- KB wins Resource Victory on battlebot, chemistry_class, minimaze
- Core Destroyed on smaller maps (default_medium2, gaussian)

**vs Blue Dragon specifically:**
- KB won game 1 (minimaze) in the 1-4 loss match via Resource Victory at 2000 turns
- This suggests KB may have a slight map advantage on minimaze
- KB can compete with BD on economy for certain map geometries

### WIN CONDITION ANALYSIS

From all KB matches analyzed:
- **Resource Victory (2000 turns):** The primary win condition. Most games go to full 2000 turns.
- **Core Destroyed:** Secondary, on smaller maps (241-337 turns observed).
- **Losses to BD:** Primarily Resource Victory losses where BD out-collects KB.

### DISTINGUISHING FEATURES -- WHAT MAKES KB #2

1. **Extreme Sentinel investment:** 10 Sentinels by turn 148 is the most aggressive turret build observed among the top 3. This creates a powerful defensive/zoning presence early.
2. **4-person team:** Maximum team size suggests diverse skill contributions and more code iterations.
3. **Previously held #1:** Peaked at #1 with 2747 rating, showing they can compete at the very top.
4. **Clean economy play:** While not as efficient as BD, KB's economy is far ahead of teams 4+.
5. **No barriers, no launchers:** KB simplifies their military to pure Sentinels, which may reduce code complexity and improve reliability.
6. **Minimaze specialist:** Appears to have a map-specific advantage on minimaze.

### WEAKNESSES

1. **Economy gap vs BD:** At round 558 on face, BD out-collected KB 10:1. This gap is KB's primary ceiling.
2. **Occasional lower-team upsets:** Lost 2-3 to WindRunners and 2-3 to food in recent history, suggesting inconsistency.
3. **"something else" upset:** Lost 0-5 to "something else" at one point, losing 25 Elo. This suggests vulnerability.
4. **Over-reliance on Sentinels:** With zero other turret types, opponents who can specifically counter Sentinels may gain an edge.

---

## TEAM 3: SOMETHING ELSE

**Rating:** ~2520-2542 (fluctuates) | **Peak Rating:** 2542 | **Peak Rank:** #2
**Matches Played:** 2527+
**Category:** MAIN | **Region:** International
**Members:** osteo (owner), amcsz, [Jython], Coderz75
**Team ID:** b4a784e9
**Team Description:** "we are something else"

### OVERVIEW
"something else" is a solid #3 with a notable rating gap below #2 Kessoku Band (~170 points) and even larger below #1 Blue Dragon (~270 points). However, they have historically peaked at #2 and can occasionally upset the top 2 teams. Their results are more volatile than BD and KB -- they get clean 5-0 wins against lower teams but also occasionally drop games.

### RECENT RECORD (from 50 most recent matches)
- vs Blue Dragon: Mostly 0-5 and 1-4 losses; managed a 2-3 loss (close!) and a 1-4 win at one point
- vs Kessoku Band: Mixed record, 4-1 wins and 1-4 losses; once got a 0-5 upset on KB
- vs MFF1: Consistently 4-1 and 5-0 wins
- vs Oxford: 1-4 wins consistently
- vs bwaaa, Dear jump, food: Mostly wins but some 3-2 close calls
- vs Jython: 5-0 stomps
- Overall estimated win rate: ~70-75%

### ECONOMY

SE has a strong economy that can compete with anyone except Blue Dragon:

**Match: SE vs MFF1 on thread_of_connection (00ada2c3, Game 4)**
- Round 140: SE 2,140 Ti collected vs MFF1 1,260 Ti collected (1.7:1 ratio)
- SE had 8 harvesters vs MFF1's 6
- SE had 20 conveyors vs MFF1's 4
- SE had a massive 967 Ti on hand (large stockpile)

**Key economic observations:**
- **Bridge-heavy strategy:** 9 bridges by round 140 is notable -- more bridge-focused than even BD on some maps. SE appears to prioritize bridges for expansion.
- **Road investment:** 64 roads by round 140 shows heavy infrastructure investment.
- **Conveyor count:** 20 conveyors at round 140 is strong but below BD levels.
- **Harvester count:** 8 harvesters is competitive.
- **Resource stockpiling:** SE seems to accumulate large Ti reserves (967 at round 140) rather than immediately reinvesting. This may indicate slightly less efficient spending.
- **No axionite collected** (same as other top teams).
- **No foundries observed.**

### MILITARY

SE has a more diversified military compared to BD and KB:

**Turret preferences:**
- **Sentinels:** Primary turret (1 observed at round 140 in the thread_of_connection game). Less aggressive Sentinel building than BD or KB.
- **Gunners:** Zero observed in the replay.
- **Launchers:** Zero observed for SE (but opponents build them against SE).
- **Breaches:** Zero observed.
- **Barriers:** Zero observed (unlike opponents who build barriers against SE).

**Key difference:** SE appears to build FEWER turrets overall compared to BD and KB. By round 140 they had only 1 Sentinel, while KB would have had 10 by that time. This suggests SE may rely more on economic victory than military control.

### OFFENSE

SE achieves Core Destroyed wins, particularly on narrow maps:

**Core Destroyed wins observed:**
- vs MFF1 on hourglass: 307 turns
- vs MFF1 on thread_of_connection: 288 turns
- vs BD: No Core Destroyed wins (only Resource Victory wins observed)

**Match: SE vs BD on corridors (2f39c48c, Game 1)**
- BD destroyed SE's core at 749 turns -- SE is vulnerable on corridors

**Pattern:** SE can rush on narrow maps but is more vulnerable to being rushed than BD or KB.

### ADAPTATION

**Map-dependent performance:**
- SE beat BD on wasteland and wasteland_oasis (both Resource Victory) -- open maps favor SE vs BD
- SE lost to BD on corridors (Core Destroyed 749t), git_branches (RV), chemistry_class (Core Destroyed 569t)
- SE appears to perform relatively better on OPEN maps and worse on narrow maps vs top teams

**Notable upset capabilities:**
- Beat KB 0-5 (massive upset, took 25 Elo from KB)
- Managed a 2-3 loss to BD (won 2 games on wasteland maps)
- These upsets suggest map randomization can favor SE against top teams on open terrain

### WIN CONDITION ANALYSIS

From all SE matches analyzed:
- **Resource Victory (2000 turns):** Primary win condition, especially on open maps.
- **Core Destroyed:** On narrow maps vs weaker teams (288-307 turns observed).
- **Losses:** Primarily via Resource Victory (out-collected) or Core Destroyed on narrow maps.

### DISTINGUISHING FEATURES -- WHAT MAKES SE #3

1. **Bridge specialist:** 9 bridges at round 140 suggests an aggressive bridging strategy to cross terrain gaps. This may be their key economic innovation.
2. **Wasteland/open map strength:** Won 2 games vs BD on wasteland-type maps -- suggests their economic build is optimized for open terrain.
3. **Upset potential:** The 0-5 on KB and 2-3 near-win vs BD shows they can occasionally beat anyone.
4. **4-person team:** Full team roster with diverse contributors.
5. **Resource stockpiling:** Large Ti reserves may enable burst-building when needed.
6. **Volatile but dangerous:** More inconsistent than BD and KB, but their ceiling is close to #2.

### WEAKNESSES

1. **Narrow map vulnerability:** Lost to BD on corridors and chemistry_class via Core Destroyed. Narrow maps expose SE.
2. **Economy gap vs BD:** While SE can compete on open maps, BD still generally out-collects them.
3. **Lower turret count:** Only 1 Sentinel at round 140 vs KB's 10 means SE may be vulnerable to military pushes.
4. **Inconsistent results:** 3-2 losses to bwaaa and food suggest occasional poor performance against lower teams.
5. **Large rating gap below KB:** 170+ point gap means SE is clearly a tier below the top 2.

---

## COMPARATIVE ANALYSIS

### HEAD-TO-HEAD MATRIX (observed from recent 50 matches each)

| | Blue Dragon | Kessoku Band | something else |
|---|---|---|---|
| **Blue Dragon** | -- | W (mostly 4-1, 5-0; ~80% match win rate) | W (mostly 5-0, 4-1; ~85% match win rate) |
| **Kessoku Band** | L (mostly 1-4, 0-5; ~20% match win rate) | -- | W (mostly 4-1, 5-0; ~70% match win rate) |
| **something else** | L (mostly 0-5, 1-4; ~15% match win rate) | L/W (mixed; ~40% match win rate) | -- |

### ECONOMIC COMPARISON

| Metric | Blue Dragon | Kessoku Band | something else |
|---|---|---|---|
| Ti collection rate | BEST (10-130x vs opponents) | GOOD (2-10x vs lower teams) | GOOD (1.7-3x vs lower teams) |
| Peak harvesters observed | 22 | 6-7 | 8 |
| Peak conveyors observed | 308 | 20 | 20 |
| Peak bridges observed | 33 | 1-2 | 9 |
| Splitter usage | Yes (4) | Minimal (0-1) | Minimal (0-1) |
| Axionite usage | None | None | None |
| Foundry usage | None | None | None |

### MILITARY COMPARISON

| Metric | Blue Dragon | Kessoku Band | something else |
|---|---|---|---|
| Primary turret | Sentinel | Sentinel | Sentinel |
| Peak Sentinels observed | 20 | 10 (by turn 148!) | 1 (by turn 140) |
| Gunner usage | Rare (1) | None | None |
| Launcher usage | Rare (1-3) | None | None |
| Breach usage | None | None | None |
| Barrier usage | Light (1-4) | None | None |
| Turret build timing | After economy | Very early (aggressive) | After economy |

### WIN CONDITION COMPARISON

| Metric | Blue Dragon | Kessoku Band | something else |
|---|---|---|---|
| Primary win type | Resource Victory | Resource Victory | Resource Victory |
| Core Destroyed frequency | ~30-40% of game wins | ~20-30% of game wins | ~30% of game wins |
| Fastest Core Destroyed | 164 turns (landscape) | 241 turns (default_medium2) | 288 turns (thread_of_connection) |
| Best map types | All (but especially open) | Minimaze, medium maps | Wasteland/open maps |
| Worst map types | Narrow (when losing) | Open (vs BD) | Narrow (vs BD) |

---

## STRATEGIC INSIGHTS FOR BEATING EACH TEAM

### TO BEAT BLUE DRAGON:
1. **Match their economy or rush early on narrow maps.** BD's Core Destroyed losses happen on narrow maps (MFF1 killed BD at turn 164 on landscape). If you can get a fast Core Destroyed on narrow maps, you can steal games.
2. **Bridge disruption:** BD relies on 33+ bridges. If bridges can be targeted/destroyed, their conveyor network collapses.
3. **Play on wasteland-type maps:** "something else" proved BD can lose Resource Victory on wasteland and wasteland_oasis. Open maps with scattered resources may slightly reduce BD's conveyor efficiency advantage.
4. **Turret counter:** BD uses almost exclusively Sentinels. If Sentinels have a specific counter (long-range Launchers?), exploit it.
5. **Don't try to out-economy them on most maps.** Their 308-conveyor, 22-harvester, 33-bridge economy is unmatched. Focus on rushing or counter-strategies.

### TO BEAT KESSOKU BAND:
1. **Out-economy them.** KB's economy is good but not BD-level. A team with BD-level economic efficiency would beat KB consistently.
2. **Counter early Sentinels.** KB builds 10 Sentinels by turn 148. If you can destroy Sentinels or bypass them with ranged attacks/Launchers, you nullify their main advantage.
3. **Avoid minimaze.** KB appears to have a map-specific advantage on minimaze.
4. **Pressure on open maps.** KB's conveyor/bridge count is lower than BD's, suggesting they may struggle on very open maps against efficient builders.
5. **Exploit no-barrier defense.** KB builds zero barriers. If barriers would help defend against your attacks, note that KB doesn't build them for defense either.

### TO BEAT SOMETHING ELSE:
1. **Rush on narrow maps.** SE is most vulnerable to Core Destroyed on narrow/corridor maps (lost to BD on corridors at 749t and chemistry_class at 569t).
2. **Build more turrets.** SE only had 1 Sentinel at turn 140. Aggressive turret building can overwhelm their light military.
3. **Deny their bridges.** SE builds 9+ bridges aggressively. Disrupting their bridge-dependent expansion could cripple their economy.
4. **Consistent pressure.** SE occasionally drops games to lower teams (3-2 to bwaaa, food). Consistent pressure may cause errors.

---

## META OBSERVATIONS

1. **Nobody uses Axionite.** All top 3 teams collected zero axionite in every observed game. This suggests either the Titanium economy is strictly superior, or axionite requires too much investment to be worthwhile at the top level. Consider whether an axionite-based strategy could be a meta-breaking innovation.

2. **Nobody uses Foundries.** Zero foundries across all top 3 teams. Whatever foundries produce may not be worth the investment compared to more harvesters/conveyors.

3. **Sentinels dominate the turret meta.** All top 3 teams prefer Sentinels over Gunners, Breaches, and Launchers. This suggests Sentinels offer the best cost-efficiency for area denial. A strategy that specifically counters Sentinels could be transformative.

4. **Conveyors > Roads for resource transport.** BD builds 308 conveyors and 174 roads. The conveyor-heavy approach suggests conveyors are the primary resource transport mechanism, with roads serving as pathways for builder movement.

5. **Bridges are key infrastructure.** BD's 33 bridges and SE's 9 bridges suggest that bridge-building is essential for efficient expansion. Teams that don't build bridges (or build very few) appear to fall behind economically.

6. **Games almost never end by Core Destroyed between top teams.** When BD vs KB play, ALL 5 games go to Resource Victory at 2000 turns. Core Destroyed wins happen primarily against lower-tier opponents or on very narrow maps.

7. **The Resource Victory tiebreaker rewards economy above all else.** Since most games between top teams go to 2000 turns, the team with more total resources collected wins. This makes economic optimization the single most important factor.

8. **Map pool matters enormously.** The random 5-map selection can swing a match. BD won 3 games vs SE on narrow maps (Core Destroyed) but lost 2 on wasteland maps (Resource Victory). If you can identify your strongest map types and optimize for them, you gain matchup advantages.

---

## KEY NUMBERS TO REMEMBER

- Blue Dragon collects ~30,000+ Ti in a full 2000-turn game on open maps
- Blue Dragon builds ~300+ conveyors, ~30+ bridges, ~20+ harvesters in late game
- Blue Dragon builds ~20 Sentinels by end game
- Kessoku Band builds 10 Sentinels by turn 148 (fastest turret scaling)
- "something else" builds 9 bridges by turn 140 (aggressive bridging)
- Core Destroyed wins on narrow maps happen as early as turn 164 (landscape)
- All top teams start with 500 Ti and collect zero Axionite
- Match duration: 3-12 minutes real time for a 5-game series

---

*Report compiled from analysis of 8+ match details and 6+ replay inspections across the top 3 teams. Data from the Cambridge Battlecode game platform (game.battlecode.cam) on April 5, 2026.*
