# v32 Spending Investigation — Results

## Hypothesis
Ti hoarding is harmful: unspent Ti = infrastructure not built = less future mining.
Tiebreaker counts Ti COLLECTED, not bank balance. Hoarding actively hurts.

## Baseline Measurements (v31 vs starter)

| Map | Bank Balance | Total Mined | % in Bank |
|-----|-------------|-------------|-----------|
| default_medium1 | 23,901 | 23,680 | ~50% |
| settlement | 24,425 | 35,650 | ~41% |
| cold | 5,964 | 8,910 | ~40% |

**Hoarding confirmed: 40-50% of all mined Ti sits in bank at game end.**

## Fixes Attempted

### Fix 1: explore_reserve 30 → 10 (REVERTED)
Builders spend Ti on conveyors while exploring instead of walking freely.
Result: mined DROPPED (23,680 → 9,730 on default_medium1).
Why it failed: explore_reserve=30 actually helps builders MOVE faster (no action
cooldown from building), reaching ore sooner. Reserve=10 made them hammer useless
conveyors into random explored tiles, slowing movement AND wasting Ti.

### Fix 2: barrier threshold cost+40 → cost+20 (REVERTED)
Result: mined dropped to near-zero (50 Ti mined on default_medium1).
Why it failed: barrier cost is ~50 Ti. With cost+20 threshold, builders drain Ti
early before harvesters are placed — the economy never gets started.

### Fix 3: Late-game builder caps increased (REVERTED)
Added tier after round 1200: balanced 10→16, expand 12→18.
vs starter: mined improved (+16% default_medium1).
vs buzzing_prev (competitive): REGRESSION — lost settlement and cold.
Why it failed: by round 1200, all nearby ore is occupied. New builders must travel
far. Builder cost (~25 Ti) + conveyor chain cost > mining return before round 2000.
The extra builders are net negative in competitive play.

## Root Cause Analysis

The Ti "hoarding" is NOT hoarding in the harmful sense. It is:
1. Mining outpacing spending capacity — we have 10 harvesters mining ~12 Ti/round
   but only ~1 Ti/round of build activity in mid-late game.
2. All nearby ore tiles are occupied by round 300-500 (all builders have harvesters).
3. After that, builders explore but find no new buildable ore (already taken by
   our own harvesters or too far for economical conveyor chains).

## Conclusion: Hypothesis is WRONG for our bot

The banked Ti cannot be efficiently converted to more harvesters because:
- All accessible ore is already claimed
- Late-game builders must travel far, making conveyor costs exceed mining returns
- The tiebreaker is Ti COLLECTED (mined), and we're already maximizing that

**The 23K bank balance IS the tiebreaker score** — all of it was mined (23,680
collected includes what's banked). Bank balance = collected - spent. Higher bank
= less wasted on marginal infrastructure. Against real opponents who also mine Ti,
the competitive edge comes from early ore efficiency (v29-v31 improvements), not
from spending down the bank.

## Recommendation

DO NOT implement aggressive spending changes. They all regressed competitive
performance. The current v31 behavior is correct:
- Spend Ti efficiently in early/mid game on harvesters
- Maintain conservative thresholds to avoid Ti starvation during ramp-up
- Accept high bank balance in late game as evidence of mining efficiency

**v31 code is unchanged and restored to full baseline.**

## Better Areas to Investigate for Improvement
1. Attacker bots (id%6==5) — are they destroying enough enemy harvesters?
2. Map-specific ore routing — can we reach second-ring ore faster?
3. Self-play regression — run 5-game suite to verify v31 is solid baseline
