# Axionite Tiebreaker Analysis
**Date:** 2026-04-06
**Researcher:** Subagent (research-only, no code changes)
**Question:** Is building a late-game foundry to deliver 1 refined Ax viable for TB#1 insurance?

---

## Context

Tiebreaker order after round 2000:
1. Total refined Ax delivered to core  ← we deliver 0; **ANY opponent with 1 stack wins this**
2. Total Ti delivered to core
3. Number of living harvesters
4. Total Ax stored
5. Total Ti stored

Current buzzing bot: mines 0 Ax across all games (empirically confirmed in strat_axionite.md April 4 tests). We win/lose TB#2 (Ti delivered). If we could deliver even 1 stack of refined Ax (10 units), we would win every TB#1 matchup where the opponent also delivers 0.

---

## Foundry Cost Math

### Direct Cost
- Foundry: 40 Ti base cost
- At round 1500 with reasonable scale (~200%): actual cost ~80 Ti
- At round 1800 with scale (~250%): actual cost ~100 Ti

### Scale Tax — The Critical Number

The +100% scale increase is ADDITIVE to existing scale. This means:

**If scale is at S% when foundry is built, it jumps to (S + 100)%.**

Everything built AFTER the foundry costs (100/S) × more Ti than without it.

| Build time | Approx scale before | Scale after | Future cost multiplier |
|------------|---------------------|-------------|------------------------|
| Round 100 | ~130% | ~230% | 1.77× more expensive |
| Round 500 | ~160% | ~260% | 1.63× more expensive |
| Round 1000 | ~190% | ~290% | 1.53× more expensive |
| Round 1500 | ~210% | ~310% | 1.48× more expensive |
| Round 1800 | ~230% | ~330% | 1.43× more expensive |

**Key insight:** Building foundry at round 1800 still costs 43% more on everything built after. But if we stop building at round 1800 (only repairs/turret ammo remain), the damage is minimal.

### What "Nothing Built After" Means
If the foundry is the **last thing ever built** (round 1900+), the 100% scale increase has zero future impact. The only cost is the 40 Ti (scaled) for the foundry itself.

---

## Logistics Chain: Time to Deliver 1 Refined Ax

### Required Infrastructure (minimum viable)
```
Ax ore tile → Ax Harvester → Conveyor(s) → Foundry → Conveyor(s) → Core
                                    ↑
                  Also needs: Ti stack input to foundry
```

The foundry requires TWO inputs simultaneously:
- 1 Raw Ax stack (from Ax harvester chain)  
- 1 Ti stack (from Ti economy chain)

And produces 1 Refined Ax stack output routed to core.

### Timing Breakdown

**Step 1: Ax Harvester first output**
- Harvesters output every 4 rounds
- First output is IMMEDIATE (round 0 of harvester's life)
- So harvester outputs Raw Ax on the same round it's built

**Step 2: Stack travels conveyor chain to foundry**
- Each conveyor hop = 1 round (resources move at end of round)
- If Ax ore is 15 tiles from core (typical), foundry placed inline = ~7-8 tiles from ore
- Chain length: ~7-8 rounds to reach foundry

**Step 3: Foundry processes**
- Foundry needs both a Ti stack AND an Ax stack
- Ti stacks are already flowing through existing chains
- If foundry is placed inline with Ti chain: Ti stack arrives within 1-2 rounds of setup
- Foundry produces 1 Refined Ax when both inputs are present

**Step 4: Refined Ax travels to core**
- Foundry → Core: ~7-8 more conveyor hops = 7-8 rounds

**Total minimum time from foundry placement: ~20-25 rounds**

### Absolute Latest Build Round
To deliver by round 2000:
- Round 1975: latest foundry placement
- But infrastructure (conveyors to Ax ore, Ax harvester) must exist BEFORE foundry
- Need the Ax ore tile discovered and builder adjacent to it

**Practical latest: Round 1960 for foundry, ~1940 for Ax harvester**

---

## Map Analysis: Which Maps Have Accessible Ax Ore?

From map_data.json, nearest Ax ore distance (Manhattan/path tiles from core center):

### Tier 1 — Close Ax ore (distance ≤ 15, viable)
| Map | Nearest Ax | Nearest Ti | Ti/Ax ratio | Notes |
|-----|-----------|-----------|-------------|-------|
| arena | 3 | 6 | 2.5× | Ax CLOSER than Ti — best candidate |
| default_medium1 | 8 | 9 | 7.3:6 | Nearly equal distance — very viable |
| default_large1 | 8 | 6 | 1× | Close together, co-located |
| cold | 11 | 10 | 18:115 | Ax slightly farther but accessible |
| galaxy | 15 | 4 | 1:2 | 15 tiles is marginal |
| gaussian | 13 | 4 | 1:3 | 13 tiles, accessible |
| face | 10 | 5 | 1:2 | Small map, close ax |
| starry_night | 12 | 10 | 58:126 | Ax nearby, ore-rich map |
| dna | 8 | 8 | 76:78 | Nearly 1:1 Ti/Ax, equal distance |

### Tier 2 — Moderate distance (15-25 tiles)
| Map | Nearest Ax | Nearest Ti | Notes |
|-----|-----------|-----------|-------|
| binary_tree | 7 | 7 | But separated colocation |
| tiles | 14 | 9 | Nearby but fragmented |
| socket | 15 | 7 | 15 tiles, elongated map |
| default_small1 | 13 | 5 | Small map, manageable |
| default_medium2 | 15 | 8 | Accessible |
| hooks | 21 | 14 | Farther |
| chemistry_class | 19 | 9 | Farther |
| landscape | 17 | 15 | Both far, co-located |
| hourglass | 20 | 5 | Far from core |
| settlement | 23 | 11 | Far, but 30 Ax tiles available |
| cubes | 21 | 14 | Large map, far |
| thread_of_connection | 21 | 4 | Very far |
| wasteland | 22 | 16 | Far |
| mandelbrot | 25 | 8 | Very far |

### Tier 3 — Inaccessible or unknown (-1 = path blocked)
| Map | Ax dist | Notes |
|-----|---------|-------|
| pixel_forest | -1 | Fragmented, no path found |
| pls_buy_cucats_merch | -1 | Fragmented |
| wasteland_oasis | -1 | 54 regions, extreme fragmentation |
| sierpinski_evil | -1 | 66 regions, extreme fragmentation |
| shish_kebab | -1 | Fragmented small map |
| cinnamon_roll | -1 | Core in corner, fragmented |
| butterfly | 13 | But fragmented (10 regions) |
| bar_chart | 14 | Fragmented (11 regions) |
| git_branches | 33 | Very far AND fragmented |
| corridors | 30 | Very far |
| battlebot | 25 | Far |
| default_large2 | 32 | Very far |
| minimaze | 25 | Maze, far |

---

## Net Economy Impact Analysis

### Scenario: "Late Foundry" (round 1900, nothing more built)

**Cost:** 40 Ti × 2.3 scale factor ≈ 92 Ti
**Scale damage:** +100% on 0 future buildings = **zero scale damage**
**Logistics:** Need pre-existing Ax harvester + conveyor chain to foundry

**Net Ti cost of entire operation:**
- Ax Harvester: 20 Ti × ~2.2 scale ≈ 44 Ti (must be built earlier, ~round 1800)
- Conveyors to Ax ore: ~5 conveyors × 3 Ti × ~2.2 scale ≈ 33 Ti
- Foundry: ~92 Ti
- Conveyors from foundry to core: ~4 × 3 Ti × ~2.3 scale ≈ 28 Ti
- **Total infrastructure cost: ~197 Ti**

**What we sacrifice:** 197 Ti NOT spent on additional harvesters or turrets.
- At round 1800 with scale ~2.2: one harvester = 44 Ti → 4-5 harvester-slots forfeited
- But at round 1800, map is likely covered already — marginal harvesters yield diminishing returns

### Scenario: "Mid Foundry" (round 1000, scale penalty active for 1000 more rounds)

At round 1000, expected builder count: ~12-15, scale ≈ 190%.
After foundry: scale ≈ 290% — 53% more expensive for remaining 1000 rounds.

Over 1000 rounds with aggressive building:
- ~5 more harvesters normally cost 5 × 20 × 1.9 = 190 Ti
- With foundry tax: 5 × 20 × 2.9 = 290 Ti → **100 Ti lost** to scale alone
- Multiple other buildings similarly taxed

**Verdict for mid-game foundry:** Net -100 to -300 Ti over game lifetime. Significant regression.

---

## The Real Obstacle: Getting an Ax Harvester Built

From strat_axionite.md (empirically tested April 4):
> "Builders find Ti first. Once a builder is adjacent to Ti ore, it builds a harvester immediately — there's no reason to pass up Ti to keep looking for Ax."

Current bot logic (`_best_adj_ore`): builds harvester on ANY adjacent ore, Ti or Ax, closest to core. Since Ti ore is more abundant AND closer to core on most maps, builders nearly always hit Ti ore first.

**Confirmed finding:** 0 Ax harvested across ALL test games.

To get even 1 Ax harvester, we'd need:
1. A builder that finds Ax ore before Ti ore, OR
2. Explicit role assignment: "this builder targets only Ax ore"
3. Both require inter-unit coordination (markers) to avoid wasting builders on Ax-seeking

The marker system can encode a "claim Ax" signal per-tile, but orchestrating which builder gets the Ax-seeker role requires careful encoding.

---

## Recommendation: CONDITIONAL YES (Late-Only Niche)

### Do NOT pursue for competitive wins
The TB#1 scenario only triggers when:
1. Both teams reach round 2000 (no core kill)
2. Both teams deliver equal Ti OR we lose TB#2
3. The opponent ALSO delivers 0 refined Ax

Given that close economy games go to TB#2 (Ti delivered), and we currently lose TB#2 to strong opponents anyway, winning TB#1 would only matter against opponents we're already close to beating.

### Narrow valid use case: Late-game "Ax insurance" (round 1900+)
**If** the following are all true:
- Map has Ax ore within 15 tiles of core (Tier 1 maps: arena, default_medium1, cold, face, dna, starry_night, default_large1)
- We are NOT building any more buildings after round ~1900 (scale tax = 0)
- We already have 8+ harvesters delivering Ti
- A builder happens to be exploring in the direction of Ax ore

Then: spend ~200 Ti total (from a ~10K-30K Ti game budget) for a shot at winning TB#1.

**Expected value:**
- Cost: ~200 Ti ≈ 1-2% of game economy. Negligible.
- Benefit: Wins any tiebreaker where opponent has 0 refined Ax delivered
- Probability of that scenario: Unknown, but non-zero on close economy maps

### What would need to change in bot code
1. Bot must track: "do we have an Ax harvester?" via markers
2. One designated builder per game targets nearest Ax ore (not Ti)
3. Foundry placement inline on the Ax → core chain, built round 1800-1950
4. Foundry needs Ti input: tap a spur off the existing Ti chain, or rely on passive Ti delivery if Ti chain passes nearby

**Complexity:** Medium. Marker-based Ax coordination is ~50 lines. Foundry inline placement is the hardest part — requires knowing the existing Ti chain layout, which varies by map.

### Comparison: TB#2 improvement vs TB#1 insurance

Current Elo is stuck at 1465-1488. Primary losses are:
- Real opponents outmine us on Ti (2-3× more Ti delivered)
- 3 auto-loss maps (galaxy, face, arena)

Winning TB#1 occasionally does NOT address the 40-50 Elo gap from chain connectivity and auto-loss maps. It's a marginal tie-flip, not a strategic upgrade.

**Priority ranking:**
1. Fix chain connectivity / auto-loss maps (HIGH impact, HIGH effort)
2. TB#2 improvement via spend-down policy (HIGH impact, LOW effort)
3. TB#1 Ax insurance (LOW impact, MEDIUM effort) ← this proposal

---

## Summary

| Factor | Assessment |
|--------|-----------|
| Foundry +100% scale tax | Severe if mid-game; negligible if last thing built (~round 1900) |
| Ax ore accessibility | Good on 7-9 maps (arena, dm1, cold, face, dna, starry_night, dl1) |
| Infrastructure time needed | ~20-25 rounds minimum after harvester is placed |
| Latest viable build round | Foundry by round 1975; Ax harvester by round 1940 |
| Current Ax harvest rate | 0 — bot never reaches Ax ore in practice |
| Code change required | Marker-based role assignment + foundry inline placement |
| Expected win conversion | Marginal (only flips TB#1 when opponent also at 0) |
| Recommended action | Defer — address chain connectivity and spend-down first |

**Bottom line:** Mathematically viable as a late-game (round 1900+) side operation on ~7 favorable maps. The scale tax is near-zero if foundry is truly the last building. BUT the primary bottleneck is that current bot never builds an Ax harvester. Fixing that requires marker coordination. Given our current Elo trajectory (flat at 1465-1488), TB#2 and auto-loss map fixes have 5-10× more impact per engineering hour. Revisit this after reaching 1550+ Elo.
