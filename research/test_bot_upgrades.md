# Test Bot Upgrades

## Task #16: smart_eco upgrade

**File:** `bots/smart_eco/main.py`

**Changes made:**
1. Added `_wall_density`, `_ore_density`, `_is_maze` instance vars
2. Scan loop now counts walls and ore tiles per round, locks in densities after round 5
3. `_is_maze` = True if wall_density > 15% OR ore_density > 12% (mirrors main bot)
4. Ore target selection: maze maps use nearest-to-builder scoring; open maps weight core proximity (builder_dist + core_dist * 2)

**Already correct (no change needed):**
- Builder caps: 4 by round 30, 6 by 100, 7 by 200, 8+ — already aggressive
- Ti reserves: cost+5 everywhere — already correct
- Builds both Ti AND Ax ore — already correct

**Expected impact:** On cold/gaussian (open maps with clustered ore), ore preference should now favor ore closer to core, reducing conveyor chain length. On butterfly/sierpinski (maze/ore-rich), nearest-ore avoids misleading core-distance scores through walls.

---

## Task #19: Randomization across test bots

### bots/balanced/main.py
**Change:** `_explore` direction index now uses `(self.my_id * 7 + rnd) % 8` instead of `(my_id * 3 + explore_idx + rnd // 150) % 8`.

**Effect:** Direction changes every round (not every 150 rounds), and the `*7` prime multiplier spreads sequential builder IDs across all 8 directions. Each builder explores a different direction each round — much less deterministic, covers map better.

### bots/barrier_wall/main.py
**Change:** `_plan_wall` now uses `count = 13 + (self.my_id % 5)` instead of hardcoded `[:15]`.

**Effect:** Barrier count varies 13–17 depending on builder ID. Different seeds/maps produce different wall sizes, making tests less seed-dependent.

### bots/rusher/main.py
**Change:** Rush threshold now `max(2, 2 + (my_id % 21) - 10)` = range 2–12 instead of hardcoded 2.

**Effect:** Some later-born builders (born rounds 3–12) may be assigned economy role instead of attacker, varying the attacker count ±~1 across different seeds/IDs. Rush pressure varies slightly each game.
