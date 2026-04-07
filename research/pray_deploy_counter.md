# Pray and Deploy Counter-Strategy Research

**Date:** 2026-04-06
**Context:** P&D is our worst nemesis — wins on hourglass, default_small1, arena, git_branches. All resource tiebreakers.

---

## Test Results

### buzzing vs starter (baseline performance)

| Map | Mode | Seed | buzzing Ti (mined) | starter Ti (mined) | Winner |
|-----|------|------|--------------------|--------------------|--------|
| hourglass | balanced (27x45=1215) | 1 | 21050 (19850) | 3902 (0) | buzzing |
| hourglass | balanced | 42 | 22127 (19820) | 3484 (0) | buzzing |
| default_small1 | tight (20x20=400) | 1 | 20976 (17430) | 4860 (0) | buzzing |
| default_small1 | tight | 42 | 20634 (17110) | 4851 (0) | buzzing |
| arena | tight (25x25=625) | 1 | 22345 (19690) | 4314 (0) | buzzing |
| arena | tight | 42 | 17279 (14860) | 4400 (0) | buzzing |
| git_branches | expand (50x35=1750) | 1 | **498 (0 mined)** | 4211 (0) | **starter wins!** |
| git_branches | expand | 42 | **477 (0 mined)** | 4352 (0) | **starter wins!** |
| git_branches | expand | 137 | **1669 (0 mined)** | 4427 (0) | **starter wins!** |

### buzzing_prev vs starter (comparison)

| Map | Seed | buzzing_prev Ti (mined) | starter Ti (mined) | Winner |
|-----|------|-------------------------|---------------------|--------|
| hourglass | 1 | 25736 (24430) | 3682 (0) | buzzing_prev |
| default_small1 | 1 | 13277 (9770) | 4677 (0) | buzzing_prev |
| arena | 1 | 7559 (4960) | 3998 (0) | buzzing_prev |
| git_branches | 1 | 18 (0) | 4280 (0) | **starter wins!** |
| git_branches | 42 | 603 (0) | 3213 (0) | **starter wins!** |
| git_branches | 137 | 989 (0) | 2040 (0) | **starter wins!** |

---

## Analysis

### Map Categorization

From map dimension analysis:
- **arena**: 25x25 = area 625 → **tight** (exactly at boundary: `area <= 625`)
- **hourglass**: 27x45 = area 1215 → **balanced**
- **default_small1**: 20x20 = area 400 → **tight**
- **git_branches**: 50x35 = area 1750 → **expand**

### Finding 1: git_branches is a universal 0-mined disaster

**Both buzzing AND buzzing_prev mine 0 Ti on git_branches.** This is not a regression — it's been broken on this map for a long time. The starter bot wins purely on passive income (10 Ti/4 rounds × 2000 rounds = 5000 Ti).

Why: 15-17 builders spawn (expand cap) but never build harvesters. On a map named "git_branches", the structure likely has:
- Long branching corridors separated by walls
- Ore tiles deep inside branch tunnels
- Builders following the expand explore formula (sector toward map edge from core, rotating every rnd//200) miss branch entrances entirely

The expand explore rotation of `rnd//200` means builders commit to one direction for 200 rounds. On a 50x35 map with branching corridors, the straight-line target from core to map edge may never intersect any ore tile. Builders spend 200 rounds building conveyor chain toward an empty wall, then rotate.

Additionally: 15 builders on a 50x35 map spend more on scale inflation than they gain. Each builder bot (+20% scale) + conveyors inflate the cost of harvesters.

### Finding 2: hourglass and default_small1 are NOT our problem

We mine 17-22k Ti on these maps vs starter's 0. P&D must be mining MORE than us on these maps — their eco is better on small/balanced maps. This is a P&D capability issue, not our map weakness.

### Finding 3: arena is not our weakness

We mine 14-22k Ti on arena vs starter's 0. P&D must be specifically strong on arena. arena=625 is exactly the tight/balanced boundary — `area <= 625` classifies it as tight. Our tight cap of `3→5→8` may be suboptimal here.

### Finding 4: buzzing_prev mines MORE on hourglass (24430 vs 19850)

buzzing_prev has expand cap `3→5→8→10+` (higher late-game). On hourglass (balanced), buzzing_prev's cap schedule may be more aggressive. But buzzing wins both vs starter by large margins.

---

## Root Cause: P&D's Advantage

P&D wins on resource tiebreakers — meaning they mine MORE Ti than us. On these maps:

1. **hourglass/default_small1/arena**: P&D likely has a faster first-harvester or more efficient conveyor routing
2. **git_branches**: We mine 0 — P&D likely mines something nonzero, winning trivially

The git_branches bug is the most actionable: we lose a guaranteed map to anyone who mines anything.

---

## Counter-Strategies

### Priority 1: Fix git_branches (0-mined = guaranteed loss)

**Root cause**: Expand explore formula targets map edges in straight lines from core. On a branching corridor map, ore is in side branches, not on direct lines to edges. Builders miss all ore.

**Fix options:**
- A) Shorten expand explore rotation: change `rnd//200` to `rnd//50` — rotate 4x faster to sample more directions
- B) Reduce reach on expand maps: currently `reach = max(w, h) = 50` for git_branches. Target within the map area rather than edges
- C) Add random jitter to explore targets so builders don't all go the exact same direction
- D) On expand maps, reduce builder cap until we know harvesters are being built (econ_cap is supposed to do this, but vis_harv=0 if builders never find ore)

**Easiest fix**: Change expand rotation from `rnd//200` to `rnd//100`. This doubles explore rotation speed on expand maps. Low risk (only affects expand mode).

### Priority 2: First-harvester speed on tight/balanced maps

On arena (tight), hourglass (balanced), default_small1 (tight): we're mining 15-22k Ti but P&D beats us. We need to understand their Ti mined — do they exceed ours? If P&D mines 25k+ on these maps, we need faster first harvesters.

The tight cap change: `3→5→8` vs smart_eco's `4→6→7→8` — on a 25x25 map, 4 builders vs 3 at round 20 means faster coverage. But we already updated balanced cap to match smart_eco. Tight cap remains `3→5→8`.

**Tight cap fix**: Change tight mode cap from `3 if rnd<=20 else (5 if rnd<=100 else 8)` to match smart_eco: `4 if rnd<=30 else (6 if rnd<=100 else 8)`.

### Priority 3: Understand P&D's actual strategy

Without a P&D replay, we can't know if they use military, rush, or pure eco on these maps. We should request an unrated match or examine ladder match history once we have submissions.

---

## Recommended Action Plan

1. **Immediate (low risk)**: Change expand explore rotation `rnd//200` → `rnd//100`
   - Expected impact: git_branches 0→nonzero Ti mined
   - Risk: negligible (only affects expand maps, explore rotation is already known-safe)

2. **Test after**: Tight cap `3→4→6` to match smart_eco on arena/default_small1/face
   - Expected impact: +1-2 harvesters earlier on tiny maps
   - Risk: test with regression suite

3. **Monitor**: After ladder deployment, check if P&D match results improve

---

## Summary Table

| Map | Our Mining | P&D Threat | Fix Priority |
|-----|------------|------------|--------------|
| git_branches | 0 (broken) | Trivial win for P&D | CRITICAL |
| arena | 14-22k (good vs starter) | P&D eco may be better | Medium |
| hourglass | 19-22k (good vs starter) | P&D eco may be better | Low |
| default_small1 | 17-20k (good vs starter) | P&D eco may be better | Low |
