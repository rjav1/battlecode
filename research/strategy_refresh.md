# Strategic Review — Fresh Eyes Analysis
## 2026-04-04 | buzzing v20 | 1474 Elo | 60% win rate (post-v8)

---

## 1. SINGLE biggest gap between us and a 1600 Elo bot?

**Economy throughput.** We mine 15-22K Ti on most maps while bots using simple d.opposite() conveyors with more builders consistently hit 25-35K Ti. Our conveyor chains break on any non-straight path, and our builder cap (`econ_cap = vis_harv * 3 + 4`) throttles spawning. A 1600 bot just needs to reliably connect 6-8 harvesters to core on every map shape — we fail to do this on constrained maps (corridors: stuck at exactly 15,039 Ti every game).

## 2. SINGLE biggest gap between us and an 1800 Elo bot?

**Conveyor network scale.** Blue Dragon (2790 Elo) builds 300+ conveyors, 30+ bridges, 20+ harvesters by endgame. We build maybe 20 conveyors and 3-5 harvesters. The 1800+ bots have solved continuous expansion — they keep sending builders out to find new ore, build harvesters, and chain them back, throughout the entire game. We essentially stop expanding after the first few harvesters because our builders get stuck, waste resources on military infrastructure, or hit the builder cap.

## 3. One method or logic block that's clearly wrong or could be 2x better?

**`_nav()` (lines 278-346) still builds conveyors for navigation.** Despite the v15 "roads for nav" intent documented in the constrained maps analysis, `_nav()` STILL builds conveyors as its primary action (line 305: `c.build_conveyor(nxt, face)`). Roads are only a tertiary fallback at line 335. The method tries conveyor first, then move, then bridge, then road. This means every builder trail is still conveyor spaghetti. **Flipping the priority — roads first for navigation, conveyors only for deliberate harvester-to-core chains — would immediately fix the constrained map problem and save 2 Ti per tile walked.**

## 4. Specific change to push from 60% to 70% win rate?

**Fix the nav/chain separation.** In `_nav()`, swap the conveyor build (line 293-307) with the road build (line 335-346). Then add a post-harvester chain-building mode: after `build_harvester()` succeeds (line 235), have the builder walk back toward core building conveyors with correct facing at each step. This one change fixes:
- corridors (15K -> 20K+ Ti)
- cold (currently inconsistent)  
- shish_kebab (0-5 record)
- galaxy (0-4 record)

These are 4 of our 5 worst maps. Winning even 1 more game per match on problem maps turns 3-2 losses into 3-2 wins.

## 5. Bugs or inefficiencies that jump out?

1. **Conveyor-before-road priority in `_nav()` is backwards** (see above). This is the #1 issue.

2. **`econ_cap` uses `vis_harv` (visible harvesters near core)** but on constrained maps harvesters are far from core and invisible — so `econ_cap` stays low and we starve on builders. The floor of `max(6, vis_harv * 3 + 4)` helps but `vis_harv` can be 0 for a long time on spread-out maps.

3. **Attacker assignment is wasteful**: `id % 6 == 5` after round 500 with 4+ harvesters means ~17% of builders become attackers. These builders walk toward enemy core laying conveyors (!) the whole way — expensive, scale-inflating, and rarely successful. Builder attack does only 2 damage per action for 2 Ti against a 500 HP core. That's 500 Ti and 250 actions minimum to kill a core, plus the conveyor trail costs.

4. **Gunner infrastructure state machine** (lines 358-481) is complex and destroys a working conveyor to build a splitter. On constrained maps where conveyors are precious, this actively harms economy. The gunner only fires along a ray — if nothing walks into the ray, it's wasted investment.

5. **Bridge fallback** tries distances 2-3 in only the top 3 ranked directions. On maps where the needed bridge is perpendicular to target, it never finds the right placement.

6. **`_best_adj_ore`** (line 650) picks ore closest to core, not ore that's easiest to chain. An ore tile 5 steps from core through a winding corridor is worse than one 8 steps away in a straight line.

## 6. What to do NEXT with 1 hour?

**One surgical change: fix `_nav()` to use roads, add post-harvester chain-building.**

Specifically:
1. **(20 min)** In `_nav()`, move road building ABOVE conveyor building. Builder walks on roads, not conveyors. Keep conveyor logic but gate it behind a `self.chain_mode` flag that's only true when walking back from a freshly-built harvester to core.

2. **(20 min)** After `c.build_harvester()` succeeds (line 235), set `self.chain_mode = True` and `self.chain_target = self.core_pos`. In chain mode, the builder walks toward core and builds conveyors facing `d` (toward core, NOT `d.opposite()`). When it reaches core adjacency, exit chain mode.

3. **(20 min)** Test on corridors, cold, shish_kebab, galaxy, default_medium1. Verify Ti mining improves. Run regression against buzzing_prev on 5 maps.

This is the single highest-leverage change available. It directly addresses the root cause identified in `constrained_maps_analysis.md`, fixes our 4 worst maps, and aligns with what top teams do (BD builds 300+ conveyors as deliberate pipelines, not navigation trails).

---

## Summary Table

| Question | Answer |
|----------|--------|
| Gap to 1600 | Economy throughput — chains break on non-straight paths |
| Gap to 1800 | Conveyor network scale — we stop at 5 harvesters, they build 20+ |
| Worst code block | `_nav()` builds conveyors for walking instead of roads |
| Change for 70% WR | Road-first nav + deliberate post-harvester conveyor chains |
| Top bug | Nav builds conveyors (3 Ti, +1% scale) instead of roads (1 Ti, +0.5%) |
| Next 1 hour | Fix `_nav()` priority, add chain-building mode, test on problem maps |
