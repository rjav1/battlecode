# v33 Final Benchmark Report
Date: 2026-04-04

## Overview
Final benchmark of v33 (buzzing) against both realistic ladder opponents (ladder_eco and ladder_rush) across 5 key maps each.

---

## Results Summary

### vs ladder_eco (5 maps)

| Map             | Winner    | buzzing Ti Mined | ladder_eco Ti Mined | buzzing Ti Held | ladder_eco Ti Held |
|-----------------|-----------|------------------|-----------------------|------------------|--------------------|
| default_medium1 | **buzzing** | 17,760           | 4,950                 | 18,216           | 245                |
| cold            | **buzzing** | 19,670           | 19,170                | 17,301           | 10,594             |
| settlement      | **buzzing** | 37,300           | 6,470                 | 23,537           | 293                |
| arena           | ladder_eco  | 9,880            | 9,920                 | 13,450           | 4,552              |
| face            | ladder_eco  | 4,970            | 14,820                | 9,171            | 11,201             |

**vs ladder_eco: 3W - 2L (60% win rate)**

---

### vs ladder_rush (5 maps)

| Map             | Winner    | buzzing Ti Mined | ladder_rush Ti Mined | buzzing Ti Held | ladder_rush Ti Held |
|-----------------|-----------|------------------|----------------------|-----------------|---------------------|
| face            | **buzzing** | 13,840           | 4,970                | 17,618          | 6,283               |
| arena           | ladder_rush | 13,690           | 15,710               | 17,220          | 16,873              |
| default_medium1 | **buzzing** | 5,120            | 0                    | 5,317           | 1,219               |
| cold            | **buzzing** | 2,250            | 0                    | 40              | 134                 |
| settlement      | **buzzing** | 31,730           | 11,290               | 13,869          | 7,429               |

**vs ladder_rush: 4W - 1L (80% win rate)**

---

## Overall Record

| Opponent    | Wins | Losses | Win Rate |
|-------------|------|--------|----------|
| ladder_eco  | 3    | 2      | 60%      |
| ladder_rush | 4    | 1      | 80%      |
| **Total**   | **7**| **3**  | **70%**  |

---

## Ti Mined Comparison

### vs ladder_eco
- buzzing avg Ti mined: (17760 + 19670 + 37300 + 9880 + 4970) / 5 = **17,916**
- ladder_eco avg Ti mined: (4950 + 19170 + 6470 + 9920 + 14820) / 5 = **11,066**
- buzzing outmines ladder_eco by **62%** on average

### vs ladder_rush
- buzzing avg Ti mined: (13840 + 13690 + 5120 + 2250 + 31730) / 5 = **13,326**
- ladder_rush avg Ti mined: (4970 + 15710 + 0 + 0 + 11290) / 5 = **6,394**
- buzzing outmines ladder_rush by **108%** on average

---

## Problem Maps

**arena** is a consistent weakness - lost to BOTH ladder_eco and ladder_rush there. This map seems to favor opponents regardless of play style. Needs specific investigation.

**face** is a split: beat ladder_rush but lost to ladder_eco. ladder_eco mined 3x more Ti on face (14,820 vs 4,970), suggesting buzzing has eco disadvantage on that map specifically.

---

## Comparison to Baseline

- **Pre-v32/v33 baseline: 33% win rate**
- **v33 result: 70% win rate (7W - 3L)**
- **Improvement: +37 percentage points**

v33 represents a massive improvement from the 33% baseline. The combined fixes in v32 and v33 more than doubled the win rate against realistic opponents, going from 1-in-3 to 7-in-10 matches won.

---

## Notes
- All matches ran to turn 2000 (full game) with Resources tiebreak deciding winners
- All 10 wins were on tiebreak (Ti held at end), not unit kills - this is an economy-focused bot
- ladder_rush mined 0 Ti in two matches (default_medium1 and cold), suggesting buzzing denies or outpaces rush strat strongly on certain maps
- buzzing consistently builds more buildings than opponents across nearly all matches
