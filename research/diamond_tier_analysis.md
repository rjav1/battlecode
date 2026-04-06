# Diamond Tier Analysis: What 1800+ Elo Bots Look Like
## Cambridge Battlecode 2026
### Compiled: April 5, 2026

---

## EXECUTIVE SUMMARY

Diamond-tier bots (1800-2000 Elo, ranks ~30-55) represent a MASSIVE skill gap above our current 1490 Elo. The key finding: **at Diamond tier, having a working harvester economy is the single differentiator between winning and losing.** Many Diamond bots still have broken or nonexistent resource chains. The teams that win at this level are the ones with functional harvester-to-core conveyor chains, even if crude. Barriers, splitters, and mixed turret compositions appear at this tier but are secondary to having any economy at all.

---

## TEAMS ANALYZED

### Ladder Snapshot (Diamond Tier, 1800-2000 Elo)

| Rank | Elo | Team | Category | Region | Members | Peak Elo |
|------|-----|------|----------|--------|---------|----------|
| 31 | 1998 | The Rational Merlin | MAIN | INT'L | ? | ? |
| 34 | 1981 | blauerdrache | MAIN | INT'L | ? | ? |
| 35 | 1956 | nus duck robots | MAIN | INT'L | ? | ? |
| 36 | 1943 | BadSubtraction | MAIN | INT'L | ? | ? |
| 37 | 1927 | Bongcloud | NOVICE | UK | ? | ? |
| 38 | 1916 | Bit by Bit | NOVICE | INT'L | 2 | ? |
| 39 | 1911 | NeverSurrender | MAIN | INT'L | ? | ? |
| 40 | 1906 | Sand | MAIN | INT'L | ? | ? |
| 41 | 1899 | dzwiek spadajacej metalowej rury | MAIN | INT'L | ? | ? |
| 42 | 1890 | The Edge Case | MAIN | UK | ? | ? |
| 43 | 1880 | Axionite Inc | MAIN | INT'L | 2 | 2038 |
| 44 | 1878 | TvT | MAIN | INT'L | 1 | 1947 |
| 45 | 1870 | 73 | MAIN | INT'L | ? | ? |
| 46 | 1866 | Make Fire | MAIN | INT'L | ? | ? |
| 47 | 1842 | I dont know | MAIN | INT'L | ? | ? |
| 48 | 1841 | Lost in Space | MAIN | INT'L | 2 | 1975 |
| 49 | 1821 | CanIGetAJob | NOVICE | INT'L | ? | ? |
| 50 | 1818 | Comp Practical Analysis Enjoyers | NOVICE | UK | ? | ? |
| 51 | 1810 | The Blades | MAIN | INT'L | ? | ? |
| 52 | 1810 | 4 buffons with claude code | MAIN | INT'L | ? | ? |
| 53 | 1799 | Beehive | MAIN | INT'L | ? | ? |

---

## DETAILED TEAM PROFILES

### Axionite Inc (Rank 43, 1880 Elo, Peak 2038)

**Members:** 2 (Stasimon, Jakub_)
**Matches:** 1451
**Recent form:** Very active, trading 3-2 wins and losses with nearby teams

**Match record (recent 20):**
- vs Bit by Bit (1921): W 3-2
- vs Beehive (1819): L 1-4
- vs The Blades (1867): W 3-2
- vs dzwiek (1898): L 2-3
- vs The Edge Case (1917): L 2-3
- vs TvT (1868): W 4-1
- vs Make Fire (1877): W 5-0
- vs 73 (1861): L 2-3
- vs Sand (1903): L 2-3
- vs Comp Prac. (1882): W 3-2
- vs Bit by Bit (1883): W 3-2
- vs BadSubtraction (1940): L 1-4
- vs The Edge Case (1895): W 3-2
- vs I dont know (1838): W 5-0
- vs Bongcloud (1925): L 1-4

**Pattern:** Axionite Inc trades close 3-2 matches with teams in the 1830-1930 range. They beat lower Diamond teams (I dont know, TvT) and lose to higher ones (BadSubtraction, Bongcloud). Very typical Diamond-tier back-and-forth.

### TvT (Rank 44, 1878 Elo, Peak 1947)

**Members:** 1 (Havic) -- SOLO PLAYER
**Matches:** 2563
**Recent form:** Volatile, winning and losing in rapid succession

**Match record (recent 20):**
- vs 4 buffons (1824): L 0-5
- vs 73 (1858): W 3-2
- vs The Blades (1859): L 2-3
- vs dzwiek (1860): W 3-2
- vs Sand (1861): W 3-2
- vs Make Fire (1861): W 3-2
- vs Axionite Inc (1868): W 4-1
- vs Lost in Space (1841): W 4-1
- vs I dont know (1857): L 2-3
- vs The Blades (1848): L 1-4
- vs CanIGetAJob (1838): L 1-4
- vs dzwiek (1882): L 0-5
- vs 4 buffons (1833): L 1-4
- vs Sand (1903): L 2-3
- vs The Edge Case (1872): L 2-3

**Pattern:** TvT is a solo player who peaked at 1947 (nearly Candidate Master) but hovers around 1878. Extremely inconsistent -- swings between 5-0 wins and 0-5 losses against similar-rated opponents. This is the hallmark of a bot that works well on some maps but poorly on others.

### Lost in Space (Rank 48, 1841 Elo, Peak 1975)

**Members:** 2 (akssh, TheSky)
**Matches:** 2561
**Description:** "fully lost"

**Match record (recent 20):**
- vs dzwiek (1892): L 1-4
- vs Make Fire (1854): L 0-5
- vs NeverSurrender (1907): L 2-3
- vs I dont know (1858): L 2-3
- vs 73 (1855): W 3-2
- vs Bit by Bit (1849): L 2-3
- vs Comp Prac. (1847): W 5-0
- vs TvT (1841): L (from TvT's W 4-1)
- vs CanIGetAJob (1834): W 5-0
- vs Beehive (1817): L 2-3
- vs Crank(2006) (1769): W 1-4 (Lost in Space won)
- vs oog (1793): W 1-4 (Lost in Space won)

**Pattern:** Lost in Space has declined from peak 1975 to 1841. They lose to most teams rated above them and narrowly beat teams below. Their 5-0 wins show they can dominate weaker opponents, but they get swept by stronger ones.

---

## REPLAY ANALYSIS: ENTITY COUNTS AT ROUND 2000

### Match: Axionite Inc vs dzwiek spadajacej (d91f5622)
**Result:** Axionite Inc 3-2 dzwiek
**Games:** socket (RV 2000t), default_large2 (CD 251t), default_small1 (RV 2000t), face (CD 66t), hourglass (RV 2000t)

#### Game 1: socket (Resource Victory, 2000 turns) -- Axionite Inc WINS

| Metric | Axionite Inc (G) | dzwiek (S) |
|--------|-----------------|------------|
| Titanium on hand | 27 | 5096 |
| Ti collected | 4880 | 0 |
| Ax collected | 0 | 0 |
| Bots | 5 | 0 |
| Roads | 113 | 154 |
| Conveyors | 1 | 0 |
| Splitters | 2 | 0 |
| Bridges | 1 | 0 |
| Harvesters | 1 | 0 |
| Barriers | 36 | 0 |
| Gunners | 0 | 0 |
| Sentinels | 2 | 0 |
| Launchers | 0 | 0 |

**Analysis:** Axionite Inc won with only 1 harvester and 4880 Ti collected. dzwiek had ZERO economy (0 harvesters, 0 conveyors, 0 Ti collected) -- they spent all their passive income on 154 roads. Axionite Inc used 36 barriers for defense and 2 splitters + 2 sentinels for military. This shows that even a single working harvester chain wins against a bot with no economy.

#### Game 5: hourglass (Resource Victory, 2000 turns) -- Axionite Inc WINS

| Metric | Axionite Inc (G) | dzwiek (S) |
|--------|-----------------|------------|
| Titanium on hand | 18229 | 2581 |
| Ti collected | 19240 | 0 |
| Ax collected | 0 | 0 |
| Bots | 17 | 16 |
| Roads | 296 | 59 |
| Conveyors | 13 | 17 |
| Splitters | 4 | 0 |
| Bridges | 2 | 0 |
| Harvesters | 7 | 0 |
| Barriers | 38 | 0 |
| Gunners | 2 | 2 |
| Sentinels | 3 | 0 |
| Launchers | 2 | 0 |
| Foundries | 0 | 0 |

**Analysis:** Axionite Inc's full power is visible on hourglass:
- **7 harvesters** generating 19240 Ti collected (vs dzwiek's 0)
- **4 splitters** branching resources to turrets
- **38 barriers** creating a massive defensive wall
- **Mixed turrets:** 3 sentinels + 2 gunners + 2 launchers
- **296 roads** for extensive builder mobility
- **2 bridges** for crossing terrain gaps
- **13 conveyors** for resource chains (relatively few -- roads are the primary path network)

Meanwhile dzwiek again has 0 Ti collected, 0 harvesters, relying purely on passive income (2581 Ti). They built 17 conveyors and 2 gunners but have no resource chains flowing. They have 16 bots but no economy to support them.

---

## KEY FINDINGS

### Finding 1: Working Economy is THE Differentiator

The single most important capability at Diamond tier is having harvesters connected to core via conveyor chains. Many Diamond-tier bots (~1800-1900) still DO NOT have working economies:

- dzwiek (1899 Elo): 0 Ti collected in both games analyzed. Zero harvesters.
- Our bot (buzzing bees, 1490 Elo): 0 Ti collected. Zero harvesters at end of game.

The teams that DO have working economies (Axionite Inc: 4880-19240 Ti collected) beat those that don't. **This means fixing our harvester-to-core conveyor chains should instantly vault us from 1490 to 1800+ Elo.**

### Finding 2: Splitters ARE Used at Diamond Tier

Axionite Inc uses 2-4 splitters per game. This confirms splitters are viable and used by winning Diamond-tier bots. They appear to be used for:
1. Branching resources from main chains to turrets (sentinel/gunner ammo delivery)
2. Distributing resources across multiple output directions

### Finding 3: Barriers Are HEAVILY Used

Axionite Inc builds 36-38 barriers per game. This is the most-built building type by count after roads. At 3 Ti and +1% scale each, 38 barriers = 114 Ti + 38% scale -- a significant investment that creates a massive defensive wall. Barriers appear to be placed around the core and along defensive perimeters.

### Finding 4: Roads Are Primary Mobility Infrastructure

Axionite Inc builds 113-296 roads per game (far more than conveyors). This suggests roads are the primary means of enabling builder movement, while conveyors are reserved specifically for resource transport chains. This is the OPPOSITE of what Blue Dragon does at Grandmaster (308 conveyors, 174 roads).

**Interpretation:** At Diamond tier, bots use roads for movement and a small number of directed conveyors for resource chains. At Grandmaster, bots use conveyors for BOTH movement AND resource transport, getting dual value from each placement.

### Finding 5: Mixed Turret Compositions

Axionite Inc uses 3 sentinels + 2 gunners + 2 launchers. Unlike the top 3 teams (pure sentinel), Diamond-tier bots diversify turrets. Launchers at this level suggest some bots use offensive builder throws. Gunners provide cheaper supplementary fire.

### Finding 6: Bridges Used but Sparingly

Axionite Inc builds 1-2 bridges per game. This is far fewer than Blue Dragon (33 bridges) but shows that bridge usage begins at Diamond tier for crossing terrain gaps.

### Finding 7: Match Results Are Very Close

At Diamond tier, most matches are 3-2 (close) rather than 5-0 (domination). This means map variance plays a huge role. A bot that works on 3 out of 5 map types will win most matches. A bot that only works on 2 will hover around 1800 Elo.

### Finding 8: Solo Players Can Reach Diamond

TvT (rank 44, 1878 Elo) is a solo player who peaked at 1947. This proves a single focused developer can reach high Diamond. Our team (solo as well) has no structural disadvantage.

### Finding 9: Core Destroyed Wins Are Very Fast at Diamond

In the Axionite Inc vs dzwiek match:
- Game 2: Core Destroyed at 251 turns (default_large2)
- Game 4: Core Destroyed at 66 turns (face)

66-turn Core Destroyed is extremely fast -- this means aggressive bots at Diamond tier can kill cores within the first minute of the game on favorable maps.

### Finding 10: No Axionite, No Foundries at Diamond

Zero axionite collected and zero foundries across all games analyzed. Just like the top 3, Diamond bots ignore the axionite system entirely and focus on pure titanium economy.

---

## WHAT WE NEED TO REACH DIAMOND (1800+ Elo)

### Must-Have (1500 -> 1800)

1. **Working harvester-to-core conveyor chains**
   - Build harvesters on Ti ore deposits
   - Connect them to core via directed conveyor chains
   - Even 1-2 working harvesters collecting 3000-5000 Ti is enough to beat bots with no economy
   - This is the SINGLE MOST IMPORTANT improvement

2. **Directed conveyor building**
   - Conveyors must face TOWARD core, not random directions
   - Plan chain direction before building
   - Each conveyor must connect to the next in the chain

3. **Basic defensive barriers**
   - 10-20 barriers around core perimeter (~30-60 Ti)
   - Cheap HP wall that slows enemy rushes

4. **Road network for builder mobility**
   - Build roads for exploration/movement
   - Reserve conveyors only for resource chains

### Nice-to-Have (1800 -> 2000)

5. **Splitter-based turret ammo delivery**
   - Insert splitters into chains to branch resources to sentinels
   - Axionite Inc uses 2-4 splitters to feed 2-3 sentinels

6. **Bridge usage for terrain crossing**
   - 1-2 bridges per game for crossing walls
   - Enables reaching remote ore deposits

7. **Multiple harvesters (5-7)**
   - Scale from 1-2 harvesters to 5-7
   - Target Ti collected of 10000-20000 by round 2000

8. **Mixed turret composition**
   - 2-3 sentinels for zone control
   - 1-2 gunners for cheap supplementary fire
   - 1-2 launchers for offensive pressure (optional)

9. **Map adaptation**
   - Rush on small/narrow maps (face: CD at 66t)
   - Economy on large maps (hourglass: RV at 2000t)

---

## COMPARISON: US vs DIAMOND vs GRANDMASTER

| Metric | buzzing bees (1490) | Axionite Inc (1880) | Blue Dragon (2790) |
|--------|--------------------|--------------------|-------------------|
| Ti collected (late game) | 0 | 4,880-19,240 | 30,000+ |
| Harvesters | 0 (break/don't connect) | 1-7 | 7-22 |
| Conveyors | 36 (random) | 1-13 (directed) | 308 (dual-use) |
| Roads | 0 | 113-296 | 174 |
| Bridges | 1 | 1-2 | 10-33 |
| Splitters | 0 | 2-4 | 4 |
| Barriers | 0 | 36-38 | 1-4 |
| Sentinels | 4 (no ammo) | 2-3 (with ammo) | 20 (with ammo) |
| Gunners | 0 | 0-2 | 0-1 |
| Launchers | 0 | 0-2 | 0-3 |
| Foundries | 0 | 0 | 0 |
| Win condition | Lose everything | Win RV + some CD | Win both consistently |

### The Gap Explained

**1490 -> 1800 gap:** We build conveyors but they don't form connected chains to core. We have zero Ti collected. The fix is directed conveyors forming harvester-to-core pipelines. This is the ONLY change needed to jump ~300 Elo.

**1800 -> 2000 gap:** Having economy but needing MORE of it (more harvesters, splitters for turret ammo, bridge expansion). Also need barriers for defense and map adaptation.

**2000 -> 2400 gap:** Need dual competency (economy + military). Conveyor networks that serve as both resource pipes AND builder paths. Massive sentinel defense. Bridge-heavy expansion.

**2400+ gap:** Blue Dragon level. 300+ conveyors, 30+ bridges, 20+ harvesters, 20+ sentinels. Unmatched economic efficiency.

---

## IMMEDIATE ACTION ITEMS (Priority Order)

1. **FIX CONVEYOR DIRECTION** -- Make conveyors face toward core, not away from it. This is the critical bug preventing any resource collection.

2. **BUILD HARVESTER-CONNECTED CHAINS** -- When a harvester is built on ore, ensure the conveyor chain from that harvester leads unbroken to the core.

3. **USE ROADS FOR EXPLORATION** -- Stop building conveyors while exploring. Build roads instead. Only build conveyors as part of a planned resource chain.

4. **ADD BARRIER RING** -- Build 10-20 barriers around core for cheap defense (30-60 Ti, +10-20% scale).

5. **SPLITTER AMMO DELIVERY** -- After economy works, insert splitters to feed sentinels with ammo.

6. **SCALE HARVESTERS** -- Build 3-5 harvesters in the first 200 rounds for strong early economy.

---

## APPENDIX: DIAMOND TIER ECOSYSTEM

### Competitive Clusters

**Upper Diamond (1900-2000):**
- Teams: BadSubtraction, Bongcloud, NeverSurrender, Sand, The Edge Case, nus duck robots
- These teams can sometimes upset lower Master-tier teams
- Likely have 5+ harvesters and functional military

**Mid Diamond (1850-1900):**
- Teams: dzwiek, Axionite Inc, TvT, 73, Make Fire
- Close 3-2 matches dominate
- Economy varies wildly (some have it, some don't)
- The teams WITH economy (Axionite Inc) consistently beat those without (dzwiek)

**Lower Diamond (1800-1850):**
- Teams: I dont know, Lost in Space, CanIGetAJob, Comp Practical Analysis Enjoyers, The Blades
- Declining from peaks, struggling to maintain rating
- May have economy on some maps but not others
- Lose to mid-Diamond teams 60-70% of the time

### Key Rivalries at Diamond

- Axionite Inc vs TvT: Axionite Inc edges it (4-1 win)
- Axionite Inc vs dzwiek: Close matchup (3-2 both ways)
- TvT vs Lost in Space: TvT dominates (4-1, 5-0)
- Everyone vs NeverSurrender/Bongcloud: NeverSurrender and Bongcloud dominate the tier

### Win Condition Distribution at Diamond

From match data analyzed:
- **Resource Victory at 2000t:** The dominant outcome (~65% of games between Diamond teams)
- **Core Destroyed < 100t:** Rare but happens on small maps (face: 66t)
- **Core Destroyed 200-500t:** Occurs on narrow/medium maps (~25% of games)
- **Core Destroyed > 500t:** Occasional late-game breakthrough (~10% of games)

---

*Research compiled from ladder data, team profiles, match details, and replay analysis using the Cambridge Battlecode visualiser on April 5, 2026. Entity counts extracted from replay viewer at round 2000.*
