# PHASE 2: Reliable Conveyor Chains + Sentinel Defense

You are a quant PhD iterating on a Cambridge Battlecode 2026 bot. Phase 1 built a working economy. Phase 2 fixes the two biggest weaknesses: **broken conveyor chains** and **zero military defense**. Do both perfectly.

## How to Work

You MUST work in a tight build-review loop:

1. **Read all context files first** (listed below)
2. **Make ONE focused change** (e.g., fix chain routing)
3. **Spawn a review agent** to audit that change
4. **Test** with `cambc run buzzing starter <map>` on 3+ maps
5. **Fix issues** found by reviewer / tests
6. **Repeat** until that change is solid
7. **Move to the next change**

Do NOT write all the code at once and test at the end. Build incrementally. Each change should be small enough that you can verify it works before moving on.

When spawning review/audit agents, give them the full file path and tell them exactly what to look for. They should read the actual code and be critical — assume the code is wrong until proven otherwise.

## Context Files (READ ALL BEFORE CODING)

1. `C:\Users\rahil\downloads\battlecode\CLAUDE.md` — Full game rules + API reference
2. `C:\Users\rahil\downloads\battlecode\bots\buzzing\main.py` — Current bot (Phase 1 output, 199 lines)
3. `C:\Users\rahil\downloads\battlecode\phases\phase1_report.md` — Phase 1 results + known issues
4. `C:\Users\rahil\downloads\battlecode\research\top3_scouting.md` — What Blue Dragon (#1) actually does
5. `C:\Users\rahil\downloads\battlecode\cambc\_types.py` — All types, constants, Controller API stubs

## Phase 1 Status

The current bot at `bots/buzzing/main.py`:
- Wins 39/42 games vs starter (93%)
- Core spawns up to 8 builders
- Builders find Ti ore, build harvesters, build conveyors as they walk
- BFS pathfinding within vision
- Average Ti mined: ~20,000 per game

### Critical Problems to Fix

**Problem 1: Conveyor chain gaps (HIGHEST PRIORITY)**
The builder builds conveyors as it walks TOWARD ore (facing `d.opposite()`). But:
- After placing a harvester, the builder moves on to find more ore. It does NOT walk back to ensure the chain connects harvester → core.
- If the builder walked through existing passable tiles (roads, other conveyors, core tiles), those segments have no conveyors, creating gaps.
- The harvester outputs to adjacent tiles — but there may be no conveyor adjacent to the harvester pointing toward the core.
- Result: harvesters produce resources that go nowhere on many maps.

**Problem 2: Zero military defense**
- No sentinels, no turrets of any kind
- Any opponent with even basic turrets walks to our core unopposed
- Blue Dragon (#1) has 20 sentinels by late game. Kessoku Band (#2) has 10 by round 148.
- We need at minimum 2-4 sentinels by round 200 to survive against real opponents.

## What to Build

### Change 1: Intentional Conveyor Chain Routing

After a builder places a harvester, it MUST build an unbroken conveyor chain from the harvester back to the core (or to an existing chain that connects to the core).

**The state machine should be:**
```
FIND_ORE → MOVE_TO_ORE → BUILD_HARVESTER → BUILD_CHAIN_TO_CORE → FIND_ORE (repeat)
```

**BUILD_CHAIN_TO_CORE state:**
- After placing harvester, the builder's new target is the core position
- As the builder walks back toward the core, it builds a conveyor at each step
- Each conveyor faces the direction TOWARD THE CORE (i.e., in the direction the builder is walking)
- Wait — think carefully about conveyor direction:
  - Resources enter from the harvester side and need to flow toward the core
  - So the conveyor at position P should face the direction from P toward the core
  - That means facing = `P.direction_to(core_pos)` (approximately)
  - Or more precisely: if the builder is at P and just came from P_prev, the conveyor at P should face the direction from P_prev toward P... No, think again.
  
**STOP. Think about conveyor direction carefully:**
- A conveyor OUTPUTS in its facing direction
- A conveyor ACCEPTS from the 3 non-facing sides
- Resources flow: harvester → conveyor → conveyor → ... → core
- So at each position along the chain, the conveyor should face TOWARD THE CORE (the direction resources need to flow)
- If position P is between the harvester and the core, the conveyor at P should face `P.direction_to(next_step_toward_core)`

**Implementation approach:**
- After building a harvester at `ore_pos`, set state to BUILD_CHAIN
- Target = core position
- Walk back toward core. At each tile:
  - Determine which direction points toward the core (or toward the next tile on the path)
  - Build a conveyor facing that direction
  - Move onto it next round
- Stop building conveyors when you reach a tile adjacent to the core (the core accepts resources directly)
- Also stop if you reach a tile that already has a conveyor pointing toward the core (chain merges with existing chain)

**Edge cases to handle:**
- Builder may need to go around walls — the chain should follow the walkable path, not a straight line
- If builder can't build a conveyor (occupied tile, wall, etc.), build on an adjacent tile
- If a conveyor already exists on a tile, don't overwrite it (check `c.get_tile_building_id(pos)`)
- The chain must be CONTINUOUS — no gaps. Verify by checking each tile between harvester and core has a conveyor or is a core tile.

### Change 2: Basic Sentinel Defense

After the economy is running (round 150+ AND 3+ harvesters built), one builder should transition to building sentinels.

**Sentinel placement rules:**
- Build sentinels facing toward the enemy core (inferred from map symmetry: enemy_core ≈ Position(map_width - 1 - core_x, map_height - 1 - core_y) for rotational symmetry)
- Place sentinels a few tiles in front of the core, along the likely enemy approach direction
- Build 2-4 sentinels total (they cost 30 Ti each, +20% scale — don't overbuild)
- Sentinels need ammo delivered via conveyors — build a conveyor branch from an existing chain to each sentinel
- Sentinels accept resources from non-facing sides, so orient the supply conveyor appropriately

**Sentinel auto-fire:**
- Add turret behavior to the Player class: if `get_entity_type() == EntityType.SENTINEL`, check `get_attackable_tiles()` for enemies and `fire()` if possible
- Sentinels fire every 3 rounds (reload cooldown), cost 10 ammo per shot
- Check `c.get_ammo_amount() >= 10` and `c.get_action_cooldown() == 0` before firing

**Keep it simple:**
- Just 2-4 sentinels, placed near the core, facing the enemy direction
- One ammo supply chain (branch from existing conveyor network)
- Auto-fire when enemies in range
- Don't overengineer — this is basic defense, not a fortress

## What NOT to Build (save for later)

- No bridges (Phase 3)
- No splitters (Phase 3)
- No markers / communication (Phase 3-4)
- No offensive operations (Phase 4)
- No launcher drops (Phase 4)
- No map-specific strategy (Phase 5)

## Coding Constraints

- Keep it in a single `bots/buzzing/main.py` file
- Python stdlib only
- Stay under 2ms CPU per unit per round
- Always use `can_*()` checks before actions
- Use `self` for persistent state — each unit has its own Player instance
- Don't break what Phase 1 built. The economy should still work. Only ADD to it.

## Build-Review Loop (MANDATORY)

### After Change 1 (conveyor chain fix):

**Spawn Review Agent — Chain Auditor:**
Tell it to read `bots/buzzing/main.py` and specifically verify:
- Does the builder ALWAYS build an unbroken chain from harvester to core?
- Is conveyor facing direction correct? (resources must flow harvester → core)
- What happens if the path to core goes around walls?
- What happens if two builders' chains need to merge?
- What happens if the builder runs out of Ti mid-chain?
- Are there any tiles in the chain that have roads instead of conveyors?
- Trace through the code step by step for a hypothetical 10-tile chain. Does it work?

**Test:**
```bash
cambc run buzzing starter default_small1 --watch
cambc run buzzing starter default_medium1 --watch
cambc run buzzing starter settlement --watch
```
Watch the replays. Verify resources are flowing. Check the Ti mined numbers.

**Fix any issues before proceeding to Change 2.**

### After Change 2 (sentinel defense):

**Spawn Review Agent — Military Auditor:**
Tell it to read `bots/buzzing/main.py` and verify:
- Are sentinels being built? When? How many?
- Is the sentinel facing the enemy direction?
- Is there an ammo supply conveyor connected to the sentinel?
- Does the auto-fire logic work? (check ammo, cooldown, then fire)
- Does adding sentinels hurt the economy? (spending too much Ti on military)
- What happens if there's no room to build a sentinel near the core?

**Test:**
```bash
cambc run buzzing starter default_medium1
cambc run buzzing starter corridors
cambc run buzzing starter hourglass
cambc run buzzing starter arena
```
Check that sentinels appear in the replay and that economy still works.

### After both changes:

**Spawn Final Integration Review Agent:**
Tell it to read `bots/buzzing/main.py` and the Phase 1 report, then evaluate:
- Does the bot still win on all maps it won before? (no regression)
- Is the Ti mined higher than Phase 1? (chain fix should increase delivery)
- Are sentinels being built without crippling the economy?
- What are the remaining weaknesses?
- What should Phase 3 focus on?

## Testing Protocol

### Regression Tests (must STILL win all of these):
```bash
cambc run buzzing starter default_small1
cambc run buzzing starter default_small2
cambc run buzzing starter default_medium1
cambc run buzzing starter default_medium2
cambc run buzzing starter default_large1
cambc run buzzing starter default_large2
cambc run buzzing starter arena
cambc run buzzing starter hourglass
cambc run buzzing starter corridors
cambc run buzzing starter settlement
```

### New Tests (verify chain fix + sentinels):
```bash
cambc run buzzing starter wasteland        # Previously lost some seeds
cambc run buzzing starter butterfly        # Fragmented map
cambc run buzzing starter cold             # Many Ti deposits
cambc run buzzing starter face             # Small rush map
cambc run buzzing starter cubes            # Largest map (CPU check)
```

### Self-play:
```bash
cambc run buzzing buzzing default_medium1  # Should not crash
```

### Compare Ti mined vs Phase 1:
Run the same maps with the same seed and compare Ti mined numbers. The chain fix should show HIGHER Ti delivery on most maps. Record the comparison.

## Success Criteria

Phase 2 is DONE when:
- **Chain connectivity:** Replays show unbroken conveyor chains from every harvester to core. Resources visibly flowing.
- **Ti mined improvement:** Average Ti mined is ≥ 10% higher than Phase 1 on the same maps/seeds
- **Sentinels exist:** 2-4 sentinels visible in replay by round 200, facing enemy direction, with ammo supply
- **Auto-fire works:** Sentinels fire at enemy builders/units that enter their range
- **No regression:** Still wins all maps that Phase 1 won
- **No CPU timeouts:** Passes on cubes (50x50)
- **All three review agents** (chain, military, integration) have signed off
- **Self-play doesn't crash**

## Output

When finished, write a report to `C:\Users\rahil\downloads\battlecode\phases\phase2_report.md` covering:
- What was changed (diff from Phase 1)
- Chain fix: how it works, before/after Ti mined comparison
- Sentinel defense: placement, ammo supply, auto-fire verification
- Test results table (map, seed, win/loss, Ti mined, sentinels built)
- Review agent findings and how they were resolved
- Known limitations
- Recommendations for Phase 3

Also provide a summary of the full file paths of everything you created or modified.
