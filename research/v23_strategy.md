# v23 Strategy Recommendation: Roads-First Navigation + Deliberate Conveyor Chains

## The Recommendation

**Roads-first navigation.** Swap `_nav()` to build roads as its primary action and reserve conveyors exclusively for deliberate harvester-to-core chains built after each harvester placement.

This is Option 1 from the evaluation list, and it is the clear winner.

---

## Why This Over the Other Options

### Option 1: Roads-first navigation — RECOMMENDED
- **Impact:** HIGH. Directly addresses root cause of our worst-map failures (corridors, shish_kebab, galaxy, cold). Saves ~2 Ti per tile walked, halves scale inflation from navigation. Enables longer supply chains that actually work.
- **Complexity:** MEDIUM. Requires restructuring `_nav()` and adding a post-harvester chain-build mode. Previous attempts failed (0 Ti) because they removed conveyors from nav without adding deliberate chain-building — the harvesters got built but resources never reached core. The fix: after `build_harvester()`, builder walks back toward core laying conveyors with correct facing at each step.
- **Why now:** We now have chain-fix logic (v14) that handles winding paths. This was the missing piece in previous road-first attempts. The chain-fix mode already walks backward and fixes conveyor directions — we just need to generalize it into "always build the chain on the walk back" instead of "sometimes fix an existing chain."

### Option 2: Marker coordination — NOT YET
- **Impact:** LOW-MEDIUM. Prevents duplicate harvesting (minor problem) and enables info sharing. But our bottleneck is not "builders harvest the same ore" — it is "conveyor trails don't deliver resources." Markers become valuable AFTER we have reliable chains.
- **Complexity:** HIGH. Encoding scheme design, marker placement timing, reading/interpreting markers, staleness handling. Lots of edge cases for limited payoff at our current level.

### Option 3: More builders — NOT YET
- **Impact:** MEDIUM but risky. More builders with current `_nav()` = more conveyor spaghetti = faster scale inflation = diminishing returns. BD runs 15+ builders because their builders lay roads for nav and build deliberate conveyor chains. Our builders would just waste Ti building misaligned conveyors. Fix nav FIRST, then raise caps.
- **Complexity:** LOW (just change cap numbers), but counterproductive without roads-first.

### Option 4: Smarter bridge placement — INCREMENTAL
- **Impact:** LOW-MEDIUM. BD builds 33 bridges vs our ~2. Better bridge placement helps on specific maps but doesn't fix the fundamental nav/chain problem. Worth doing AFTER roads-first.
- **Complexity:** MEDIUM.

### Option 5: Something else — Attacker removal
- The strategy_refresh doc correctly identifies that attacker mode (id%6==5 after round 500) is wasteful: 2 damage per action against a 500 HP core, laying conveyors the whole way. This should be removed as a side fix in v23, but it is not the main lever.

---

## Exactly What to Build

### Change 1: `_nav()` — roads before conveyors

Current order in `_nav()` (lines 301-367):
1. Build conveyor (3 Ti, +1% scale) — **WRONG: this is navigation, not resource transport**
2. Move
3. Bridge fallback
4. Road fallback (1 Ti, +0.5% scale)

New order:
1. **Build road** (1 Ti, +0.5% scale) — navigation infrastructure
2. Move
3. Bridge fallback
4. ~~Conveyor~~ — **REMOVED from nav entirely**

Conveyors are ONLY built in the new chain-build mode (Change 2).

### Change 2: Post-harvester chain-build mode

After `c.build_harvester()` succeeds (currently line 253):
1. Set `self.chain_mode = True`, `self.chain_target = self.core_pos`
2. In chain mode, builder walks back toward core
3. At each step, build a conveyor on the tile the builder is LEAVING, facing the direction toward the harvester (i.e., `d.opposite()` of travel direction — same as current logic, but only during chain-building)
4. Exit chain mode when builder reaches core adjacency (distance_squared <= 8)

This is structurally similar to the existing `_fix_chain()` logic (lines 513-564) but simpler:
- `_fix_chain()` walks back along `self.fix_path` fixing existing conveyors
- Chain-build mode walks back toward core building NEW conveyors with correct facing
- Can reuse `self.fix_path` (already recorded during nav) as the chain route

### Change 3: Remove conveyor-before-road in nav for ALL builders

Gate: `if self.chain_mode:` builds conveyors. Otherwise, `_nav()` only builds roads.

### Side fix: Remove attacker mode

Delete lines 214-219 (attacker assignment) and the `_attack()` method. Attackers waste builders, lay expensive conveyor trails, and almost never kill a 500 HP core. Every builder should be economic.

---

## Expected Impact

### Maps we currently lose:
| Map | Current problem | Expected fix |
|-----|----------------|--------------|
| corridors | 15,039 Ti every game (stuck) | Roads let builders traverse corridors without wasting conveyors. Deliberate chains back to core deliver Ti. Target: 20K+ Ti |
| shish_kebab | 0-5 record | Long narrow paths = road nav works perfectly. Chain-build connects distant harvesters |
| galaxy | 0-4 record | Scattered ore = road exploration + targeted chain-back |
| cold | inconsistent | Same pattern — roads for exploration, chains for delivery |

### Economy improvement estimate:
- Current: ~15-22K Ti on most maps
- Target: ~25-30K Ti — closing the gap to 1600 Elo bots
- Mechanism: 3x cheaper navigation (1 Ti roads vs 3 Ti conveyors), 0% wasted conveyors that don't connect to core, lower scale inflation enabling more buildings overall

### Win rate estimate:
- Current: ~60%
- Target: 65-70% — winning 1-2 more games per match on problem maps turns 2-3 losses into 3-2 wins

---

## Implementation Notes

### Why previous road-first attempts failed (0 Ti):
The previous attempt swapped roads for conveyors in nav but did NOT add chain-building. Result: harvesters got built, but there were no conveyors connecting them to core. Resources piled up at harvesters with nowhere to go. The fix is the chain-build mode — it must be implemented simultaneously with the road-first swap.

### Key invariant to maintain:
Every harvester must have a continuous conveyor chain back to core. The chain-build mode guarantees this by building the chain immediately after harvester placement, following the exact path the builder took (recorded in `self.fix_path`).

### Risk:
The main risk is that chain-build mode fails on complex paths (multiple direction changes). Mitigation: the existing `_fix_chain()` logic already handles this. If a chain has 3+ direction changes, `_fix_chain()` activates to correct conveyor facings. Keep this as a secondary pass.

### What NOT to change:
- BFS pathfinding — works fine
- Harvester placement logic — works fine  
- Barrier/gunner placement — works fine (can optimize later)
- Core spawning logic — raise builder cap AFTER road-first proves out

---

## Summary

One surgical change with the highest leverage available: **stop wasting conveyors on navigation, use roads instead, and build deliberate conveyor chains from each harvester back to core.** This is what Blue Dragon does (174 roads + 308 deliberate conveyors vs our 0 roads + 20 misaligned conveyors). It directly fixes our 4 worst maps and closes the economy gap that is the #1 barrier to climbing.

Previous attempts failed because they removed conveyors from nav without adding chain-building. This time we do both simultaneously.
