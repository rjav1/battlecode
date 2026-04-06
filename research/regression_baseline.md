# Regression Test Results

**Date:** 2026-04-06 17:20:16
**Bot:** buzzing
**Duration:** 152s
**Verdict:** PASS

## Summary

| Suite | Result | Details |
|-------|--------|---------|
| Core Regression | PASS | 4/5 vs buzzing_prev |
| Opponent Gauntlet | MET | 9/14 (64%) |
| Self-Play | PASS | No crash |

## Core Regression: buzzing vs buzzing_prev

| Map | Result | Condition | Turns | Our Ti | Their Ti | Our Ax | Their Ax |
|-----|--------|-----------|-------|--------|----------|--------|----------|
| default_medium1 | WIN | resources | 2000 | 9790 | 4950 | 0 | 0 |
| cold | LOSS | resources | 2000 | 19670 | 19700 | 0 | 0 |
| face | WIN | resources | 2000 | 18590 | 9910 | 0 | 0 |
| settlement | WIN | resources | 2000 | 27740 | 9480 | 0 | 0 |
| galaxy | WIN | resources | 2000 | 13670 | 9940 | 0 | 0 |

## Opponent Gauntlet

| Opponent | Map | Result | Condition | Turns | Our Ti | Their Ti |
|----------|-----|--------|-----------|-------|--------|----------|
| balanced | cold | LOSS | resources | 2000 | 19670 | 21560 |
| balanced | galaxy | LOSS | resources | 2000 | 3530 | 9920 |
| barrier_wall | face | LOSS | resources | 2000 | 11010 | 20060 |
| barrier_wall | settlement | WIN | resources | 2000 | 29320 | 21290 |
| sentinel_spam | default_medium1 | WIN | resources | 2000 | 23070 | 18620 |
| sentinel_spam | cold | LOSS | resources | 2000 | 19220 | 27640 |
| rusher | face | LOSS | resources | 2000 | 510 | 9930 |
| rusher | default_medium1 | WIN | resources | 2000 | 0 | 0 |
| ladder_eco | galaxy | WIN | resources | 2000 | 9940 | 9920 |
| ladder_eco | settlement | WIN | resources | 2000 | 38010 | 0 |
| ladder_rush | cold | WIN | resources | 2000 | 2270 | 0 |
| ladder_rush | face | WIN | resources | 2000 | 13780 | 4980 |
| ladder_bridge | settlement | WIN | resources | 2000 | 28060 | 0 |
| ladder_bridge | galaxy | WIN | resources | 2000 | 13680 | 9910 |

## Self-Play Stability

- **Result:** OK (resources, turn 2000)
- **A Ti:** 9780, **B Ti:** 4950
