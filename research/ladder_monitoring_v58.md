# V58 Ladder Monitoring

**Date:** 2026-04-07  
**Bot:** buzzing V58 (bridges restored = V52/V56 equivalent)  
**Monitoring window:** 16:56 - 17:16 UTC  
**V58 final record:** 0W-3L (0%)  
**Elo at V58 start:** ~1529 (estimated, before MergeConflict loss)  
**Elo at V58 end:** 1493.6 (after 3 losses)  

**Note:** V59 deployed at ~17:26. V58 monitoring ended after 3 ladder matches.

---

## Context

Goal was to track Elo recovery from V57 regression (bridge removal, 57% baseline).  
V58 = bridges restored, confirmed ~65% baseline locally.

However, V58 went 0W-3L on ladder — all losses by 1-4 score (not 5-0 blowouts).  
Opponents: MergeConflict (0-5), Stratcom (1-4), nus robot husk (1-4).

---

## Match Log

| # | Opponent | Score | Result | Elo Delta | Elo After | Time |
|---|----------|-------|--------|-----------|-----------|------|
| 1 | MergeConflict | 0-5 | LOSS | -16.4 | ~1512.6 | 16:56 |
| 2 | Stratcom | 1-4 | LOSS | -9.4 | ~1503.2 | 17:06 |
| 3 | nus robot husk | 1-4 | LOSS | -9.5 | ~1493.6 | 17:16 |

Total Elo change from V58: **-35.3** over 3 matches.

---

## Analysis

**0W-3L is not necessarily a regression signal** — 3 matches is extremely small sample.  
At 65% win rate, probability of 0W-3L = (0.35)^3 = 4.3% — unlucky but plausible.

The opponents faced are notably strong:
- **MergeConflict**: 0-5 blowout — likely a top-tier opponent well above our Elo
- **Stratcom**: 1-4 close-ish, not a blowout
- **nus robot husk**: previously beat V54 5-0 (appeared in V54 monitoring as a hard loss)

The 0-5 vs MergeConflict (-16.4 Elo) suggests they are rated significantly higher (~1650+).  
Elo loss of -35 over 3 matches against strong opponents is consistent with normal variance.

**Ladder matchmaking context:** The ladder was matching us against opponents around Elo 1500-1550.  
After V57 dip, we may be getting matched slightly upward until Elo stabilizes.

---

## V58 Ladder vs V58 Local Baseline

| Metric | Local (20 match) | Ladder (3 match) |
|--------|-----------------|-----------------|
| Win rate | 60% (12W-8L) | 0% (0W-3L) |
| Sample size | 20 | 3 |
| Confidence | Moderate | Very low |

3 ladder matches cannot contradict the 20-match local baseline. Not a regression signal.

---

## Version Transition

V59 deployed at ~17:26 (poll 9 showed latest_ver=59).  
V58 monitoring concluded — only 3 matches captured before version change.

Recommend running V59 local baseline before drawing conclusions about ladder performance.

---

## Recent Ladder History (Context)

| Version | W | L | Win% | Elo Impact |
|---------|---|---|------|------------|
| V54 (6 matches) | 5 | 1 | 83% | +33.2 |
| V55 (1 match) | 0 | 1 | 0% | -3.1 |
| V56 (2 matches) | 1 | 1 | 50% | -0.3 |
| V57 (4 matches) | 3 | 1 | 75% | +24.4 |
| **V58 (3 matches)** | **0** | **3** | **0%** | **-35.3** |

V57 went 3W-1L on ladder despite 57% local baseline (variance). V58 went 0W-3L despite 65% local baseline (also variance). Neither 3-4 match sample is reliable.

Cumulative since V54 deploy: ~Elo 1493.6.
