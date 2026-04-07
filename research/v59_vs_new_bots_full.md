# V59 vs New Test Bots — Full Results

**Date:** 2026-04-06
**Bot version:** buzzing (V59 — chain-join bridge removed, core-only bridge with dist gate)

---

## Results

| Test | buzzing mined | opponent mined | Buildings buzz/opp | Winner |
|------|--------------|----------------|---------------------|--------|
| vs mergeconflict cold | 17480 | 8930 | 451 / 220 | **buzzing WIN** |
| vs mergeconflict default_medium1 | 1450 | 14310 | 289 / 219 | **mergeconflict WIN** |
| vs mergeconflict corridors | 10060 | 4990 | 24 / 11 | **buzzing WIN** |
| vs fast_rush face | 18270 | 3790 | 207 / 33 | **buzzing WIN** |
| vs fast_rush arena | 9920 | 0 | 242 / 26 | **buzzing WIN** |
| vs hybrid_defense cold | 19670 | 18220 | 433 / 383 | **buzzing WIN** |
| vs hybrid_defense galaxy | 14210 | 22110 | 338 / 177 | **hybrid_defense WIN** |

**Overall: 5W-2L**

---

## Critical Findings

### Loss 1: default_medium1 vs mergeconflict — 1450 vs 14310 mined

This is a catastrophic result. buzzing only mines 1450 Ti on default_medium1 while mergeconflict (a simple 3-builder bot) mines 14310. Building count: 289 vs 219.

mergeconflict mines 10x more Ti than buzzing on this map. This is the same map where V59 was showing 19760 mined vs smart_eco earlier in the session. Something is very wrong with this specific matchup.

**Hypothesis:** The chain-join bridge logic in V59 (now core-only) still fires on default_medium1 ore tiles that are within dist²<=25 of core. The bridge is being placed on tiles that block the conveyor chain delivery — either occupying the only adjacent tile to the harvester, or targeting a core tile whose input side is already occupied.

Alternatively: with 289 buildings and only 1450 mined, buzzing is spending nearly all Ti on conveyors/bridges that don't deliver. The building count explosion (289) vs mergeconflict's 219 suggests aggressive over-building.

**Action needed:** Debug this specific matchup. 1450 mined with 289 buildings = massive Ti waste, not a chain-direction issue.

### Loss 2: galaxy vs hybrid_defense — 14210 vs 22110 mined

buzzing mines 14210, hybrid_defense mines 22110 (+56%). Building count: 338 vs 177. buzzing builds 2x more buildings and mines significantly less.

hybrid_defense wins on galaxy despite having sentinels (military overhead). This means hybrid_defense's economy is cleaner — fewer wasted conveyors.

galaxy is an expand map (large). The building count explosion (338 for buzzing) on an expand map points to the explore_reserve issue on large maps: during exploration, buzzing builds conveyors along exploration paths (not connected to any harvester), wasting Ti.

**Key signal:** 338 buildings, 14210 mined = 42 Ti per building. hybrid_defense: 177 buildings, 22110 mined = 125 Ti per building. buzzing's per-building efficiency is 3x worse.

---

## Summary of Weaknesses Exposed

1. **default_medium1 vs mergeconflict:** 1450 mined is an outlier even for buzzing — something specific about this matchup causes near-total economic collapse. Needs dedicated debug run.

2. **galaxy vs hybrid_defense:** Conveyor sprawl on expand maps. 338 buildings / 14210 mined = poor efficiency. Hybrid's sentinel overhead doesn't hurt it enough to overcome this gap.

3. **fast_rush:** Not a threat — buzzing wins comfortably on both face and arena. The rush pressure test validates our rush defense is adequate.

4. **cold vs hybrid_defense:** Very close (19670 vs 18220) — buzzing wins by 1450 Ti mined differential. Healthy competition.

---

## Priority Investigations

1. **debug default_medium1 vs mergeconflict** — 1450 mined is anomalous, not representative of normal V59 behavior on that map. May be a specific seed interaction with bridge placement.
2. **galaxy building sprawl** — 338 buildings on an expand map vs hybrid_defense's 177 suggests exploration conveyor waste is still an issue at large scale.
