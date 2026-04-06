# v42 Varied Baseline Test Results

**Date:** 2026-04-06  
**Bot:** buzzing (v42)  
**Test:** 30 matches vs random opponents on random maps with random seeds  
**Previous baseline:** 45%

---

## Overall Win Rate

**14W - 16L - 0D = 47% win rate**

Slight improvement over the 45% baseline but still well below the 60% target for ladder climbing.

---

## Win Rate by Opponent

| Opponent | W | L | Win Rate |
|----------|---|---|----------|
| adaptive | 3 | 0 | 100% |
| turtle | 4 | 1 | 80% |
| fast_expand | 2 | 1 | 67% |
| ladder_rush | 1 | 0 | 100% |
| smart_eco | 2 | 2 | 50% |
| rusher | 1 | 3 | 25% |
| sentinel_spam | 1 | 4 | 20% |
| smart_defense | 0 | 2 | 0% |
| balanced | 0 | 2 | 0% |
| barrier_wall | 0 | 1 | 0% |

**Strengths:** Dominant vs adaptive, turtle, ladder_rush — passive/late-game opponents.  
**Weaknesses:** Loses badly to sentinel_spam, rusher, smart_defense, balanced — aggressive or well-rounded opponents.

---

## Win Rate by Map Type

| Map Type | W | L | Win Rate | Notes |
|----------|---|---|----------|-------|
| Tight | 2 | 8 | **20%** | Critical weakness |
| Balanced | 5 | 5 | 50% | Neutral |
| Expand | 7 | 3 | **70%** | Strong |

**Interpretation:** Buzzing is an economy bot that shines when it can spread out. Tight maps heavily favor aggressive and defensive bots. The 20% tight-map win rate is a serious liability since ladder matches span 5 maps including tight ones.

---

## Top 3 Worst Matchups to Fix

### 1. sentinel_spam (1W-4L, 20%)
**Problem:** Sentinel turrets shred builder bots before economy is online, and we have no early counter. Sentinels cover huge area (r^2=32 vision) and stun with refined Ax ammo.  
**Fix direction:** Earlier gunner placement or barrier walls to block sentinel lines of sight. Prioritize Ti spend on defense before heavy economy on maps with short distances.

### 2. rusher (1W-3L, 25%)
**Problem:** Rusher sends builder bots to our base early and attacks our buildings (2 Ti per attack). We can't respond fast enough.  
**Fix direction:** Earlier sentinel or gunner near core. Detect incoming builders via markers. Fast-build barriers around core to block rush paths.

### 3. smart_defense (0W-2L, 0%)
**Problem:** Smart_defense appears to build strong mid-game turret networks and out-economy us while defended. We don't have the offensive punch to break a turtled defense.  
**Fix direction:** Build launchers to throw our builders into their base as saboteurs, or breach turrets to crack fortified positions. Need offensive capability, not just passive economy.

---

## Key Observations

- **Tight maps are the biggest problem**: 20% win rate on tight maps vs 70% on expand maps — a 50-point gap. Since ladder match sets include tight maps, this drags us down significantly.
- **We beat passive bots convincingly**: 100% vs adaptive, 80% vs turtle — economy advantage wins long games.
- **Aggressive bots exploit our slow defense startup**: sentinel_spam + rusher + balanced together account for 9 of our 16 losses.
- **Arena map is especially bad**: 3 losses on arena specifically (sentinel_spam x2, balanced x1). Arena appears to be a tight map that heavily favors defensive turret play.

---

## Raw Results

| # | Opponent | Map | Map Type | Seed | Result |
|---|----------|-----|----------|------|--------|
| 1 | adaptive | pixel_forest | expand | 1942 | WIN |
| 2 | smart_defense | default_small2 | tight | 5141 | LOSS |
| 3 | ladder_rush | butterfly | balanced | 1478 | WIN |
| 4 | smart_eco | default_large1 | expand | 782 | WIN |
| 5 | sentinel_spam | gaussian | balanced | 7973 | LOSS |
| 6 | sentinel_spam | default_large1 | expand | 2288 | LOSS |
| 7 | fast_expand | landscape | expand | 4355 | WIN |
| 8 | turtle | butterfly | balanced | 5571 | LOSS |
| 9 | sentinel_spam | arena | tight | 2677 | LOSS |
| 10 | barrier_wall | galaxy | expand | 4964 | LOSS |
| 11 | rusher | galaxy | expand | 5784 | LOSS |
| 12 | rusher | binary_tree | balanced | 7845 | LOSS |
| 13 | fast_expand | default_small1 | tight | 600 | LOSS |
| 14 | turtle | arena | tight | 2989 | WIN |
| 15 | smart_eco | default_small1 | tight | 5071 | LOSS |
| 16 | smart_eco | default_small2 | tight | 5753 | LOSS |
| 17 | turtle | galaxy | expand | 6021 | WIN |
| 18 | sentinel_spam | arena | tight | 7036 | LOSS |
| 19 | balanced | arena | tight | 310 | LOSS |
| 20 | sentinel_spam | galaxy | expand | 3429 | WIN |
| 21 | smart_eco | default_large1 | expand | 7811 | WIN |
| 22 | adaptive | cold | balanced | 7533 | WIN |
| 23 | smart_defense | gaussian | balanced | 9182 | LOSS |
| 24 | rusher | mandelbrot | balanced | 2398 | WIN |
| 25 | rusher | face | tight | 5286 | LOSS |
| 26 | balanced | gaussian | balanced | 1326 | LOSS |
| 27 | adaptive | dna | balanced | 9055 | WIN |
| 28 | turtle | default_small2 | tight | 9640 | WIN |
| 29 | fast_expand | galaxy | expand | 8753 | WIN |
| 30 | turtle | cold | balanced | 3919 | WIN |
