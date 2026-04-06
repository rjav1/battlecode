# v24 Benchmark Results
Date: 2026-04-04
Bot: buzzing (v24)
Seed: 1

All matches run to turn 2000 (tiebreak by Resources).

## Results Table

| Opponent | Map | Winner | Our Ti Mined | Their Ti Mined | Gap |
|---|---|---|---|---|---|
| smart_eco | settlement | **buzzing** | 37,290 | 19,200 | +18,090 |
| smart_eco | cold | smart_eco | 10,510 | 14,460 | -3,950 |
| smart_eco | default_medium1 | **buzzing** | 18,770 | 4,900 | +13,870 |
| smart_defense | default_medium1 | **buzzing** | 18,890 | 14,650 | +4,240 |
| sentinel_spam | default_medium1 | **buzzing** | 33,140 | 3,010 | +30,130 |
| balanced | default_medium1 | **buzzing** | 22,120 | 4,520 | +17,600 |

## v22 vs v24 Comparison

| Opponent | Map | v22 Our Ti | v24 Our Ti | Change | v22 Win? | v24 Win? |
|---|---|---|---|---|---|---|
| smart_eco | settlement | 19,590 | 37,290 | **+17,700** | No | **Yes** |
| smart_eco | cold | 8,440 | 10,510 | +2,070 | No | No |
| smart_eco | default_medium1 | 22,990 | 18,770 | -4,220 | Yes | Yes |
| smart_defense | default_medium1 | 4,960 | 18,890 | **+13,930** | No | **Yes** |
| sentinel_spam | default_medium1 | 19,520 | 33,140 | +13,620 | Yes | Yes |
| balanced | default_medium1 | 21,920 | 22,120 | +200 | Yes | Yes |

## Record
- v22: 4W - 4L (50%)
- v24: **5W - 1L** (83%)

## Key Findings

### Major Wins vs v22 Baseline
- **settlement vs smart_eco**: Flipped from a loss (-21,550 gap) to a decisive WIN (+18,090 gap). We mined 37,290 Ti vs their 19,200 — nearly double their output. This is the biggest improvement: +17,700 Ti.
- **smart_defense default_medium1**: Flipped from a loss (-9,690 gap) to a win (+4,240 gap). We now mine 18,890 vs their 14,650. Previously our worst matchup on this map; now a clear victory.
- **sentinel_spam default_medium1**: Already winning, but gap exploded from +15,670 to +30,130. Dominant.

### Persistent Weakness: cold vs smart_eco
- Still losing cold, but gap has significantly narrowed: was -23,560, now only -3,950.
- We mine 10,510 vs their 14,460. Still behind but much more competitive.
- This is the only remaining loss in the test set.

### Minor Regression: smart_eco default_medium1
- Still winning, but our Ti mined dropped from 22,990 to 18,770 (-4,220).
- Gap vs opponent unchanged (they still mine ~4,900), so we win, but our absolute output dipped slightly.
- Worth monitoring but not alarming — we still dominate this matchup.

## Summary

v24's sector-based exploration has delivered massive improvements on open/large maps (settlement, smart_defense). The cold map remains the one weak point — smart_eco still outmines us there by ~4k Ti. All other matchups are either maintained or substantially improved.

**Overall: strong upgrade from v22. Main remaining task: fix cold map economy.**

## Ladder Check (2026-04-04 ~08:00 UTC)
No "buzzing" or "bees" matches visible in the top 40 ladder entries. The ladder shows active matches between other teams (muteki, Byte-Sized, 3MiceLoc, gramaticka, etc.). Our bot does not appear to be currently scheduled for ladder matches.
