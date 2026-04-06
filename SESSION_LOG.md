# SESSION LOG — buzzing bees Battlecode 2026
## Written: 2026-04-04 (after ~7+ hours of continuous development)
## Purpose: Full context handoff for a future planner agent

---

## 1. CURRENT STATE (start here)

### Ladder Status
- **Elo: 1488** (rank #134 of 573)
- **Record: 24W-30L (44.4%)** across 54 matches
- **Peak Elo: 1508** (match 25, Gold tier momentarily)
- **Current trend: FLAT** — oscillating 1485-1490, not climbing
- All 54 matches played on 2026-04-06 (ladder run day)
- Nearby teams have 2,400-2,600 matches (well-converged Elos), we have only 54 (still volatile)

### Current Bot
- **File:** `C:\Users\rahil\downloads\battlecode\bots\buzzing\main.py`
- **Version: v31** (docstring says v31 — rush defense + tight-map defense)
- **Line count: 894 lines** (was 851 at v30; autoloss-fixer agent may have expanded it)
- **Submitted version on ladder:** v30 was the last confirmed clean submission. v31 is in progress.
- **What v31 added (autoloss-fixer agent, currently in progress):**
  - Earlier gunner on expand maps (round 150 vs 200) — galaxy defense
  - Barriers enabled on tight maps (round 100, 2+ harvesters) — was previously disabled
  - Sentinel building on ALL map modes after round 120 with 2+ harvesters

### Active Agent Task
- Task #43 (`in_progress`): Fix 3 auto-loss maps — galaxy 0-8, face 0-5, arena 0-4
- The autoloss-fixer agent (v31 code) is the result of this task
- Status: code written, may or may not be tested/submitted

### Key Files
- Bot: `C:\Users\rahil\downloads\battlecode\bots\buzzing\main.py`
- Prev bot: `C:\Users\rahil\downloads\battlecode\bots\buzzing_prev\main.py`
- Deploy checklist: `C:\Users\rahil\downloads\battlecode\DEPLOY_CHECKLIST.md`
- Test suite: `C:\Users\rahil\downloads\battlecode\test_suite.py`

---

## 2. WHAT WORKS (do NOT change these)

### Core Architecture: d.opposite() Conveyor System
- Every tile the builder walks on gets a conveyor facing `d.opposite()` (facing back toward where builder came from)
- This creates breadcrumb chains from core outward to harvesters
- **This is the ONLY architecture that delivers Ti to core.** Proven over 30 versions.
- **Roads-first + deliberate chain building has FAILED 3 times** (Phase 2, Phase 6, v23 experiments). NEVER try again.
- Critical reason roads-first fails: builders can't build conveyors on tiles with roads (can_build_conveyor returns False on occupied tiles), so later chain-building can't fill the road tiles.

### Sector-Based Exploration (v23 breakthrough)
- Large maps (area >= 1600): `(id + explore_idx + round//200) % 8` targeting map EDGES from core position
- Balanced maps (area 626-1599): `(mid*3 + explore_idx + round//50) % 8` core-relative, fast rotation
- Result: settlement went 19.6K → 37.3K Ti (+90%), starry_night +233%, cold +67%
- **Critical insight:** builders fan out to DIFFERENT quadrants by ID to cover the whole map

### Wall-Density + Ore-Density Adaptive Ore Scoring
- Scan visible tiles at round 5, lock in `_wall_density` and `_ore_density`
- `_check_is_maze()`: wall_density > 0.15 OR ore_density > 0.12 → use pure builder_dist ore scoring
- `_check_needs_low_reserve()`: wall_density > 0.15 AND ore_density > 0.08 → explore_reserve = 5 (not 30)
- Open maps (default_medium1): `builder_dist + core_dist*2` (prefer ore closer to core = shorter chains)
- Tight/maze maps: pure `builder_dist` (grab nearest ore ASAP, every tile contested)
- Cold fix: wall_density from diamond-shaped walls triggers maze mode → correct nearest scoring
- Butterfly fix: ore_density > 12% triggers ore-rich mode for position A (wall_density < 15% there)

### Chain-Fix for Winding Paths (v15)
- After building first 2 harvesters, if outbound path had 3+ direction changes, walk back along recorded path
- During walk-back, fix conveyors at BEHIND tiles (tiles just left, within action r^2=2)
- Fix = destroy + rebuild with correct facing
- `fix_path` capped at 30 entries (prevents CPU timeout)
- Safety: if rebuild fails, restore original direction

### Marker-Based Ore Claiming (v28-v29)
- Place `place_marker(value=1)` on claimed ore tile ONLY when distance_squared(target) > 2
- Do NOT place marker when adjacent (blocks can_build_harvester)
- Ore scan includes marker-covered tiles with +10000 score penalty (soft discourage, not hard exclude)
- Hard exclusion caused cold regression (builders saw too few targets, over-explored)
- `destroy()` before harvester build (zero action cooldown cost)

### Map-Size Adaptation
- tight (area <= 625): cap 3→5→7, no barriers, nearest-ore scoring, bridge threshold bc+10
- balanced (625-1600): cap 3→5→8→10, full features, core-proximity ore scoring
- expand (area >= 1600): cap 3→6→9→12, full features, sector exploration
- `econ_cap = max(6 + round//200 capped at 10, vis_harv*3+4)` — time-ramp prevents starvation on large maps where harvesters are outside core vision

### Proven Patterns That Work
- `d.opposite()` outbound chain architecture
- BFS pathfinding within vision (8-directional, diagonal through wall corners works)
- Ore-directed first builder spawn (v30) — saves 2-5 rounds
- Wall-density triggered maze mode for corridors, cold (different ore scoring)
- Ore-density triggered ore-rich mode for butterfly
- econ_cap floor prevents large-map builder starvation
- Marker claiming prevents duplicate ore targeting
- Explore reserve = 30 when far from core (prevents wasteful chain sprawl on large maps)
- Bridge fallback in `_nav()` when stuck (costs 20 Ti, bc+20 threshold)

---

## 3. WHAT DOESN'T WORK (proven dead ends — never revisit)

### Roads-First Navigation
- **Failed 3 times.** Phase 2 return-trip chain building: -46% on some maps. Phase 6 roads+deliberate-chains: complete failure. v23 experiment with roads-first: BROKE economy.
- Root cause: `can_build_conveyor()` returns False on tiles with roads. Roads permanently block conveyor placement on those tiles.
- Once a tile has a road, it can never become a conveyor chain link.

### 40+ Builder Scaling (v4 catastrophe)
- v4 set builder cap to 40. **Went 0-5 on ladder.** +800% scale = economy collapse.
- 15+ builders is the max before scale costs overwhelm income
- More builders without more harvesters = waste. Build harvesters first, THEN scale builders.

### Axionite Economy
- Top 3 teams (Blue Dragon, Kessoku Band, something else) all collect zero axionite
- Foundry costs +100% scale — doubles all building costs
- Ruled out after testing: Ax never mined reliably, foundry is a trap

### Launcher Drops
- Launcher r^2=26 is too short. Throws never fire in testing. Target must be passable.
- Ruled out as viable strategy.

### Attacker Builder
- Builder-as-attacker does only 2 damage per action vs 500 HP core = 250 actions minimum
- Walks to enemy laying conveyors the whole way — scale inflation with zero impact
- Current v30 has attacker kept in code but it's low-priority

### Sentinel Without Ammo
- Sentinels without ammo = 30 Ti + 20% scale for a 30 HP obstacle
- Barriers give same HP for 3 Ti + 1% scale (10x better HP/Ti ratio)
- Sentinel ammo REQUIRES splitter → branch conveyor → sentinel architecture
- Never arm sentinels without splitter infrastructure

### More Builders Without Better Exploration
- Tested builder caps of 10, 12, 15 — none improved settlement Ti beyond baseline
- smart_eco gets 41K with 8 builders because it FINDS ore efficiently, not builder count
- Extra builders without accessible ore = wasteful conveyor sprawl + higher scale costs

---

## 4. THE REAL PROBLEMS (from 54 ladder matches)

### Auto-Loss Maps (0 wins)
| Map | Record | Severity |
|-----|--------|----------|
| galaxy | 0-8 | Critical — 8 games lost = 0% ever |
| face | 0-5 | Critical — core destroyed twice (137t, 319t) |
| arena | 0-4 | Critical — structural economy failure |

These 3 maps alone account for ~17 individual game losses. If we went 50/50 on them, ~8-9 extra wins = ~30-50 Elo gain.

**galaxy:** Large open map. Opponents have better exploration that finds more of the distributed ore. We mine too little.

**face:** Compact map, cores close together. Core destroyed at turn 137 (Warwick CodeSoc) and 319 (Polska Gurom). Our bot has no early rush defense. Need barriers/sentinels earlier on compact maps.

**arena:** 25x25 rotational map. Smart_eco mines 3.4x more from position B than we do. Position A vs B matters enormously. Even after v26 nearest-ore fix (+22% on position A), smart_eco still out-mines us.

### 4 Nemesis Teams (0-14 combined record)
| Team | Record | Elo | Notes |
|------|--------|-----|-------|
| The Defect | 0-4 (5-15 maps) | 1521 | Beats us on ALL map types. Fundamentally better economy. |
| KCPC-B | 0-4 (4-16 maps) | 1472 | Lower Elo than us but 0-5 sweeps. True Elo may be ~1550+, only 62 matches. |
| One More Time | 0-3 (4-11 maps) | 1523 | 40-49 bots, pure economy, connected conveyor chains, no military. Cold: 3.14x more Ti with HALF our harvesters. |
| Polska Gurom | 0-3 (6-9 maps) | 1476 | Solo player, dual competency: Core Destroyed us turn 319 on face AND beats us on economy maps. |

These 4 teams account for 14 of 30 losses (47%). If we went 50/50 against them, we'd gain ~40-50 Elo to ~1530-1540.

### Core Destroyed Vulnerability
- Warwick CodeSoc destroyed our core in 137 turns on face (and 190 turns on shish_kebab)
- Core has 500 HP. They dealt 500 damage in 137 turns = ~3.6 HP/turn average
- Our barriers and early gunners don't trigger early enough on compact maps

### Chain Connectivity Gap (root cause of all economy losses)
- We build 30-43 harvesters but collect 2-3x LESS Ti than opponents with 8-22 harvesters
- One More Time's cold game: their 22 harvesters collected 3.14x more than our 43 harvesters
- Root: d.opposite() chains break on winding paths. Only harvesters whose path happens to be straight deliver to core.
- The constrained_maps_analysis.md proved: on corridors, EXACTLY 1 harvester's output reaches core (9,930 Ti = 1 harvester + passive income). All other harvesters' chains are broken.

### Real Opponents vs Local Testing Gap
- **Local win rate: ~85%** (vs our own test bots)
- **Ladder win rate: 44.4%** (vs real opponents)
- Real opponents run 40-49 bots with connected conveyor chains
- Our test suite uses bots that play similar to us — doesn't reflect the enemy

### Resource Hoarding
- Real opponents keep bank <300 Ti at all times
- We hoard 3,000-18,000 Ti unspent (worthless for Resource Victory tiebreaker)
- Resource Victory is based on TOTAL COLLECTED, not bank balance

---

## 5. VERSION HISTORY (chronological)

### Phases 1-5 (Foundation)

**v1 (Phase 1) — ~150 lines**
- Pure economy bot: d.opposite() conveyors, BFS nav, ID-diversified exploration
- 14/14 local wins but no military and many architectural gaps

**v2 (Phase 2, ladder submission) — ~280 lines**
- Added chain-building return trip state machine + sentinel defense
- Chain-build: major improvement on some maps, regression on others
- Sentinels unarmed (no ammo supply)
- **SUBMITTED:** First ladder version

**v3 (Phase 3) — ~215 lines**
- Removed chain-building (caused net regression)
- Added symmetry detection (rotational/horizontal/vertical)
- Improved sentinel placement adjacent to conveyors
- 13/14 local wins (wasteland always loses)

**v4 (Phase 4, DISASTER) — ~260 lines**
- TRIED: Builder cap ramp to 40 max
- **0-5 on ladder. Economy collapse. Scale explosion.**
- Also added improved exploration rotation + bridge fallback
- Bridge fallback (reactive) kept; builder scaling REVERTED

**v5 (Phase 5) — ~260 lines**
- Added basic attacker (1 builder/4 toward enemy core)
- Sentinel ammo attempts failed — requires splitters (Phase 6+)
- **SUBMITTED:** Version 2 on ladder

### Versions 6-15 (Economy Tuning)

**v6-v9** — incremental tuning, not individually documented

**v10 — Map-Size Adaptation**
- Round 1 map detection: tight (<=625) / balanced (625-1600) / expand (>=1600)
- Mode-specific builder caps
- 5/5 wins in regression
- **SUBMITTED**

**v11 — Gunners Replace Sentinels**
- Gunners: 10 Ti + 10% scale vs sentinels: 30 Ti + 20% scale
- Simpler placement (no splitter needed, gunners use direct fire)
- 5/5 regression wins
- **SUBMITTED**

**v12 — Lower Bridge Threshold**
- Bridge threshold: bc+50 → bc+20 (normal), bc+10 (tight)
- Bridge priority raised above road in `_nav()`
- Cold: +192%, galaxy: +198%
- 5/5 regression wins
- **SUBMITTED**

**v13 — No Barriers on Tight Maps + Delayed Military**
- No barriers on tight maps (saves 18 Ti)
- Gunner trigger: round 200→400, attacker trigger: round 500→700
- Economy compounds longer before military investment
- 5/5 regression wins

**v14 — Lower Reserves + Faster Exploration**
- Core spawn reserve: cost+10 → cost+5
- Builder harvester reserve: cost+15 → cost+5
- Explore rotation: every 150 rounds → every 100 rounds
- default_medium1: +32.5%, face: +61.3%
- 5/5 regression wins

**v15 — Chain-Fix for Winding Conveyor Paths**
- Path recording during navigation (capped at 30 entries)
- After building 2+ harvesters, if path had 3+ direction changes, walk back and fix
- Fix during walk-back: destroy + rebuild with correct facing on ADJACENT tiles
- cold: +119%, default_medium1: +427%
- 5/7 wins in regression (hourglass and shish_kebab regressions)

**v16 — shish_kebab Exploration + Early Barrier Anti-Rush**
- shish_kebab: explore range = max(w,h) on tight maps
- Early barriers: 2 barriers near core after first harvester built
- galaxy vs rusher: survived to turn 2000 (was core destroyed at turn 86)
- 5/5 regression wins
- **SUBMITTED AS VERSION 18**

**v17 — Raise econ_cap Multiplier**
- `econ_cap = vis_harv * 3 + 4` (was *2+3)
- Allows more builders when more harvesters visible
- default_medium1 vs smart_eco: now LEADING (+3090 Ti)
- 5/5 regression wins

**v18 — econ_cap Floor**
- `econ_cap = max(6, vis_harv * 3 + 4)`
- Floor of 6 prevents builder starvation on large maps where harvesters are outside vision
- 3/5 regression wins (meets threshold)

### Versions 19-30 (Feature Development)

**v19 — Harvest Axionite Ore**
- Scan includes `ORE_AXIONITE` alongside `ORE_TITANIUM`
- default_medium1: 34,734 Ti (massive improvement)
- 4/5 regression wins (corridors symmetric tie)
- **SUBMITTED AS VERSION 21**

**v20 — Prefer Ore Closer to Core**
- `score = builder_dist + core_dist * 2` (was just builder_dist)
- Shorter conveyor chains = more efficient delivery
- default_medium1: +62%, settlement: +big improvement
- 3/5 regression wins (cold and corridors regressions)
- **SUBMITTED AS VERSION 22**

**v21 — Simplify Gunner Placement**
- Replaced complex splitter-based gunner state machine with simple direct placement
- Find any empty adjacent tile → build gunner facing enemy
- No chain destruction (old method destroyed a working conveyor)
- 4/6 wins (tested both positions)

**v22 — Wall-Density-Adaptive Ore Scoring**
- Scan visible tiles at round 5, compute wall fraction
- wall_density > 0.15 → maze mode → pure builder_dist scoring
- wall_density <= 0.15 → open mode → core_dist*2 scoring
- corridors: +49% (maze mode), cold: +71%, default_medium1: no regression
- 5/6 wins
- **SUBMITTED AS VERSION 24**

**v23 — Sector-Based Exploration on Large Maps**
- Large maps (area >= 1600): `(id + explore_idx + round//200) % 8` targeting edges
- No *3 multiplier — consecutive IDs get adjacent sectors, covering all 8 directions
- settlement: 19.6K → 37.3K (+90%), starry_night +233%, cold +67%
- **NOW BEATS smart_eco on settlement**

**v24 — Sector Exploration Extended to Balanced Maps**
- Balanced maps (area 626-1599): `(mid*3 + explore_idx + round//50) % 8`
- Fast rotation (every 50 rounds vs 200) — sweeps sectors quickly
- cold: +23-145%, corridors: symmetric, default_medium1: marginal
- 4/6 wins
- **SUBMITTED AS VERSION 26**

**v25 — Reduce Wasteful Exploration Conveyors**
- explore_reserve = 30 when builder is >7 tiles from core (dist_sq > 50)
- Reduces wasteful conveyors in areas unlikely to connect to core
- time_floor = min(6 + round//200, 10) — gradually ramps builder floor
- cold vs smart_eco: +64%, corridors: +96%
- cold P1 still loses (mining more but spending more on buildings = net loss by 1500 Ti)

**v26 — Nearest-Ore Scoring on Tight Maps**
- `use_nearest = is_maze or map_mode == "tight"` 
- Tight maps now use pure builder_dist like maze maps
- arena +22% from position A
- 4/4 regression wins
- **SUBMITTED** (as version 28 or similar)

**v27 — Ore-Density Detection for Butterfly**
- Added `_ore_density` tracking alongside wall_density
- `_check_is_maze()`: wall_density > 0.15 OR ore_density > 0.12
- `_check_needs_low_reserve()`: wall_density > 0.15 AND ore_density > 0.08 (AND avoids cold false-positives)
- butterfly position A: +16.7%, position B: +10.7%
- Now wins 1-1 vs smart_eco on butterfly (was 0-2)
- **SUBMITTED**

**v28 — Marker-Based Ore Claiming**
- `place_marker(value=1)` on target ore tiles to signal intent
- Other builders skip tiles with allied markers (except our own)
- BUG: marker placement on ore blocked can_build_harvester → cold regressed
- 4/6 wins (galaxy improved, but cold regressed)
- **SUBMITTED** (later fixed by v29)

**v29 — Fix Cold Regression (Marker Distance Guard)**
- Only place claim marker when distance_squared(target) > 2 (not adjacent)
- Include marker-covered tiles in ore scan with +10000 score penalty (not hard-exclude)
- Don't abandon target when marker (vs real building) is on ore tile
- cold restored to v27 baseline, no regressions
- **SUBMITTED**

**v30 — Spawn First Builder Toward Nearest Ore**
- In `_core`, when spawning first builder (units == 0), scan visible tiles for nearest ore
- Try that direction first → builder starts moving toward ore immediately
- Saves 2-5 rounds → ~50-125 extra Ti over 2000-round game
- 4/6 wins (cold/settlement losses are map asymmetry, not regressions)
- **SUBMITTED — this is the last confirmed clean submission**

**v31 — Rush Defense + Tight-Map Defense (IN PROGRESS, autoloss-fixer agent)**
- Earlier gunner on expand maps: round 150 instead of 200
- Barriers enabled on tight maps: round 100, requires 2+ harvesters
- Sentinel building on ALL map modes after round 120 with 2+ harvesters
- Targeting galaxy 0-8, face 0-5, arena 0-4
- **Status unknown — may be partially tested or awaiting test/submission**

---

## 6. INFRASTRUCTURE (tools and test bots)

### Test Opponent Bots (in `C:\Users\rahil\downloads\battlecode\bots\`)
| Bot | Purpose |
|-----|---------|
| `adaptive/` | Map-size adaptive bot (beat buzzing 4-2 in v23 experiments) |
| `axionite_first/` | Tests axionite economy (RULED OUT) |
| `balanced/` | Balanced strategy bot |
| `barrier_wall/` | Barrier-heavy defensive bot |
| `bridge_expand/` | Bridge-focused expansion |
| `buzzing/` | Current live bot |
| `buzzing_prev/` | Previous version baseline |
| `buzzing_v24/` | Snapshot at v24 |
| `eco_debug/` | Debug bot for economy tracing |
| `eco_opponent/` | Economy-focused opponent |
| `fast_expand/` | Fast expansion tester |
| `gunner_defense/` | Gunner-based defense |
| `launcher_drop/` | Launcher drop strategy (RULED OUT) |
| `rusher/` | Rush strategy bot (for testing defense) |
| `sentinel_spam/` | Heavy sentinel strategy |
| `smart_defense/` | Smart defensive bot |
| `smart_eco/` | Clean economy bot with same d.opposite() pattern (our primary regression target) |
| `smart_hybrid/` | Hybrid economy+defense |
| `splitter_test/` | Proof-of-concept splitter→sentinel ammo delivery |
| `starter/` | Official starter bot |
| `test_attacker/` | Test attacker strategy |
| `turtle/` | Turtle defensive strategy |

### Test Suite
- **File:** `C:\Users\rahil\downloads\battlecode\test_suite.py`
- 108 games: 6 opponents × 6 maps × 3 seeds
- Exit code 0 if >60% win rate, non-zero if failing
- Run time: ~5 minutes
- Note: had `ModuleNotFoundError: No module named 'cambc.cambc_engine'` issue — use `bin/cambc.exe` directly

### Deploy Checklist
- **File:** `C:\Users\rahil\downloads\battlecode\DEPLOY_CHECKLIST.md`
- Regression: 5 maps vs buzzing_prev, need 3/5 wins
- Self-play crash test on default_medium1
- Ti mined check: medium+ maps should mine >10K
- Submission via API

### Research Documents
| File | Content |
|------|---------|
| `research/ladder_deep_review.md` | CRITICAL: Complete 54-match analysis with Elo trajectory, map W/L, opponent records |
| `research/nemesis_analysis.md` | Deep analysis of 4 teams we've never beaten (The Defect, KCPC-B, One More Time, Polska Gurom) |
| `research/top3_scouting.md` | Blue Dragon (#1), Kessoku Band (#2), something else (#3) strategies |
| `research/strategic_assessment.md` | Brutally honest gap analysis — written early, still accurate |
| `research/strategy_refresh.md` | Fresh eyes review at v20 — identified nav/chain separation as root issue |
| `research/constrained_maps_analysis.md` | Why cold/corridors/shish_kebab fail: d.opposite() breaks on winding paths |
| `research/economy_debug.md` | First economy debug — identified 8 root causes |
| `research/splitter_test_results.md` | PROVEN: Harvester→Conv→Splitter→BranchConv→Sentinel delivers ammo in 1 round |
| `research/robust_testing_guide.md` | Statistical framework: need 12 matches to detect 20pp improvement, 40 for 10pp |

### Key Numbers to Remember
- Splitter→sentinel ammo delivery cost: 62 Ti total (harvester 20 + conv 3 + splitter 6 + branch 3 + sentinel 30)
- Sentinel ammo arrives within 1 round of placement
- Splitter sends ~1/3 of resource stacks to branch (alternates 3 outputs)
- Passive income: 10 Ti every 4 rounds = 2.5 Ti/round
- Per harvester: 2.5 Ti/round
- Blue Dragon: 308 conveyors, 33 bridges, 22 harvesters, 20 sentinels, 15+ builders → 30K+ Ti

---

## 7. NEXT STEPS (what to work on)

### Immediate (autoloss-fixer in progress)
Task #43 is `in_progress`. The autoloss-fixer agent wrote v31 which attempts to fix galaxy/face/arena. Before proceeding:

1. **Verify v31 test results.** If not yet tested, run regression (5 maps vs buzzing_prev, 3/5 wins required).
2. **Check if v31 actually helps galaxy/face/arena** — run each against starter/rusher.
3. **Submit if tests pass.** Update buzzing_prev after submission.
4. Mark task #43 as `completed`.

### High Priority (post-autoloss-fix)
**Deep Economy Fix: Chain Connectivity**

The core problem from the nemesis analysis: we build 30-43 harvesters but collect 2-3x LESS Ti than opponents with 8-22 harvesters. The root cause is CHAIN CONNECTIVITY — d.opposite() creates chains that work on straight paths but break on winding paths.

However: ROADS-FIRST HAS FAILED 3 TIMES. Do not attempt roads-first.

The specific thing to investigate: **Why do our chain-fix (v15) and winding path repair work on some maps but not solve the full gap?** The nemesis replay analysis shows One More Time gets 3.14x more Ti on cold with HALF our harvesters. Their connected network is the key.

Potential approaches (to be explored carefully):
- Increase chain-fix trigger sensitivity (currently triggers only on 3+ direction changes, first 2 harvesters)
- Extend chain-fix to ALL harvesters, not just first 2
- Add chain-verification: periodically check if harvesters are delivering (Ti at core increasing?)

### Medium Priority
**Armed Gunners (splitter-based ammo)**

The splitter_test_results.md proved the pattern works:
```
Harvester → Conv(chain_dir) → Splitter(chain_dir) → Branch(perp_dir) → Sentinel(perp_dir)
```

Implementation needs:
- Insert splitter into existing conveyor chain (destroy one conveyor, rebuild as splitter)
- Add branch conveyor perpendicular to chain
- Build sentinel facing same direction as branch conveyor
- Timing: after 4+ harvesters, only on non-tight maps
- Do NOT build sentinels without this infrastructure (30 Ti wasted as obstacle)

### Medium Priority
**Marker Coordination Expansion**

Current markers only claim ore tiles. Could expand to:
- Mark explored zones (prevent builders from re-exploring same area)
- Mark enemy positions (signal enemy sightings to other builders)
- Mark chain gaps (builders near a broken chain signal for repair)

### Long-Term
**40+ Bot Scaling (only if economy supports it)**

The nemesis bots run 40-49 builders. We cap at 12. But more builders only help if:
1. Economy generates enough Ti to cover scale costs
2. Builders find ore efficiently (exploration solved)
3. Chains actually deliver (chain connectivity solved)

Don't attempt until chain connectivity is fixed and Ti mined is consistently >25K on medium maps.

---

## 8. MANAGEMENT PRINCIPLES

### Workflow Rules (from management_principles.md)
1. **Small blocks only.** One feature per agent. Never "implement A + B + C" in one task.
2. **Never wait for user input.** Always have wheels turning. If one agent blocked, parallelize.
3. **Always delegate.** Planner never does hands-on coding. Spawn agents for everything.
4. **PhD/quant mindset.** Hypothesis → experiment → data → conclusion. Measure everything.
5. **BFS not DFS.** Test multiple strategies in parallel. Let data decide.

### Model Allocation
- **Opus:** Creative/complex problems (strategy design, architecture decisions, debugging novel issues)
- **Sonnet:** Execution tasks (testing, deploying, following clear instructions, running matches)
- **Haiku:** Simple tasks (git sync, file reads, status checks)

### Context Management
- Fresh agents > long-running ones. After 10+ messages, spawn replacement with fresh brief.
- Every agent prompt must be self-contained — include ALL context files.
- Subagents CANNOT use SendMessage on Windows (in-process mode limitation). Use files for coordination.

### Agent Coordination Rules
- Files on disk = primary coordination between agents
- Never assign 2 agents to same file (risk of overwrites)
- 3-5 focused agents > 10 scattered ones
- Always verify agent claims — they think they're always right
- Critic → Verifier pipeline catches both real bugs AND false alarms

### Testing Standards (from robust_testing_guide.md)
- **Never revert after single match loss.** A 55% win rate bot has 40.7% chance of losing any given match.
- **Revert only if:** 5+ matches AND win rate < 30% AND local testing confirms regression
- **Regression gate:** 5 maps vs buzzing_prev, 3/5 wins required (minimum bar)
- **Strong gate:** Run both positions (A vs B AND B vs A) for reliable results
- **Paired comparison:** Always test same (map, seed) pairs to eliminate map variance
- Statistical note: need ~40 matches to detect 10pp improvement; ~12 for 20pp improvement

### User Profile (from user_profile.md)
- Wants PhD/quant-level rigor — data-driven, no assumptions, measure everything
- Full delegation — planner never does hands-on work
- Assembly-line workflow with review loops (build → critic → verifier → fix → test)
- Nonstop execution — never wait for user input
- BFS exploration of strategies — test multiple approaches in parallel
- Goal: #1 on leaderboard. International qualifier: April 20, 2026.

---

## 9. CRITICAL NUMBERS SUMMARY

| Metric | Value |
|--------|-------|
| Current Elo | 1488 |
| Peak Elo | 1508 (match 25) |
| Rank | #134 / 573 |
| Matches played | 54 |
| Win rate | 44.4% (24W-30L) |
| Galaxy record | 0-8 |
| Face record | 0-5 |
| Arena record | 0-4 |
| vs nemeses | 0-14 |
| Local test win rate | ~85% |
| Ladder win rate | 44.4% |
| Qualifier date | April 20, 2026 |
| Bot lines | 894 (v31) |
| Blue Dragon conveyors | 308 |
| Our conveyors | ~20-50 |
| Blue Dragon Ti/game | 30,000+ |
| Our Ti/game | 10,000-25,000 |

---

## 10. SPLITTER AMMO PATTERN (proven, ready to implement)

Exact pattern from `research/splitter_test_results.md`:

```
Harvester (on Ti ore)
    ↓
Conv1 (facing chain_dir)  ← picks up Ti from harvester
    ↓
Splitter (facing chain_dir)  ← accepts from Conv1 behind it
    ↓ (branch output)
Branch Conveyor (facing perp_dir = chain_dir.rotate_left.rotate_left)
    ↓
Sentinel (facing perp_dir)  ← ammo enters from opposite side (correct!)
```

Rules:
1. Splitter faces chain_dir (same as conveyors in main chain)
2. Branch conveyor on one of splitter's 3 forward output tiles, facing perpendicular (90°)
3. Sentinel faces SAME direction as branch conveyor
4. Do NOT face sentinel toward branch conveyor (that would BLOCK ammo entry)
5. Ammo arrives within 1 round of sentinel placement
6. ~1/3 of Ti stacks go to sentinel (splitter alternates 3 outputs)

Cost: 62 Ti total. Infrastructure complete in ~6-10 rounds.

---

*Log written 2026-04-04 from 30 phase reports, 8 research documents, 3 memory files, and current bot state.*
*Next planner: read this log, check current bot file for v31 test status, then continue from Section 7.*
