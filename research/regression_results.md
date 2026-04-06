# Regression Test Results

**Date:** 2026-04-06 19:00:16
**Bot:** buzzing
**Duration:** 56s
**Verdict:** FAIL

## Summary

| Suite | Result | Details |
|-------|--------|---------|
| Core Regression | FAIL | 2/5 vs buzzing_prev |
| Opponent Gauntlet | MET | 0/0 (0%) |
| Self-Play | PASS | No crash |

## Core Regression: buzzing vs buzzing_prev

| Map | Result | Condition | Turns | Our Ti | Their Ti | Our Ax | Their Ax |
|-----|--------|-----------|-------|--------|----------|--------|----------|
| default_medium1 | LOSS | resources | 2000 | 4960 | 9760 | 0 | 0 |
| cold | LOSS | resources | 2000 | 19670 | 19700 | 0 | 0 |
| face | LOSS | resources | 2000 | 9790 | 9920 | 0 | 0 |
| settlement | WIN | resources | 2000 | 37390 | 9760 | 0 | 0 |
| galaxy | WIN | resources | 2000 | 13660 | 9940 | 0 | 0 |

## Self-Play Stability

- **Result:** OK (resources, turn 2000)
- **A Ti:** 9840, **B Ti:** 9380
