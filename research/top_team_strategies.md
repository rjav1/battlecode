# Top Team Strategies: What 1600+ Elo Bots Do Differently
## Research Date: 2026-04-07
## Based On: replay_analysis_apr6.md, diamond_tier_analysis.md, top3_scouting.md, contender_scouting.md, global match data

---

## Our Current Position

**Elo: ~1458 (V59, declining from ~1503)**  
**V59 ladder record: 6W-7L (46%) since 17:10 deploy**  
**Gap to 1600: ~142 Elo — roughly 3-4 wins net above expectation**

---

## The 1600+ Tier: Who's There

From ladder snapshot (April 5–7, 2026):

| Elo Band | Tier | Example Teams | Match Style |
|----------|------|---------------|-------------|
| 2400+ | Grandmaster | Blue Dragon (~2791), Kessoku Band (~2720), something else (~2530) | Dual: economy + military |
| 2200-2400 | Master (contender) | MFF1 (2386), bwaaa (2352), Dear jump (2330), Oxford (2327) | Military rush OR economy |
| 2000-2200 | Candidate Master | Rational Merlin (1998), blauerdrache (1981) | Economy starting to work |
| 1800-2000 | Diamond | Axionite Inc (1880), TvT (1878), Bit by Bit (1916) | Harvesters + directed chains |
| 1600-1800 | Emerald | ~40-80 teams | Working economy on most maps |
| 1400-1600 | Silver/Gold | Us, KCPC-B, Chameleon, natto warriors | Broken chains or map-specific gaps |

**Note:** The `ladder --limit 20` global snapshot (19:25) shows active teams: Velocity, Aviators, MEEBs, erk, FactoryManager all visible. We'd need Elo data to confirm which are 1600+. From the April 5 scouting, the clear 1600+ barrier is around rank 80-100.

---

## What 1600+ Teams Do That We Don't: Empirical Analysis

### Source 1: MergeConflict (1521 Elo, now likely higher) — the team that 5-0'd us

**Round 1702 snapshot (from replay_analysis_apr6.md):**

| Metric | MergeConflict | buzzing bees |
|--------|---------------|--------------|
| Ti collected | 16,760 | 10,840 |
| Harvesters | 7 | 12 |
| Bots | 2 | 10 |
| Conveyors | 32 | 73 |

**Their Ti/harvester: 2,394**  
**Our Ti/harvester: 903**  
**Efficiency gap: 2.6x** — they mine nearly 3x more per harvester.

They win with FEWER harvesters, FEWER bots, FEWER conveyors. The differentiator is delivery efficiency.

### Source 2: Polska Gurom (~1487 Elo at time of match)

**Round 1117 snapshot:**

| Metric | Polska Gurom | buzzing bees |
|--------|-------------|--------------|
| Ti collected | 6,640 | 10,780 |
| Bots | 2 | 10 |
| Conveyors | 9 | 101 |
| Bridges | 33 | 1 |
| Sentinels | 6 | 1 |

We had MORE Ti collected but lost to core destruction. They won with 6 sentinels and 33 bridges against our 101 conveyors and 1 sentinel.

**Key: they destroyed our core with 10,000+ Ti in our bank because we never spent it on defense.**

### Source 3: Axionite Inc (Diamond, ~1880 Elo)

- 7 harvesters → **19,240 Ti collected** (vs our ~11,000)
- Only **13 conveyors** (we build 70-100+)
- 4 **splitters** to branch resources to turrets
- 38 **barriers** as defense ring
- Mixed turrets: 3 sentinel + 2 gunner + 2 launcher

### Source 4: Blue Dragon (Grandmaster, ~2791 Elo)

- 22 harvesters → **30,000+ Ti** collected
- **308 conveyors** — dual-use as movement paths AND resource chains
- **33 bridges** — heavy bridge usage for terrain crossing
- 20 sentinels — late-game defensive wall
- 174 roads for builder movement

---

## Root Cause Diagnosis: Why We're Stuck at ~1470

### Problem 1: Conveyor Overbuilding (CRITICAL)

We build 70-101 conveyors. Each is +1% scale. At 100 conveyors: everything costs 2x.
- MergeConflict uses 32. Polska Gurom uses 9 + 33 bridges.
- We're not building fewer because our exploration lays conveyors as nav paths.
- **The V59 fix partially addressed this (removed chain-join bridges that broke chains) but not the root cause: we still build exploration conveyors.**

**Impact on scaling:** If we build 80 conveyors + 12 harvesters + 8 bots, that's +80 +60 +160 = +300% scale. Every harvester that should cost 20 Ti costs 80 Ti. Every bot that should cost 30 Ti costs 120 Ti.

### Problem 2: Ti Hoarding (CRITICAL)

We accumulate 10,000+ Ti unspent by round 1000-1200. Against Polska Gurom we had 10,408 Ti at round 1117 with only 1 sentinel. They killed our core 183 rounds later.

**We have no spend-down logic.** Resources accumulate but aren't converted into turrets, more harvesters, or healing.

### Problem 3: Bot Overspawning (HIGH)

10 bots at +20% each = +200% scale. MergeConflict and Polska Gurom run 2 bots and beat us with this structural advantage. Our econ_cap is `max(time_floor, vis_harv * 3 + 4)` — on large maps `vis_harv` underestimates, spawning too many bots.

### Problem 4: No Sentinel Delivery Chain (MEDIUM)

We build sentinels but they don't fire because we have no ammo delivery. Polska Gurom's 6 sentinels were actively firing. Our 1 sentinel at round 1117 was likely empty. V47 added gunner ammo delivery but sentinels are the meta turret of choice — they deal 18 damage with 3-round reload and wide area effect.

### Problem 5: No Defensive Barriers (MEDIUM)

Axionite Inc uses 36-38 barriers around core. At 3 Ti each (+1% scale), 20 barriers costs 60 Ti and +20% scale — the cheapest HP investment available. We build 0 barriers.

---

## What the 1600+ Elo Tier Looks Like Specifically

Based on Emerald-tier analysis and teams we've fought at ~1480-1550:

**Teams beating us (1480-1550 range):** Chameleon, KCPC-B, natto warriors, binary bros, Quwaky, oslsnst, Code Monkeys

**Pattern from our V59 losses:**
- Consistent 1-4 scores (we win 1 game, lose 4) on the losses
- We win 3-2 when we edge it
- No 0-5 sweeps against us since V52 (Botz4Lyf 2-3 win confirms we're not helpless)

**Likely what 1600 teams have that 1470 teams don't:**
1. Working conveyor chains on 3-4 of 5 map types (not just balanced maps)
2. Spending Ti before it piles up — more harvesters or sentinel ammo delivery
3. Fewer bots (2-4 vs our 8-10)
4. Sentinel placement early (round 200-400) to deny builder rushes

---

## The Path to 1600: Gap Analysis

Current: ~1470 Elo. Target: 1600+. Need: +130 Elo ≈ net +10 matches won vs expected.

### Change 1: Fix Conveyor Count (Expected Impact: +30-50 Elo)

**What to change:** Stop building conveyors during exploration. Use roads instead (already partially done in V49+ with explore ti_reserve). Goal: < 40 conveyors per game average.

**How:** The `ti_reserve=999999` exploration fix already suppresses conveyors during nav. But we may still be building too many conveyors in the conveyor-path phase. Need to verify actual conveyor count per game in current V59 vs opponents.

**Evidence:** MergeConflict beats us with 32 conveyors vs our 73. If we halve conveyor count, scaling drops ~40%, making each subsequent harvester cost 40% less.

### Change 2: Sentinel Ammo Delivery (Expected Impact: +20-30 Elo)

**What to change:** Sentinels are our defense but we haven't confirmed ammo is being delivered. V47 added gunner ammo delivery — we need the same for sentinels.

**How:** After building a sentinel, assign a builder to lay a conveyor from the nearest Ti resource chain to the sentinel's input side.

**Evidence:** All 1800+ teams use sentinels with ammo. KB has 10 sentinels by round 148. An unarmed sentinel is 30 Ti + 20% scale wasted.

### Change 3: Ti Spend-Down Logic (Expected Impact: +20-30 Elo)

**What to change:** If Ti > 800 and round > 400, auto-build sentinels or more harvesters. Don't hoard.

**How:** In core spawn logic: if `ti > 800 and round > 400 and sentinel_count < 3`, build a sentinel at the next safe perimeter tile.

**Evidence:** We had 10,408 Ti at round 1117 with 1 sentinel and lost by core destruction. If we'd built 4-5 sentinels at round 400 (600 Ti), Polska Gurom's push would have failed.

### Change 4: Bot Cap at 4 (Expected Impact: +15-20 Elo)

**What to change:** Hard cap bots at 4 total (including any currently alive). Currently econ_cap can reach 8-10 on large maps.

**How:** `if c.get_unit_count() >= 5: return` before spawning logic (core already does something like this, but the threshold is too high).

**Evidence:** MergeConflict and Polska Gurom win with 2 bots. Each extra bot is +20% scale AND a 30 Ti investment. Going from 8 bots to 4 bots frees 120 Ti and saves +80% scale.

### Change 5: Basic Barrier Ring (Expected Impact: +10-15 Elo)

**What to change:** Build 10-15 barriers around core perimeter once Ti > 200.

**How:** After first harvester is built and Ti > 200, designate 10 tiles around core as barrier positions. Any idle builder builds them when passing through.

**Evidence:** Axionite Inc (1880 Elo) uses 38 barriers. Each is 3 Ti (+1% scale), so 15 barriers = 45 Ti +15% scale — very cheap HP. Makes core rushes slower.

---

## Combined Expected Elo Gain

| Change | Expected Gain | Risk | Status |
|--------|--------------|------|--------|
| Fix conveyor count (< 40/game) | +30-50 Elo | Medium — may affect chain quality | Partial (explore suppression done) |
| Sentinel ammo delivery | +20-30 Elo | Low — turrets are useless without it | Not done |
| Ti spend-down logic | +20-30 Elo | Low — we hoarded 10k Ti and lost | Not done |
| Bot cap at 4 | +15-20 Elo | Low — 2 bots beat us consistently | Not done |
| Barrier ring | +10-15 Elo | Low — cheap HP | Not done |
| **Total (non-overlapping)** | **+80-120 Elo** | | |

Reaching ~1590-1590 from these 5 changes is realistic. With some luck and opponent variance, 1600+ is achievable within a version or two.

---

## What 1800+ Requires Beyond That

The Diamond tier (1800+) adds:
- 5-7 harvesters with confirmed working chains on ALL map types (not just balanced)
- Splitters for turret ammo distribution
- Map adaptation (rush on tight/small, economy on expand/large)
- 15-20k Ti collected by round 2000 (we currently collect 10-15k on good games)

The 1600→1800 gap is primarily about chain reliability across all map types and per-game consistency, not architectural changes.

---

## Current V59 Ladder Status (19:25 check-in)

V59 matches since deploy:
| Time | Result | Score | Opponent |
|------|--------|-------|----------|
| 17:26 | LOSS | 1-4 | Chameleon |
| 17:39 | LOSS | 1-4 | KCPC-B |
| 17:47 | WIN | 3-2 | O_O |
| 17:57 | LOSS | 1-4 | natto warriors |
| 18:06 | WIN | 2-3 | Botz4Lyf (as B, scored 3) |
| 18:17 | LOSS | 3-2 | oslsnst (as B, scored 2) |
| 18:27 | WIN | 3-2 | Cenomanum |
| 18:35 | LOSS | 1-4 | binary bros |
| 18:46 | LOSS | 3-2 | Code Monkeys (as B, scored 2) |
| 18:57 | WIN | 1-4 | MWLP (as B, scored 4) |
| 19:06 | WIN | 3-2 | N |
| 19:15 | LOSS | 3-2 | Quwaky (as B, scored 2) |
| 19:25 | WIN | 4-1 | Pray and Deploy |

**V59 total: 6W-7L (46%)**, current Elo ~1468. Recovering from the early LOSS run.

The 74% local baseline → 46% ladder gap confirms our test suite opponents are weaker than real ladder opponents. This is partly expected (Elo ≈1470 so we face 1470-ish opponents, not our local test bots which may be around ~1200-1400).

---

## Architectural Changes Required to Reach 1600+

Summary in priority order:

1. **Sentinel ammo delivery** — highest confidence improvement, pure upside
2. **Ti spend-down** — stop hoarding, build sentinels or harvesters when Ti > 800
3. **Tighter bot cap** — hard cap at 4 bots maximum
4. **Barrier ring** — 10-15 barriers around core once Ti > 200
5. **Conveyor reduction** — verify V59 actual conveyor count; if still > 50, investigate why

None of these require architectural rewrites. They are targeted additions to the existing bot structure. Estimated combined impact: **+80-120 Elo**, bringing us from ~1470 to ~1550-1590.
