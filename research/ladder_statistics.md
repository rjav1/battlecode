# Cambridge Battlecode 2026 -- Competitive Ladder Statistics
## Snapshot taken: 2026-04-04 (live data)

---

## 1. LADDER OVERVIEW

| Metric | Value |
|---|---|
| Total teams registered | 572 |
| Teams with Elo (ranked) | 227 |
| Teams unranked (0 matches or <100) | 345 |
| Main bracket teams | 336 (164 ranked) |
| Novice bracket teams | 236 (63 ranked) |
| UK region teams | 205 (58 ranked) |
| International teams | 367 |
| Minimum matches to receive rank | 100 |

### Filter Options on Ladder Page
- **Bracket**: All / Main / Novice
- **Region**: All / UK / Int'l

---

## 2. RANK TIER SYSTEM

Official tier thresholds (from home page):

| Tier | Elo Threshold | Teams in Tier | % of Ranked |
|---|---|---|---|
| Grandmaster | 2400+ | 3 | 1.3% |
| Master | 2200+ | 10 | 4.4% |
| Candidate Master | 2000+ | 18 | 7.9% |
| Diamond | 1800+ | 19 | 8.4% |
| Emerald | 1600+ | 39 | 17.2% |
| Gold | 1500+ | 34 | 15.0% |
| Silver | 1400+ | 34 | 15.0% |
| Bronze | <1400 | 76 | 33.5% |
| **Total ranked** | | **227** | |

Note: Tier counts from home page (3+10+18+19+39+34+34+76 = 233, slight discrepancy with 227 likely due to real-time elo changes around boundaries or rounding at time of snapshot).

---

## 3. ELO DISTRIBUTION

### Summary Statistics (ranked teams only, n=227)

| Stat | Value |
|---|---|
| Maximum | 2791 (Blue Dragon) |
| Minimum | 358 (:pensive:) |
| Median | 1529 |
| Mean | 1565 |
| P90 (top 10%) | 2075 |
| P75 (top 25%) | 1775 |
| P25 (bottom 25%) | 1363 |
| P10 (bottom 10%) | 1157 |
| Standard deviation (approx) | ~450 |

### Elo Histogram (100-point bins)

| Elo Range | Count | Bar |
|---|---|---|
| 2700-2799 | 2 | ## |
| 2600-2699 | 0 | |
| 2500-2599 | 1 | # |
| 2400-2499 | 0 | |
| 2300-2399 | 5 | ##### |
| 2200-2299 | 5 | ##### |
| 2100-2199 | 7 | ####### |
| 2000-2099 | 11 | ########### |
| 1900-1999 | 9 | ######### |
| 1800-1899 | 11 | ########### |
| 1700-1799 | 16 | ################ |
| 1600-1699 | 21 | ##################### |
| 1500-1599 | 36 | ************************************ |
| 1400-1499 | 35 | ################################### |
| 1300-1399 | 27 | ########################### |
| 1200-1299 | 13 | ############# |
| 1100-1199 | 12 | ############ |
| 1000-1099 | 5 | ##### |
| 900-999 | 3 | ### |
| 800-899 | 2 | ## |
| 700-799 | 1 | # |
| 600-699 | 1 | # |
| 500-599 | 0 | |
| 400-499 | 0 | |
| 300-399 | 4 | #### |

**Key observation**: The distribution peaks heavily in the 1400-1600 range (Gold/Silver tier), with a long tail downward. There is a notable cluster at the very bottom (300-399) which likely represents bots that crash or perform very poorly.

### Cumulative Distribution

| Percentile | Elo |
|---|---|
| Top 1% (rank ~2) | 2712+ |
| Top 5% (rank ~11) | 2236+ |
| Top 10% (rank ~23) | 2075+ |
| Top 20% (rank ~45) | 1862+ |
| Top 30% (rank ~68) | 1690+ |
| Top 50% (rank ~114) | 1529+ |
| Top 75% (rank ~170) | 1363+ |
| Top 90% (rank ~204) | 1157+ |

---

## 4. MATCH ACTIVITY ANALYSIS

### Match Count Distribution

| Match Count Range | Teams | % of Total 572 |
|---|---|---|
| 2500+ matches | 114 | 19.9% |
| 2000-2499 | 50 | 8.7% |
| 1500-1999 | 24 | 4.2% |
| 1000-1499 | 26 | 4.5% |
| 500-999 | 9 | 1.6% |
| 100-499 | 10 | 1.7% |
| 10-99 | 2 | 0.3% |
| 1-9 | 0 | 0.0% |
| 0 (never played) | 337 | 58.9% |

**Key findings**:
- **58.9% of registered teams have never played a match** (337 of 572)
- The active core is ~235 teams (41% of total)
- 114 teams have played 2500+ matches -- these are the fully engaged competitors
- The maximum match count observed is 2529 (approaching some apparent cap around 2528)
- Most ranked teams have 2500+ matches, indicating the ladder is mature

---

## 5. BRACKET COMPARISON: MAIN vs NOVICE

### Main Bracket

| Metric | Value |
|---|---|
| Total teams | 336 |
| Ranked teams | 164 |
| Highest Elo | 2791 (Blue Dragon) |
| Lowest ranked Elo | 358 |
| Median Elo | 1561 |

### Novice Bracket

| Metric | Value |
|---|---|
| Total teams | 236 |
| Ranked teams | 63 |
| Highest Elo | 2273 (Lorem Ipsum) |
| Lowest ranked Elo | 362 |
| Median Elo | 1451 |
| UK teams | 92 |
| Int'l teams | 144 |

### Top 10 Novice Teams

| Rank | Team | Elo | Region | Matches |
|---|---|---|---|---|
| 1 | Lorem Ipsum | 2273 | Int'l | 2420 |
| 2 | Operation Marvin | 2230 | UK | 2526 |
| 3 | Por Favor | 2080 | Int'l | 1428 |
| 4 | Signal | 2012 | Int'l | 2358 |
| 5 | Bongcloud | 1910 | UK | 2526 |
| 6 | Bit by Bit | 1891 | Int'l | 2260 |
| 7 | Comp Practical Analysis Enjoyers | 1840 | UK | 2526 |
| 8 | CanIGetAJob | 1832 | Int'l | 1659 |
| 9 | Crank(2006) | 1743 | Int'l | 1570 |
| 10 | Young Birds | 1665 | Int'l | 2526 |

**Novice vs Main observations**:
- The top novice team (Lorem Ipsum, 2273) would rank #9 overall -- competitive with main bracket masters
- Novice has a lower median Elo (1451 vs 1561) but the gap is smaller than expected
- Some novice teams are clearly capable of competing with main bracket teams
- 2 novice teams (Lorem Ipsum, Operation Marvin) are in the Master tier

---

## 6. MATCH SCORE DISTRIBUTION (from 50 recent completed matches)

Matches are Best-of-5 (all 5 games always played, regardless of early clinch).

| Score | Count | % |
|---|---|---|
| 5-0 / 0-5 (sweep) | 4 | 8% |
| 4-1 / 1-4 (dominant) | 19 | 38% |
| 3-2 / 2-3 (close) | 27 | 54% |
| **Total** | **50** | |

**Key finding**: Over half of matches (54%) go 3-2, meaning games are highly competitive at most Elo levels. Only 8% are clean sweeps. The format plays all 5 games regardless, so "3-2" means the winner won 3 and lost 2 of the 5 games.

### Live Match Snapshot (at time of data collection)
- **41 matches running, 0 queued**
- Matches span all tiers from Bronze to Grandmaster
- Example live matches observed:
  - something else (GM 2520) vs Blue Dragon (GM 2797) -- Game 5/5, score 1-3
  - Dear jump (Master 2330) vs bwaaa (Master 2352) -- Game 5/5, score 2-2
  - Squishy (CM 2128) vs Postmodern Prosperos (CM 2148) -- Game 5/5, score 2-2
  - MFF1 (Master 2386) vs Lorem Ipsum (Master 2273) -- Game 1/5, score 0-0

---

## 7. FEATURED GAMES ANALYSIS (from home page)

| Team 1 | Elo 1 | Team 2 | Elo 2 | Map | Turns | Time Ago |
|---|---|---|---|---|---|---|
| bwaaa | 2351 | food | 2309 | arena | 143t | 6h |
| MFF1 | 2350 | bwaaa | 2393 | hourglass | 2000t | 21h |
| something else | 2520 | Kessoku Band | 2622 | pls_buy_cucats_merch | 2000t | 1d |
| Jython | 2271 | bwaaa | 2351 | dna | 781t | 4h |
| 3MiceLockIntoCambridge | 2116 | cheesynachos | 2082 | default_large1 | 2000t | 10h |
| Postmodern Prosperos | 2184 | PPP | 2093 | wasteland_oasis | 2000t | 1h |
| bwaaa | 2379 | Lorem Ipsum | 2256 | cubes | 2000t | 19h |
| cheesynachos | 2056 | 3MiceLockIntoCambridge | 2078 | gaussian | 2000t | 15h |
| Operation Marvin | 2211 | test | 2162 | mandelbrot | 2000t | 15h |
| Oxford | 2320 | Operation Marvin | 2237 | default_large2 | 690t | 9h |

### Map Frequency (from featured games)

| Map | Appearances |
|---|---|
| default_large1 | 1 |
| default_large2 | 1 |
| arena | 1 |
| hourglass | 1 |
| pls_buy_cucats_merch | 1 |
| dna | 1 |
| wasteland_oasis | 1 |
| cubes | 1 |
| gaussian | 1 |
| mandelbrot | 1 |

Maps appear diverse -- no single map dominates the featured rotation.

### Turn Count Analysis

| Metric | Value |
|---|---|
| Games reaching 2000t (max turns) | 7 of 10 (70%) |
| Games ending early | 3 of 10 (30%) |
| Early-end turn counts | 143t, 781t, 690t |
| Average turns (all) | 1459t |
| Average turns (non-max) | 538t |

**Key meta insight**: 70% of featured games go to the full 2000-turn limit, indicating that the current meta involves slow, resource-accumulation strategies rather than early aggression. When games DO end early, they tend to end very early (143t = decisive early win) or moderately (690-781t = mid-game collapse).

---

## 8. TOP 5 TEAM PROFILES

### #1 Blue Dragon -- Elo 2790 (Grandmaster)

| Attribute | Value |
|---|---|
| Current Elo | 2790 |
| Peak Elo | 2797 |
| Current Rank | #1 of 572 |
| Peak Rank | #1 |
| Matches | 2512 |
| Bracket | main |
| Region | International |
| Members | 2/4 (Benjamin Kovacs [owner], SamH) |
| Type | Non-student |

**Recent match results (last 50 matches, last ~6 hours)**:
- Blue Dragon is absolutely dominant -- the vast majority of their recent matches are 5-0 wins
- They beat every other top team convincingly
- Key results from last 50:
  - vs something else (GM): 5-0 W, 4-1 W, 1-4 W, 0-5 W (multiple)
  - vs Kessoku Band (GM): 4-1 W, 3-2 W (with occasional losses 3-2)
  - vs MFF1 (Master): 5-0 W, 0-5 W, 3-2 L (mixed but mostly dominant)
  - vs bwaaa (Master): 5-0 W, 5-0 W, 5-0 W
  - vs food (Master): 5-0 W, 4-1 W, 4-1 W
  - vs Oxford (Master): 5-0 W, 5-0 W
  - vs Dear jump (Master): 5-0 W, 5-0 W, 5-0 W
- Elo has climbed from ~2754 to ~2797 in the last 6 hours

**Most frequent opponents** (from 50 matches):
- Kessoku Band: 8 matches
- MFF1: 7 matches
- something else: 7 matches
- Dear jump Give me a job plz: 6 matches
- bwaaa: 5 matches
- food: 5 matches

### #2 Kessoku Band -- Elo 2702-2712 (Grandmaster)

| Attribute | Value |
|---|---|
| Current Elo | ~2706 |
| Peak Elo | 2747 |
| Current Rank | #2 of 572 |
| Peak Rank | #1 |
| Matches | 2506 |
| Bracket | main |
| Region | International |
| Members | 4/4 (gura [owner], Varity, jzhc, Hallooz) |

**Key facts**: Kessoku Band previously held #1 (peak rank #1, peak 2747) but has been overtaken by Blue Dragon's recent surge. They are the only other team to have reached Grandmaster level consistently.

### #3 something else -- Elo 2520-2528 (Grandmaster)

| Attribute | Value |
|---|---|
| Current Elo | ~2520 |
| Peak Elo | 2542 |
| Current Rank | #3 of 572 |
| Peak Rank | #2 |
| Matches | 2527 |
| Bracket | main |
| Region | International |
| Members | 4/4 (osteo [owner], amcsz, [Jython], Coderz75) |

**Key facts**: Third-highest rated team, previously peaked at #2. Full 4-person roster. Consistently competitive at GM level but gets dominated by Blue Dragon (5-0 losses observed multiple times).

### #4 MFF1 -- Elo 2384-2386 (Master)

| Attribute | Value |
|---|---|
| Current Elo | ~2384 |
| Peak Elo | 2408 |
| Current Rank | #4 of 572 |
| Peak Rank | #2 |
| Matches | 2527 |
| Bracket | main |
| Region | International |
| Members | 4/4 (SK1PY [owner], Merlin, Svizel pritula, PatrikPrit) |

**Key facts**: Strong Master-tier team that has briefly hit Grandmaster (peak 2408 vs 2400 threshold). All international. Has peaked at #2 but can't consistently beat the top 3.

### #5 bwaaa -- Elo 2348-2352 (Master)

| Attribute | Value |
|---|---|
| Current Elo | ~2348 |
| Peak Elo | 2432 |
| Current Rank | #5 of 572 |
| Peak Rank | #2 |
| Matches | 2529 (highest match count observed) |
| Bracket | main |
| Region | International |
| Members | 4/4 (turska [owner], Intellegent [UK], NiFe, nife) |

**Key facts**: Also previously reached Grandmaster (peak 2432). Mixed UK/international team. Highest match count observed (2529). Has peaked at #2 rank but gets dominated by Blue Dragon.

---

## 9. COMPETITION SCHEDULE

| Date | Event | Status |
|---|---|---|
| Mar 16 | Launch event (2pm UK) | Done |
| Apr 5 | Sprint 3 tournament stream | Done |
| Apr 11 | Sprint 4 submission snapshot | 6d 3h remaining |
| Apr 12 | Sprint 4 tournament stream | 6d 22h remaining |
| Apr 20 | International qualifier | 15d 3h remaining |
| Apr 29 | Submissions freeze | 24d 3h remaining |
| Apr 29 | UK qualifier | 24d 3h remaining |
| Apr 29 | Novice tournament | 24d 3h remaining |
| May 5 | Live finals | 30d 3h remaining |

**International finalists receive an all-expenses-paid trip to Cambridge.**

---

## 10. STRATEGIC IMPLICATIONS

### What Elo do you need?

| Goal | Required Elo | Approx Rank |
|---|---|---|
| Reach Grandmaster | 2400+ | Top 3 |
| Reach Master | 2200+ | Top 13 |
| Reach Candidate Master | 2000+ | Top 31 |
| Top 10% | ~2075 | Top 23 |
| Top 25% | ~1775 | Top 57 |
| Top 50% (median) | ~1529 | Top 114 |

### Qualifying threshold estimates
- The International qualifier is April 20 (15 days away)
- UK qualifier is April 29 (24 days away)
- Without published qualification criteria, based on past competitive programming events, qualifying thresholds are likely:
  - International: Top 16-32 teams (Elo ~1800-2100 range)
  - UK: Potentially top 8-16 UK teams
  - Novice: Separate bracket
- Currently only 58 UK teams are ranked; top UK teams: test (2236), Faceit lvl 10 (2055), drop table (2038), St Johns Sauce (2030)

### How many matches do you need?
- 100 matches minimum to get a rank
- Active competitive teams have 2000-2528 matches
- At current pace, the ladder is running ~41 concurrent matches continuously
- Teams accumulate ~100+ matches per day at full activity

### Who will you likely face?
- Matchmaking appears to pair teams within similar Elo ranges
- At ~1500 Elo (Gold/Silver tier), you'll face the densest population bracket (71 teams between 1400-1600)
- At ~2000 Elo, you face a smaller pool of ~31 teams, meaning you'll repeatedly face the same opponents

### Meta observations
- 70% of top-level games go to the full 2000 turn limit
- This suggests a slow, economy-focused meta rather than rush/aggression
- When games end early, they tend to be decisive (143t = one side collapses almost immediately)
- The gap between #1 (Blue Dragon, 2790) and #3 (something else, 2520) is 270 Elo -- enormous
- Blue Dragon appears to have a significant strategic advantage over all other teams

---

## 11. FULL RANKED LADDER (All 227 teams)

### Ranks 1-50

| Rank | Elo | Team | Bracket | Region | Matches |
|---|---|---|---|---|---|
| 1 | 2791 | Blue Dragon | main | Int'l | 2510 |
| 2 | 2712 | Kessoku Band | main | Int'l | 2504 |
| 3 | 2520 | something else | main | Int'l | 2526 |
| 4 | 2386 | MFF1 | main | Int'l | 2526 |
| 5 | 2352 | bwaaa | main | Int'l | 2528 |
| 6 | 2330 | Dear jump Give me a job plz | main | Int'l | 2518 |
| 7 | 2327 | Oxford | main | Int'l | 2526 |
| 8 | 2325 | food | main | Int'l | 1847 |
| 9 | 2273 | Lorem Ipsum | novice | Int'l | 2420 |
| 10 | 2266 | Jython | main | Int'l | 2525 |
| 11 | 2236 | test | main | UK | 2524 |
| 12 | 2230 | Operation Marvin | novice | UK | 2526 |
| 13 | 2223 | WindRunners | main | Int'l | 2525 |
| 14 | 2182 | meowl fan club | main | Int'l | 2192 |
| 15 | 2158 | 3MiceLockIntoCambridge | main | Int'l | 1728 |
| 16 | 2148 | Postmodern Prosperos | main | Int'l | 2509 |
| 17 | 2141 | Oogway | main | Int'l | 2527 |
| 18 | 2128 | Squishy | main | Int'l | 2374 |
| 19 | 2121 | PPP | main | Int'l | 2052 |
| 20 | 2102 | cheesynachos | main | Int'l | 2307 |
| 21 | 2099 | sixseven | main | Int'l | 1048 |
| 22 | 2080 | Por Favor | novice | Int'l | 1428 |
| 23 | 2075 | okbro | main | Int'l | 769 |
| 24 | 2055 | Faceit lvl 10 | main | UK | 850 |
| 25 | 2038 | drop table | main | UK | 2526 |
| 26 | 2030 | St Johns Sauce | main | UK | 1836 |
| 27 | 2026 | Los Camalares | main | Int'l | 2527 |
| 28 | 2020 | Goobie Woobies | main | Int'l | 2525 |
| 29 | 2012 | Signal | novice | Int'l | 2358 |
| 30 | 2011 | The Rational Merlin | main | Int'l | 2136 |
| 31 | 2010 | gramaticka chiba | main | Int'l | 1868 |
| 32 | 1995 | kwasson_plusplus | main | Int'l | 2241 |
| 33 | 1976 | blauerdrache | main | Int'l | 2072 |
| 34 | 1972 | JDK: More like IDK | main | Int'l | 2525 |
| 35 | 1957 | Sand | main | Int'l | 2526 |
| 36 | 1940 | nus duck robots | main | Int'l | 534 |
| 37 | 1933 | NeverSurrender | main | Int'l | 2295 |
| 38 | 1925 | The Edge Case | main | UK | 2139 |
| 39 | 1914 | BadSubtraction | main | Int'l | 1785 |
| 40 | 1910 | Bongcloud | novice | UK | 2526 |
| 41 | 1891 | Bit by Bit | novice | Int'l | 2260 |
| 42 | 1885 | TvT | main | Int'l | 2527 |
| 43 | 1882 | dzwiek spadajacej metalowej rury | main | Int'l | 2527 |
| 44 | 1864 | I dont know | main | Int'l | 2020 |
| 45 | 1862 | 73 | main | Int'l | 2138 |
| 46 | 1858 | Axionite Inc | main | Int'l | 1416 |
| 47 | 1856 | Make Fire | main | Int'l | 2527 |
| 48 | 1840 | Comp Practical Analysis Enjoyers | novice | UK | 2526 |
| 49 | 1832 | CanIGetAJob | novice | Int'l | 1659 |
| 50 | 1832 | Lost in Space | main | Int'l | 2525 |

### Ranks 51-100

| Rank | Elo | Team | Bracket | Region | Matches |
|---|---|---|---|---|---|
| 51 | 1802 | The Blades | main | Int'l | 1138 |
| 52 | 1788 | 4 buffons with claude code | main | Int'l | 2525 |
| 53 | 1784 | not a great name | main | Int'l | 2289 |
| 54 | 1781 | Beehive | main | Int'l | 219 |
| 55 | 1779 | oog | main | Int'l | 1457 |
| 56 | 1775 | Tootill Labs | main | UK | 2484 |
| 57 | 1775 | Woodpecker no 1 | main | Int'l | 2297 |
| 58 | 1765 | Mr Worldwide | main | UK | 2083 |
| 59 | 1761 | AspiringGMs | main | Int'l | 2526 |
| 60 | 1743 | Crank(2006) | novice | Int'l | 1570 |
| 61 | 1726 | laapa chondey | main | Int'l | 1450 |
| 62 | 1715 | Lanis Mobile Gang | main | Int'l | 1648 |
| 63 | 1714 | the_best_team | main | Int'l | 366 |
| 64 | 1711 | MEEBs | main | UK | 2526 |
| 65 | 1710 | closedAI | main | UK | 2135 |
| 66 | 1709 | jjec | main | UK | 2018 |
| 67 | 1703 | seal team 4 | main | Int'l | 1907 |
| 68 | 1690 | Mind of Metal and Wheels | main | Int'l | 2525 |
| 69 | 1686 | Git Gud | main | Int'l | 1583 |
| 70 | 1678 | OoooulingHui | main | Int'l | 2056 |
| 71 | 1666 | Dont Jump | main | Int'l | 2526 |
| 72 | 1665 | Young Birds | novice | Int'l | 2526 |
| 73 | 1664 | nothing ever battles | main | Int'l | 2061 |
| 74 | 1658 | Kamikaze | main | Int'l | 1135 |
| 75 | 1651 | Matikanefukukitaru | main | Int'l | 1737 |
| 76 | 1651 | Ethzzzzz | main | Int'l | 2526 |
| 77 | 1650 | Import ChatGPT | main | UK | 2527 |
| 78 | 1649 | Matikanetannhauser | main | Int'l | 1681 |
| 79 | 1649 | Lazy People | main | Int'l | 1006 |
| 80 | 1648 | secret_sauce | novice | Int'l | 1739 |
| 81 | 1643 | Robinson College | main | UK | 135 |
| 82 | 1638 | Trivonacci | novice | Int'l | 2523 |
| 83 | 1635 | KAIZEN | main | Int'l | 128 |
| 84 | 1624 | Silver Chromate | main | UK | 2525 |
| 85 | 1609 | sacred stack of njtz | novice | Int'l | 2527 |
| 86 | 1608 | Super AI | main | Int'l | 2527 |
| 87 | 1607 | ff | novice | Int'l | 514 |
| 88 | 1605 | rmielamud | novice | Int'l | 2526 |
| 89 | 1599 | Wireless | novice | Int'l | 2527 |
| 90 | 1599 | BFS Enjoyers | main | Int'l | 2526 |
| 91 | 1592 | Mama Mia | main | Int'l | 2526 |
| 92 | 1591 | eidooheerfmaet2 | novice | Int'l | 449 |
| 93 | 1586 | 0_day | main | UK | 2526 |
| 94 | 1580 | zimno mi w jaja | novice | Int'l | 2305 |
| 95 | 1577 | Central Procrastination Unit | novice | UK | 2526 |
| 96 | 1576 | vedi-veci-fatalerror | main | Int'l | 2526 |
| 97 | 1571 | OpenCheliped 3 | main | Int'l | 793 |
| 98 | 1568 | stay sharp and keep trying | main | Int'l | 2524 |
| 99 | 1567 | Nah Id Lose | main | Int'l | 1316 |
| 100 | 1566 | Byte-Sized | novice | UK | 2526 |

### Ranks 101-150

| Rank | Elo | Team | Bracket | Region | Matches |
|---|---|---|---|---|---|
| 101 | 1563 | muteki | main | Int'l | 2521 |
| 102 | 1563 | Duck Duck Goose | main | Int'l | 2093 |
| 103 | 1561 | bot123 | main | Int'l | 1905 |
| 104 | 1555 | smartmonkey | main | Int'l | 1106 |
| 105 | 1551 | KJOW | main | Int'l | 2168 |
| 106 | 1549 | Tylenol Enthusiasts | main | Int'l | 2526 |
| 107 | 1547 | Bumchit | main | Int'l | 1253 |
| 108 | 1544 | nus robot husk | main | Int'l | 1239 |
| 109 | 1544 | Stratcom | novice | UK | 2527 |
| 110 | 1541 | One More Time | main | Int'l | 2526 |
| 111 | 1539 | MergeConflict | novice | Int'l | 1331 |
| 112 | 1535 | Warwick CodeSoc | main | UK | 2526 |
| 113 | 1530 | X_101 | main | Int'l | 2138 |
| 114 | 1529 | Ash Hit | main | UK | 2526 |
| 115 | 1528 | - | novice | UK | 184 |
| 116 | 1524 | eidooheerfmaet | novice | Int'l | 1193 |
| 117 | 1524 | Peanut | main | UK | 14 |
| 118 | 1520 | chicken tikka masala | novice | UK | 2526 |
| 119 | 1516 | Solo Gambling | novice | Int'l | 250 |
| 120 | 1516 | Taro Noodle House | main | Int'l | 2527 |
| 121 | 1514 | Guildhall CodingSoc | main | UK | 2181 |
| 122 | 1511 | Aggressive Toasters | main | Int'l | 2526 |
| 123 | 1511 | Vibecoders | main | Int'l | 2525 |
| 124 | 1503 | New Jabees | main | Int'l | 2527 |
| 125 | 1498 | nibbly-finger | main | UK | 2527 |
| 126 | 1495 | The Defect | main | Int'l | 2526 |
| 127 | 1494 | Pray and Deploy | main | UK | 2527 |
| 128 | 1493 | SPAARK | main | Int'l | 2527 |
| 129 | 1492 | Polska Gurom | main | Int'l | 2526 |
| 130 | 1492 | Highly Suspect | main | Int'l | 2526 |
| 131 | 1483 | double up | main | Int'l | 1836 |
| 132 | 1478 | Quwaky | main | Int'l | 1440 |
| 133 | 1475 | Fake Analysis | novice | Int'l | 2526 |
| 134 | 1471 | Chameleon | novice | UK | 2328 |
| 135 | 1469 | ah | main | Int'l | 2514 |
| 136 | 1465 | N | main | Int'l | 2121 |
| 137 | 1464 | DODO | main | UK | 769 |
| 138 | 1459 | Some People | main | UK | 2527 |
| 139 | 1457 | natto warriors | main | UK | 2526 |
| 140 | 1457 | MEOW MEOW MEOW MEOW MEOW | main | UK | 2299 |
| 141 | 1455 | Cenomanum | novice | UK | 2526 |
| 142 | 1455 | Atomic | novice | Int'l | 2392 |
| 143 | 1453 | strong vibe | main | Int'l | 2526 |
| 144 | 1452 | andrew_and_friends | novice | Int'l | 2527 |
| 145 | 1451 | Aviators | novice | Int'l | 2526 |
| 146 | 1450 | HAL9000 | main | UK | 2526 |
| 147 | 1443 | O_O | main | Int'l | 2526 |
| 148 | 1443 | Code Monkeys | main | UK | 2526 |
| 149 | 1434 | binary bros | novice | UK | 2526 |
| 150 | 1434 | 5goatswalkintoabarbut1dies | main | Int'l | 2172 |

### Ranks 151-200

| Rank | Elo | Team | Bracket | Region | Matches |
|---|---|---|---|---|---|
| 151 | 1433 | BulkX | novice | Int'l | 2328 |
| 152 | 1430 | Botz4Lyf | novice | Int'l | 2526 |
| 153 | 1424 | MWLP | main | Int'l | 2527 |
| 154 | 1421 | oslsnst | main | Int'l | 2526 |
| 155 | 1413 | ken-is-goated | main | UK | 2526 |
| 156 | 1412 | EEZ | main | Int'l | 2526 |
| 157 | 1408 | Dino | novice | Int'l | 835 |
| 158 | 1407 | cutie fan club | main | Int'l | 1452 |
| 159 | 1405 | :3 | main | UK | 2526 |
| 160 | 1399 | no_friends_to_make_a_team | novice | Int'l | 2519 |
| 161 | 1397 | pacman | novice | Int'l | 1939 |
| 162 | 1396 | arnon (inactive) | main | UK | 2522 |
| 163 | 1394 | NoGarbageCollectors | main | UK | 2526 |
| 164 | 1391 | Three Bolts One Bug | main | Int'l | 2526 |
| 165 | 1389 | cr4zy-fr1es | novice | Int'l | 2526 |
| 166 | 1385 | Patata para lavavajillas | novice | Int'l | 2001 |
| 167 | 1384 | Mysticmage45 | main | Int'l | 671 |
| 168 | 1380 | JAGUAR | novice | Int'l | 2170 |
| 169 | 1377 | Team Goldhill | main | Int'l | 269 |
| 170 | 1377 | Clankers | main | UK | 2526 |
| 171 | 1363 | MoneroMiners | main | Int'l | 1744 |
| 172 | 1357 | kemu_saba | main | Int'l | 2527 |
| 173 | 1349 | object Object | novice | UK | 2526 |
| 174 | 1343 | green burger | novice | UK | 2526 |
| 175 | 1340 | planless | main | Int'l | 1856 |
| 176 | 1340 | Solo | main | UK | 2527 |
| 177 | 1338 | gaslighting | novice | UK | 2526 |
| 178 | 1337 | Testing | novice | Int'l | 1212 |
| 179 | 1336 | OG | main | UK | 2003 |
| 180 | 1330 | dark_fire | novice | Int'l | 2010 |
| 181 | 1328 | unemployed | main | Int'l | 12 |
| 182 | 1314 | Javapie | main | Int'l | 2004 |
| 183 | 1313 | randomusergroup | main | UK | 2527 |
| 184 | 1308 | Letofa | novice | Int'l | 1146 |
| 185 | 1306 | Pufferfish | main | Int'l | 2527 |
| 186 | 1305 | weigoat | main | Int'l | 2526 |
| 187 | 1294 | I am bad at coding | main | Int'l | 2526 |
| 188 | 1292 | a toofpick changes everythang | main | UK | 2527 |
| 189 | 1289 | United4Ever | novice | UK | 1607 |
| 190 | 1288 | mop | novice | Int'l | 1458 |
| 191 | 1287 | Slayers_of_Serpents | novice | Int'l | 1987 |
| 192 | 1284 | NikDotDuckTrick | main | Int'l | 251 |
| 193 | 1280 | switch | novice | Int'l | 2066 |
| 194 | 1279 | Bezdarnost | novice | Int'l | 1260 |
| 195 | 1253 | ACatLocksOutOfCambridge | main | Int'l | 1131 |
| 196 | 1249 | Room 40z | novice | Int'l | 2527 |
| 197 | 1246 | We wear shoes sometimes | main | Int'l | 2527 |
| 198 | 1214 | 67 | main | Int'l | 2527 |
| 199 | 1210 | Velocity | novice | Int'l | 602 |
| 200 | 1195 | erk | main | Int'l | 2526 |

### Ranks 201-227

| Rank | Elo | Team | Bracket | Region | Matches |
|---|---|---|---|---|---|
| 201 | 1194 | Hussain | novice | UK | 2526 |
| 202 | 1180 | umbracine | main | Int'l | 2527 |
| 203 | 1179 | SS10 | novice | Int'l | 2526 |
| 204 | 1166 | TheWarriors | main | Int'l | 2527 |
| 205 | 1157 | Titan Marauders | novice | Int'l | 2385 |
| 206 | 1154 | Enter team name | novice | UK | 2527 |
| 207 | 1133 | Psyduck Hold | main | Int'l | 1067 |
| 208 | 1132 | pigeon | main | UK | 2132 |
| 209 | 1126 | TheWeatherApp | main | Int'l | 2527 |
| 210 | 1125 | Manny and his Minions | main | Int'l | 2526 |
| 211 | 1119 | pika pikachu | novice | Int'l | 176 |
| 212 | 1099 | nahhh | main | Int'l | 1150 |
| 213 | 1079 | FactoryMustGrow | main | Int'l | 2327 |
| 214 | 1074 | sauce_destroyer | main | UK | 1007 |
| 215 | 1067 | meow | main | Int'l | 2526 |
| 216 | 1065 | OBS | novice | Int'l | 1933 |
| 217 | 984 | brumbaclarts | main | UK | 1911 |
| 218 | 959 | not adgato | main | UK | 2136 |
| 219 | 957 | YeezyBullyMarch27 | novice | Int'l | 1815 |
| 220 | 854 | efwerfwefqwe | novice | Int'l | 1394 |
| 221 | 816 | wandering_supernova | main | UK | 2526 |
| 222 | 712 | AI | main | Int'l | 2136 |
| 223 | 691 | ackk | main | Int'l | 1199 |
| 224 | 366 | --dangerously-skip-permissions | main | Int'l | 2527 |
| 225 | 362 | Skilled | novice | Int'l | 2526 |
| 226 | 361 | Operation Blade | main | UK | 2526 |
| 227 | 358 | :pensive: | main | Int'l | 2526 |

---

## 12. Elo CHANGE PATTERNS (from recent match history)

From the 50 most recent completed matches, Elo changes observed:

| Elo Change | Context |
|---|---|
| +/-2 to +/-3 | Close Elo matchups (within ~20 Elo) |
| +/-5 | Moderate Elo gap (~100-200 Elo) |
| +/-7 to +/-10 | Significant Elo mismatch (200-400 Elo) |
| +/-13 | Large Elo gap (500+ Elo) |
| +/-18 | Very large gap with upset |
| UR (Unrated) | Challenge matches (don't affect Elo) |

Observed examples:
- Blue Dragon (2795) -10 / MFF1 (2374) +10 on a 3-2 loss (400 Elo gap upset)
- Kessoku Band (2701) -13 / Blue Dragon (2774) +13 on 0-5 (small GM gap, decisive)
- jjec (1789) +18 / AspiringGMs (1761) -18 on 5-0 (close Elo but sweep amplifies)

---

*Data collected from https://game.battlecode.cam on 2026-04-04. All Elo values are approximate and subject to real-time fluctuation as matches continuously resolve.*
