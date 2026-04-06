# v22 Baseline Results
Date: 2026-04-04
Bot: buzzing (v22)
Seed: 1

All matches run to turn 2000 (tiebreak by Resources).

## Results Table

| Opponent | Map | Winner | Our Ti Mined | Their Ti Mined | Gap |
|---|---|---|---|---|---|
| smart_eco | default_medium1 | **buzzing** | 22,990 | 4,900 | +18,090 |
| smart_eco | cold | smart_eco | 8,440 | 32,000 | -23,560 |
| smart_eco | settlement | smart_eco | 19,590 | 41,140 | -21,550 |
| smart_eco | corridors | **buzzing** | 14,790 | 14,660 | +130 |
| smart_defense | default_medium1 | smart_defense | 4,960 | 14,650 | -9,690 |
| smart_defense | cold | smart_defense | 9,920 | 14,500 | -4,580 |
| sentinel_spam | default_medium1 | **buzzing** | 19,520 | 3,850 | +15,670 |
| balanced | default_medium1 | **buzzing** | 21,920 | 3,740 | +18,180 |

## Summary

- Record: **4W - 4L** (50%)
- Wins: vs smart_eco (default_medium1, corridors), vs sentinel_spam, vs balanced
- Losses: vs smart_eco (cold, settlement), vs smart_defense (default_medium1, cold)

## Key Observations

### Strengths
- Crushes weaker opponents (sentinel_spam, balanced) decisively — 15k-18k Ti gap
- Wins on corridors vs smart_eco by a razor margin (+130 Ti) — competitive on tight maps

### Weaknesses
- **smart_eco on open/large maps is a serious problem**: -23,560 on cold, -21,550 on settlement
  - smart_eco mines 32k-41k Ti vs our 8-19k — nearly double
  - We are likely building too many non-economic structures on these maps
- **smart_defense beats us on all tested maps**: we mine only ~5-10k vs their 14-15k
  - We are being economically outpaced even on default_medium1

### Target for v23+
Every future version must beat the following benchmarks:
- vs smart_eco default_medium1: >22,990 Ti mined (currently winning, maintain)
- vs smart_eco cold: >8,440 Ti mined (currently losing badly)
- vs smart_eco settlement: >19,590 Ti mined (currently losing badly)
- vs smart_eco corridors: >14,790 Ti mined (winning by slim margin)
- vs smart_defense default_medium1: >4,960 Ti mined (currently losing)
- vs smart_defense cold: >9,920 Ti mined (currently losing)
- vs sentinel_spam default_medium1: >19,520 Ti mined (winning, maintain)
- vs balanced default_medium1: >21,920 Ti mined (winning, maintain)
