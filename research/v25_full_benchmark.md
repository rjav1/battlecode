# v25 Full Benchmark Results
Date: 2026-04-04
Bot: buzzing (v25)
Opponent: smart_eco
Seed: 1

All matches run to turn 2000 (tiebreak by Resources).

## Results Table

| Map | Winner | Our Ti Mined | Their Ti Mined | Gap |
|---|---|---|---|---|
| default_medium1 | **buzzing** | 18,770 | 4,900 | +13,870 |
| cold | **buzzing** | 17,230 | 14,340 | +2,890 |
| settlement | **buzzing** | 34,100 | 19,170 | +14,930 |
| corridors | **buzzing** | 14,790 | 14,660 | +130 |
| face | smart_eco | 14,560 | 17,710 | -3,150 |
| arena | smart_eco | 9,890 | 34,020 | -24,130 |
| hourglass | **buzzing** | 24,460 | 24,370 | +90 |
| galaxy | **buzzing** | 14,650 | 9,930 | +4,720 |
| shish_kebab | **buzzing** | 14,540 | 9,840 | +4,700 |
| butterfly | smart_eco | 24,870 | 34,810 | -9,940 |

## Overall Record

**7W - 3L (70%)**

## Map Rankings

### Best Maps (largest positive Ti gap)
1. settlement: +14,930 Ti gap — dominant, nearly 2x their output
2. default_medium1: +13,870 Ti gap — consistent top performer
3. galaxy: +4,720 Ti gap — solid win on large open map
4. shish_kebab: +4,700 Ti gap — good control of tight corridor map

### Worst Maps (losses / narrowest margins)
1. arena: -24,130 Ti gap — **critical weakness**, mined only 9,890 vs their 34,020 (3.4x deficit)
2. butterfly: -9,940 Ti gap — significant loss, large open map disadvantage
3. face: -3,150 Ti gap — moderate loss
4. corridors: +130 Ti gap — barely won, essentially a toss-up
5. hourglass: +90 Ti gap — extremely narrow win, almost a loss

## Average Ti Gap

| Metric | Value |
|---|---|
| Wins average gap | +5,904 Ti |
| Losses average gap | -12,407 Ti |
| Overall average gap | +879 Ti |

## Key Findings

### Cold Map Fixed (v25 Success)
- v24: cold was a **loss** at -3,950 gap
- v25: cold is now a **win** at +2,890 gap
- Primary objective of v25 achieved

### Critical Weakness: arena
- Our worst result by far: 9,890 vs their 34,020 Ti mined
- We mine only 29% of what they mine on this map
- arena appears to be a large open map where their eco strategy vastly outperforms ours
- Gap is 3x worse than second-worst loss (butterfly)
- **Priority target for v26**

### Secondary Weakness: butterfly
- Lost -9,940 Ti gap; we mined 24,870 vs their 34,810
- Both are large Ti-rich maps where we underperform
- Likely same root cause as arena: open-map exploration/expansion deficit

### Near-Losses: corridors and hourglass
- corridors: +130 gap — essentially a coin flip, any variance could flip this
- hourglass: +90 gap — same concern, nearly identical Ti mined (24,460 vs 24,370)
- Both tight wins suggest our strategy is marginal on these map types

### Stable Wins: settlement, default_medium1, galaxy, shish_kebab
- These maps are reliably won with comfortable margins
- No changes needed

## v24 vs v25 Comparison (overlapping maps)

| Map | v24 Gap | v25 Gap | Change |
|---|---|---|---|
| cold | -3,950 | +2,890 | **+6,840** (flipped!) |
| settlement | +18,090 | +14,930 | -3,160 (still winning) |
| default_medium1 | +13,870 | +13,870 | 0 (stable) |

## Recommendations for v26

1. **arena** (top priority): Investigate why their eco output is 3.4x ours. Likely open-map builder deployment or Ti node coverage issue.
2. **butterfly**: Related to arena — large open map performance. Fix arena strategy should transfer.
3. **corridors/hourglass hardening**: Both are razor-thin wins. Marginal improvements could solidify these.
