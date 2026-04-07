# V60 vs Latest Eco-Debug Bots

**Date:** 2026-04-06  
**Bot:** buzzing V60  
**Purpose:** Test buzzing against eco-debugger's two new bots (ladder_oslsnst, ladder_passive) to help diagnose economy issues

---

## Results Summary

| Match | Opponent | Map | Result | Buzzing Ti (mined) | Opponent Ti (mined) | Buzzing Bldg | Opp Bldg |
|-------|----------|-----|--------|--------------------|---------------------|--------------|----------|
| 1 | ladder_oslsnst | default_medium1 | WIN | 9213 (12650) | 5230 (0) | 492 | 1 |
| 2 | ladder_oslsnst | galaxy | WIN | 16884 (17410) | 5226 (0) | 298 | 2 |
| 3 | ladder_oslsnst | cold | WIN | 1475 (15080) | 5230 (0) | 247 | 1 |
| 4 | ladder_passive | default_medium1 | WIN | 21605 (23000) | 5434 (0) | 292 | 1 |
| 5 | ladder_passive | galaxy | WIN | 11477 (14200) | 4624 (4950) | 396 | 27 |
| 6 | ladder_passive | cold | WIN | 12272 (19670) | 5114 (0) | 630 | 3 |

**Record: 6W-0L (100%)**

---

## Bot Analysis

### ladder_oslsnst
- **Behavior:** Completely non-functional. Mines 0 Ti across all 3 maps. Builds only 1-2 buildings (just the core + 1 attempt).
- **Status:** Bot code appears incomplete or broken — no builder logic executing at all.
- **Not a valid baseline opponent.**

### ladder_passive
- **Behavior:** Mixed. Outputs debug log lines showing builder position tracking but largely non-functional.
  - galaxy: **4950 Ti mined, 27 buildings** — partial functionality. Had an `AttributeError: 'Player' object has no attribute 'explore_dir'` (did you mean `explore_idx`?) suggesting a variable rename bug. Still mined ~4950 Ti despite the error.
  - cold/default_medium1: 0 Ti mined, 1-3 buildings — more broken.
- **AttributeError details:** `'Player' object has no attribute 'explore_dir'. Did you mean: 'explore_idx'?` — this fires but the match continues (error caught internally). Variable `explore_dir` was renamed to `explore_idx` in the code but not all references were updated.
- **Not a valid baseline opponent in current state.**

---

## Eco Comparison: Buzzing Performance

| Map | Buzzing Ti Mined | Notes |
|-----|-----------------|-------|
| default_medium1 | 12650–23000 | Balanced map, strong performance |
| galaxy | 14200–17410 | Expand map, strong |
| cold | 15080–19670 | Balanced map, very strong |

These numbers are consistent with buzzing's known baseline (~61-65% win rate). No unexpected behavior on buzzing's side.

---

## Key Finding for Eco-Debugger

**ladder_passive has a bug:** `explore_dir` attribute referenced but not found — likely renamed to `explore_idx` elsewhere in the code. Fix: search for all uses of `explore_dir` in `bots/ladder_passive/main.py` and update to `explore_idx` (or vice versa).

On galaxy (only map where ladder_passive partially worked), it achieved 4950 Ti mined with 27 buildings — same ballpark as buzzing_prev's 4950 Ti on galaxy in previous tests. This suggests the underlying eco logic may be correct once the attribute error is fixed.

**ladder_oslsnst** has a deeper issue — 0 buildings beyond core across all maps suggests the core isn't spawning builders or builders aren't executing any logic.
