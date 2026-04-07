# Regression Test Results

**Date:** 2026-04-06 20:35:13
**Bot:** buzzing
**Duration:** 206s
**Verdict:** PASS

## Summary

| Suite | Result | Details |
|-------|--------|---------|
| Core Regression | PASS | 5/5 vs buzzing_prev |
| Opponent Gauntlet | MET | 9/14 (64%) |
| Self-Play | PASS | No crash |

## Core Regression: buzzing vs buzzing_prev

| Map | Result | Condition | Turns | Our Ti | Their Ti | Our Ax | Their Ax |
|-----|--------|-----------|-------|--------|----------|--------|----------|
| default_medium1 | WIN | resources | 2000 | 4960 | 4940 | 0 | 0 |
| cold | WIN | resources | 2000 | 19670 | 0 | 0 | 0 |
| face | WIN | resources | 2000 | 4970 | 4950 | 0 | 0 |
| settlement | WIN | resources | 2000 | 27440 | 0 | 0 | 0 |
| galaxy | WIN | resources | 2000 | 16080 | 4970 | 0 | 0 |

## Opponent Gauntlet

| Opponent | Map | Result | Condition | Turns | Our Ti | Their Ti |
|----------|-----|--------|-----------|-------|--------|----------|
| balanced | cold | LOSS | resources | 2000 | 19670 | 22100 |
| balanced | galaxy | LOSS | resources | 2000 | 3530 | 9920 |
| barrier_wall | face | LOSS | resources | 2000 | 8010 | 16310 |
| barrier_wall | settlement | WIN | resources | 2000 | 29170 | 21290 |
| sentinel_spam | default_medium1 | WIN | resources | 2000 | 24040 | 18620 |
| sentinel_spam | cold | LOSS | resources | 2000 | 18860 | 23520 |
| rusher | face | LOSS | resources | 2000 | 530 | 9930 |
| rusher | default_medium1 | WIN | resources | 2000 | 200 | 0 |
| ladder_eco | galaxy | WIN | resources | 2000 | 9940 | 9940 |
| ladder_eco | settlement | WIN | resources | 2000 | 31970 | 1190 |
| ladder_rush | cold | WIN | resources | 2000 | 1860 | 1070 |
| ladder_rush | face | WIN | resources | 2000 | 5430 | 4970 |
| ladder_bridge | settlement | WIN | resources | 2000 | 29320 | 0 |
| ladder_bridge | galaxy | WIN | resources | 2000 | 13680 | 9910 |

## Self-Play Stability

- **Result:** OK (resources, turn 2000)
- **A Ti:** 9840, **B Ti:** 9380
