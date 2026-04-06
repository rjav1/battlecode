# PHASE 5: Arm Sentinels, Add Offense, Submit to Ladder

You are a quant PhD building a championship bot for Cambridge Battlecode 2026. Phases 1-4 built a working economy that beats the starter bot 16/17. But we've ONLY tested against the starter bot, which mines 0 Ti every game. We have no idea how we perform against real opponents. Phase 5 addresses the two glaring weaknesses (unarmed sentinels, no offense) and then SUBMITS to the competitive ladder.

## HOW TO WORK — THE IRON RULES

**UNLIMITED compute, UNLIMITED time, UNLIMITED agents.** Use them ALL. ONE small change at a time. Get it PERFECT before moving on.

```
For EACH change:
  1. Write the code (20-50 lines)
  2. Spawn 3 agents IN PARALLEL:
     Agent A: Code Reviewer (assume code is wrong, find bugs)
     Agent B: Devil's Advocate (try to break it, adversarial scenarios)
     Agent C: Scenario Tracer (trace 5 concrete examples line-by-line)
  3. Fix everything they find
  4. Test 8+ maps, 2+ seeds
  5. Spawn Test Auditor — compare numbers vs Phase 4
  6. NO regressions allowed. If any map regressed, fix before moving on.
  7. ALL agents must sign off before next change
```

### ZERO ASSUMPTIONS. PROVE EVERYTHING.
- Sentinel fires? **Watch the replay and SEE it fire.**
- Ammo reaches sentinel? **Watch resources flow on the conveyor.**
- Launcher throws builder? **Watch it in the replay.**
- Conveyor direction correct? **Trace with exact positions on paper.**
- "It won" ≠ "it works." **Check Ti mined numbers.**

### CREATIVE AGENT USE
- **"Opponent Simulator" agent**: Write a simple aggressive bot that sends builders to attack our core. Test our sentinels against it.
- **"Ammo Flow Calculator" agent**: Model harvester → conveyor → sentinel throughput mathematically
- **"Launcher Strategist" agent**: Read the API docs on launchers and design optimal placement
- **"Red Team" agent**: Write the simplest bot that would BEAT us, then make us survive it
- **"Replay Analyst" agent**: Watch replays and describe what happens round by round

## Context Files (READ ALL FIRST)

1. `C:\Users\rahil\downloads\battlecode\CLAUDE.md` — Full game rules + API (ESPECIALLY sentinels, launchers, splitters)
2. `C:\Users\rahil\downloads\battlecode\bots\buzzing\main.py` — Current bot (260 lines, Phase 4)
3. `C:\Users\rahil\downloads\battlecode\phases\phase4_report.md` — Phase 4 results
4. `C:\Users\rahil\downloads\battlecode\research\top3_scouting.md` — Blue Dragon uses 20 sentinels, Kessoku Band has 10 by round 148
5. `C:\Users\rahil\downloads\battlecode\research\contender_scouting.md` — Gap between Master and Grandmaster is DUAL COMPETENCY (both economy AND military wins)
6. `C:\Users\rahil\downloads\battlecode\cambc\_types.py` — API stubs, GameConstants

## Current Weaknesses

1. **Sentinels never fire.** They cost 30 Ti + 20% scale each and do nothing. A 3 Ti barrier would be more useful. This is actively hurting us — wasting resources AND unit cap slots.

2. **Zero offensive capability.** On narrow maps (corridors, hourglass, face), the top teams win by Core Destroyed at round 164-749. We can't do this. We lose every game that requires aggression.

3. **No self-defense.** If an opponent sends builders to destroy our conveyors, we have no way to stop them. Our sentinels don't fire. We have no barriers protecting infrastructure.

## Three Changes (in order, ONE AT A TIME)

### Change 1: Sentinel Ammo Supply (HIGHEST PRIORITY)

**The problem:** Sentinels need 10 ammo per shot (fires every 3 rounds). They accept resources from any non-facing side. Currently they're placed near conveyors but don't reliably receive ammo.

**The fix — use a splitter:**

A splitter costs 6 Ti (+1% scale). It accepts resources from behind and alternates output across 3 forward directions. If we place a splitter on an existing conveyor chain, it can feed both the core AND a sentinel.

**Implementation:**
1. When placing a sentinel, also build a splitter on the nearest conveyor chain tile
2. The splitter should face such that one of its 3 output directions points toward the sentinel
3. Build 1-2 conveyors connecting splitter output to the sentinel
4. The splitter accepts from behind (the conveyor chain continues to feed it)
5. Resources alternate: ~1/3 goes to the sentinel, ~2/3 continues toward core

**Splitter mechanics (from CLAUDE.md):**
- `c.build_splitter(pos, direction)` — faces the given direction
- Accepts input from behind ONLY (opposite of facing)
- Alternates output between: facing direction, facing.rotate_left(), facing.rotate_right()
- Each output is tried in least-recently-used order

**Alternative (simpler): Place sentinel DIRECTLY adjacent to a conveyor chain.**
If the sentinel is on a non-facing side of a conveyor, resources entering that conveyor might overflow to the sentinel. But this relies on the conveyor being full (resource stacks backing up). May not work reliably.

**Best approach:** Try the simple approach first (sentinel adjacent to conveyor). Test if it gets ammo. If not, add a splitter.

**Verification:**
- Run against starter on default_medium1 with `--watch`
- Fast-forward to round 300+
- Look at the sentinel: does it have ammo? Does it fire when enemies are near?
- If the starter bot never approaches, write a tiny test bot that sends a builder toward the enemy core, and test against THAT
- The sentinel should fire at the approaching builder

**Test bot for verification (write to bots/test_attacker/main.py):**
```python
# Simple bot that sends builders toward the enemy
from cambc import Controller, Direction, EntityType, Position
DIRS = [d for d in Direction if d != Direction.CENTRE]

class Player:
    def __init__(self):
        self.target = None
    def run(self, c):
        if c.get_entity_type() == EntityType.CORE:
            pos = c.get_position()
            if c.get_action_cooldown() == 0 and c.get_unit_count() < 5:
                for d in DIRS:
                    if c.can_spawn(pos.add(d)):
                        c.spawn_builder(pos.add(d))
                        return
        elif c.get_entity_type() == EntityType.BUILDER_BOT:
            if self.target is None:
                w, h = c.get_map_width(), c.get_map_height()
                pos = c.get_position()
                self.target = Position(w - 1 - pos.x, h - 1 - pos.y)
            pos = c.get_position()
            d = pos.direction_to(self.target)
            if d == Direction.CENTRE:
                return
            nxt = pos.add(d)
            if c.can_move(d):
                c.move(d)
            elif c.get_action_cooldown() == 0:
                if c.can_build_road(nxt):
                    c.build_road(nxt)
```

Test: `cambc run buzzing test_attacker default_medium1 --watch` — watch if our sentinels fire at their approaching builders.

### Change 2: Basic Offensive Capability

**Why:** The research shows that the gap between Master and Grandmaster is DUAL COMPETENCY — winning by both Core Destroyed AND Resource Victory. On narrow maps (face at dist 9, arena at dist 8), the top teams kill the enemy core in 164-749 rounds. We currently can't do this.

**Simple approach — builder raid:**
- After round 400 (economy established), designate 1 builder as an attacker
- Attacker builds roads/conveyors toward the enemy core (using symmetry-detected direction)
- When the attacker reaches enemy buildings, use `c.fire(pos)` to attack the building on its tile (2 damage, costs 2 Ti)
- Priority targets: enemy conveyors (20 HP, cut supply lines), then harvesters (30 HP, cut income)
- The attacker can also `c.destroy()` any allied buildings it stands on (but that's useless against enemy buildings — `destroy()` only works on your own team's buildings)

**IMPORTANT API DETAIL:** Builder bots can only `fire()` at their OWN tile — they attack the building underneath them. So the attacker must:
1. Walk onto the enemy building's tile (conveyors are walkable by any team!)
2. Call `c.fire(c.get_position())` — deals 2 damage to the building on that tile
3. Costs 2 Ti per attack + action cooldown
4. Enemy conveyor has 20 HP → 10 attacks to destroy = 20 Ti + 10 rounds

**Implementation:**
- Add an `_attacker` role/state for one builder
- Designated by: `self.my_id % 4 == 2` AND `c.get_current_round() > 400`
- Target: enemy core position (from symmetry detection)
- Movement: build roads/conveyors toward enemy, walk on enemy conveyors when possible
- Combat: `c.fire(c.get_position())` when standing on a tile with an enemy building
- Fallback: if stuck or no path to enemy, revert to economy builder behavior

**Start simple:** Just one attacker sending probing builders toward the enemy. Don't overengineer. This is about having SOME offensive pressure, not a full army.

### Change 3: Submit to Ladder

After Changes 1 and 2 are tested and reviewed:

1. Run the full test suite one final time (all 17 maps)
2. Run self-play to verify no crashes
3. Submit: `cambc submit bots/buzzing/`
4. Monitor the first 10 ladder matches
5. Record results in the report

**If submission fails** (file structure wrong, etc.), debug and fix. The submission requires:
- A directory with `main.py` containing a `Player` class
- Max 5 MB zip, 50 MB decompressed, 500 files
- No native extensions (.so, .pyd)
- All imports at top level

Our bot is a single `main.py` file — should be straightforward.

**After submission:**
- Play 10+ ladder matches (happens automatically every 10 min)
- Watch replays of losses to understand what opponents are doing
- Record our Elo and what we're losing to
- This data informs Phase 6 priorities

## What NOT to Build (save for Phase 6+)

- No markers / communication protocol (Phase 6)
- No map-specific strategies (Phase 6)
- No launcher drops (Phase 7)
- No axionite / foundries (probably never — top teams don't use them)

## Testing Protocol

### Regression suite (MUST still win all):
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
cambc run buzzing starter face
cambc run buzzing starter cubes
cambc run buzzing starter cold
cambc run buzzing starter starry_night
cambc run buzzing starter dna
cambc run buzzing starter butterfly
cambc run buzzing starter wasteland
```

### Military verification:
```bash
cambc run buzzing test_attacker default_medium1 --watch  # Do sentinels fire?
cambc run buzzing test_attacker corridors --watch        # Does attacker reach enemy?
cambc run buzzing test_attacker face --watch             # Short map — fast core pressure?
```

### Record in comparison table:
| Map | Phase 4 Ti | Phase 5 Ti | Sentinels Fire? | Attacker Active? | Change % |
|-----|-----------|-----------|:---:|:---:|----------|

### After ladder submission:
| Match # | Opponent | Opponent Elo | Result | Maps Won/Lost | Notes |
|---------|----------|-------------|--------|--------------|-------|

## Success Criteria

Phase 5 is DONE when:
- **Sentinels fire:** Verified in replay — sentinel fires at enemy builders on at least 3 maps
- **Attacker works:** Builder walks toward enemy, attacks enemy buildings, deals damage
- **No regression:** 16/17 wins vs starter (same as Phase 4)
- **Submitted to ladder:** Bot uploaded and playing ranked matches
- **First 5+ ladder matches recorded:** Win/loss, opponent Elo, maps
- **All review agents** signed off on each change
- **Self-play doesn't crash**
- **No CPU timeouts**

## Output

Write report to `C:\Users\rahil\downloads\battlecode\phases\phase5_report.md`:
- Sentinel ammo: how it works, does it fire, replay verification
- Attacker: how it works, what it targets, replay verification
- Test results table: Phase 4 vs Phase 5 for all maps
- Military verification results (vs test_attacker bot)
- Ladder submission status and first match results (if available)
- All review agent findings and resolutions
- Known limitations
- Phase 6 recommendations based on ladder performance

Provide a summary of all file paths created or modified.
