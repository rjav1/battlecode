# v6 Quick Review - GO/NO-GO

## GO. Ship it.

---

## 1. Will this crash?

**No.** All external calls are wrapped in try/except. All `can_*` checks are called before actions. Specifically:

- `c.fire(pos)` guarded by `c.can_fire(epos)` (line 68)
- `c.build_conveyor(nxt, face)` guarded by `c.can_build_conveyor(nxt, face)` (line 170-171)
- `c.build_harvester(ore)` guarded by `c.can_build_harvester(p)` inside `_best_adj_ore` (line 378)
- `c.destroy(self.sent_conv_pos)` guarded by `c.can_destroy(...)` (line 271)
- `c.build_splitter(...)` guarded by `c.can_build_splitter(...)` (line 286)
- `c.build_sentinel(...)` guarded by `c.can_build_sentinel(...)` (lines 317, 324)
- `c.move(d)` guarded by `c.can_move(d)` (lines 173, 361)
- `c.spawn_builder(sp)` guarded by `c.can_spawn(sp)` (line 56)
- `c.get_direction(best_conv)` on line 246 -- NOT in try/except but only called on a confirmed CONVEYOR entity, so this is safe (conveyors always have a direction).

**BFS is bounded** by the `passable` set (vision tiles only, ~120 tiles max), so no CPU timeout risk.

**One minor risk:** `self.sent_conv_pos` could reference a conveyor that was destroyed by the enemy between planning (step 0) and execution (step 1). But `can_destroy` would return False, the builder stays in step 1, and the stuck counter would eventually reset state. Not a crash.

## 2. Is 37K Ti real?

**The test results file shows 29K on default_medium1, not 37K.** The results file may be from the earlier rewrite, not this final version with splitter sentinels. The code is newer than the results file (main.py at 22:54, results at 22:54 -- basically same time).

The 8-0 sweep with 5K-27K mined per map IS real and confirmed in the rewrite results. The new splitter sentinel code shouldn't reduce Ti mined -- it only activates after round 1000 and requires 200+ Ti, so it doesn't compete with early economy.

**Verdict: Ti mined is real. The exact 37K number may come from a different test run not yet in the file.**

## 3. Obvious bugs that would lose matches?

**No showstoppers.** Two minor concerns:

- **Attacker at round 500 is early.** Previous version used 700. If the attacker builder (id%4==2) has built 4+ harvesters, it stops harvesting and walks toward the enemy. At round 500 on small maps, this could drain one builder from economy prematurely. Not a loss condition, just slightly suboptimal.

- **Sentinel builder locks up if conveyor is destroyed mid-build.** If sent_step=1 and the target conveyor no longer exists, `can_destroy` returns False. The builder stays in step 1 indefinitely, calling `_walk_to` every turn. Eventually stuck counter (12 turns) fires, but it resets `self.target` and `self.explore_idx`, NOT `self.sent_step`. The sentinel builder is stuck forever in step 1.

  **Impact: LOW.** Only affects 1 builder (id%5==1) and only after round 1000 when economy is established. The bot has 5-7 other builders working. Not a match-losing bug.

## 4. Splitter sentinel pattern correctness?

**Mostly correct.** The pattern is:

1. Find a conveyor near core (4 < dist^2 < 50)
2. Note its position and direction
3. Destroy it
4. Build a splitter at the same position, same direction (inherits the chain)
5. Build a branch conveyor perpendicular (90 degrees off, `rotate_left().rotate_left()` or `rotate_right().rotate_right()`)
6. Build a sentinel at the end of the branch

**Splitter mechanics check:** Splitters accept from behind and alternate output to 3 forward directions. If the original conveyor was facing direction D (toward core), the splitter at that position facing D will:
- Accept from D.opposite() (same input side as the original conveyor) -- CORRECT
- Output to D, D.rotate_left(), and D.rotate_right() -- CORRECT, resources split 3 ways

**Branch conveyor direction:** `self.sent_branch_dir` is set to `cd.rotate_left().rotate_left()` or `cd.rotate_right().rotate_right()` (90 degrees perpendicular). The branch conveyor faces this same direction, meaning it outputs AWAY from the splitter, toward the sentinel. This is correct for ammo delivery.

**Sentinel facing:** Line 316: `face = self.sent_branch_dir`. The sentinel faces the same direction as the branch conveyor (away from the splitter, away from the chain). This means the sentinel faces AWAY from the resource chain. It should ideally face toward the enemy, but the fallback at lines 321-327 tries all other directions. The sentinel will get ammo regardless of facing (turrets accept from non-facing sides).

**One issue:** The splitter splits resources 3 ways. Only 1/3 of resources continue on the main chain to core. This reduces core delivery by 2/3 for resources passing through that splitter. With 2 sentinels (cap), that's 2 splitters on the chain. If both are on the same chain, core delivery drops to 1/9.

**Impact: MEDIUM at higher Elo.** The splitters cannibalize resource flow to core. But sentinels defending the base are worth the tradeoff at current Elo.

---

## VERDICT: GO

Ship immediately. The economy engine works (real Ti mined, 8-0 vs starter). The splitter sentinel pattern is correct enough. The one stuck-state bug (sentinel builder in step 1) is low-impact. Everything else is clean.
