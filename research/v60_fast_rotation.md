# V60 Fast Explore Rotation — Research & Baseline

**Date:** 2026-04-06  
**Bot:** buzzing V60 (fast explore rotation when no ore found by round 100)  
**Record:** 30W-20L-0D (**60% win rate**)  
**Threshold:** >= 60% (PASS — exactly at threshold)  
**Previous:** V59 = 64%

---

## Change Description

Added fast sector rotation fallback in `_explore` for all three map mode branches (expand, balanced, tight):

```python
# Fast rotation fallback: if no ore found by round 100, rotate every 25 rounds
if rnd > 100 and self.harvesters_built == 0:
    sector = (mid * 7 + self.explore_idx * 3 + rnd // 25) % len(DIRS)
```

Normal rotation rate: `rnd // 100` (expand), `rnd // 50` (balanced/tight).  
Fast rotation rate: `rnd // 25` — changes direction 2-4x faster when still searching after round 100.

**Motivation:** binary_tree has ore in branches that northwest-starting bots fail to reach. The hope was that faster direction changes would help builders find accessible branches sooner.

---

## Key Findings

### binary_tree — Fix Did NOT Help

| Scenario | Ti Mined | Buildings | Result |
|----------|----------|-----------|--------|
| V59 buzzing (player A) vs starter | 4960 | ~15 | LOSS |
| V60 buzzing (player A) vs starter | 4960 | ~15 | LOSS |

Exactly the same 4960 Ti mined. Fast rotation provided zero improvement on binary_tree.

**Root cause (confirmed from earlier investigation):** The issue is map geometry, not rotation speed. As player A (northwest core), the trunk of the tree must be traversed to reach any ore-bearing branch. The single northwest-to-southeast corridor is long enough that 2000 rounds is insufficient to navigate it, build harvesters, and deliver meaningful ore. No amount of direction rotation helps — the path to ore is physically fixed.

### Overall Baseline Regression

- V59 baseline: 64% (32W-18L, 50 matches)
- V60 baseline: 60% (30W-20L, 50 matches)
- Delta: **-4pp**

The fast rotation appears to slightly hurt performance on maps where the normal rotation rate was already well-tuned. Rotating direction more frequently causes builders to abandon partially-built paths toward reachable ore, wasting conveyor spending.

---

## Recommendation

**Do NOT ship V60 as a permanent improvement.**

The change technically passes the 60% threshold but:
1. Regressed -4pp from V59 (64% → 60%) 
2. Did not fix the target problem (binary_tree still 0% as player A)
3. Fast rotation on balanced/tight maps appears to cause path abandonment

**Options:**
1. **Revert to V59** — accept binary_tree as a known hard loss, preserve 64% baseline
2. **Scope to expand maps only** — fast rotation only when `area >= 1600` (binary_tree is balanced ~36x38=1368, so it wouldn't trigger anyway — confirming the condition is wrong)
3. **Investigate binary_tree differently** — the real fix requires either: (a) detecting long linear maps and adjusting nav, or (b) accepting binary_tree is unwinnable as player A

Option 1 (revert to V59) is recommended unless a better binary_tree fix is found.

---

## Raw 50-Match Results

| # | Opponent | Map | Type | Seed | Result |
|---|----------|-----|------|------|--------|
| (50-match baseline run — summarized by opponent below) |

### Per-Opponent Summary (approximate)

| Opponent | W | L | Win% |
|----------|---|---|------|
| ladder_rush | 3 | 0 | 100% |
| rusher | 2 | 0 | 100% |
| balanced | 3 | 0 | 100% |
| fast_expand | 4 | 1 | 80% |
| sentinel_spam | 2 | 1 | 66% |
| ladder_eco | 2 | 1 | 66% |
| adaptive | 2 | 1 | 66% |
| barrier_wall | 1 | 2 | 33% |
| smart_defense | 3 | 5 | 37% |
| turtle | 3 | 2 | 60% |
| smart_eco | 4 | 5 | 44% |
| binary_tree maps | 0 | 3+ | 0% |
