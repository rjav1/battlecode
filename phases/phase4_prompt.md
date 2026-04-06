# PHASE 4: Scale the Economy — Bridges, More Builders, Full Map Harvesting

You are a quant PhD building a championship-tier Cambridge Battlecode bot. Phases 1-3 built a working economy with symmetry detection and sentinel placement. But we're mining 5-42K Ti per game while the #1 team (Blue Dragon) mines 30K+ consistently. The gap is because they harvest the ENTIRE map with 22 harvesters, 33 bridges, and 15+ builders. We harvest only nearby ore with 3-10 harvesters and 8 builders. Phase 4 closes this gap.

## HOW TO WORK — THE IRON RULES

**You have UNLIMITED compute, UNLIMITED time, UNLIMITED agents.** Use them ALL.

### Rule 1: ONE SMALL CHANGE AT A TIME

Do NOT write bridges + builder scaling + exploration all at once. Pick ONE. Get it perfect. Move on.

```
┌─────────────────────────────────────────────────────────────┐
│  For EACH small change:                                      │
│                                                              │
│  1. Write the code change (20-50 lines max)                  │
│  2. Spawn 3 agents IN PARALLEL:                              │
│     Agent A: Code Reviewer — finds bugs, traces edge cases   │
│     Agent B: Devil's Advocate — tries to break it            │
│     Agent C: Scenario Tracer — walks through 5 concrete      │
│              examples step by step                           │
│  3. Fix everything they find                                 │
│  4. Test on 8+ maps, 2+ seeds each                          │
│  5. Spawn Test Auditor agent — compares numbers vs Phase 3   │
│  6. If ANY regression → diagnose and fix before proceeding   │
│  7. Only when ALL agents sign off → move to next change      │
│                                                              │
│  NEVER skip step 2. NEVER skip step 4. NEVER.               │
└─────────────────────────────────────────────────────────────┘
```

### Rule 2: ZERO ASSUMPTIONS

- You think conveyors face the right way? **Trace it manually** with positions.
- You think bridges work? **Build one in a test and watch the replay.**
- You think more builders help? **Measure Ti mined with 8 vs 12 vs 15 builders.**
- You think a change improved things? **Run 3 seeds per map and compare averages.**
- "It won" is NOT proof it works well. **Check Ti mined numbers.**

### Rule 3: CREATIVE AGENT USE

Be creative with your unlimited agents:
- **Spawn a "Bridge Expert" agent** that reads the game docs and figures out optimal bridge placement patterns
- **Spawn a "Blue Dragon Reverse Engineer" agent** that reads `research/top3_scouting.md` and extracts exact build orders and timings
- **Spawn a "Map Scout" agent** that reads `research/map_analysis.md` and identifies which maps need bridges most
- **Spawn parallel test runners** — test 5 maps simultaneously
- **Spawn a "Resource Flow Mathematician"** that calculates expected Ti delivery rates for different configurations
- **Spawn a "Counter-Strategist"** that thinks about what opponents will do to our expanded economy
- **Spawn a "Red Team" agent** that writes a simple attack bot and tests if our economy survives

The more diverse perspectives you get, the more confident you can be. Don't just code and test — THINK from multiple angles.

### Rule 4: PERFECTION STANDARD

A change is "done" when:
- 3+ independent agents agree it's correct
- It improves Ti mined on target maps WITHOUT hurting others
- Tested on 10+ maps with 2+ seeds
- You can explain exactly WHY it works
- Edge cases are handled (what if no valid bridge target? what if Ti runs out mid-bridge?)

## Context Files (READ ALL BEFORE CODING)

1. `C:\Users\rahil\downloads\battlecode\CLAUDE.md` — Full game rules + API reference (ESPECIALLY the bridge section)
2. `C:\Users\rahil\downloads\battlecode\bots\buzzing\main.py` — Current bot (215 lines, Phase 3)
3. `C:\Users\rahil\downloads\battlecode\phases\phase3_report.md` — Phase 3 results
4. `C:\Users\rahil\downloads\battlecode\phases\phase2_report.md` — Phase 2 results (chain-building attempts)
5. `C:\Users\rahil\downloads\battlecode\research\top3_scouting.md` — Blue Dragon analysis (CRITICAL — read the economy section)
6. `C:\Users\rahil\downloads\battlecode\research\map_analysis.md` — All 38 maps with ore counts, distances, classifications
7. `C:\Users\rahil\downloads\battlecode\cambc\_types.py` — All types, constants, Controller API

## What Blue Dragon Does That We Don't

From `research/top3_scouting.md`:

```
Blue Dragon (2791 Elo, #1 team):
- 22 harvesters (we get 3-10)
- 308 conveyors (we get ~50-200)
- 33 bridges (we get 0) ← THIS IS HUGE
- 174 roads (we use roads minimally)
- 15+ builders (we cap at 8)
- 4 splitters (we use 0)
- 30,000+ Ti per game (we get 5K-42K)
```

Blue Dragon's economy is 3-10x ours. The main levers:
1. **Bridges** — they use 33 bridges to cross terrain and connect distant harvester sites. We use 0.
2. **Builder count** — they run 15+ builders to build infrastructure faster. We cap at 8.
3. **Full map coverage** — they harvest ORE EVERYWHERE, not just near the core.

## The Three Changes (do them in order, ONE AT A TIME)

### Change 1: Increase Builder Count

**Current:** `cap = 2 if rnd <= 40 else (4 if rnd <= 200 else (6 if rnd <= 500 else 8))`

**Target:** More builders, faster scaling. Blue Dragon runs 15+.

**But be careful:** Each builder costs 30 Ti (scaled) and adds +20% to the global cost scale. 15 builders = +300% scale. The key is that MORE HARVESTERS generate enough income to offset the higher costs.

**Approach:**
- Increase the cap gradually: 3 by round 30, 6 by round 150, 10 by round 400, 14 by round 800
- BUT only spawn when income justifies it. Check `c.get_global_resources()[0]` — if Ti is above a threshold (e.g., 200+ Ti available), keep spawning. If Ti drops below 100, slow down.
- The core should be AGGRESSIVE about spawning in early game (rounds 1-100) to get the economy rolling fast. Blue Dragon's advantage starts from the very first minute.

**What to measure:**
- Run on 5 maps with the old cap (8) and new cap (14), same seeds
- Compare Ti mined at round 500, round 1000, round 2000
- If the higher builder count results in LOWER Ti mined (because scale costs eat the income), dial back

### Change 2: Add Bridge Support

**What bridges do:**
- Bridge: 20 Ti, +10% scale, 20 HP
- Teleports resources to a target tile within distance² ≤ 9 (up to 3 tiles away)
- Bypasses normal conveyor direction rules — can feed any building from any side
- `c.build_bridge(pos, target)` — pos is where the bridge is built, target is where it sends resources
- `c.can_build_bridge(pos, target)` — checks legality

**When to use bridges:**
- When a wall blocks the straight conveyor path from harvester to core
- When the conveyor chain would need to detour 5+ tiles around an obstacle
- When connecting distant harvester sites to the main conveyor trunk line
- Blue Dragon uses bridges AGGRESSIVELY (33 per game) — they're a key part of efficient expansion

**Implementation approach:**
- During outbound navigation (`_nav`), when the builder hits a wall or obstacle that forces a long detour:
  - Check if a bridge could skip the obstacle (is there a valid tile within dist² ≤ 9 on the other side?)
  - If yes AND we can afford it (20 Ti is expensive early), build the bridge
- Alternative approach: after placing a harvester, if the conveyor chain back to core would be very long, build a bridge to shortcut it
- Start simple: add bridge-building as a fallback when conveyors can't be placed in the desired direction

**Critical rules for bridges:**
- Bridge target must be within distance² ≤ 9 of the bridge position
- Bridge has no direction — it outputs to the target tile specifically
- Bridge accepts resources from ANY adjacent tile
- Bridge costs 20 Ti + 10% scale — use judiciously (don't spam bridges for 1-tile gaps)
- Only build bridges when they save 3+ tiles of conveyor chain

**What to measure:**
- Run on fragmented maps (sierpinski_evil, butterfly, wasteland, bar_chart) with and without bridges
- Count bridges built vs conveyor count
- Compare Ti mined — bridges should help on maps with walls/gaps

### Change 3: Explore the Full Map

**Current problem:** Builders only find ore within their vision radius (~4.5 tiles). Once they harvest nearby ore, they explore in their ID-diversified direction, which is random and often inefficient.

**Target:** Builders should systematically explore the entire map, especially toward distant ore patches.

**Approach:**
- When no ore is visible, explore toward the map edges and corners — that's where undiscovered ore is
- Use the symmetry detection to know which half of the map is "ours" — prioritize exploring our half first, then the enemy half
- Spread builders out: divide the map into quadrants or sectors, assign each builder to a different sector
- When a builder finds ore and builds a harvester, it should continue exploring PAST that ore to find more distant patches, not return to the core area

**Implementation:**
- Modify `_explore` to use a smarter exploration target:
  - Instead of `far = Position(pos.x + dx * 15, pos.y + dy * 15)` (arbitrary offset)
  - Use the actual map dimensions: `Position(map_width * sector_x, map_height * sector_y)` for each builder's assigned sector
  - Each builder gets a different sector based on its ID
- Add a "frontier" concept: builders should move toward the edge of the explored area
- Track discovered ore positions on `self` to avoid revisiting empty regions

**What to measure:**
- Harvester count at round 500, 1000, 2000
- Total Ti mined
- How much of the map's ore is being harvested vs left untouched

## What NOT to Build

- No splitters (Phase 5)
- No markers / communication (Phase 5)
- No offensive operations (Phase 5+)
- No axionite / foundries (Phase 5+)
- No sentinel ammo chains (comes naturally as conveyor network grows)

## Testing Protocol

### For each change, test on these maps (2 seeds each):

**Core regression set (MUST still win all):**
```bash
cambc run buzzing starter default_small1
cambc run buzzing starter default_medium1
cambc run buzzing starter default_large2
cambc run buzzing starter settlement
cambc run buzzing starter face
```

**Bridge-critical maps (where bridges should help):**
```bash
cambc run buzzing starter butterfly      # Fragmented, 94 Ti ore
cambc run buzzing starter wasteland      # Currently losing
cambc run buzzing starter bar_chart      # Fragmented, 20 Ti
cambc run buzzing starter sierpinski_evil # 66 regions
cambc run buzzing starter cold           # 115 Ti ore
```

**Large economy maps (where more builders should help):**
```bash
cambc run buzzing starter settlement     # 148 Ti ore
cambc run buzzing starter cubes          # 134 Ti ore, 50x50
cambc run buzzing starter starry_night   # 184 Ti ore
cambc run buzzing starter dna            # 78 Ti ore, 21x50
```

### Record EVERYTHING in a comparison table:
| Map | Phase 3 Ti | Phase 4 Ti | Harvesters | Builders | Bridges | Change % |
|-----|-----------|-----------|------------|----------|---------|----------|

### Additional verification:
- Self-play: `cambc run buzzing buzzing default_medium1` — no crashes
- CPU check: `cambc run buzzing starter cubes` — no timeouts on 50x50
- Watch 3+ replays to verify bridges work, builders spread out, economy scales

## Success Criteria

Phase 4 is DONE when:
- **Ti mined improves ≥20% on average** across all maps vs Phase 3
- **Harvester count is 10+ on maps with abundant ore** (settlement, cubes, cold)
- **Bridges are used** on maps with wall obstacles (2+ bridges per game on fragmented maps)
- **Builder count reaches 10+ by round 500** on most maps
- **No regressions** — every map that Phase 3 won is still won
- **No CPU timeouts**
- **3+ review agents** signed off on each change
- **Tested on 15+ maps** with 2+ seeds each

## Output

Write report to `C:\Users\rahil\downloads\battlecode\phases\phase4_report.md`:
- Each change described with before/after comparison
- Ti mined comparison table: Phase 3 vs Phase 4 for all tested maps
- Bridge usage: which maps built bridges, how many, did they help
- Builder scaling: how many builders at round 200, 500, 1000
- Harvester count at round 200, 500, 1000
- All review agent findings and resolutions
- Known limitations
- Phase 5 recommendations

Provide a summary of all file paths created or modified.
