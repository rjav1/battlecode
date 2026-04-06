# Elo Collapse Post-Mortem Analysis

**Date:** 2026-04-06
**Current Elo:** 1438 (started ~1488, dropped ~50 points)
**Total matches analyzed:** 114 ladder matches

---

## 1. Overall Record

**Total: 50W - 64L (43.9% win rate)**

### Record by Score Margin
| Score | Count | % of Losses/Wins |
|-------|-------|------------------|
| 5-0 wins | 3 | 6% of wins |
| 4-1 wins | 18 | 36% of wins |
| 3-2 wins | 29 | 58% of wins |
| 2-3 losses | 24 | 37.5% of losses |
| 1-4 losses | 17 | 26.6% of losses |
| 0-5 losses | 6 | 9.4% of losses |
| 3-2 losses | 17 | 26.6% of losses |

**Key observation:** Most wins are narrow (3-2), most losses are by larger margins. We lose badly more often than we win convincingly. This is a classic economy bot problem -- we're map-dependent and have no ability to punish or defend.

---

## 2. Loss Categorization by Victory Condition

### Core Destroyed Losses (military)
Out of all individual game losses across all matches, the following were core_destroyed:

| Match | Opponent | Map | Round | 
|-------|----------|-----|-------|
| HAL9000 1-4 | HAL9000 | default_medium1 | 95 |
| HAL9000 1-4 (early) | HAL9000 | galaxy | 86 |
| oslsnst 3-2 | oslsnst | starry_night | 1028 |
| oslsnst 3-2 | oslsnst | default_large1 | 1332 |
| Polska 2-3 | Polska Gurom | face | 339 |
| Polska 3-2 (early) | Polska Gurom | face | 319 |
| Polska 3-2 | Polska Gurom | binary_tree | 1300 |
| oslsnst 4-1 | oslsnst | bar_chart | 165 |
| oslsnst 4-1 | oslsnst | default_medium1 | 451 |
| oslsnst 4-1 | oslsnst | starry_night | 667 |
| oslsnst 4-1 | oslsnst | arena | 335 |
| oslsnst 4-1 (11:46) | oslsnst | hooks | 808 |
| oslsnst 4-1 (11:46) | oslsnst | hourglass | 1978 |
| Warwick 1-4 | Warwick CodeSoc | face | 137 |
| Warwick 1-4 | Warwick CodeSoc | shish_kebab | 190 |

**Total: 15 individual game losses by core destruction**

**Rush-vulnerable maps (core destroyed <500 rounds):**
- `face` - 3 times (rounds 137, 319, 339)
- `default_medium1` - 2 times (rounds 95, 451) 
- `bar_chart` - 1 time (round 165)
- `shish_kebab` - 1 time (round 190)
- `arena` - 1 time (round 335)
- `galaxy` - 1 time (round 86)

**Rush opponents:** HAL9000, oslsnst, Polska Gurom, Warwick CodeSoc

### Resource Victory Losses (economy)
**The VAST majority of losses are resource/economy losses at round 2000.** This is the dominant loss mode. Specific tiebreakers used:
- `titanium_collected` - most common
- `resources` - very common (generic resource tiebreaker)
- `harvesters` - 2 games
- `titanium_stored` - rare

**Economy losses are ~90%+ of all individual game losses.**

---

## 3. Version-to-Time Mapping

| Version | Uploaded | Active Period (approx) |
|---------|----------|----------------------|
| v1-v4 | 02:02-02:41 | 02:02-02:52 |
| v5-v9 | 02:52-03:04 | 02:52-03:20 |
| v10-v15 | 03:20-03:44 | 03:20-04:28 |
| v16-v17 | 04:28-04:29 | 04:28-04:38 |
| v18-v23 | 04:38-05:03 | 04:38-06:47 |
| v24 | 07:09 | 07:09-07:50 |
| v25 | 07:50 | 07:50-08:02 |
| v26 | 08:02 | 08:02-08:25 |
| v27-v29 | 08:25-08:35 | 08:25-09:23 |
| v30-v32 | 09:23-09:51 | 09:23-12:15 |
| v33 | 12:15 | 12:15-12:51 |
| v34-v35 | 12:51-12:55 | 12:51-13:28 |
| v36 | 13:28 | 13:28-14:26 |
| v37-v38 | 14:26-14:28 | 14:26-14:58 |
| v39 | 14:58 | 14:58-15:12 |
| v40 | 15:12 | 15:12-16:02 |
| v41-v43 | 16:02-16:11 | 16:02-16:33 |
| v44 | 16:33 | 16:33-17:06 |
| v45 | 17:06 | 17:06-present |

### Per-Period Win Rates (approximate, based on match start times)

**Early versions (v1-v15, 02:00-04:28):**
Matches: One More Time 1-4 L, Chameleon 2-3 L, SPAARK 2-3 W, KCPC-B 0-5 L, :3 1-4 L, HAL9000 1-4 L, SPAARK 3-2 W, MEOW 3-2 W, 5goats 3-2 L, Polska 3-2 L
Record: ~3W-7L (30% WR) -- **TERRIBLE start**

**Mid versions (v16-v23, 04:28-07:09):**
Matches: oslsnst 4-1 W, The Defect 3-2 L, BulkX 4-1 W, Pray/Deploy 3-2 W, Solo 3-2 W, KCPC-B 3-2 L, andrew 4-1 W, Chameleon 3-2 L, SPAARK 4-1 L, Quwaky 5-0 W, Solo 4-1 W, Taro 4-1 W, Highly Suspect 4-1 L, Vibecoders 2-3 L, Wireless 4-1 L
Record: ~8W-7L (53% WR) -- **best period**

**v24-v29 (07:09-09:23):**
Matches: oslsnst 3-2 L, Ash Hit 2-3 L, TuTuDuDu 4-1 W, SPAARK 3-2 L, Cenomanum 2-3 L, The Defect 4-1 L, Fake Analysis 1-4 L, One More Time 3-2 L, andrew 3-2 L, Code Monkeys 3-2 W, Quwaky 4-1 W, Some People 3-2 W
Record: ~4W-8L (33% WR) -- **degradation**

**v30-v35 (09:23-13:28):**
Matches: SPAARK 3-2 W, Polska 3-2 L, KCPC-B 3-2 L, The Defect 1-4 L, Some People 4-1 W, oslsnst 2-3 L, Solo Gambling 2-3 L, Cenomanum 3-2 W, eidooheerfmaet 4-1 W, Highly Suspect 3-2 W, natto 2-3 L, Warwick 1-4 L, KCPC-B 3-2 W, Chameleon 4-1 W, Ash Hit 2-3 L, oslsnst 4-1 L, eidooheerfmaet 2-3 L, Cenomanum 2-3 L, Fake Analysis 3-2 W, 5goats 4-1 W, MEOW 3-2 L, O_O 4-1 L, natto 3-2 L, andrew 4-1 L
Record: ~10W-14L (42% WR)

**v36-v45 (13:28-present):**
Matches: ah 4-1 W, N 1-4 L, Dino 3-2 W, Ash Hit 2-3 L, double up 3-2 L, MEOW 5-0 W, Pray/Deploy 0-5 L, EEZ 4-1 W, Fake Analysis 3-2 W, eidooheerfmaet 4-1 W, Ash Hit 3-2 L, Some People 3-2 W, Chameleon 3-2 W, O_O 5-0 W, Warwick 3-2 W, MergeConflict 4-1 L, Polska 3-2 L, One More Time 4-1 L, Highly Suspect 0-5 L, The Defect 4-1 W, N 3-2 L, oslsnst 4-1 L, Quwaky 3-2 L, SPAARK 2-3 L, Dino 3-2 W, 5goats 4-1 W, Some People 4-1 W, Vibecoders 1-4 L, N 3-2 W, O_O 3-2 W, Chameleon 4-1 L, MergeConflict 4-1 L, natto 3-2 L, Polska 2-3 L, MEOW 3-2 W, oslsnst 3-2 W, The Defect 5-0 L, BulkX 3-2 W, Code Monkeys 3-2 L, Fake Analysis 4-1 W, strong vibe 3-2 W, Dino 3-2 L, natto 1-4 L, oslsnst 3-2 L, MWLP 5-0 W, MEOW 0-5 L, HAL9000 1-4 L, BulkX 4-1 W
Record: ~25W-23L (52% WR)

---

## 4. Map Analysis: Where We Lose Most

### Maps where we CONSISTENTLY LOSE (individual game W-L across all matches):

| Map | Wins | Losses | Win% | Notes |
|-----|------|--------|------|-------|
| face | 4 | 10 | 29% | **WORST MAP** - also rush-vulnerable (3 core kills) |
| galaxy | 3 | 8 | 27% | Very bad |
| landscape | 2 | 7 | 22% | Very bad |
| wasteland_oasis | 2 | 6 | 25% | Bad |
| default_large2 | 3 | 7 | 30% | Bad |
| mandelbrot | 2 | 6 | 25% | Bad |
| cubes | 3 | 5 | 38% | Below average |
| bar_chart | 3 | 5 | 38% | Below average + rush-vulnerable |
| shish_kebab | 1 | 5 | 17% | Very bad + rush-vulnerable |
| tree_of_life | 2 | 5 | 29% | Bad |
| starry_night | 1 | 4 | 20% | Bad + rush-vulnerable |
| socket | 3 | 5 | 38% | Below average |
| settlement | 1 | 3 | 25% | Bad |
| wasteland | 2 | 4 | 33% | Below average |
| hooks | 3 | 4 | 43% | Slightly below average |
| dna | 3 | 3 | 50% | Average |

### Maps where we CONSISTENTLY WIN:

| Map | Wins | Losses | Win% | Notes |
|-----|------|--------|------|-------|
| sierpinski_evil | 7 | 2 | 78% | **BEST MAP** |
| pls_buy_cucats_merch | 5 | 2 | 71% | Strong |
| tiles | 5 | 2 | 71% | Strong |
| default_small2 | 4 | 1 | 80% | Strong |
| cold | 4 | 4 | 50% | Decent |
| default_large1 | 4 | 2 | 67% | Strong |
| hourglass | 5 | 3 | 63% | Decent |
| battlebot | 4 | 3 | 57% | Decent |
| corridors | 4 | 3 | 57% | Decent |

---

## 5. The Defect Reversal Investigation

### Timeline:
1. **04:45** - The Defect 3-2 L (our v22/23 era, their bot already beating us)
2. **07:56** - The Defect 4-1 L (our v25, they beat us again)
3. **09:35** - The Defect 1-4 L (our v30/31, still losing)
4. **16:17** - The Defect 4-1 **W** (our v43/44 era, WE WIN)
5. **19:16** - The Defect 5-0 L (our v45, they crush us)

**Analysis:** The Defect beat us 3 out of 5 encounters. The one win at 16:17 was with v43 on favorable maps (hooks, default_large1, cold, corridors). Then at 19:16 with v45, they 5-0'd us on landscape, wasteland, hooks, starry_night, chemistry_class -- ALL maps where we're weak.

**Verdict:** The Defect likely did NOT dramatically update their bot. The 5-0 vs 4-1 swing is primarily explained by **map selection**. When we got favorable maps (hooks, default_large1, cold, corridors) we won. When we got unfavorable maps (landscape, wasteland, starry_night) we lost all 5. This is evidence of extreme map-dependency in our bot.

---

## 6. Nemesis Teams (most losses against)

| Team | Record | Elo Impact | Pattern |
|------|--------|------------|---------|
| oslsnst | 2W-5L | -27 | Core destroyed us repeatedly, also beats us in economy |
| The Defect | 1W-4L | -28 | Pure economy dominance except on our best maps |
| Polska Gurom | 0W-4L | -14 | Mix of rushes and economy |
| natto warriors | 0W-4L | -19 | Pure economy loss every time |
| Ash Hit | 0W-4L | -11 | Pure economy loss |
| SPAARK | 2W-4L | -15 | Pure economy loss |
| Chameleon | 2W-3L | -13 | Economy loss |
| KCPC-B | 1W-3L | -22 | Economy loss |
| Highly Suspect | 2W-2L | -6 | Volatile (4-1 win, 0-5 loss, 3-2 loss, 4-1 win) |
| HAL9000 | 0W-2L | -20 | Rush AND economy |
| MergeConflict | 0W-2L | -19 | Economy |
| One More Time | 0W-3L | -22 | Economy |

---

## 7. Root Cause Analysis

### Primary Root Cause: WEAK ECONOMY ON MOST MAP TYPES

The data is overwhelming. **~90% of individual game losses are resource/economy losses at round 2000.** We are not producing enough resources compared to competent opponents.

### Contributing Factors:

1. **Extreme map dependency:** We win consistently on only ~5-6 maps (sierpinski_evil, pls_buy_cucats_merch, tiles, default_small2, default_large1) and lose consistently on ~10+ maps. This means in a 5-game match with random maps, the odds are stacked against us.

2. **No rush defense:** When opponents rush us, we lose our core in as few as 86 rounds. Maps like `face`, `default_medium1`, `bar_chart`, and `shish_kebab` are extremely vulnerable. We lose 15 individual games to core destruction.

3. **Economy scaling issues on larger/complex maps:** We lose badly on `landscape`, `galaxy`, `wasteland_oasis`, `default_large2`, `mandelbrot` -- maps that likely require more sophisticated resource routing, bridging, or expansion strategies.

4. **Version churn without improvement:** We submitted 45 versions in one day. The per-period win rates show:
   - v1-v15: 30% WR
   - v16-v23: 53% WR (peak)
   - v24-v29: 33% WR (regression!)
   - v30-v35: 42% WR
   - v36-v45: 52% WR
   
   The v24-v29 period was the worst regression. Something broke between v23 and v24 that was never fully recovered from.

5. **No military capability:** We have zero ability to threaten opponent cores. Every single game win we have is via resource tiebreaker at round 2000. Opponents with rush capability get free wins on rush-friendly maps AND compete economically elsewhere.

---

## 8. Specific Recommended Fixes

### Priority 1: Fix economy on weak maps
- Analyze what makes us strong on sierpinski_evil/tiles/pls_buy_cucats_merch but weak on face/galaxy/landscape
- Likely issue: our resource chain building strategy doesn't adapt well to different ore placements and distances
- Focus on maps where we get 0-5'd: these represent complete economy failure

### Priority 2: Basic rush defense
- HAL9000 killed our core at round 86 (galaxy), round 95 (default_medium1)
- oslsnst killed our core at round 165, 335, 451, 667, 808
- Warwick killed us at round 137 and 190
- Need barriers/turrets on maps with nearby enemy spawn

### Priority 3: Investigate v24 regression
- v23 was uploaded at 05:03, v24 at 07:09
- The win rate dropped from 53% to 33% at this transition
- Need to diff v23 vs v24 to find what broke

### Priority 4: Map-adaptive strategy
- Our bot plays identically regardless of map geometry
- Need at minimum: detection of nearby ore, distance to enemy, and whether rush defense is needed

### Priority 5: Consider adding military capability
- We can never win by core destruction (0 such wins in 114 matches)
- Even a simple rush option on favorable maps would flip some 2-3 losses to 3-2 wins

---

## 9. Elo Loss Breakdown

Total Elo lost from losses: **approximately -380 Elo from losses**
Total Elo gained from wins: **approximately +330 Elo from wins**  
Net: **~-50 Elo**

### Biggest Elo hits (losses with highest Elo impact):
| Match | Elo Lost | Score |
|-------|----------|-------|
| MEOW 0-5 | -16.1 | 0-5 |
| The Defect 5-0 | -16.2 | 0-5 |
| KCPC-B 0-5 | -15.8 | 0-5 |
| Highly Suspect 0-5 | -15.5 | 0-5 |
| Pray and Deploy 0-5 | -15.4 | 0-5 |
| :3 1-4 | -10.2 | 1-4 |
| SPAARK 4-1 | -10.1 | 1-4 |
| HAL9000 1-4 (early) | -10.0 | 1-4 |
| One More Time 1-4 | -9.9 | 1-4 |
| Fake Analysis 1-4 | -9.9 | 1-4 |

**The 5 sweeps (0-5 losses) alone cost us ~79 Elo.** If we could convert even 2 of those to 2-3 losses instead, we'd recover ~20 Elo.

---

## 10. Summary

The Elo collapse is primarily caused by:
1. **Fundamentally weak economy** that loses to most equally-rated bots in resource production
2. **Extreme map dependency** -- we only reliably win on ~5 specific maps
3. **Zero military capability** -- no rush, no defense, no turrets
4. **Version churn** -- 45 versions in one day without systematic testing led to regressions (especially v24)

The bot needs a ground-up economy overhaul more than tactical tweaks. The fact that we can win on sierpinski_evil at 78% but lose on face at 29% suggests our resource chain building is inflexible and doesn't adapt to different map geometries.
