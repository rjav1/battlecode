# Local Bot Loss Debug — barrier_wall and sentinel_spam

Date: 2026-04-06

## Match Results Summary

| Match | Winner | buzzing Ti mined | opponent Ti mined | buzzing Buildings | opponent Buildings |
|-------|--------|-----------------|-------------------|-------------------|-------------------|
| buzzing vs barrier_wall (arena) | barrier_wall | 4,960 | 19,740 | 225 | 110 |
| buzzing vs barrier_wall (dna) | barrier_wall | 18,090 | 27,410 | 467 | 152 |
| buzzing vs barrier_wall (shish_kebab) | barrier_wall | 9,000 | 9,400 | 113 | 43 |
| buzzing vs sentinel_spam (default_large2) | sentinel_spam | 14,790 | 19,610 | 420 | 207 |
| buzzing vs sentinel_spam (landscape) | **buzzing** | 15,090 | 11,870 | 343 | 132 |

**Pattern across losses:** buzzing builds 2–4x as many buildings as the opponent but mines 25–75% less Ti. This is a classic "wide and thin" failure — too many conveyors, too few harvesters per builder, too much Ti locked in infrastructure per unit of output.

---

## What barrier_wall and sentinel_spam do

### barrier_wall
- Spawns exactly **3 builders**, hard cap.
- All 3 builders mine Ti ore (only 2 actively mine long-term; 1 switches to barrier-building after round 60).
- Navigation: build `d.opposite()` conveyors as walkway but with a **Ti reserve of only 15** for conveyors. This is very similar to buzzing's approach.
- **No gunners, no attackers, no sentinels, no late-game features** — pure economy + 10–15 barriers.
- Harvesters: both "miner" builders focus exclusively on harvesters. No early barrier distraction, no gunner builder role, no sentinel splice, no Ax tiebreaker.

### sentinel_spam
- Spawns exactly **4 builders**, hard cap.
- 3 builders mine full-time; 1 switches to sentinel placement after round 150.
- Sentinels are built unarmed (as obstacles/vision); no ammo chain needed.
- Same pure-focus miner approach otherwise.

---

## What they do better than buzzing

### Issue 1: Fewer builders = more Ti per builder = faster harvester ramp

**barrier_wall:** 3 builders, no attacker, no gunner-builder. All spending goes to harvesters + conveyors.

**sentinel_spam:** 4 builders, no attacker role, no gunner-builder role. All spending goes to harvesters.

**buzzing:** Spawns up to 10–16 builders depending on map mode. Multiple builders are assigned secondary roles:
- `id%5==1` → gunner builder (switches at round 60/120/150)
- `id%6==5` after round 500 → attacker
- `id%6==2` at round 1800+ → Ax tiebreaker

These role assignments pull builders away from mining **before the economy is mature**. On arena (small map), buzzing mined only 4,960 Ti vs barrier_wall's 19,740 — a 4x deficit — despite having 13 units to barrier_wall's 3.

**Root cause:** The econ_cap formula allows too many builders relative to harvesters. The formula `max(time_floor, vis_harv * 3 + 4)` on expand maps lets the core keep spawning when Ti is high, but each new builder is a cost-scaling hit (+20%) AND an additional unit competing for ore tiles and Ti for conveyors.

### Issue 2: Builder Ti reserve during navigation is too conservative on large maps

**buzzing's `_explore`:** Uses `explore_reserve = 30 if core_dist_sq > 50 else 5`. When builders are far from core exploring, they hold back 30 Ti and don't lay conveyors. This means builders spend more turns doing nothing (can't move without conveyors if off the conveyor grid).

**barrier_wall/sentinel_spam:** Same `d.opposite()` conveyor approach but with a fixed reserve of 15 — always try to lay a conveyor when navigating. They never get stuck waiting for Ti.

**Key result:** barrier_wall and sentinel_spam build *fewer* conveyors per harvester (shorter chains, more compact layouts on small/medium maps), but each conveyor is more productive. Buzzing builds sprawling conveyor networks that waste Ti and don't deliver resources faster.

### Issue 3: Too many buildings blocking the cost scale meter

**buzzing at round 2000 (arena):** 225 buildings. **barrier_wall:** 110 buildings.

Every building buzzing places increases the global cost scale. With 225 buildings vs 110, buzzing is paying significantly more for each new harvester and conveyor. The cost scale penalty compounds: every extra conveyor laid during exploration adds +1% to all future costs. With 115 extra buildings, that's roughly a 115% additive increase in the scale factor (dominated by conveyor/road scale of +1% each and harvester +5%).

Buzzing's habit of laying conveyors aggressively during exploration — even far from ore — inflates building count dramatically without proportional income gain. A conveyor 15 tiles from core that never carries a resource still costs 1% scale increase and 3 Ti.

---

## Top 3 Issues and Specific Code Changes

### Fix 1: Reduce builder cap aggressively and remove premature role splits

**Current behavior (buzzing main.py ~line 96-126):**
- `expand` cap goes up to 16 with high-bank override to 25
- Builders spawned into gunner/attacker/sentinel roles that drain economy before it's established

**What to change:**
- Hard cap builders at 8 for balanced maps and 12 for expand maps. The econ_cap formula correctly gating on `vis_harv * 3 + 4` is good — but the ceiling is too high.
- Delay gunner builder role to round 200+ on balanced maps, 300+ on expand maps, and require 5+ harvesters before any builder switches to gunner duty.
- Delay attacker role to round 800+ and require 8+ harvesters.
- The Ax tiebreaker (round 1800) is fine as-is but the AX builder wastes 200 rounds wandering when no Ax ore is in vision — it should return to mining rather than exploring blindly.

Code location: `bots/buzzing/main.py` lines 96–126 (core cap logic), 361–367 (attacker assignment), 373–378 (gunner builder), 381–388 (sentinel splice).

### Fix 2: Fix the Ax tiebreaker builder stuck-loop bug

**Current behavior (shish_kebab debug log):** Builder `id=1676` finds Ax ore tiles at `Position(x=12, y=5)` and `Position(x=12, y=7)` from round 1801 onward but oscillates between `Position(x=9, y=4)` and `Position(x=9, y=5)` every single round from r1801 to r1900. This is an oscillation bug — the builder is stuck bouncing between two tiles and never reaches the Ax ore.

The `_build_ax_tiebreaker` step=0→1 transition sets `_ax_foundry_pos` to a **conveyor** near the Ax harvester, not the ore tile itself. If that conveyor is 3+ tiles away but the builder can't navigate there due to wall/path issues, `_walk_to` oscillates.

**What to change:**
- In `_build_ax_tiebreaker` step 1, add the same stuck detection used in the main builder loop (detect if pos hasn't changed in 5+ rounds, then reset `_ax_step = 0` to find a new target).
- Alternatively, fall back to normal mining if Ax foundry target is unreachable within 50 rounds.

Code location: `bots/buzzing/main.py` lines 806–899 (`_build_ax_tiebreaker`).

### Fix 3: Reduce exploration Ti reserve and eliminate wasteful far-from-ore conveyor laying

**Current behavior (buzzing main.py ~line 627-631):**
```python
explore_reserve = 30 if core_dist_sq > 50 else 5
```
When exploring far from core, builders hold 30+ Ti before placing conveyors. But the stuck-detection eventually fires (after 12 rounds), clears the target, and the builder wanders. Meanwhile it still lays conveyors as walkways even when there's no ore within reach.

**What to change:**
- Lower `explore_reserve` to 15 (matching barrier_wall's approach) to keep builders moving even when far from core.
- Add a check before laying exploration conveyors: only build a conveyor during exploration if the builder is within X tiles of a visible ore tile (e.g., `total_ore_count > 0` from the already-computed vision scan). If no ore in vision, use road-only navigation (cheaper, +0.5% scale vs +1%).
- This dramatically reduces the building count inflation from exploration conveyors that lead nowhere.

Code location: `bots/buzzing/main.py` lines 583–632 (`_explore` method), line 627–631 (explore_reserve logic).

---

## Summary Table

| Issue | barrier_wall approach | buzzing problem | Fix |
|-------|----------------------|-----------------|-----|
| Builder count | Hard cap 3 builders, all miners | Spawns 10–16 builders, multiple non-miners | Lower hard cap, delay role switches |
| Cost scale inflation | 43–110 buildings | 113–467 buildings | Stop laying exploration conveyors when no ore in sight |
| Ax builder oscillation | N/A | Builder oscillates 200 rounds, never builds foundry | Add stuck detection to `_build_ax_tiebreaker` |

**Expected impact:** Reducing building count from ~400 to ~200 on large maps should cut the cost scale roughly in half, making each harvester and builder significantly cheaper and allowing faster ore coverage. Even recapturing 20% of the Ti efficiency gap (currently 3–4x behind) would flip these losses.
