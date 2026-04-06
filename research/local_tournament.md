# Local Tournament Results — 2026-04-04

## buzzing vs New Test Fleet (3 maps each)

| Opponent | Map | Winner | Our Ti | Their Ti | Notes |
|----------|-----|--------|--------|----------|-------|
| barrier_wall | default_medium1 | **buzzing** | 29,530 | 17,481 | Strong win, 2x mining |
| barrier_wall | corridors | barrier_wall | 15,039 | 15,188 | Very close loss, corridors is tight |
| barrier_wall | settlement | **buzzing** | 20,636 | 19,176 | Narrow win |
| sentinel_spam | default_medium1 | sentinel_spam | 17,583 | 29,678 | Heavy loss, 4 builders + sentinels out-economy us |
| sentinel_spam | corridors | sentinel_spam | 15,039 | 24,839 | Loss, they mine significantly more |
| sentinel_spam | settlement | sentinel_spam | 21,745 | 24,076 | Loss, consistent pattern |
| fast_expand | default_medium1 | **buzzing** | 13,565 | 3,771 | Win, they failed to mine on this map |
| fast_expand | corridors | fast_expand | 15,039 | 24,531 | Loss on corridors again |
| fast_expand | settlement | **buzzing** | 35,487 | 2,317 | Dominant win, they failed |
| balanced | default_medium1 | balanced | 17,583 | 29,486 | Loss, their economy is strong |
| balanced | corridors | balanced | 15,039 | 24,771 | Loss on corridors |
| balanced | settlement | **buzzing** | 6,362 | 7,205 | Win (tiebreaker, likely harvesters) |

### New Fleet Summary

| Opponent | W | L | Win Rate |
|----------|---|---|----------|
| barrier_wall | 2 | 1 | 67% |
| sentinel_spam | 0 | 3 | 0% |
| fast_expand | 2 | 1 | 67% |
| balanced | 1 | 2 | 33% |
| **Total** | **5** | **7** | **42%** |

## buzzing vs Existing Opponents (default_medium1)

| Opponent | Winner | Our Ti | Their Ti | Notes |
|----------|--------|--------|----------|-------|
| starter | **buzzing** | 24,841 | 3,342 | Easy win, starter does nothing |
| eco_opponent | eco_opponent | 21,123 | 35,936 | Loss, pure eco bot out-mines us |
| rusher | **buzzing** | 2,430 | 294 | Win, rusher wastes resources on roads |
| turtle | **buzzing** | 22,331 | 14,567 | Win, turtle is slower |
| test_attacker | **buzzing** | 24,033 | 5,277 | Win, attacker has no economy |

### Existing Opponents Summary

| Opponent | Result | Win Rate |
|----------|--------|----------|
| starter | W | 100% |
| eco_opponent | L | 0% |
| rusher | W | 100% |
| turtle | W | 100% |
| test_attacker | W | 100% |
| **Total** | **4-1** | **80%** |

## Overall Win Rate Matrix

| Opponent | Strategy Type | Result | Record |
|----------|--------------|--------|--------|
| starter | Passive | **WIN** | beat easily |
| rusher | Aggression | **WIN** | they starve themselves |
| test_attacker | Aggression | **WIN** | no economy = no threat |
| turtle | Def + Eco | **WIN** | we out-mine them |
| barrier_wall | Def + Eco | **WIN** | 2-1 across maps |
| fast_expand | Pure Eco (6 builders) | **MIXED** | 2-1, fails on some maps |
| eco_opponent | Pure Eco (d.opposite) | **LOSS** | they out-mine us significantly |
| sentinel_spam | Eco + Sentinels | **LOSS** | 0-3, consistent losses |
| balanced | Eco + Def + Atk | **LOSS** | 1-2, their eco is stronger |

**Overall: 10 W / 8 L (56% win rate)**

## Key Findings

### We beat:
1. **Passive/starter bots** — trivially
2. **Rush/attack bots** — they waste resources on aggression with no economy
3. **Turtle defense** — our economy is better than pure turtling
4. **Barrier wall** — barriers alone don't win resource races

### We lose to:
1. **sentinel_spam (0-3)** — CRITICAL VULNERABILITY. 4 builders with basic eco + sentinels consistently out-mine us. The sentinels aren't even armed — it's purely that 4 builders with d.opposite() conveyors produces more than our approach.
2. **eco_opponent (0-1)** — Pure d.opposite() economy with 3-7 builders scales better than our economy.
3. **balanced (1-2)** — A mid-tier bot with 4 builders and d.opposite() conveyors beats us on most maps.

### Corridors Map Problem:
- We scored exactly 15,039 Ti on corridors across ALL matches. This suggests our economy is capped/stuck on this map layout.
- Opponents with d.opposite() conveyors consistently beat us on corridors.

### Root Cause Analysis:
The common thread in all losses is **d.opposite() conveyor economy**. Bots using d.opposite() conveyors mine 20-35k Ti while we mine 13-22k Ti. Our conveyor chain approach (harvester -> chain back to core) appears to be less efficient than the simpler d.opposite() method used by eco_opponent, sentinel_spam, and balanced.

### Priority Improvements:
1. **Economy overhaul** — Adopt d.opposite() conveyor strategy or improve chain efficiency
2. **Corridors map** — Investigate why we're capped at 15,039 Ti
3. **Counter sentinel_spam** — Need a way to deal with unarmed sentinels blocking paths
