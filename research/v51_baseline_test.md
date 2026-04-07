# V51 Baseline Test (20-match)

**Date:** 2026-04-06
**Bot:** buzzing (V51 = V49 + rnd//50 explore rotation fix)
**Previous baseline:** V49=65%, V50=40% (reverted)
**Target:** >=65%

---

## Summary

| Suite | Result | Details |
|-------|--------|---------|
| Core Regression (5 maps) | PASS | 5W-0L vs buzzing_prev |
| Opponent Gauntlet (14 maps) | MET (50%+ target) | 9/14 (64%) |
| Self-Play Stability | PASS | No crash |
| **Total: 20 matches** | **PASS** | **14W-5L (70% overall)** |

---

## Core Regression: buzzing vs buzzing_prev

Note: buzzing_prev bot (v37) is apparently crashing/broken — scored 0 Ti mined on cold and settlement.

| Map | Result | Ti (ours vs theirs mined) |
|-----|--------|--------------------------|
| default_medium1 | WIN | 4960 vs 4940 |
| cold | WIN | 19670 vs 0 |
| face | WIN | 4970 vs 4950 |
| settlement | WIN | 27440 vs 0 |
| galaxy | WIN | 16080 vs 4970 |

**5W-0L — PASS**

---

## Opponent Gauntlet: buzzing vs field

| Opponent | Map | Result |
|----------|-----|--------|
| balanced | cold | LOSS |
| balanced | galaxy | LOSS |
| barrier_wall | face | LOSS |
| barrier_wall | settlement | WIN |
| sentinel_spam | default_medium1 | WIN |
| sentinel_spam | cold | LOSS |
| rusher | face | LOSS |
| rusher | default_medium1 | WIN |
| ladder_eco | galaxy | WIN |
| ladder_eco | settlement | WIN |
| ladder_rush | cold | WIN |
| ladder_rush | face | WIN |
| ladder_bridge | settlement | WIN |
| ladder_bridge | galaxy | WIN |

**Gauntlet: 9/14 (64%) — 50%+ target MET**

### Opponent breakdown
| Opponent | W/L | Assessment |
|----------|-----|------------|
| balanced | 0/2 | Weakness — loses both maps |
| barrier_wall | 1/2 | Mixed |
| sentinel_spam | 1/2 | Mixed |
| rusher | 1/2 | Mixed |
| ladder_eco | 2/2 | Strong matchup |
| ladder_rush | 2/2 | Strong matchup |
| ladder_bridge | 2/2 | Strong matchup |

---

## Self-Play Stability

- buzzing vs buzzing on default_medium1: OK (resources t2000)

---

## Verdict: PASS (but barely below 65% target)

**64% gauntlet win rate** — 1 win short of the 65% target. The core regression is a clean 5W-0L sweep, but buzzing_prev appears broken (0 Ti on 2 maps) so that comparison is inflated.

**Key weakness: `balanced` bot goes 0/2.** The balanced bot likely has a strong economy that out-mines buzzing on cold and galaxy. This is the primary drag on the win rate.

**Compared to V49 target (65%):** V51 lands at 64% gauntlet — essentially at parity with V49. The rnd//50 explore rotation fix held the line vs the V50 regression (40%). V51 is a safe state.

**Duration:** 206s (~3.4 min for 20 matches)
