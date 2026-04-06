# MASTER ROADMAP: Win the International Qualifier
## Team buzzing bees | Target: #1 | Qualifier: April 20, 2026
## Synthesized from Advisor Alpha (Quant), Beta (Architect), Gamma (Meta-Researcher)

---

## EXECUTIVE SUMMARY

**The meta is economy-dominated.** Featured games at the top routinely go to 2000 rounds (tiebreaker wins). Core destruction is rare among top teams. This means the winning bot must:

1. Build the strongest economy possible (harvesters + conveyor chains)
2. Defend it with efficient turrets (sentinels with stun, gunners at chokes)
3. Disrupt the enemy economy (launcher drops, builder raids)
4. Optimize for tiebreakers when core destruction isn't achievable
5. Adapt strategy based on map layout and enemy behavior

**The strategy: Adaptive Turtle.** Default to economy + defense, but detect and counter aggression. Shift to offense when economically dominant.

---

## CRITICAL NUMBERS

| Metric | Value | Why |
|--------|-------|-----|
| Optimal builders | 3-4 | Each is +20% scale; diminishing returns past 4 |
| Harvesters target | 5-8 | Payback in ~15 rounds; 490 Ti lifetime ROI each |
| Foundries | 0 or 1 | +100% scale; only if Ax ore accessible + need refined Ax |
| Foundry timing | After round 200-300 | Build AFTER main infrastructure to minimize scale damage |
| First harvester | By round 10-15 | Every round delayed = ~2.5 Ti/round lost |
| First turret | By round 100-150 | After 3+ harvesters connected |
| Submit by | Day 4-5 (Apr 9-10) | Need 100+ matches for rating; matches every 10 min |
| Min games for rank | 100+ | ~17 hours of continuous matchmaking |
| Target Elo | 2200+ (Master) | Top 20 qualifier territory |

---

## PHASE 0: FOUNDATION (Days 1-2, Apr 5-6)

### Goal: Working economy bot that beats starter on all maps

**Architecture** (multi-file, from Advisor Beta):
```
bots/buzzing/
  main.py               # Player class, thin dispatcher
  constants.py           # Thresholds, marker types, magic numbers
  utils.py               # fast_direction(), Position helpers

  roles/
    core_brain.py         # Spawning, conversion, marker hub
    economy_builder.py    # Ore finding, harvester + conveyor building
    military_builder.py   # Turrets, ammo supply
    scout.py              # Exploration, enemy intel
    attacker.py           # Offensive operations
    turret_brain.py       # Auto-fire logic

  systems/
    markers.py            # Encode/decode u32 protocol
    pathfinding.py        # BFS with CPU budgeting
    symmetry.py           # Map symmetry detection
```

**Deliverables:**
1. Core spawns 3 builders
2. Builders find ore, build harvesters, lay conveyor chains to core
3. Greedy movement with road-building (build road, move next round)
4. Basic resource management (check affordability before building)

**Gate:** Beats starter bot 5/5 on default maps. No TLE on `cambc test-run`.

---

## PHASE 1: ROBUST ECONOMY (Days 2-4, Apr 6-8)

### Goal: Reliable 4-6 harvester economy with connected supply chains

**Tasks:**
1. BFS pathfinding with CPU budget awareness (max 400 nodes, bail at 1500us)
2. Conveyor chain planning: BFS from harvester to core, each step = conveyor
3. Ore scanning: `get_nearby_tiles()` → filter `ORE_TITANIUM/ORE_AXIONITE`
4. Budget-aware building: always reserve 50 Ti emergency buffer
5. Scale monitoring: check `get_scale_percent()`, halt non-essential building above 250%
6. Edge cases: no ore near core (send builders far), ore behind walls, all ore taken

**Key insight from Alpha:** Conveyor length does NOT affect steady-state throughput (still 1 stack/4 rounds). Only latency. Minimize chain length but don't obsess.

**Key insight from Beta:** Cache ALL API calls. Call `get_nearby_tiles()` ONCE per round. Each Rust→Python crossing costs 2-50us.

**Gate:** 4+ harvesters connected by round 80 on 18/20 maps. Win rate vs starter ≥ 90%.

---

## PHASE 2: MARKER COMMUNICATION (Days 4-5, Apr 8-9)

### Goal: Coordinated builder behavior via marker protocol

**Protocol (from Advisor Beta):**
```
Bit layout: [TYPE:4][ROUND_STAMP:10][PAYLOAD:18]

Types:
  0x1 = ORE_FOUND        [ore_type:1][x:8][y:8]
  0x2 = HARVESTER_BUILT   [x:8][y:8]
  0x3 = ENEMY_SPOTTED     [entity_type:4][x:8][y:8]
  0x4 = ENEMY_CORE        [x:8][y:8][confidence:2]
  0x5 = ROLE_CLAIM        [role_id:3][builder_id_low:15]
  0x9 = BUILDER_COUNT     [role0:3][role1:3][role2:3][role3:3]
  0xA = RESOURCE_STATUS   [ti_bucket:4][ax_bucket:4][scale:4]
  0xB = MAP_SYMMETRY      [sym_type:2][confidence:2]

Staleness: age = (current_round - stamp) % 1024. Stale if > 100 rounds.
```

**Bulletin Board (core tiles):**
The core's 9 tiles serve as fixed communication channels. Core updates the most critical marker each round (rotates through them). Builders read on spawn and when passing.

**Coordination rules:**
- Core assigns builder roles via spawn-tile marker
- Builders claim ore tiles with HARVESTER_BUILT markers (prevents duplicates)
- Scouts place ENEMY_SPOTTED markers along their path
- Round-stamped markers let readers judge freshness

**Gate:** No duplicate harvesters. Builders spread to different ore patches on 20 maps.

---

## PHASE 3: MAP INTELLIGENCE + DEFENSE (Days 5-7, Apr 9-11)

### Goal: Symmetry detection, enemy core prediction, turret defense line

**Map symmetry** (from Advisors Alpha + Beta):
- Maps guaranteed symmetric (reflection or rotation)
- Test point-reflection: tile(x,y) env == tile(w-1-x, h-1-y) env
- Test h-reflection: tile(x,y) env == tile(w-1-x, y) env
- Test v-reflection: tile(x,y) env == tile(x, h-1-y) env
- Pick highest-scoring match from visible tiles
- Predict enemy core = mirror of own core position under detected symmetry

**Turret placement:**
- Gunners (cheap, 10 Ti) facing enemy approach at choke points
- Sentinels (30 Ti) behind chokes for area denial — stun is devastating with refined Ax
- Place turrets where conveyor supply is easy (branch from existing chains)

**Ammo supply:**
- Splitter from harvester chain → branch to turrets
- Each gunner needs 2 ammo/shot, fires every round → 1 stack/5 rounds needed
- Each sentinel needs 10 ammo/shot, fires every 3 rounds → 1 stack/3 rounds

**Gate:** Enemy core predicted correctly 18/20 maps. Turrets operational by round 150. Kills enemy scouts.

### SUBMIT TO LADDER (Apr 10-11, Sprint 4 snapshot)

---

## PHASE 4: OFFENSE + ADAPTATION (Days 7-10, Apr 11-14)

### Goal: Disrupt enemy economy, adapt to opponent behavior

**Offensive toolkit:**
1. **Launcher drop** (highest leverage): Build launcher near front, throw builder into enemy base. Builder uses `destroy()` on allied buildings, `fire()` on enemy buildings (2 dmg, 2 Ti, own tile only). One builder inside can dismantle economy in 10-20 rounds.
2. **Builder raids**: Road network toward enemy, destroy conveyors (cut supply lines)
3. **Conveyor denial**: Build barriers on key tiles between enemy harvesters and core

**Adaptive logic:**
- **If enemy scouts near base early (round < 100):** Shift to defense, build barriers + gunner
- **If no enemy contact by round 200:** They're turtling → build launcher, prepare raid
- **If losing economy race:** Go aggressive early, cut their supply lines
- **Phase transitions:** Early (1-100) pure economy → Mid (100-800) military + expansion → Late (800-2000) tiebreaker optimization

**Tiebreaker strategy (from Alpha):**
- TB#1: Refined Ax delivered to core → build 1 foundry, pipe refined Ax to core
- TB#2: Ti delivered to core → keep harvesters + chains alive
- TB#3: Living harvesters → protect them with barriers
- `c.convert()` moves Ax→Ti stat. Do NOT convert if winning TB#1. DO convert if losing TB#1 to try winning TB#2.

**Gate:** Disrupts enemy economy 15/20 maps. Destroys core 5/20 maps. Beats Phase 3 bot ≥ 55%.

---

## PHASE 5: OPPONENT STUDY + COUNTER-META (Days 10-13, Apr 14-17)

### Goal: Study top 20, build counters, tune parameters

**Replay study protocol (from Gamma):**
For each top-20 team, watch 3+ replays and record:
- First harvester round, total harvesters, foundry timing
- Builder count, turret types/count, first turret round
- Offensive actions: launcher usage, builder raids, timing
- Map-specific adaptations
- Win condition (core destroyed vs tiebreaker N)

**Counter-strategy matrix:**

| They Play | We Counter With |
|-----------|----------------|
| Economy turtle | Launcher drop + builder raid; cut conveyors |
| Early rush | Barriers + sentinel stun wall; punish weak economy |
| Turret fortress | Out-economy them; tiebreaker win |
| Launcher aggression | Inward-facing gunners; armoured conveyors |
| Sentinel stun wall | Breach from safe distance; or just out-economy |

**Parameter tuning (run 50+ games per config):**
- Builder count: test 3 vs 4 vs 5
- Harvester target: test 4 vs 6 vs 8
- Attack timing: test round 200 vs 300 vs 400
- Foundry timing: test round 150 vs 250 vs never
- Turret count: test 2 vs 4 vs 6

**Map-specific logic:**
- Small maps (20-25): faster aggression, fewer harvesters needed
- Large maps (40-50): more economy focus, launchers for reach
- Choke maps: sentinel + barrier walls dominate
- Open maps: expansion speed matters most

**Gate:** Win rate ≥ 60% vs previous version. Elo climbing on ladder.

---

## PHASE 6: HARDENING + QUALIFIER PREP (Days 13-16, Apr 17-20)

### Goal: Zero crashes, zero TLE, maximum consistency

**Robustness sweep:**
1. Run all 38 maps × 10 seeds = 380 games. Fix any failures.
2. Remote test-run: 100 games. Zero TLE tolerance.
3. Edge cases: core in corner, no nearby ore, narrow corridors, 50x50 maps

**CPU optimization:**
- Profile every major function with `c.get_cpu_time_elapsed()`
- Replace `position.direction_to()` with precomputed sign-based lookup
- Use `collections.deque(maxlen=N)` for bounded history
- Bail-out check before every expensive block: `if elapsed > 1500: return`

**Final tuning:**
- Submit daily to ladder, analyze losses
- Iterate on specific matchups where we lose
- Accumulate 200+ matches for reliable Elo

**Anti-fragility:**
- Bot must never hard-lose to anything (floor > ceiling)
- If something fails, gracefully degrade (no economy? still build turrets. No turrets? still play for tiebreaker)
- Every state machine has timeout transitions (stuck > 20 rounds → reset)

**Gate:** Elo ≥ 2000 (Candidate Master). Zero TLE. ≥ 55% win rate vs top 50.

---

## KEY EXPLOITS & EDGES

1. **Walk on enemy conveyors:** Conveyors are walkable by ANY team. Enemy's conveyor highway = your infiltration route.

2. **Builder-on-building tanking:** If a builder bot stands on a building, turret attacks hit ONLY the builder (30 HP shield for the building underneath).

3. **Destroy is free:** `destroy()` on allied buildings costs no action cooldown. A builder can demolish multiple own-buildings per round. Enemy buildings require `fire()` (2 dmg, 2 Ti, own tile).

4. **Scale warfare:** Destroying enemy buildings reduces THEIR cost scaling. Raid enemy conveyors = double benefit (cut income + reduce their scale).

5. **Launcher range beats most turrets:** Launcher r²=26 > Gunner r²=13, Breach r²=5. Can throw builders over turret defense lines.

6. **Sentinel stun lock:** 2 sentinels with refined Ax on the same lane = permanent stun (+5 action/move cooldown each, sentinel reloads in 3 rounds).

7. **Foundry last:** Build foundry AFTER all other infrastructure to minimize the +100% scale penalty on everything else.

8. **Resource can feed enemies:** Conveyors can accidentally route resources to enemy buildings. Always check output direction doesn't point at enemy.

---

## EXECUTION TIMELINE

| Day | Date | Phase | Key Milestone | Submit? |
|-----|------|-------|---------------|---------|
| 1 | Apr 5 | 0 | Scaffold + economy skeleton | No |
| 2 | Apr 6 | 0-1 | Working economy, beats starter | No |
| 3 | Apr 7 | 1 | 4+ harvesters, conveyor chains | No |
| 4 | Apr 8 | 1-2 | Marker protocol, coordinated builders | No |
| 5 | Apr 9 | 2-3 | Symmetry detection, basic turrets | Yes (v1) |
| 6 | Apr 10 | 3 | Full defense line, scouting | Yes (v2) |
| 7 | Apr 11 | 3-4 | **Sprint 4 snapshot** — offense layer | Yes (v3) |
| 8 | Apr 12 | 4 | Launcher drops, builder raids | Yes |
| 9 | Apr 13 | 4-5 | Adaptive strategy switching | Yes |
| 10 | Apr 14 | 5 | Opponent replay study begins | Yes |
| 11 | Apr 15 | 5 | Counter-meta implementation | Yes |
| 12 | Apr 16 | 5-6 | Parameter tuning, map-specific logic | Yes |
| 13 | Apr 17 | 6 | Hardening, edge case fixes | Yes |
| 14 | Apr 18 | 6 | Full test suite, CPU optimization | Yes |
| 15 | Apr 19 | 6 | Final ladder grinding | Yes |
| 16 | Apr 20 | -- | **INTERNATIONAL QUALIFIER** | Final |

---

## DAILY DEVELOPMENT LOOP

```
Morning:
  1. Check ladder results from overnight matches
  2. Analyze any losses — watch replays, identify weakness
  3. Prioritize today's fixes/features

Build:
  4. Implement highest-priority change
  5. Local test: `cambc run buzzing buzzing_prev --watch` (5 maps)
  6. Remote test: `cambc test-run buzzing buzzing_prev` (verify no TLE)
  7. If win rate ≥ 55% vs previous: promote

Ship:
  8. `cambc submit bots/buzzing/` — push to ladder
  9. Tag version in local notes: v0.X — [description of change]
  10. Monitor first 10 ladder matches for regressions
```

---

## RISK REGISTER

| Risk | Impact | Mitigation |
|------|--------|------------|
| CPU timeout (TLE) | Bot dies mid-round | Bail-out checks everywhere; BFS node caps; cache API calls |
| Economy collapse (enemy raids) | Can't build anything | Barriers around core conveyors; inward gunners; armoured conveyors |
| No ore near core | Delayed economy | Scout early; plan long-distance harvester expeditions |
| Foundry too early | Crippling scale penalty | Build foundry LAST, after all key infrastructure |
| Duplicate harvester builds | Wasted resources | Marker-based claims with freshness checking |
| Builder stuck (no path) | Unit wasted | Timeout transitions in state machine; fallback to random walk |
| Conveyor feeds enemy | Resources lost | Check output tile for enemy buildings before placing |
| Late submission (no matches) | Can't calibrate Elo | Submit by Day 5 at latest; iterate daily |

---

## METRICS TO TRACK

Every version should record:
- Win rate vs starter (should be ≥ 95%)
- Win rate vs previous version (should be ≥ 55%)
- Average round when game ends (< 2000 = we're killing cores = good)
- Average harvesters alive at round 200
- TLE rate (must be 0%)
- Win rate by map category (small/medium/large/choke/open)
- Ladder Elo (target trajectory: 1500 → 1700 → 1900 → 2100 → 2200+)
