# Comprehensive Baseline Report
**Date:** 2026-04-06  
**Bot:** buzzing  
**Test:** 50-match randomized + 7 focused matches against new ladder bots

---

## Overall Win Rate (50-match randomized)

**33W - 17L - 0D = 66% win rate**

### 95% Confidence Interval
Using Wilson score interval for n=50, k=33, p=0.66:
- Lower bound: ~52%
- Upper bound: ~78%
- **Point estimate: 66% ± 13pp** (we can say with 95% confidence win rate is above 52%)

Status: **Borderline for climbing** — 60% target met, but confidence interval touches 52%. Need more matches or improvements to solidify.

---

## Breakdown by Opponent

| Opponent | W | L | Win% | Notes |
|----------|---|---|------|-------|
| ladder_eco | 3 | 0 | 100% | Strong matchup |
| smart_defense | 2 | 0 | 100% | Strong matchup |
| barrier_wall | 4 | 1 | 80% | Good, 1 loss on cold |
| fast_expand | 2 | 0 | 100% | Strong matchup |
| turtle | 2 | 0 | 100% | Strong matchup |
| sentinel_spam | 3 | 1 | 75% | Mostly good |
| adaptive | 3 | 2 | 60% | Even matchup |
| balanced | 2 | 3 | 40% | PROBLEMATIC |
| smart_eco | 4 | 3 | 57% | Inconsistent |
| ladder_rush | 2 | 3 | 40% | PROBLEMATIC |
| rusher | 2 | 4 | 33% | WORST MATCHUP |

---

## Breakdown by Map Type

| Map Category | W | L | Win% |
|-------------|---|---|------|
| Tight (face, arena, shish_kebab, small1, small2) | 5 | 3 | 62.5% |
| Balanced (medium, cold, corridors, hourglass, dna, gaussian, mandelbrot, binary_tree, butterfly) | 13 | 6 | 68% |
| Expand (galaxy, settlement, landscape, wasteland, tree_of_life, large1, large2, pixel_forest) | 15 | 8 | 65% |

Map type has limited discriminating power — losing spread across all categories.

---

## Breakdown by Map Size

| Map Size | W | L | Win% |
|---------|---|---|------|
| Small (face, small1, small2, shish_kebab, arena) | 5 | 3 | 62.5% |
| Medium (cold, corridors, dna, mandelbrot, gaussian, binary_tree, default_medium1) | 11 | 5 | 68.8% |
| Large (large1, large2, galaxy, settlement, landscape, wasteland, tree_of_life, pixel_forest) | 17 | 9 | 65.4% |

Medium maps slightly favor buzzing. Small maps are worst (62.5%) — likely due to limited expansion room.

---

## Top 5 Worst Matchups

### 1. rusher — 2W/4L (33% win rate)
- **Maps lost:** default_large1, gaussian, dna, binary_tree
- **Pattern:** rusher attacks early before economy is established; buzzing's harvesters get disrupted
- **Priority fix:** Improve early defense, detect incoming rusher earlier

### 2. ladder_rush — 2W/3L (40% win rate)
- **Maps lost:** default_large1 (×2), default_medium1
- **Pattern:** Similar to rusher — aggressive early pressure overwhelms economy setup
- **Priority fix:** Same as rusher — early rush detection

### 3. balanced — 2W/3L (40% win rate)
- **Maps lost:** face, default_small1, tree_of_life
- **Pattern:** Consistent, well-rounded opponent beats buzzing on both tight and large maps; buzzing's strategy is not uniformly better
- **Priority fix:** Review what balanced does differently on small and large maps

### 4. adaptive — 3W/2L (60% — marginal)
- **Maps lost:** gaussian, cold
- **Pattern:** Inconsistent — buzzing wins big maps but loses open medium maps
- **Priority fix:** Open map efficiency

### 5. smart_eco — 4W/3L (57% — marginal)
- **Maps lost:** pixel_forest, galaxy, wasteland
- **Pattern:** Losses concentrated on large maps and pixel_forest
- **Priority fix:** Large-map expansion speed

---

## Focused Tests: New Ladder Bots

### vs ladder_bridge
| Map | Result | Buzzing Ti | Opponent Ti | Notes |
|-----|--------|-----------|-------------|-------|
| cold | LOSS | 11078 | 17763 | Large Ti gap — opponent had 20 units vs our 8 |
| galaxy | WIN | 9083 | 10275 | Narrow win despite fewer buildings |
| settlement | WIN | 15358 | 55 | Dominant — opponent nearly collapsed |

**ladder_bridge record: 1W-2L (33%)**  
Critical issue on cold: 8 units vs 20 — severe unit count gap suggests a build order issue or builder bot dying early.

### vs ladder_dual
| Map | Result | Buzzing Ti | Opponent Ti | Notes |
|-----|--------|-----------|-------------|-------|
| face | LOSS | 7140 | 9865 | Outbuilt on tight map |
| arena | LOSS | 4339 | 17018 | Crushed — massive 4x Ti gap |

**ladder_dual record: 0W-2L (0%)**  
Arena loss is alarming: 4339 vs 17018 Ti. ladder_dual exploits tight maps with superior building density or economy. This is a serious concern for competitive ladder play since many tournament maps are tight.

### vs ladder_mega_eco
| Map | Result | Buzzing Ti | Opponent Ti | Notes |
|-----|--------|-----------|-------------|-------|
| default_medium1 | WIN | 6234 | 89 | Crushed — opponent went bankrupt |
| galaxy | WIN | 11021 | 272 | Crushed — opponent went bankrupt |

**ladder_mega_eco record: 2W-0L (100%)**  
ladder_mega_eco appears to be a "too greedy" bot that runs out of resources — buzzing beats it easily on both tests.

---

## Overall Focused Test Summary

| Opponent | Result | Record |
|----------|--------|--------|
| ladder_bridge | Mixed | 2W-1L |
| ladder_dual | Bad | 0W-2L |
| ladder_mega_eco | Good | 2W-0L |

---

## Key Findings

1. **66% overall win rate against internal test suite** — meets 60% threshold but with wide CI
2. **rusher and ladder_rush are the biggest weaknesses** — rush defense is the #1 priority improvement
3. **ladder_dual is a serious threat** — 0-2 with huge Ti gaps suggests systematic vulnerability to tight-map economic bots
4. **balanced bot beats us 60% of the time** — need to understand what it does better
5. **buzzing dominates passive/greedy bots** (ladder_eco, turtle, ladder_mega_eco, fast_expand) — core economy is solid
6. **Unit count disparity** — multiple losses show 8 units vs 12-20 opponent; builder bot efficiency needs investigation

---

## Priority Action Items

| Priority | Issue | Impact |
|----------|-------|--------|
| HIGH | Rush defense (rusher/ladder_rush 33-40% WR) | +5-8pp overall |
| HIGH | Tight map performance (ladder_dual 0%) | Critical for tournament |
| MEDIUM | Large map expansion (smart_eco losses on large maps) | +3-5pp overall |
| LOW | balanced matchup analysis | +3pp overall |

---

## Statistical Note

50 matches gives us power to detect ~15pp differences at 95% confidence. The 66% win rate vs internal bots is encouraging but:
- Internal bots may not represent true competitive ladder strength
- ladder_dual being 0-2 is a significant red flag
- Need real ladder matches (test-run submissions) for true calibration
