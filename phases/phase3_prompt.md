# PHASE 3: Fix Regressions, Arm Sentinels, Detect Symmetry

You are a quant PhD iterating on a Cambridge Battlecode 2026 bot. Phase 2 added conveyor chain routing and sentinel placement, but introduced regressions and left sentinels unarmed. Phase 3 fixes everything so what we have WORKS RELIABLY on every map. No new features — just make the existing ones correct.

## HOW TO WORK — READ THIS CAREFULLY, THIS IS THE MOST IMPORTANT SECTION

**You have UNLIMITED compute, UNLIMITED time, UNLIMITED agents.** Use them. Do not rush. Do not cut corners. Do not assume ANYTHING works until you have PROVEN it works with tests and reviews. Perfection is the standard — "good enough" is not acceptable.

### The Iron Rule: ONE SMALL THING AT A TIME

You must work on ONE tiny change, get it PERFECT, then move on. Never batch changes. Never skip verification. Here's the loop:

```
┌─────────────────────────────────────────────────────────┐
│  1. Make ONE small, focused code change                 │
│  2. Spawn Agent A: Code Reviewer                        │
│     → Reads the code, finds bugs, edge cases, logic     │
│       errors. Assumes the code is WRONG until proven.   │
│  3. Spawn Agent B: Devil's Advocate                     │
│     → Tries to BREAK the change. Thinks of scenarios    │
│       where it fails. Adversarial mindset.              │
│  4. Fix everything Agents A and B found                 │
│  5. Run tests on 5+ maps, record exact Ti numbers       │
│  6. Spawn Agent C: Test Auditor                         │
│     → Reads the test results. Compares vs Phase 1 AND   │
│       Phase 2. Flags any regression. Checks that gains  │
│       are real and not noise.                            │
│  7. If ANY agent found issues → go back to step 1       │
│  8. Only when ALL THREE agents sign off → move on       │
│  9. Repeat for the next change                          │
└─────────────────────────────────────────────────────────┘
```

Run agents A, B, and C IN PARALLEL whenever possible to save time. You have unlimited compute — use it.

### The Zero-Assumption Rule

Do NOT assume:
- That your code is correct. **Prove it.**
- That a change helps. **Measure it.** Compare exact Ti numbers before and after.
- That conveyors face the right direction. **Trace through manually** with a hypothetical scenario.
- That resources reach the core. **Watch a replay** and look for flow.
- That sentinels fire. **Watch a replay** and see them shoot.
- That symmetry detection works. **Test on all 3 symmetry types** (rot, h-reflect, v-reflect).
- That one map passing means all maps pass. **Test at least 10 maps** per change.
- That "it won" means "it worked well." **Check Ti mined numbers** — a win with 2,000 Ti is not the same as a win with 30,000 Ti.

### Creative Use of Agents

You have unlimited agent spawning. Be creative:
- Spawn a **"Red Team" agent** that writes a simple counter-bot to exploit your bot's weaknesses, then test against it
- Spawn a **"Mathematician" agent** that models the resource flow mathematically — how many rounds until first delivery? What's the throughput per chain?
- Spawn a **"Map Specialist" agent** that picks the 5 hardest maps for your bot and explains WHY they're hard
- Spawn **parallel test runners** — run 5 maps simultaneously instead of sequentially
- Spawn a **"Replay Analyst" agent** that watches replays and reports what it sees (builder idle time, chain gaps, sentinel positioning)

The more perspectives you get, the more certain you can be. Don't just rely on YOUR judgment — get 3-5 agents to independently verify every change.

### What Perfection Looks Like

A change is "perfect" when:
- 3+ independent review agents agree it's correct
- It improves Ti mined on the maps it targets WITHOUT hurting any other map
- The code is clean, handles all edge cases, and has no assumptions
- You can explain exactly WHY it works, not just that it works
- You've tested it on maps of every type (small, large, choked, open, fragmented)
- You've tested with multiple seeds (at least 2 per map) to rule out luck

## Context Files (READ ALL BEFORE CODING)

1. `C:\Users\rahil\downloads\battlecode\CLAUDE.md` — Full game rules + API reference
2. `C:\Users\rahil\downloads\battlecode\bots\buzzing\main.py` — Current bot (~280 lines, Phase 2 output)
3. `C:\Users\rahil\downloads\battlecode\phases\phase2_report.md` — Phase 2 results + known issues
4. `C:\Users\rahil\downloads\battlecode\phases\phase1_report.md` — Phase 1 baseline numbers
5. `C:\Users\rahil\downloads\battlecode\research\top3_scouting.md` — What top teams do
6. `C:\Users\rahil\downloads\battlecode\research\map_analysis.md` — All 38 maps (includes symmetry types)
7. `C:\Users\rahil\downloads\battlecode\cambc\_types.py` — All types, constants, Controller API

## Current Bot Status (Phase 2)

14/14 wins vs starter, but with regressions:

| Map | Phase 1 Ti | Phase 2 Ti | Change |
|-----|--------:|--------:|-------:|
| default_small1 | 24,190 | 21,520 | **-11%** |
| default_medium2 | 26,130 | 14,170 | **-46%** |
| wasteland | 12,260 | 50 | **-99%** |
| default_small2 | 23,980 | 33,260 | +39% |
| default_medium1 | 19,200 | 32,710 | +70% |
| settlement | 38,600 | 54,650 | +42% |
| arena | 23,580 | 33,630 | +43% |
| face | 4,980 | 9,800 | +97% |

The regressions are caused by builders spending rounds walking back to core during chain-building instead of finding more ore. On maps where ore is plentiful and close, this time cost outweighs the chain connectivity benefit.

Known issues from Phase 2 reviewers:
- Sentinels never fire (no ammo supply)
- Enemy direction assumes rotational symmetry (wrong for 22/38 maps)
- Existing wrong-direction conveyors not corrected during chain-build

## Three Changes to Make (in this order)

### Change 1: Fix Regressions (HIGHEST PRIORITY)

**Root cause:** The chain-building return trip (`BUILD_CHAIN_TO_CORE` state) forces every builder to walk all the way back to core after every harvester. On some maps/seeds, this costs 20-40 rounds of travel time where the builder could be finding more ore.

**Fix approach — make chain building smarter:**
- The builder does NOT need to walk all the way back to the core. It only needs to walk back until it reaches a tile that ALREADY has a conveyor pointing toward the core (joining an existing chain).
- When the builder reaches an existing conveyor chain (a conveyor on a tile that is connected toward the core), stop the chain-build and resume ore-seeking.
- Also: if the builder is already close to the core when it places the harvester (within ~5 tiles), the chain is likely already mostly built from the outbound trip. In that case, do a quick verify-and-patch rather than a full walk-back.
- Also: cap the chain-building return trip at a maximum of 15-20 tiles. If the builder hasn't connected in 20 steps, give up and resume ore-seeking (the partial chain is better than no mining at all).

**How to detect "existing chain":** When walking back, check `c.get_tile_building_id(pos)` at each tile. If there's a conveyor (EntityType.CONVEYOR) there, check its facing direction with `c.get_direction(bid)`. If it faces generally toward the core (within 45 degrees), this chain is probably connected — stop here.

**Test after this change:**
```
cambc run buzzing starter default_medium2
cambc run buzzing starter default_small1
cambc run buzzing starter wasteland
cambc run buzzing starter settlement   # Must not regress
cambc run buzzing starter arena        # Must not regress
```
Verify: Ti mined on medium2 and small1 should recover to at least Phase 1 levels, while settlement and arena stay at Phase 2 levels.

### Change 2: Sentinel Ammo Supply

**The problem:** Sentinels are built near the core but have no conveyor delivering resources to them. They cost 30 Ti + 20% scale but never fire. This is worse than building nothing.

**Fix approach — route ammo from existing conveyor network:**
- When a sentinel is placed, note its position.
- The builder that placed the sentinel should build 1-3 conveyors connecting the sentinel to the nearest existing conveyor chain.
- Conveyors feeding the sentinel must face TOWARD the sentinel (so resources flow into it).
- Sentinels accept resources from any non-facing direction. So if the sentinel faces EAST, you can feed it from the NORTH, SOUTH, or WEST side.
- A sentinel needs 10 ammo per shot and fires every 3 rounds. So 1 stack (10 resources) every 3 rounds = pretty fast consumption. A single conveyor chain from a harvester won't supply enough for continuous fire, but any ammo is better than none.

**Simple implementation:**
- After building a sentinel at `sent_pos`, enter a brief `SUPPLY_SENTINEL` state
- Find the nearest tile with an existing conveyor or building (within 3 tiles of the sentinel)
- Build 1-3 conveyors bridging from that existing structure to the sentinel
- Each bridging conveyor faces toward the sentinel
- Exit state after 3-5 rounds (don't spend too long on this)

**Alternatively (simpler):** Just place the sentinel ADJACENT to an existing conveyor that carries resources. Then the conveyor naturally feeds the sentinel. This requires choosing the sentinel placement to be next to an active conveyor chain. Modify `_try_place_sentinel` to prefer positions adjacent to existing conveyors.

Pick whichever approach is simpler and more reliable. The goal is that sentinels get SOME ammo, even if not a dedicated supply.

**Test after this change:**
```
cambc run buzzing starter default_medium1 --watch
```
Watch the replay. Verify:
- Sentinel appears near core
- Resources visibly flow to the sentinel
- Sentinel fires when enemies approach (if starter bot sends builders near)
- If no enemies approach, at least verify ammo count increases (check in replay)

### Change 3: Map Symmetry Detection

**The problem:** Enemy core direction is calculated assuming rotational symmetry (`Position(w-1-cx, h-1-cy)`). But from the map analysis, maps use THREE symmetry types:
- Rotational (16 maps): enemy at `(w-1-cx, h-1-cy)` ✓
- Horizontal reflection (15 maps): enemy at `(w-1-cx, cy)` ← currently WRONG
- Vertical reflection (7 maps): enemy at `(cx, h-1-cy)` ← currently WRONG

Sentinels face the wrong direction on 22/38 maps.

**Fix approach — detect symmetry from visible terrain:**
On the first round, the core has vision radius² = 36 (~6 tiles). Sample visible tiles and check which symmetry matches:

```python
def _detect_symmetry(self, c):
    """Check which symmetry type the map uses."""
    pos = c.get_position()  # Core center
    w, h = c.get_map_width(), c.get_map_height()
    
    scores = {'rot': 0, 'h': 0, 'v': 0}
    total = 0
    for tile in c.get_nearby_tiles():
        env = c.get_tile_env(tile)
        total += 1
        # Rotational: (x,y) -> (w-1-x, h-1-y)
        rot_mirror = Position(w - 1 - tile.x, h - 1 - tile.y)
        # Horizontal reflection: (x,y) -> (w-1-x, y)  
        h_mirror = Position(w - 1 - tile.x, tile.y)
        # Vertical reflection: (x,y) -> (x, h-1-y)
        v_mirror = Position(tile.x, h - 1 - tile.y)
        
        if c.is_in_vision(rot_mirror) and c.get_tile_env(rot_mirror) == env:
            scores['rot'] += 1
        if c.is_in_vision(h_mirror) and c.get_tile_env(h_mirror) == env:
            scores['h'] += 1
        if c.is_in_vision(v_mirror) and c.get_tile_env(v_mirror) == env:
            scores['v'] += 1
    
    return max(scores, key=scores.get)
```

Then compute enemy core position accordingly:
```python
if sym == 'rot':
    enemy = Position(w - 1 - cx, h - 1 - cy)
elif sym == 'h':
    enemy = Position(w - 1 - cx, cy)
elif sym == 'v':
    enemy = Position(cx, h - 1 - cy)
```

**Important:** This detection only works if some mirror tiles are within vision. For cores near the center of large maps, the mirrors may also be near the center and visible. For cores in corners, the mirrors are in opposite corners and NOT visible — but in that case, ALL three symmetries give similar enemy direction (roughly "opposite corner"), so it doesn't matter much.

Run this detection ONCE in the core's first round and store the result. Pass it to builders via a marker on a core tile, or just let each builder compute it independently (wasteful but simple).

**For now:** Just compute it in the core and store on `self`. Since builders can't share globals, also have each builder compute it independently when they first see the core. The computation is cheap (~100 tiles to check).

**Test after this change:**
```
cambc run buzzing starter hourglass     # Vertical reflection
cambc run buzzing starter battlebot     # Horizontal reflection
cambc run buzzing starter default_large1  # Rotational
```
Verify sentinels face the correct enemy direction by watching replays.

## What NOT to Build

- No bridges (Phase 4)
- No splitters (Phase 4)
- No markers / communication (Phase 4)
- No offensive operations (Phase 5)
- No axionite / foundries (Phase 5+)

## Review Agents (MANDATORY at each step — spawn in parallel)

For EVERY change, you MUST spawn at least 3 agents simultaneously:

### Agent Pattern for EVERY Change:

**Agent A — Code Reviewer (skeptic):**
"Read `bots/buzzing/main.py`. Assume the code is WRONG. Find every bug, every edge case, every logic error in [specific change]. Trace through the code step by step with a concrete scenario. For example: builder at position (15, 10), core at (5, 5), harvester just placed at (16, 11). Walk through every line. Does it work? What if Ti runs out? What if the path goes through walls? What if another builder's conveyor is in the way? Be ruthless."

**Agent B — Devil's Advocate (adversarial):**
"Read `bots/buzzing/main.py`. Your job is to BREAK [specific change]. Think of the worst-case scenario. What map layout would make this fail? What seed? What if ore is in a corner surrounded by walls on 3 sides? What if the core is at the edge of the map? What if all ore is 30 tiles away? What if there are 0 axionite tiles and 2 titanium tiles? Think of 10 scenarios that could break this, and for each, explain whether the code handles it."

**Agent C — Test Auditor (data scientist):**
"Here are the test results: [paste results]. Compare every number against Phase 1 AND Phase 2. Flag ANY regression (even 5%). Calculate the average improvement. Check if gains are statistically meaningful or could be seed noise (suggest testing with 3+ seeds). Are there maps we forgot to test? Which map is most likely to regress and should be tested next?"

### After Change 1 — ADDITIONAL Regression-Specific Reviews:

**Agent D — Scenario Tracer:**
"Read `bots/buzzing/main.py`. Trace the chain-building logic for these EXACT scenarios, line by line:
1. Builder places harvester 3 tiles from core. Outbound path already has conveyors. What happens?
2. Builder places harvester 15 tiles from core. No existing conveyors on return path. What happens?
3. Builder places harvester 8 tiles from core. Tiles 3-5 on the return path have another builder's conveyors facing the wrong direction. What happens?
4. Builder places harvester. Ti drops to 5 during chain-building. What happens?
5. Builder's chain-building path goes through a 1-tile diagonal squeeze between walls. What happens?"

### After Change 2 — ADDITIONAL Ammo-Specific Reviews:

**Agent E — Resource Flow Modeler:**
"Read `bots/buzzing/main.py` and model the resource flow mathematically. How many rounds until the first resource stack reaches the sentinel? What's the throughput? If a harvester outputs every 4 rounds and the sentinel needs 10 ammo per shot every 3 rounds, will the sentinel ever accumulate enough to fire? Is the conveyor between harvester and sentinel shared with the core delivery chain? If so, does the sentinel steal resources from the core? Calculate exact numbers."

### After Change 3 — ADDITIONAL Symmetry-Specific Reviews:

**Agent F — Map Verifier:**
"Read `bots/buzzing/main.py` and `research/map_analysis.md`. For each of these maps, determine the correct symmetry type and the correct enemy core position:
- arena (rot, 25x25)
- hourglass (vert, 27x45)
- battlebot (horiz, 21x29)
- default_large2 (horiz, 50x30)
- galaxy (rot, 40x40)
- default_small2 (vert, 21x21)
Does the code compute the correct enemy position for each? Show the math."

### Final Integration Review (after ALL 3 changes):

Spawn 3 agents in parallel:

**Final Agent 1 — Full Regression Check:**
"Compare Phase 3 Ti mined vs Phase 1 AND Phase 2 for all 14+ maps. Create a table. Flag any map where Phase 3 is worse than Phase 1. Calculate overall improvement percentage."

**Final Agent 2 — Replay Verification:**
"Run `cambc run buzzing starter default_medium1 --watch` and describe what you see. Are builders finding ore? Are conveyor chains connected? Do sentinels have ammo? Do sentinels fire? Are resources flowing to the core? How many harvesters by round 200?"

**Final Agent 3 — Weakness Finder:**
"Read `bots/buzzing/main.py` and `research/top3_scouting.md`. What are the top 5 ways a real opponent (not starter bot) would beat us? What is our biggest vulnerability? What should Phase 4 prioritize? Be specific — name exact attacks, exact map types, exact scenarios."

## Testing Protocol

### Full regression suite (all maps, compare Ti mined vs Phase 2):
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
cambc run buzzing starter wasteland
cambc run buzzing starter butterfly
cambc run buzzing starter face
cambc run buzzing starter cubes
```

### Record in a comparison table:
| Map | Phase 1 | Phase 2 | Phase 3 | Sentinels | Notes |
|-----|---------|---------|---------|-----------|-------|

### Additional tests:
```bash
cambc run buzzing starter cold          # Large Ti deposits
cambc run buzzing starter galaxy        # Large open
cambc run buzzing starter binary_tree   # Tree walls
cambc run buzzing buzzing default_medium1  # Self-play (no crashes)
```

## Success Criteria

Phase 3 is DONE when:
- **No regressions vs Phase 1:** Every map mines at LEAST as much Ti as Phase 1 (not Phase 2)
- **Most maps improved vs Phase 2:** At least 8/14 maps have higher Ti than Phase 2
- **Sentinels have ammo:** Replays show resources reaching sentinels on at least 3 maps
- **Sentinels fire:** On maps where the starter bot approaches, sentinels fire (verify in replay)
- **Symmetry correct:** Enemy direction verified on 1 rotational, 1 horizontal, 1 vertical map
- **14/14 wins vs starter** (no map lost)
- **No CPU timeouts** on cubes
- **All review agents** signed off
- **Self-play doesn't crash**

## Output

Write report to `C:\Users\rahil\downloads\battlecode\phases\phase3_report.md`:
- What was changed (describe each of the 3 changes)
- Ti mined comparison table: Phase 1 vs Phase 2 vs Phase 3 for all 14 maps
- Sentinel verification: which maps show armed sentinels, do they fire
- Symmetry verification: which maps tested, was direction correct
- Review agent findings and resolutions
- Known limitations
- Phase 4 recommendations

Also provide a summary of the full file paths of everything you created or modified.
