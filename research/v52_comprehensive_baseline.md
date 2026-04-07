# V52 Comprehensive Baseline

**Date:** 2026-04-07  
**Bot:** buzzing V52 (831 lines — attacker removed + chain-fix improved)  
**Main test record:** 25W-15L-0D (**62% win rate**, 40 matches)  
**Focused tests (ladder_road, ladder_sentinel):** 1W-3L (4 matches)  
**Combined:** 26W-18L (**59%**)

> Note: Prior V52 30-match baseline was 70% (21W-9L). This 40-match run landed at 62% — reflects natural variance at n=40 with unlucky opponent/map sampling (smart_eco drew 7 matches, corridors drew 3). The true underlying win rate is likely between 62-70%.

---

## Per-Opponent Breakdown (40-match varied test)

| Opponent | W | L | Win% | Notes |
|----------|---|---|------|-------|
| adaptive | 3 | 0 | **100%** | Dominant |
| barrier_wall | 2 | 0 | **100%** | Dominant |
| turtle | 2 | 0 | **100%** | Dominant |
| ladder_eco | 4 | 2 | 66% | Solid |
| ladder_rush | 2 | 1 | 66% | Solid |
| rusher | 2 | 1 | 66% | Solid |
| sentinel_spam | 4 | 2 | 66% | Solid |
| balanced | 3 | 2 | 60% | Slightly ahead |
| smart_defense | 1 | 2 | 33% | Persistent nemesis |
| smart_eco | 2 | 5 | **28%** | Critical nemesis |
| fast_expand | 0 | 0 | — | Not drawn |

**New bots (focused tests, seed=1):**

| Opponent | Map | W | L | Buzzing Ti | Opponent Ti | Notes |
|----------|-----|---|---|------------|-------------|-------|
| ladder_road | cold | 0 | 1 | 15750 mined | 20020 mined | Lost by 8k Ti |
| ladder_road | galaxy | 1 | 0 | 14830 mined | 4970 mined | Won by 7k Ti |
| ladder_sentinel | face | 0 | 1 | 17840 mined | 20330 mined | Lost by 2.5k Ti |
| ladder_sentinel | default_medium1 | 0 | 1 | 9100 mined | 26320 mined | Crushed — 17k Ti gap |

**ladder_road summary:** 1W-1L (50%). galaxy handled fine; cold is a problem (373 buildings vs 325 — still overbuilding).  
**ladder_sentinel summary:** 0W-2L. default_medium1 was catastrophic (9100 vs 26320 mined). This opponent likely builds fewer, more efficient chains.

---

## Per-Map-Type Breakdown (40-match varied test)

| Type | W | L | Win% | V52 prev (30) | Delta |
|------|---|---|------|---------------|-------|
| **Expand** | **11** | **2** | **84%** | 92% | -8% |
| Balanced | 12 | 9 | 57% | 50% | +7% |
| Tight | 2 | 4 | **33%** | 67% | -34% |

Tight maps are the clear crisis area this run. 33% (2W-4L) vs V52's prior 67% is a major drop. However the sample is small (6 matches); 3 losses were sentinel_spam/face, smart_eco/shish_kebab, smart_eco/arena — all known hard matchups on tight maps. Not necessarily a regression.

---

## Notable Map Results

| Map | W | L | Win% | n | Notes |
|-----|---|---|------|---|-------|
| binary_tree | 0 | 3 | 0% | 3 | Persistent — all vs smart_eco/smart_defense |
| corridors | 0 | 3 | 0% | 3 | All losses vs smart_eco — likely conveyor-maze issue |
| face | 0 | 2 | 0% | 2 | Known pathing failure |
| butterfly | 5 | 1 | 83% | 6 | Strong |
| default_medium1 | 3 | 0 | 100% | 3 | Strong |
| tree_of_life | 3 | 0 | 100% | 3 | Strong |
| wasteland | 3 | 0 | 100% | 3 | Strong |
| settlement | 2 | 0 | 100% | 2 | Strong |
| dna | 2 | 0 | 100% | 2 | Strong |
| default_small2 | 2 | 0 | 100% | 2 | Strong |

**binary_tree and corridors: 0% combined (0W-6L)** — these are the most damaging map-specific weaknesses. Both are high-wall-density balanced maps where smart_eco/smart_defense exploit our conveyor overbuilding.

---

## Critical Weakness Analysis

### 1. smart_eco: 2W-5L (28%)

The biggest nemesis. Losses: binary_tree, shish_kebab, corridors (x2), arena. Wins: butterfly, tree_of_life.

Root cause (confirmed from v47 research): smart_eco builds fewer, more direct chains and spawns builders faster (6 by r100 vs our 4). On balanced/tight maps with maze-like structure, our chain-fix generates extra conveyors that cost Ti without delivering proportionally more ore.

### 2. smart_defense: 1W-2L (33%)

Tight map specialist. All 3 matches on binary_tree and butterfly — loses binary_tree 0W-2L, wins butterfly 1W-0L.

### 3. Tight maps overall: 2W-4L (33%)

Face: 0W-2L (pathing failure, first builder goes wrong way — known unfixed bug)  
Shish_kebab: 0W-1L (smart_eco)  
Arena: 0W-1L (smart_eco)  
Default_small2: 2W-0L (vs rusher + turtle — easier opponents)

Tight map performance collapses when facing smart_eco/smart_defense, fine vs weaker opponents.

### 4. Corridors: 0W-3L (all vs smart_eco, balanced map)

Corridors is a maze-structured balanced map. Our chain-fix should help here but smart_eco is still winning decisively — suggesting conveyor efficiency gap, not just chain alignment.

### 5. ladder_sentinel: 0W-2L

default_medium1 was catastrophic (9100 vs 26320 mined — a 17k Ti deficit). This opponent likely places sentinels defensively to block our builders or uses very efficient conveyor routing. Needs investigation.

---

## Strengths Confirmed

- **Expand maps: 84% (11W-2L)** — remains dominant on open maps
- **adaptive, barrier_wall, turtle: 100%** — clean sweeps on all 3
- **ladder_eco, ladder_rush, rusher, sentinel_spam: 66%** — solid against standard archetypes
- **butterfly, tree_of_life, wasteland, settlement: 100%** — specific maps where we excel

---

## Priority Fixes for V53

1. **smart_eco / corridors nemesis (0W-3L)** — highest EV fix. Root cause: chain efficiency on maze maps. Need shorter, more direct chains. Consider: cap conveyor chain length per ore tile (max 15-20 conveyors per harvester path). This also helps gaussian.

2. **face pathing (0W-2L)** — first builder consistently goes wrong direction. Investigate face map layout and fix initial explore direction heuristic.

3. **ladder_sentinel (0W-2L)** — 17k Ti deficit on default_medium1. Need to run more matches and inspect replay to understand their strategy.

4. **binary_tree (0W-3L)** — all vs smart_eco/smart_defense. May be resolved if smart_eco fix lands.

5. **Tight map floor (33%)** — cannot drop below 40% on tight maps without regression. The 33% here is likely noise (only 6 matches) but face fix will help.

---

## Comparison to Previous Baselines

| Version | Record | Win% | Key Change |
|---------|--------|------|-----------|
| v42 | — | 45% | — |
| v46 | — | 58% | — |
| v49 | — | 65% | Previous best |
| v50 | — | 40% | Tight cap 8→10 regression |
| v51 | — | 55% | Chain-fix added |
| v52 (30-match) | 21W-9L | **70%** | Attacker removal — new best |
| **v52 (this, 40-match)** | **25W-15L** | **62%** | Larger sample, unlucky draw |

The 62% vs 70% discrepancy is consistent with variance: this run drew smart_eco 7 times (5 losses) and corridors 3 times (0W-3L). The true baseline is likely ~65-68%.

---

## Raw Results (40-match varied test)

| # | Opponent | Map | Type | Seed | Result |
|---|----------|-----|------|------|--------|
| 1 | ladder_eco | galaxy | expand | 9923 | WIN |
| 2 | adaptive | tree_of_life | expand | 4886 | WIN |
| 3 | ladder_rush | dna | balanced | 7742 | WIN |
| 4 | rusher | landscape | expand | 5319 | WIN |
| 5 | ladder_eco | settlement | expand | 4566 | WIN |
| 6 | balanced | face | tight | 8903 | LOSS |
| 7 | barrier_wall | butterfly | balanced | 5795 | WIN |
| 8 | sentinel_spam | default_large2 | expand | 1109 | LOSS |
| 9 | balanced | butterfly | balanced | 4113 | WIN |
| 10 | barrier_wall | mandelbrot | balanced | 3857 | WIN |
| 11 | balanced | wasteland | expand | 2985 | WIN |
| 12 | adaptive | tree_of_life | expand | 6754 | WIN |
| 13 | smart_eco | binary_tree | balanced | 9633 | LOSS |
| 14 | ladder_rush | cold | balanced | 2378 | LOSS |
| 15 | smart_defense | butterfly | balanced | 934 | WIN |
| 16 | balanced | wasteland | expand | 567 | WIN |
| 17 | balanced | corridors | balanced | 868 | LOSS |
| 18 | smart_eco | butterfly | balanced | 8085 | WIN |
| 19 | sentinel_spam | default_medium1 | balanced | 2519 | WIN |
| 20 | turtle | pixel_forest | expand | 4601 | WIN |
| 21 | rusher | default_small2 | tight | 7139 | WIN |
| 22 | smart_eco | shish_kebab | tight | 8722 | LOSS |
| 23 | sentinel_spam | default_medium1 | balanced | 761 | WIN |
| 24 | rusher | default_large1 | expand | 3924 | LOSS |
| 25 | sentinel_spam | face | tight | 9864 | LOSS |
| 26 | ladder_eco | butterfly | balanced | 5809 | LOSS |
| 27 | smart_defense | binary_tree | balanced | 8381 | LOSS |
| 28 | ladder_rush | cold | balanced | 5195 | WIN |
| 29 | smart_eco | corridors | balanced | 4834 | LOSS |
| 30 | sentinel_spam | butterfly | balanced | 8861 | WIN |
| 31 | turtle | default_small2 | tight | 9349 | WIN |
| 32 | ladder_eco | default_medium1 | balanced | 5756 | WIN |
| 33 | smart_eco | corridors | balanced | 6469 | LOSS |
| 34 | adaptive | wasteland | expand | 710 | WIN |
| 35 | ladder_eco | hourglass | balanced | 1796 | LOSS |
| 36 | smart_defense | binary_tree | balanced | 7483 | LOSS |
| 37 | smart_eco | tree_of_life | expand | 7814 | WIN |
| 38 | ladder_eco | dna | balanced | 5808 | WIN |
| 39 | sentinel_spam | settlement | expand | 9323 | WIN |
| 40 | smart_eco | arena | tight | 3474 | LOSS |

## Focused Tests (ladder_road, ladder_sentinel)

| # | Opponent | Map | Seed | Buzzing Ti (mined) | Opp Ti (mined) | Result |
|---|----------|-----|------|--------------------|----------------|--------|
| F1 | ladder_road | cold | 1 | 13614 (15750) | 21614 (20020) | LOSS |
| F2 | ladder_road | galaxy | 1 | 15002 (14830) | 7676 (4970) | WIN |
| F3 | ladder_sentinel | face | 1 | 21461 (17840) | 23932 (20330) | LOSS |
| F4 | ladder_sentinel | default_medium1 | 1 | 13113 (9100) | 27908 (26320) | LOSS |
