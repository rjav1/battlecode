# Strategy Research: Axionite-First Economy

**Date:** 2026-04-04
**Bot:** `bots/axionite_first/main.py`
**Hypothesis:** Win TB#1 (refined axionite delivered to core) by harvesting Ax ore, building a foundry, and delivering refined Ax.

## Theory

Tiebreaker order after 2000 rounds:
1. Total refined axionite delivered to core
2. Total titanium delivered to core
3. Number of living harvesters
4. Total axionite currently stored
5. Total titanium currently stored
6. Coinflip

If nobody mines axionite, TB#1 is always tied at 0. The real tiebreaker becomes TB#2 (Ti delivered). If we could deliver even 1 refined Ax while the opponent delivers 0, we'd win TB#1 regardless of their Ti advantage.

## Implementation

Three iterations tested:
- **v1:** Role-based (ax_hunter, foundry_builder), per-instance harvester tracking
- **v2:** Foundry placed inline by replacing conveyor near core, vision-based harvester counting
- **v3:** Simplified roles, all builders seek both ore types, Ax preference when no Ax harvester exists

## Test Results (v3 final)

| Matchup | Map | Winner | Ax Mined (us) | Ti Mined (us) | Ti Mined (opp) |
|---------|-----|--------|---------------|----------------|-----------------|
| vs starter | default_medium1 | **axionite_first** | 0 | 25,740 | 0 |
| vs buzzing | default_medium1 | **axionite_first** | 0 | 25,930 | 16,100 |
| vs buzzing | settlement | **axionite_first** | 0 | 19,660 | 17,910 |
| vs buzzing | cold | **axionite_first** | 0 | 21,180 | 10,530 |
| vs buzzing | corridors | **buzzing** | 0 | 9,850 | 9,930 |

**Record: 4W-1L** (all wins on Ti economy, TB#2 -- never on TB#1)

## Key Finding: AXIONITE IS NEVER MINED

Across ALL tests on ALL maps, axionite mined = 0. The "axionite-first" strategy completely fails to achieve its stated goal. Here's why:

### Why Axionite Doesn't Get Harvested

1. **Ti ore is more abundant and closer:** Every map has 2-4x more Ti ore than Ax ore. Ti ore tiles are more likely to be near the core and along natural exploration paths.

2. **Builders find Ti first:** The standard exploration pattern (build conveyors, move outward) encounters Ti ore before Ax ore. Once a builder is adjacent to Ti ore, it builds a harvester immediately -- there's no reason to pass up Ti to keep looking for Ax.

3. **Per-instance state is blind:** Each builder tracks its own `harvesters_built` and `has_ax_harvester`. Builder #1 builds 3 Ti harvesters but builder #2 doesn't know that and also builds Ti harvesters. No inter-unit communication about Ax needs.

4. **Foundry cost is devastating:** +100% scale cost. Building a foundry early doubles all future costs for marginal benefit. The foundry builder trigger (round 80 + enough Ti + id%3==1) rarely fires because the specific builder with id%3==1 may not have enough visibility or be near core.

### Even If Axionite Were Mined

Even if we solved the harvesting problem, the logistics chain is extremely complex:
- **Two-input foundry:** Foundry needs BOTH Ti stacks AND Raw Ax stacks to produce Refined Ax
- **Conveyor routing:** Raw Ax conveyors must feed INTO the foundry, Ti conveyors must also feed in from a different side
- **Output routing:** Refined Ax output must route FROM foundry TO core via more conveyors
- **Chain conflicts:** Existing Ti -> core chains would need to be split to route some Ti to foundry instead

This requires precise multi-directional conveyor engineering that our simple "d.opposite() conveyor" approach cannot achieve.

### Foundry Scale Cost Analysis

Building ONE foundry adds +100% to the cost scale. This means:
- If scale is at 150% when you build the foundry, it jumps to 250%
- All subsequent harvesters, conveyors, turrets, builders cost 67% more
- The Ti economy penalty is massive for a resource that only matters in tiebreakers

## Conclusion

**Axionite-first is NOT a viable strategy.** The hypothesis is theoretically sound (winning TB#1 would be decisive) but practically impossible with current bot architecture because:

1. Ti ore dominates map layouts and builder paths
2. Foundry +100% scale cost cripples economy
3. Multi-input/output foundry logistics require conveyor engineering beyond simple chain building
4. Markers (the only inter-unit comms) would need a complex encoding scheme for Ax coordination
5. The wins we got were purely from being a decent Ti economy bot, not from Ax at all

### Why Nobody Uses Axionite

The top players don't use axionite because:
- The foundry tax (+100% scale) makes it a net negative for economy
- Ti economy is simpler, more reliable, and more scalable
- TB#1 only matters if both players go to round 2000 with equal Ti -- vanishingly rare
- The infrastructure cost (foundry + routing conveyors) could build 2+ more harvesters instead

### Potential (Unlikely) Niche

The ONLY scenario where Ax-first could work:
- Very late game (round 1500+) when scale is already maxed and Ti is abundant
- Build a single foundry near an existing Ax ore + Ti chain
- Deliver a token amount of refined Ax for TB#1 insurance
- This would be a minor optimization to add to an already-winning bot, NOT a core strategy

**Verdict: Not meta-breaking. The meta is correct -- Ti economy wins.**
