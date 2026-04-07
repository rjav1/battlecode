# V53 git_branches Fix

**Date:** 2026-04-06
**Change:** Expand explore rotation `rnd//200` → `rnd//100` (line 533 in `_explore`)

## Regression Result

**PASS** (4W-1L — face map loss is pre-existing)

| Map | Result | Our Ti | Their Ti |
|-----|--------|--------|----------|
| default_medium1 | WIN | 4960 | 4940 |
| cold | WIN | 19610 | 0 |
| face | LOSS | 8600 | 11710 |
| settlement | WIN | 31110 | 0 |
| galaxy | WIN | 14170 | 4950 |

## git_branches Results After Fix

| Seed | buzzing Ti (mined) | starter Ti (mined) | Winner |
|------|--------------------|--------------------|--------|
| 137 | 6631 (4810) | 3400 (0) | buzzing ✓ |
| 999 | 4436 (4820) | 4171 (0) | buzzing ✓ |
| 256 | 1723 (0) | 3520 (0) | starter |
| 500 | 570 (0) | 4711 (0) | starter |

**Partial improvement**: some seeds now mine Ti and win, others still show 0.

## Root Cause Analysis

The rotation fix (2× faster) helps when the initial sector direction happens to point into a branch corridor, but doesn't solve the structural problem:

- **`reach = max(w,h) = 50`**: Builders target the far map edge from core
- git_branches has ore inside wall-enclosed branch corridors
- BFS routes builders around walls toward the edge target, bypassing interior branch entrances
- Seeds where core is near a branch entrance → ore found (fixed)
- Seeds where core is far from any branch entrance → builders reach the edge with no ore seen

## Stronger Fix Needed (not implemented)

Reduce `reach` from `max(w,h)` to `min(w,h)//2` or `15` on expand maps, so builders explore the map interior rather than targeting the extreme edge. This would require testing on all expand maps to ensure galaxy/settlement/cubes don't regress.

## Other Broken Expand Maps Found

`wasteland` (40x40) also mines 0 Ti on tested seeds — same structural issue.

## Decision

Deploy this partial fix (regression PASS, improves some git_branches seeds). The reach-reduction fix is a separate task requiring broader expand map testing.
