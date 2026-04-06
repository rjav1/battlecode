# PHASE 1: Build the Economic Engine

You are a quant phd building a competitive bot for Cambridge Battlecode 2026. This is the FIRST phase — a pure titanium economy bot. Nothing else. Do it perfectly.

## Context Files (READ THESE FIRST)

Before writing ANY code, read these files thoroughly:

1. `C:\Users\rahil\downloads\battlecode\CLAUDE.md` — Complete game rules, API reference, all mechanics
2. `C:\Users\rahil\downloads\battlecode\research\top3_scouting.md` — What the #1 team actually does (critical intel)
3. `C:\Users\rahil\downloads\battlecode\research\map_analysis.md` — All 38 maps analyzed with features
4. `C:\Users\rahil\downloads\battlecode\bots\starter\main.py` — The starter bot we must beat
5. `C:\Users\rahil\downloads\battlecode\cambc\_types.py` — All game types, enums, constants, Controller API stubs

## What the Research Tells Us

The #1 team (Blue Dragon, 2791 Elo) wins through PURE ECONOMIC EFFICIENCY:
- 20+ titanium harvesters
- 300+ conveyors
- 33+ bridges
- Zero axionite. Zero foundries. Zero gunners. Zero breaches.
- They out-collect opponents 132:1 in titanium
- ~70% of their wins are Resource Victory at the 2000-round limit

Our bot needs to be an economy machine first. Everything else comes later.

## What to Build

A bot at `bots/buzzing/main.py` (single file for now) that does:

### Core Behavior
- Spawn builders (start with 3, we'll tune later)
- Track spawn count via `self` (instance variable persists across rounds)

### Builder Behavior
1. **Find ore:** Scan visible tiles for `ORE_TITANIUM` using `c.get_nearby_tiles()` + `c.get_tile_env()`
2. **Move to ore:** Navigate toward the nearest unharvested Ti ore tile
3. **Build harvester:** When adjacent to ore, `c.build_harvester(pos)`
4. **Build conveyor chain:** After placing harvester, build conveyors pointing back toward the core. Each conveyor faces the direction of the next step toward core.
5. **Repeat:** Return toward core area, find next ore, repeat

### Movement
- Builders can ONLY walk on: conveyors (any team), roads (any team), allied core tiles
- To move onto an empty tile, the builder must FIRST build a road or conveyor there (costs 1 action cooldown), then move there NEXT round
- Pattern: build road/conveyor on target tile this round -> move onto it next round
- Use `pos.direction_to(target)` for direction, try rotated alternatives if blocked

### Conveyor Chain Logic
- After building a harvester, trace a path back toward the core
- At each step, build a conveyor facing toward the core (the direction of the next step)
- Conveyors accept resources from 3 non-output sides and push toward their facing direction
- The harvester outputs every 4 rounds — the chain carries stacks of 10 to the core
- Conveyors are also walkable, so they double as pathways

### Critical Rules
- Always use `can_build_*()` / `can_move()` before acting — avoid GameError exceptions
- Check `c.get_action_cooldown() == 0` before building, `c.get_move_cooldown() == 0` before moving
- Building costs action cooldown. You CANNOT build + move in the same round.
- Check affordability: `c.get_global_resources()` returns `(titanium, axionite)`, compare against `c.get_harvester_cost()` etc.
- Keep a titanium reserve (don't spend below 30 Ti) so you can always build roads
- `c.get_position()` with no args = this unit's position. With an ID = that entity's position.

## Architecture Requirements

- Single `main.py` file with a `Player` class that has `__init__` and `run(self, c: Controller)` methods
- Use `c.get_entity_type()` to branch between CORE and BUILDER_BOT behavior
- Instance variables on `self` persist across rounds for EACH unit independently
- No shared globals — each unit is an isolated Python environment
- Only Python standard library imports allowed (no numpy, etc.)
- Must stay under 2ms CPU per unit per round

## What NOT to Build (save for later phases)

- No turrets, no military, no combat
- No markers / communication protocol
- No axionite harvesting or foundries
- No scouting or enemy detection
- No bridges or splitters (conveyors only for now)
- No multi-file architecture (single main.py for now)

## Assumptions to Test Empirically

IMPORTANT: Do NOT assume anything works. After writing the bot, TEST these:

1. **Diagonal movement through wall corners:** Can a builder move diagonally between two wall tiles that share only a corner? Run the bot on maps like `butterfly` and `sierpinski_evil` to check. If the builder gets stuck, diagonal squeeze is blocked.

2. **Conveyor chain delivery:** Do resources actually flow through your conveyor chain to the core? Watch the replay with `cambc run buzzing starter --watch` and verify titanium stacks move along conveyors.

3. **Harvester placement:** Can you build a harvester on an ore tile that has a wall adjacent to it? Test edge cases.

4. **Builder walking on conveyors:** Verify builders can walk on conveyors regardless of the conveyor's facing direction and regardless of which team built them.

5. **Action + move cooldown interaction:** Confirm that after building (action cooldown +1), the builder cannot move until next round.

6. **Core tile walkability:** Verify builders can stand on allied core tiles (the 3x3 footprint).

## Testing Protocol

After writing the bot:

1. **Run against starter on all 6 default maps:**
   ```
   cambc run buzzing starter default_small1
   cambc run buzzing starter default_small2
   cambc run buzzing starter default_medium1
   cambc run buzzing starter default_medium2
   cambc run buzzing starter default_large1
   cambc run buzzing starter default_large2
   ```
   The bot MUST win all 6.

2. **Run against starter on competitive maps from featured games:**
   ```
   cambc run buzzing starter arena
   cambc run buzzing starter hourglass
   cambc run buzzing starter corridors
   cambc run buzzing starter wasteland
   cambc run buzzing starter settlement
   ```

3. **Watch at least 2 replays** with `--watch` flag to visually verify:
   - Builders are finding ore and building harvesters
   - Conveyor chains are connected and resources flow to core
   - Builders aren't getting stuck or idling
   - No errors in the console output

4. **Check for CPU timeouts:** Run on the largest map (`cambc run buzzing starter cubes`) and verify no TLE.

5. **Self-play test:** `cambc run buzzing buzzing` — should not crash.

## After Coding and Testing: Spawn Review Agents

Once you have a working bot that passes all tests, spawn TWO review agents:

### Review Agent 1: Code Quality Review
Have it read `bots/buzzing/main.py` and review for:
- Edge cases that could cause crashes (division by zero, index out of bounds, etc.)
- CPU budget risks (unbounded loops, expensive operations)
- Correctness of conveyor chain direction logic
- Whether the bot handles all map geometries (small, large, choked, open)
- Whether the movement logic can get permanently stuck
- Any GameError exceptions that could be thrown

### Review Agent 2: Strategic Review
Have it read `bots/buzzing/main.py` AND `research/top3_scouting.md` and evaluate:
- Is the conveyor topology efficient? (straight lines vs unnecessary detours)
- Is the harvester placement strategy good? (nearest ore vs strategic ore)
- Is the builder count appropriate? (too few = slow setup, too many = scale penalty)
- How does this compare to what Blue Dragon does?
- What's the biggest weakness an opponent could exploit?

Fix any issues found by the reviewers. Then re-test and keep iterating until perfect

## Success Criteria

Phase 1 is DONE when:
- Bot wins 10/10 against starter on default maps (run each twice with different seeds)
- Bot wins 8/10 against starter on competitive maps
- No CPU timeouts on any map
- Replays show clear conveyor chains delivering titanium to core
- At least 3 harvesters are built and connected by round 100
- Review agents have signed off with no critical issues
- All mechanical assumptions have been tested empirically

## Output

When finished, write a brief report to `C:\Users\rahil\downloads\battlecode\phases\phase1_report.md` covering:
- What was built
- Test results (win/loss on each map)
- Assumptions tested and results
- Issues found by reviewers and how they were fixed
- Known limitations for future phases
