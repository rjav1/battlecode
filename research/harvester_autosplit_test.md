# Harvester Auto-Split Test — default_medium1

**Date:** 2026-04-08
**Match:** buzzing vs starter, default_medium1, seed 1
**Result:** buzzing wins (tiebreak) — 34,630 Ti mined, 260 buildings

---

## Does V61 ever place 2+ conveyors adjacent to a harvester?

**Answer: No. Almost never by design.**

Reading the bot code (`bots/buzzing/main.py`):

The builder navigates to an ore tile by calling `_nav()`, which builds **one conveyor per tile per step** as it walks. The conveyor faces the direction the builder came from (i.e., `face = d.opposite()`), forming a single chain. After placing a harvester, it immediately sets `self._bridge_target = ore` and attempts a bridge shortcut to the nearest allied conveyor or core tile on the next round.

There is **no logic that places a second conveyor on an adjacent tile of a finished harvester**. The builder moves on to the next ore target immediately after harvesting.

The only case where a harvester might get 2 adjacent conveyors is accidental — if two builders happen to approach the same ore from different directions. This would be rare and uncoordinated.

---

## What auto-split would give us

Game rule: *"Harvester prioritises outputting in directions used least recently."*

This means a harvester with **2 adjacent conveyors** outputs alternately to each — effectively splitting its output stack between two delivery chains. Net effect: same throughput per harvester (still 1 stack every 4 rounds), but the stack is routed down whichever chain has gone longest without receiving. No throughput gain per harvester — it's a routing feature, not a doubling feature.

**Key clarification:** Auto-split does NOT double output. It splits the existing output between 2 chains. The only benefit is:
- Parallel delivery paths (resilience if one chain is blocked or destroyed)
- Can feed two separate destinations from one harvester (e.g., foundry + core)

---

## Would deliberately placing 2 conveyors help?

**Verdict: Marginal benefit at best, costs an extra building.**

Each extra conveyor adjacent to a harvester costs 3 Ti × scale (at 200 buildings = ~3x scale = 9 Ti). It adds +1% to global cost scale and doesn't increase harvester throughput. It only helps if:

1. You have two separate delivery destinations (e.g., one chain to core, one to foundry)
2. The existing single chain is congested with stacks (unlikely — stacks move every round, chain capacity is rarely the bottleneck at our scale)

Given our **building bloat crisis** (260 buildings on default_medium1, 496 on cold), adding more conveyors per harvester would worsen cost scaling without proportional gain.

---

## The Real Throughput Question

From this match: **34,630 Ti mined** with 260 buildings vs barrier_wall's 29,730 Ti with 101 buildings (prior deep dive, gaussian).

The throughput gap vs our hardest opponents comes from:

1. **We mine MORE raw Ti** on maps where we win — but on problem maps (cold, gaussian) we mine 15-45% less because our chains are longer and our cost scale is higher
2. **Longer chains = higher conveyor cost = fewer harvesters affordable** — the vicious cycle
3. **Auto-split would add conveyors, making the cycle worse**

---

## Conclusion

- V61 does NOT use harvester auto-split — single conveyor chain per harvester
- Auto-split does not increase throughput; it splits existing output between routes
- Deliberately adding a second adjacent conveyor per harvester would cost extra buildings (+1% scale each) with no throughput gain
- The correct fix remains **reducing total building count** (cap/prune roads and conveyors), not adding more buildings per harvester
- Auto-split could be useful only in a future foundry-based Ax economy (one chain to foundry, one to core from same harvester) — not relevant to current Ti-only strategy
