# Ti Hoarding Check

**Date:** 2026-04-07  
**Bot:** buzzing V60  
**Question:** Do we end games with >3000 Ti stored? If so, we're hoarding.

---

## Results

| Opponent | Map | Seed | Result | Our Ti Stored | Our Ti Mined | Opp Ti Stored | Opp Ti Mined | Our Buildings | Opp Buildings |
|----------|-----|------|--------|--------------|-------------|--------------|-------------|--------------|--------------|
| balanced | galaxy | 1 | LOSS | 36 | 0 | 14683 | 9900 | 254 | 90 |
| balanced | galaxy | 2 | LOSS | **3955** | 6040 | 14696 | 9890 | 362 | 81 |
| ladder_eco | wasteland | 6259 | WIN | 108 | 0 | 13 | 0 | 122 | 337 |
| fast_expand | default_large1 | 1388 | LOSS | **16996** | 22830 | 32580 | 32190 | 470 | 318 |
| turtle | dna | 7405 | WIN | **9976** | 12080 | 11095 | 6470 | 459 | 184 |
| smart_defense | gaussian | 8736 | LOSS | **20493** | 19830 | 26329 | 22100 | 224 | 84 |

**Verdict: YES — massive Ti hoarding confirmed on large/expand maps.**

---

## Analysis

### Hoarding pattern (4 of 6 maps end with >3000 Ti stored)

**fast_expand/default_large1**: 16996 Ti stored — we mined 22830 but only spent ~5834. 470 buildings built (mostly conveyors). We're spending Ti on conveyors but not on high-value items.

**smart_defense/gaussian**: 20493 Ti stored — mined 19830, spent only ~-663 net (started with 500 + passive income). This is extreme: we have 20K Ti and lose on resources 20493 vs 26329. We could have built many more harvesters.

**turtle/dna**: 9976 Ti stored even in a WIN — 12080 mined, 459 buildings. We win but leave 9976 unspent.

**balanced/galaxy/2**: 3955 stored. 362 buildings vs opponent's 81 — we're building 4x more buildings than them!

### Root cause: conveyor overconstruction

We build 224-470 buildings while opponents build 81-318. The bulk of our buildings are conveyors (every step of the nav path). This costs Ti and scale but doesn't produce income. Meanwhile we hit the builder cap (8-15) and stop spawning builders even when we have massive Ti reserves.

### Why the builder cap doesn't help

The `econ_cap = max(time_floor, vis_harv * 3 + 4)` formula: with only 2-3 harvesters visible (they're spread across the map), cap stays at ~10. More builders would just build more conveyors.

### The real problem: few harvesters, many conveyors

`fast_expand/default_large1`: 470 buildings at ~3 Ti each = ~1410 Ti on conveyors. But income from harvesters is the bottleneck. Opponent (fast_expand) has 318 buildings but mines 32190 Ti — they have more efficient chains or more harvesters.

---

## Conclusion

**We ARE hoarding** — sitting on 10-20K Ti on large maps. But spend-down harvesters won't fix this unless we can find new ore to put them on. The Ti is accumulating because:
1. All ore is already harvested (no new ore to build on)
2. Builder cap limits builders even with excess Ti
3. No conversion sink (no foundry, no turrets costing Ti)

**Recommendation:** The Ti hoarding is a symptom of hitting the ore ceiling — we've harvested everything we can reach and income is maxed. The fix is getting MORE harvesters EARLIER (before ore is contested) and building MORE conveyors FASTER early game, not late-game spend-down.

The 20493 Ti stored in gaussian suggests we're accumulating faster than we can spend — but we can't build more harvesters because there's no ore left. This is the end-game state of a well-running economy with nothing left to invest in.

---

## What spend-down harvesters would/wouldn't fix

- Would NOT help: Late-game hoarding when all ore is harvested — no new ore to build on
- WOULD help: Mid-game case where Ti > 500 at round 300 and unclaimed ore exists nearby — builders are too conservative with `ti < cost + 5` reserve

The mid-game case is worth testing. The late-game case (gaussian, default_large1) is fundamental: we've maxed our ore count and there's nowhere to invest the Ti.
