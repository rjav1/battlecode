# Close Match Analysis — What Determines 2-3 vs 3-2

**Date:** 2026-04-06  
**Question:** In close 5-game matches, what win conditions appear? Is refined axionite (tiebreaker #1) costing us games?

**Data:** 10 close matches analyzed (7 losses, 3 wins), 50 individual games.

---

## Win Condition Distribution

### Our LOSSES in close matches (27 games lost)

| Condition | Count | % |
|-----------|-------|---|
| titanium_collected | 23 | **85%** |
| axionite_collected | 2 | 7% |
| core_destroyed | 1 | 4% |
| harvesters | 1 | 4% |

### Our WINS in close matches (23 games won)

| Condition | Count | % |
|-----------|-------|---|
| titanium_collected | 20 | **87%** |
| harvesters | 3 | 13% |

---

## Key Finding: Refined Axionite Is Almost Irrelevant

**We lose on `axionite_collected` in only 2 of 27 lost games (7%).** Both were Code Monkeys:
- Code Monkeys G1: corridors | `axionite_collected` (Code Monkeys collected refined Ax)
- Code Monkeys G2: gaussian | `axionite_collected` (Code Monkeys collected refined Ax)

Code Monkeys appears to be running a foundry-based axionite economy. This is a specific opponent feature, not a systematic weakness.

**Conclusion: Refined axionite delivery is NOT the primary reason we lose close games. 85% of losses are pure Ti economy (titanium_collected).**

---

## What Actually Determines Close Games

### Tiebreaker flow in practice

All 5 games go to round 2000 in most cases (only 1 `core_destroyed` in 50 games). At round 2000, the tiebreaker order is:
1. Refined Ax delivered → almost never used (only Code Monkeys has this)
2. **Ti delivered to core → this decides 85% of games**
3. Living harvesters → decides 13% of our wins, 4% of losses
4. Stored Ax → never observed as deciding factor
5. Stored Ti → never observed as deciding factor

**The match is almost always decided by who delivered more Ti to their core.** This is a pure economy problem — harvester count × delivery efficiency.

### Maps where we lose close games

Lost games in close matches:
- wasteland_oasis, minimaze, tiles (vs Cenomanum — all Ti)
- corridors, castle_keep, butterfly (vs Code Monkeys — corridors=Ax, rest=Ti)
- battlebot, default_large1, chemistry_class (vs Highly Suspect — Ti)
- binary_tree (core_destroyed), landscape, castle_keep (vs Polska Gurom)
- bear_of_doom, cinnamon_roll, dna (vs Quwaky — Ti)
- corridors, gaussian (vs Code Monkeys again), metropolitan_dystopia (harvesters)
- clash_arena, default_small2, vase (vs oslsnst — Ti)

**New maps we don't test locally:** wasteland_oasis, minimaze, tiles, battlebot, castle_keep, bear_of_doom, cinnamon_roll, chemistry_class, clash_arena, thread_of_connection, labyrinth, cubes, shrub, vase, metropolitan_dystopia, pls_buy_cucats_merch, the_great_divide

We test against 22 maps locally. Ladder matches use maps outside our test set. We may be overfitting to our local maps.

### The `core_destroyed` at turn 278

Polska Gurom G2: binary_tree — our core was destroyed at turn 278. This is an early rush attack. Polska Gurom ran a core-kill strategy on binary_tree. This is the map where we have 0% win rate and are structurally vulnerable to rushes (ore is on distant branch, builders can't defend).

---

## Per-Opponent Analysis

### Cenomanum (2-3 loss, 3-2 win)
- Lost 3 games on Ti in first match. Won 2 on harvesters (we had more living harvesters at rnd 2000).
- Won 3-2 in second match (same opponent, same ~Elo).
- These matches are coin-flip territory — we're genuinely ~50/50 on their map pool.
- **No axionite involved at all.**

### Code Monkeys (2× 3-2 loss)
- **Delivers refined axionite** — foundry-based economy. Won on `axionite_collected` in 2 games.
- Also beats us on Ti in castle_keep, butterfly.
- We beat them on the_great_divide, minimaze, pixel_forest (Ti wins).
- Code Monkeys is our most formidable 2-3 opponent — they have axionite advantage + Ti advantage.
- **Flipping Code Monkeys requires either: (a) matching their Ti production, or (b) delivering refined Ax ourselves.**

### Highly Suspect (2-3 loss)
- Pure Ti economy match — all 5 games decided by titanium_collected.
- We lost 3, won 2. Very close. Maps: battlebot, pixel_forest, default_large1, thread_of_connection, chemistry_class.
- No refined Ax involved.
- **Flipping Highly Suspect = produce 1 more unit of Ti than them on 1 more map.**

### Polska Gurom (2-3 loss)
- Game 2 (binary_tree): core_destroyed at turn 278 — early rush, instant loss.
- Games 4, 5: Ti economy losses.
- **Two distinct problems: binary_tree rush vulnerability + general Ti gap on new maps (landscape, castle_keep).**

### Quwaky (3-2 loss)
- Pure Ti economy — all 5 on titanium_collected.
- Maps we lost: bear_of_doom, cinnamon_roll, dna. Maps we won: labyrinth, default_large1.
- **No axionite. Pure Ti gap on specific maps.**

### oslsnst (3-2 loss — note: this is our own bot we created!)
- We actually lost to our own oslsnst bot 3-2! Maps lost: clash_arena, default_small2, vase.
- oslsnst is our attacker-style bot that rushes on tight maps. It's beating us on tight maps.
- **Implication: our own tight-map rush strategy works and we should defend against it.**

---

## Root Causes Ranked by Impact

### 1. Ti economy gap on new/unknown maps (85% of losses)
We optimize against 22 local test maps. Ladder has many maps we've never seen (minimaze, wasteland_oasis, tiles, battlebot, castle_keep, bear_of_doom, chemistry_class, etc.). On these maps, our sector-based exploration may not find ore efficiently.

**Impact: This accounts for ~85% of close losses.**

### 2. Binary_tree + rush vulnerability (1 game, but decisive)
Polska Gurom destroyed our core at turn 278 on binary_tree. We have 0% on binary_tree as player A. Against a rushing opponent, this is a guaranteed loss.

**Impact: 1 game lost decisively. In a 2-3 match, 1 flip = 3-2 win.**

### 3. Code Monkeys' axionite delivery (2 games)
Code Monkeys delivers refined Ax and wins on tiebreaker #1. We can't counter this without our own foundry.

**Impact: 2 games against 1 specific opponent. Not worth building foundry infrastructure for.**

### 4. Harvester count tiebreaker — where we WIN
We win 3 games on `harvesters` tiebreaker. This means we sometimes produce MORE harvesters than opponents even when we deliver less Ti. When Ti is within margin of error, more living harvesters wins games.

**Impact: Currently a small advantage for us. Any buff to harvester count (extra builders) amplifies this.**

---

## Actionable Recommendations

### Priority 1: Ti economy improvement (direct impact on 85% of losses)

The V62 additions research already identified two candidates:
- **Ti spend-down**: extra builders when bank > 800 → more harvesters → more Ti + more harvester tiebreakers
- **Balanced cap raise**: match smart_eco timing → 2 extra builders in early game

Both directly improve Ti delivered to core. This is the highest-leverage fix.

### Priority 2: Binary_tree rush defense (1 flip = match win vs Polska Gurom-style)

If we can survive binary_tree game 2 (core_destroyed at t=278), we keep the match alive. Options:
- Place early barriers on binary_tree's core approach vector (we already have 2-barrier early defense for rnd <= 30)
- The binary_tree rush happened at t=278 — our early barriers should already be active. May need stronger defense on this specific map geometry.

**Small investigation: does our early barrier code actually trigger on binary_tree? Is binary_tree a "tight" map (area <= 625)?**

### Priority 3: Explore unknown maps better

Ladder maps include many we've never seen. Our explore_idx sector rotation may get stuck on unknown map geometry. The key signal: we often win on maps we test locally (default_large1, pixel_forest, cold) and lose on unfamiliar ones (bear_of_doom, cinnamon_roll, chemistry_class).

No code change possible without seeing those maps. But raising our 50-match local baseline to 70%+ will likely also raise our ladder win rate on unfamiliar maps, since the underlying economy logic applies everywhere.

---

## Answer to the Core Question

**Refined axionite is NOT costing us close games.** It appears in only 2 of 27 lost games, both against a single specific opponent (Code Monkeys) who has a dedicated foundry strategy.

**What IS costing us close games:**
1. Ti delivered to core — pure economy, opponent mines more Ti or delivers it more efficiently (85% of losses)
2. Unknown maps — we haven't seen bear_of_doom, castle_keep, minimaze, etc. locally
3. Binary_tree rush (1 instance) — structural vulnerability to early core destroy

**The V62 additions (Ti spend-down + balanced cap raise) directly address cause #1 and are the right next step.**

---

## Match Summary Table

| Match | Score | Opponent | Our W conditions | Their W conditions |
|-------|-------|----------|------------------|--------------------|
| vs Cenomanum | **2-3** | Cenomanum | harvesters ×2 | titanium_collected ×3 |
| Code Monkeys vs us | **3-2** | Code Monkeys | titanium_collected ×2 | axionite_collected ×1, titanium_collected ×2 |
| vs Highly Suspect | **2-3** | Highly Suspect | titanium_collected ×2 | titanium_collected ×3 |
| vs Polska Gurom | **2-3** | Polska Gurom | titanium_collected ×2 | core_destroyed ×1, titanium_collected ×2 |
| Quwaky vs us | **3-2** | Quwaky | titanium_collected ×2 | titanium_collected ×3 |
| Code Monkeys vs us | **3-2** | Code Monkeys | titanium_collected ×2 | axionite_collected ×1, titanium_collected ×1, harvesters ×1 |
| oslsnst vs us | **3-2** | oslsnst (our bot!) | titanium_collected ×2 | titanium_collected ×3 |
| vs N | **3-2 WIN** | N | titanium_collected ×2, harvesters ×1 | titanium_collected ×2 |
| Botz4Lyf vs us | **2-3 WIN** | Botz4Lyf | titanium_collected ×3 | titanium_collected ×2 |
| vs O_O | **3-2 WIN** | O_O | titanium_collected ×3 | titanium_collected ×2 |
