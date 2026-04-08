# Top Ladder Study — What 1600+ Teams Do

**Date:** 2026-04-08 ~22:10 UTC  
**Data source:** `cambc ladder --limit 20` + match history per top team  
**Our position:** Rank #144, 1461 Elo, 408 matches

---

## Top 20 Ladder (as of 2026-04-08 22:00 UTC)

| Rank | Team | Rating | Matches | Category | Region |
|------|------|--------|---------|----------|--------|
| 1 | Blue Dragon | 2834 | 2950 | main | international |
| 2 | something else | 2680 | 2965 | main | international |
| 3 | Kessoku Band | 2604 | 2945 | main | international |
| 4 | MFF1 | 2469 | 2965 | main | international |
| 5 | Citadel | 2410 | 2967 | main | international |
| 6 | Dear jump Give me a job plz | 2390 | 2957 | main | international |
| 7 | Squishy | 2383 | 2815 | main | international |
| 8 | bwaaa | 2361 | 2969 | main | international |
| 9 | okbro | 2314 | 1210 | main | international |
| 10 | cheesynachos | 2302 | 2749 | main | international |
| 11 | Jython | 2302 | 2964 | main | international |
| 12 | Lorem Ipsum | 2301 | 2860 | novice | international |
| 13 | Operation Marvin | 2268 | 2965 | main | uk |
| 14 | sixseven | 2233 | 1489 | main | international |
| 15 | food | 2231 | 2288 | main | international |
| 16 | Por Favor | 2227 | 1868 | novice | international |
| 17 | Comp Practical Analysis Enjoyers | 2223 | 2967 | main | uk |
| 18 | Los Camalares | 2213 | 2968 | main | international |
| 19 | meowl fan club | 2196 | 2632 | main | international |
| 20 | test | 2181 | 2965 | main | uk |

---

## Match Pattern Analysis

### Blue Dragon (#1, 2834 Elo)
Recent matches: 4-1 vs "Dear jump Give me a job plz", 4-1 vs "something else"
- **Pattern:** Consistent 4-1 and 5-0 wins. Very rarely loses a series.
- **Known strategy:** Core destruction via offensive push (confirmed from binary_tree research — kills by round 297)
- **Implication:** Their bot wins by core kill on most maps, not just binary_tree

### something else (#2, 2680 Elo)
Recent: 1-4 loss to Blue Dragon (as Team A), 4-1 loss to Blue Dragon (as Team B)
- Only losing to #1 consistently
- Pattern suggests strong economic bot, possibly with some offensive capability

### Kessoku Band (#3, 2604 Elo)
Recent: 4-1 loss to MFF1 (unrated), 4-1 vs Squishy
- High Elo, played fewer rated games than others
- Tested by MFF1 (unrated practice, 4-1 win for Kessoku)

---

## What Separates 1500 from 1600?

Based on available data (our experience + match patterns):

### Teams in 1500-1600 range (around rank #100-150)

We're at rank #144, 1461. Teams just above us (Polska Gurom 1467, Chameleon 1466, N 1463) have very similar Elo and similar 50/50 win rates against us.

The ladder around 1400-1600 is extremely competitive — small advantages in specific maps determine wins. A team needs to win specific map matchups consistently.

### Key differentiators for 1600+ (our hypothesis)

1. **Win on binary_tree and other asymmetric maps**
   - Teams in 1500-1600 likely win ~50% on most maps but lose specifically on maps like binary_tree where there's extreme ore asymmetry
   - 1600+ teams have specific strategies for these maps (rush, specialized explore)

2. **Better conveyor chain efficiency**
   - From replay_analysis_apr6.md: MergeConflict (1600+ Elo) mines 2394 Ti/harvester vs our 903 Ti/harvester
   - They use 32 conveyors for 7 harvesters (4.6/harvester) vs our 73 for 12 (6.1/harvester)
   - More efficient chains = more Ti per building = lower scale penalty

3. **Fewer redundant buildings**
   - Top bots likely cap builders earlier and don't over-explore
   - Our bot builds 200-350 buildings vs opponents' 300-500 (when we win), suggesting we DO build fewer
   - But on cold/galaxy we build 547 — far too many

4. **Reliable 4-1 wins instead of coin-flip 3-2s**
   - Our V61 record: mostly 3-2 wins. Top 1600+ teams win 4-1 routinely.
   - 4-1 consistently beats 3-2: three 3-2 wins is only 3 points; a 4-1 is 4 points in 5-map series

---

## Our Path to 1600

To climb from 1461 to 1600 requires approximately 7-10 more wins than losses (each win/loss moves ~10-15 Elo at this tier).

### Most Impactful Improvements (priority order)

1. **Fix binary_tree (0% → 50%):** Adding a working offensive push OR improving early explore to reach the close ore would add ~3-5 Elo per match occurrence
   
2. **Reduce cold/galaxy over-building:** Building 547 on cold vs opponents' ~50 is a 10x scale difference. Cap builders at scale > 200% would significantly improve cold performance.

3. **Improve chain efficiency:** Shorter conveyor chains (bridges, better routing) → more Ti per harvester → win more maps at same building count

4. **Win 4-1 instead of 3-2:** If we can convert our 3-2 wins to 4-1 by winning 1 more map per series, that's a significant Elo boost.

---

## Teams to Study Further

| Team | Elo | Why |
|------|-----|-----|
| Pray and Deploy | ~1459 | We're 1W-4L vs them — specifically we need to understand what maps they beat us on |
| KCPC-B | ~unknown | 0W-3L vs them — confirmed nemesis, high skill |
| Solo Gambling | ~unknown | 5-0 swept us — clearly outclasses us |
| Code Monkeys | ~unknown | 0W-3L — another nemesis |
| Highly Suspect | ~unknown | 2W-3L (including two 5-0 sweeps against us) |
