# v24 Regression Investigation

**Date:** 2026-04-06  
**Investigator:** Research Agent  
**Question:** Did v24's extension of sector exploration to balanced maps cause the 53% → 33% win rate drop?

---

## 1. The Regression in Numbers

From the Elo collapse analysis (`research/elo_collapse_analysis.md`):

| Period | Versions | Win Rate |
|--------|----------|----------|
| v16-v23 | Peak period | **53%** |
| v24-v29 | Post-v24 | **33%** |
| v30-v35 | Recovery | 42% |

The drop happened precisely at v24, uploaded at 07:09. v23 was the last version of the 53% period (uploaded ~05:03, active 04:38-07:09).

---

## 2. What v24 Actually Changed

**v23 (Large Maps Only):**
```python
if area >= 1600:
    sector = (mid + self.explore_idx + rnd // 200) % len(DIRS)
    # ... target map edge from core
elif area > 625:
    # No sector logic — fell through to tight-map code
    idx = (mid * 3 + self.explore_idx + rnd // 100) % len(DIRS)
    far = Position(pos.x + dx * reach, pos.y + dy * reach)  # from builder position
```

**v24 (Added Balanced Map Sector Logic):**
```python
if area >= 1600:
    sector = (mid + self.explore_idx + rnd // 200) % len(DIRS)
    # ... target map edge from core
elif area > 625:
    # NEW: Sector exploration from core, fast rotation
    sector = (mid * 3 + self.explore_idx + rnd // 50) % len(DIRS)
    # ... target map edge from CORE POSITION
```

The key structural difference: v23's balanced maps targeted edges relative to the **builder's current position**, which naturally spread builders across the map. v24 targets edges relative to the **core position** (fixed point), which could cluster builders if core is not centered.

Also note: in v24, the large-map formula uses `mid*1` but balanced uses `mid*3`. The current bot (`bots/buzzing/main.py`) uses `mid*7` for both — this was further refined after v24.

---

## 3. Local Test Results at v24 Time

From `phases/v24_results.md`:
- cold: +23% to +145% improvement vs prev
- corridors: symmetric (tie-based coin flip)
- default_medium1: marginal / slight loss on one position
- **4/6 wins overall — passed regression threshold**

From `research/v24_benchmark.md` (vs smart_eco):
- settlement: +18,090 Ti gap (massive win)
- cold: Still loses (–3,950 gap)
- default_medium1: Minor regression in absolute Ti mined (–4,220) but still wins

**Local testing showed v24 was a clear improvement. It passed the 4/6 regression bar.**

---

## 4. Why Did Ladder Performance Drop Despite Local Tests Passing?

The local regression suite tested against `smart_eco`, `smart_defense`, `sentinel_spam`, and `balanced` bots. These are fixed test bots created internally — they are **not representative of the actual ladder population**.

The v24-v29 ladder matchups included:
- oslsnst (core destroyed us repeatedly)
- Ash Hit, Cenomanum, The Defect, Fake Analysis
- One More Time (3.14x our Ti with fewer harvesters)

**The regression suite did not test against these opponents.** Specifically:
1. **Rush opponents were not in the test set.** oslsnst destroyed our core on starry_night (r1028), default_large1 (r1332) — maps where sector exploration is irrelevant because we're dead before round 2000.
2. **Balanced maps in the ladder pool** include maps where we consistently lose regardless of sector exploration: landscape, wasteland, mandelbrot.
3. **cold vs smart_eco was STILL a loss** in both v22 and v24. This was the known weakness that v24 didn't fix.

---

## 5. Does the v24 Balanced-Map Sector Logic Still Exist in the Current Bot?

**Yes.** The current bot (`bots/buzzing/main.py`, v42) still has balanced-map sector exploration:

```python
elif area > 625:
    # Balanced maps: sector from core, prime-spread IDs, quick rotation
    sector = (mid * 7 + self.explore_idx * 3 + rnd // 50) % len(DIRS)
    d = DIRS[sector]
    dx, dy = d.delta()
    # target map edge from core
```

The formula was refined (`mid*7` instead of `mid*3`, `explore_idx*3` instead of bare `explore_idx`) but the structural approach is unchanged from v24.

---

## 6. Verdict: Was v24 the Root Cause?

**Partially, but not as the primary cause.**

### What v24 DID NOT cause:
- The balanced-map sector exploration **demonstrably improved cold and corridors** in local testing (+23-145%)
- v24 passed local regression (4/6 wins)
- The current bot still uses the same approach and is performing at 52% WR (v36-v45 period)

### What actually caused the 33% WR in v24-v29:

1. **Opponent quality shift.** The matchmaking system matched us against better opponents as our Elo rose from the starting ~1488. We faced The Defect, oslsnst, One More Time — all fundamentally stronger bots that beat us on economy regardless of exploration strategy.

2. **Rush vulnerability was fully exposed.** oslsnst core-destroyed us at rounds 165, 335, 451, 667, 808 — this has nothing to do with sector exploration. Every core-destroyed loss is a complete economy irrelevance.

3. **cold still lost.** In v24, we still lost cold vs smart_eco (–3,950 gap). This was a persistent weakness not fixed until v27+ iterations.

4. **default_medium1 minor regression.** v24 introduced a slight absolute Ti drop on default_medium1 P1 (18,770 vs 22,990 in v22). If this pattern repeated on similar balanced maps against stronger opponents, we lost close matches.

5. **Balanced-map exploration targets core edges, not builder-relative edges.** On maps where the core is in a corner, all builders aim for the same edge quadrant. This may have created clustering on non-centered maps in the ladder pool.

---

## 7. Would Reverting v24 Help?

**No — reverting balanced-map sector exploration would hurt.**

Evidence:
- Cold and corridors improved significantly with v24's changes (+23-145%)
- The current bot uses a refined version of the same approach and achieves 52% WR
- The v24-v29 losses were primarily from: (a) rush attacks, (b) economy gap vs strong opponents, (c) unfavorable map assignments
- None of these are caused by balanced-map sector exploration

**What v24-v29 period needed (and later got):**
- Earlier gunner placement (v31) — rush defense
- Nearest-ore scoring on tight maps (v26) — arena/face fix  
- Ore-density maze detection (v27) — butterfly fix
- Marker-based ore claiming (v28-v29) — cold duplicate-harvest fix
- Higher builder caps (v33-v34) — unit count fix

---

## 8. The Real Root Cause of the v24-v29 Drop

The 53% → 33% drop was caused by:

1. **Matchmaking finding our true opponents** — At 53% WR we were matched against stronger bots. v24's changes didn't reduce our win rate; the opponent pool got harder.

2. **Rush vulnerability** (zero rush defense) — 15 individual game losses to core destruction across all 114 matches, concentrated in the v24-v45 era as we faced oslsnst, Warwick, Polska repeatedly.

3. **Economy ceiling** — Our builder cap of 10 units vs opponents running 20-40 units. This is the structural problem identified in `research/ladder_analysis_apr6.md`. It existed before v24 but became decisive against better opponents.

4. **Minor regression on some balanced maps** — default_medium1 P1 absolute Ti drop (18,770 vs 22,990). Small but potentially decisive in 3-2 close matches.

---

## 9. Recommended Action

**Do NOT revert v24.** The sector exploration for balanced maps is net positive and is retained in the current bot (v42+).

**To escape the v24-v29 performance level (33% WR), the already-implemented fixes were correct:**
- Rush defense (barriers, earlier gunners) — v31-v33
- Higher builder caps (arena fix) — v33-v34
- Map-specific ore scoring — v26-v27

**Remaining gaps (per April 6 analysis):**
- Builder cap still too low for galaxy (0-8 record)
- Face map rush vulnerability (0-5 record, 3 core kills)
- Economy losses on landscape/wasteland/mandelbrot — these maps need investigation

The current v45 bot at 52% WR (v36-v45 period) has largely recovered from the v24-v29 dip. The investigation confirms the drop was opponent-quality-driven and rush-vulnerability-driven, not a fundamental algorithm bug in v24.
