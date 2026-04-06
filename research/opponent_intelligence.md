# Opponent Intelligence Report

**Date:** 2026-04-06
**Matches analyzed:** 83 ladder matches (415 individual games)
**Overall record:** 38W-45L (46% win rate)

---

## Executive Summary

- **97% of games end by resource tiebreaker** (405/415). Only 10 games ended in core destruction.
- **We have NEVER destroyed an enemy core.** All 10 core destructions were against us.
- **Our biggest weakness is economy on large/open maps.** We go 0-13 on `galaxy` and 1-10 on `shish_kebab`.
- **Rush opponents are rare (3/36 unique opponents) but devastating** — we are 1W-5L against them.
- **Close matches dominate** — 48 of 83 matches were 3-2, and we lose the majority (21W-27L).

---

## Strategy Distribution

| Strategy | Unique Opponents | Total Matches | Our Record | Win Rate |
|----------|-----------------|---------------|------------|----------|
| Pure Economy | 32 | 73 | 36W-37L | 49% |
| Rush | 3 | 6 | 1W-5L | 17% |
| Dual (Economy+Military) | 1 | 4 | 1W-3L | 25% |

**Key insight:** The meta is overwhelmingly Pure Economy. 88% of opponents play Pure Economy. The few that rush or play dual absolutely crush us.

---

## Win Condition Breakdown

| Win Condition | Total Games | We Won | Our Win Rate |
|---------------|------------|--------|-------------|
| Resources (tiebreaker at R2000) | 405 | 204 | 50% |
| Core Destroyed | 10 | 0 | 0% |

We are exactly coinflip-level at economy. We have zero offensive capability.

---

## Opponents We Consistently Lose To

### Tier 1: Always Beat Us (0 wins)
| Opponent | Record | Strategy | Notes |
|----------|--------|----------|-------|
| Ash Hit | 0W-4L | Pure Economy | Consistently out-economies us, all 3-2 scores |
| One More Time | 0W-3L | Pure Economy | 4-1 and 3-2 blowouts, beats us on large maps |
| Polska Gurom | 0W-3L | Rush | Core kills on face/shish_kebab + economy edge |
| The Defect | 0W-3L | Pure Economy | 4-1 blowouts, strong on open maps |

### Tier 2: Usually Beat Us (<=25% WR)
| Opponent | Record | Strategy | Notes |
|----------|--------|----------|-------|
| oslsnst | 1W-3L | Dual | Core kills at rounds 808, 1099, 1978 + economy |
| KCPC-B | 1W-3L | Pure Economy | Including a 0-5 sweep |
| natto warriors | 0W-2L | Pure Economy | |
| andrew_and_friends | 1W-2L | Pure Economy | 4-1 blowout loss |
| Warwick CodeSoc | 1W-1L | Rush | Core kills at rounds 137, 190, 255, 414 |

---

## Core Destruction Analysis (ALL Against Us)

Every single core destruction was inflicted on us. Sorted by round:

| Round | Map | Opponent | Speed |
|-------|-----|----------|-------|
| 86 | galaxy | HAL9000 | Ultra-fast rush |
| 137 | face | Warwick CodeSoc | Very fast rush |
| 190 | shish_kebab | Warwick CodeSoc | Fast rush |
| 255 | chemistry_class | Warwick CodeSoc | Fast rush |
| 319 | face | Polska Gurom | Fast rush |
| 414 | shish_kebab | Warwick CodeSoc | Mid rush |
| 808 | hooks | oslsnst | Mid-game military |
| 1099 | tiles | oslsnst | Late-game military |
| 1300 | binary_tree | Polska Gurom | Late-game military |
| 1978 | hourglass | oslsnst | End-game military |

**Rush-vulnerable maps:** galaxy, face, shish_kebab, chemistry_class — these have short rush distances.

---

## Map Performance

### Worst Maps (< 30% WR)
| Map | Record | WR | Notes |
|-----|--------|-----|-------|
| galaxy | 0W-13L | 0% | Total disaster. 1 core kill against us here too |
| shish_kebab | 1W-10L | 9% | 2 core kills against us |
| arena | 1W-7L | 12% | Pure economy losses |
| face | 3W-12L | 20% | 2 core kills against us |
| minimaze | 1W-4L | 20% | Small sample but bad |
| wasteland_oasis | 3W-11L | 21% | Consistent economy losses |
| default_large2 | 3W-11L | 21% | Large map, economy gap |
| binary_tree | 3W-9L | 25% | 1 core kill against us |
| wasteland | 2W-5L | 29% | Open map problems |
| mandelbrot | 3W-7L | 30% | |

### Best Maps (> 70% WR)
| Map | Record | WR | Notes |
|-----|--------|-----|-------|
| default_small2 | 10W-1L | 91% | Our best map |
| pls_buy_cucats_merch | 12W-2L | 86% | Very strong |
| sierpinski_evil | 11W-2L | 85% | Very strong |
| gaussian | 4W-1L | 80% | |
| starry_night | 8W-3L | 73% | |
| git_branches | 8W-3L | 73% | |
| default_medium1 | 8W-3L | 73% | |
| default_large1 | 5W-2L | 71% | |
| tiles | 10W-4L | 71% | |

**Pattern:** We excel on small/medium maps with structured layouts. We fail on large, open maps where economy optimization matters more.

---

## Detailed Strategy Profiles for Test Bot Replication

### 1. Pure Economy Bot (replicates Ash Hit, One More Time, The Defect, KCPC-B)

These opponents beat us purely by gathering more resources. They never attack. They win at round 2000 by resource tiebreaker.

**How to replicate:**
- **Builders:** 2-3 builder bots. First one spawns immediately, builds harvesters on nearby ore. Second spawns around round 30-50 to expand.
- **Economy priority:** Maximize harvesters on ore tiles. Every titanium AND axionite ore within reach should get a harvester.
- **Conveyor chains:** Efficient shortest-path conveyor chains from harvesters back to core. Use splitters when 2+ harvesters feed from same direction.
- **Axionite handling:** Build 1 foundry early (by round 100) to refine raw axionite. Route raw Ax through foundry, then refined Ax to core. This is likely where we lose — opponents refine Ax and convert it to Ti (1 Ax = 4 Ti), massively boosting their total.
- **Expansion:** After nearby resources tapped, send builder bots out on roads to reach distant ore deposits.
- **No military:** Zero turrets, zero barriers. All resources into economy.
- **Map preference:** Beats us hardest on galaxy, wasteland_oasis, default_large2, face, arena — maps with spread-out resources.

**Key economic insight:** At round 2000, the tiebreaker is total refined axionite delivered to core FIRST, then total titanium. Opponents who efficiently refine and deliver axionite have a massive advantage. We may be losing the axionite game entirely.

### 2. Rush Bot (replicates Warwick CodeSoc, Polska Gurom, HAL9000)

These opponents kill our core, sometimes as early as round 86.

**How to replicate:**
- **Builders:** 1-2 builders, immediate aggressive pathing toward enemy core.
- **Economy:** Minimal — just enough Ti income to build attack infrastructure.
- **Attack approach (Warwick CodeSoc style — core kills at R137, R190, R255, R414):**
  - Build roads/conveyors toward enemy base immediately
  - Set up gunner turrets within range of enemy core
  - Feed gunners with Ti ammo via conveyor chain
  - Gunner does 10 damage per shot, core has 500 HP = 50 shots to kill
  - With 2 gunners firing every round, core dies in ~25 rounds after setup
- **Attack approach (HAL9000 style — core kill at R86):**
  - Ultra-aggressive. Must be using breach turrets or multiple gunners with pre-built supply chains.
  - Possibly uses launcher to throw builder bot onto enemy core tile, then attacks with builder (2 damage per attack, costs 2 Ti).
- **Map preference:** Works best on small maps with short distances: galaxy, face, shish_kebab, chemistry_class.
- **Builder bot count:** Likely 1-2 max. No resources wasted on defense or economy.

### 3. Dual Bot (replicates oslsnst)

Economy focus with mid/late-game military transition. Core kills at rounds 808, 1099, 1978.

**How to replicate:**
- **Phase 1 (rounds 1-300):** Pure economy. Harvesters, conveyors, foundry. Same as Pure Economy bot.
- **Phase 2 (rounds 300-600):** Build roads/conveyors toward enemy territory while maintaining economy.
- **Phase 3 (rounds 600+):** Set up turrets (likely sentinels or gunners) near enemy core. Feed with ammo via long conveyor chains.
- **Key trait:** Patient. Doesn't rush. Builds economy first, then uses resource advantage to overwhelm with military.
- **Military units:** Likely sentinels (18 damage, huge range r^2=32) or gunners. May use breach for the 40+20 splash damage.
- **Map preference:** Works on medium/large maps where there's time to build up: hooks, tiles, binary_tree, hourglass.
- **Builder count:** 2-3. One for economy, one for military infrastructure.

---

## Actionable Recommendations

1. **Economy is the #1 priority.** 97% of games are won by resources. We need to close the economy gap on large maps.
2. **Axionite refining is likely our biggest hole.** We should check if we're building foundries and properly routing Ax->Foundry->Core.
3. **We need basic core defense.** 10 core kills against us with 0 by us. Even 1-2 barriers or gunners near core would help.
4. **Map-specific strategies:** Our bot likely uses a one-size-fits-all approach. Maps like galaxy (0-13!) need special handling.
5. **Rush defense is critical.** When we face rushers we almost always lose. We need to detect incoming builders/turrets and respond.

---

## Match Score Distribution

| Score | Count | Our Wins | Our Losses |
|-------|-------|----------|------------|
| 5-0 | 6 | 3 | 3 |
| 4-1 | 29 | 14 | 15 |
| 3-2 | 48 | 21 | 27 |

We lose more close matches than we win (21W-27L in 3-2 games). This means small economy improvements would flip many losses into wins.

---

## Repeated Opponents (played 3+ times)

| Opponent | Total Matches | Our Record | Trend |
|----------|--------------|------------|-------|
| Ash Hit | 4 | 0W-4L | Consistently worse |
| SPAARK | 5 | 3W-2L | Competitive |
| Chameleon | 4 | 2W-2L | Even |
| Cenomanum | 4 | 2W-2L | Even |
| oslsnst | 4 | 1W-3L | Usually lose |
| KCPC-B | 4 | 1W-3L | Usually lose |
| One More Time | 3 | 0W-3L | Consistently worse |
| Polska Gurom | 3 | 0W-3L | Consistently worse (rusher) |
| Solo Gambling | 4 | 3W-1L | Usually win |
| Some People | 3 | 3W-0L | Always win |
| eidooheerfmaet | 3 | 2W-1L | Usually win |
| The Defect | 3 | 0W-3L | Consistently worse |
| Highly Suspect | 3 | 2W-1L | Usually win |
| MEOW MEOW... | 3 | 2W-1L | Usually win |
| Fake Analysis | 3 | 2W-1L | Slightly better but lost 1-4 blowout |
| andrew_and_friends | 3 | 1W-2L | Usually lose |
| 5goatswalk... | 3 | 2W-1L | Usually win |
