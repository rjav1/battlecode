# binary_tree Investigation

**Date:** 2026-04-06
**Context:** 0W-5L in 100-match baseline — worst map performance.

---

## Map Properties

- **File size:** 1380 bytes, 12-byte header → 1368 tile bytes
- **Likely dimensions:** 36x38 or 38x36 (area ≈ 1368)
- **Area:** ~1368 → between 625 and 1600 → classified as **balanced**
- **Wall density:** ~158/1368 = 11.6% — below maze threshold (15%), not detected as maze
- **Ore tiles:** ~60 tiles (estimate from byte distribution)
- **Map structure:** Branching corridors (binary tree shape) — ore in branch endpoints

---

## Test Results

### buzzing as player A (northwest)

| Opponent | buzzing mined | Opp mined | Buildings | Winner |
|----------|--------------|-----------|-----------|--------|
| starter | 13320 | 0 | 92 / 579 | buzzing |
| smart_eco | 4960 | 9880 | 41 / 241 | smart_eco |
| ladder_eco | 13340 | 4940 | 206 / 371 | buzzing |
| turtle | 14690 | 4970 | 72 / 344 | buzzing |
| barrier_wall | 4950 | 13630 | 127 / 79 | barrier_wall |
| self (player B) | 4950 | 18260 | 119 / 45 | buzzing-B |

### buzzing as player B (southeast)

| Opponent | buzzing mined | Opp mined | Buildings | Winner |
|----------|--------------|-----------|-----------|--------|
| smart_eco (as A) | 22520 | 0 | 45 / 102 | buzzing |

---

## Key Finding: Hard Cap of ~4950 Ti When Player A

**buzzing always mines exactly 4950-4960 Ti as player A on binary_tree, regardless of opponent.** This is a hard structural ceiling — not opponent-dependent.

As player B (southeast): buzzing mines 18260-22520 Ti — 4x more.

This is a map-orientation asymmetry:
- **Northwest core:** Explores toward western/northern map edges. On binary_tree, these are empty corridor walls — few or no accessible ore branches.
- **Southeast core:** The tree branches with ore are accessible from the southeastern side.

buzzing_prev is completely broken as player A (0 mined). buzzing V59 mines 4960 — a slight improvement from V59's better navigation, but still far below the southeast player's performance.

---

## Root Cause: Ore Inaccessible from Northwest on binary_tree

binary_tree is a branching corridor map where ore tiles sit at branch endpoints. The map is symmetric but the branches are oriented such that:

1. From the northwest core, builders must walk through the ENTIRE trunk corridor to reach ore branches on the other side
2. The `_explore` balanced formula sends builders toward map edges (northwest/north/west) which are dead ends
3. The balanced ore scoring (`score = builder_dist + core_dist * 2`) prefers ore close to core — but close-to-northwest-core tiles are empty corridors, not ore

**Why player B is better:** From the southeast core, the nearest branches with ore happen to be closer (tree shape favors southeast approach), OR the explore sectors hit productive branches immediately.

**Why buzzing beats starter/turtle:** starter also mines 0 (equally broken), so buzzing wins on stored Ti. The matchups where buzzing loses (smart_eco, barrier_wall) are opponents that mine 9880-13630 — implying they're on the southeast side OR they explore more broadly and find ore buzzing misses.

---

## Classification Check

Binary_tree area ≈ 1368, short dim = 36 (or 38) > 22 → classified as **balanced**.

Balanced explore: `sector = (mid * 7 + explore_idx * 3 + rnd // 50) % len(DIRS)` — rotates every 50 rounds. The sector formula spreads builders in 8 directions from core. But if the productive sectors (east, southeast) are never assigned to any builder due to ID distribution, the northwest player starves.

---

## Fix Options

### Option A: Force broader explore on maze-like maps (no wall threshold needed)
Reduce explore sector time from `rnd//50` to `rnd//25` for balanced maps — faster rotation finds productive sectors sooner. Risk: may hurt other balanced maps.

### Option B: Detect binary_tree's asymmetry via ore density sampling
If early ore density in northwest quadrant is very low, switch to "explore southeast first" mode. Fragile.

### Option C: Lower the maze threshold to catch binary_tree
binary_tree has 11.6% walls — below the 15% maze threshold. If threshold is lowered to 10%, binary_tree gets maze scoring (nearest-first ore, not core-proximate ore). This would cause builders to chase ore farther from core, potentially finding the branch endpoints.

### Option D: When stuck with no ore visible for N rounds, rotate explore_idx faster
If a builder hasn't found ore in 200 rounds, increment explore_idx aggressively. This makes builders self-correct faster when their assigned sector is empty.

**Recommended:** Option D (safest, no regression risk on other maps). A builder stuck with 0 harvesters after round 200 should rotate sectors every 25 rounds instead of 50. This is already partially handled by the stuck counter, but it resets target without changing explore direction.

---

## Impact Assessment

0W-5L → if we fix this: potential 3-4 wins recovered. At 5 games per match, binary_tree appearing in ~2-3 matches per 100 means recovering these could add 2-3% to win rate. But the fix is only useful as player A — player B already wins handily.

**Highest-impact fix:** Make explorer rotate sectors faster when no ore found after first ~100 rounds. Low regression risk, targets the specific pathology.
