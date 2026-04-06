# Launcher Drop Strategy Research

## Concept

Build a launcher turret forward toward the enemy base, then throw builder bots
into enemy territory to attack their buildings and core. Launchers cost 20 Ti,
need no ammo, and throw within r^2=26 (~5.1 tiles). Thrown builders could
bypass walls and defenses entirely.

## Test Results

### launcher_drop vs starter

| Map | Winner | LD Ti (mined) | Starter Ti (mined) | LD Bldgs | Starter Bldgs |
|-----|--------|--------------|-------------------|----------|---------------|
| face | launcher_drop | 13661 (9550) | 4426 (0) | 63 | 283 |
| corridors | launcher_drop | 17000 (13290) | 2412 (0) | 81 | 529 |

**2-0 vs starter** -- but wins are from economy alone, not launcher throws.

### launcher_drop vs buzzing

| Map | Winner | LD Ti (mined) | Buzzing Ti (mined) | LD Bldgs | Buzzing Bldgs |
|-----|--------|--------------|-------------------|----------|---------------|
| face | launcher_drop | 20719 (17240) | 17073 (12760) | 109 | 103 |
| corridors | launcher_drop | 17823 (13560) | 15039 (9930) | 43 | 23 |
| default_medium1 | launcher_drop | 23401 (21440) | 21886 (17910) | 178 | 143 |
| arena | buzzing | 27018 (23700) | 27151 (24430) | 124 | 190 |
| default_small1 | buzzing | 9326 (4890) | 22470 (19240) | 27 | 167 |
| galaxy | buzzing | 13210 (9700) | 12971 (9930) | 131 | 235 |

**3-3 vs buzzing** -- very close margins on most maps.

### Overall: 5-3 (win-loss)

## Critical Finding: Launcher Throws Never Fire

**The launcher turret was built in several games but NEVER successfully threw
a builder in any test.** The `can_launch(bot_pos, target_pos)` check always
fails because:

1. **r^2=26 range is only ~5.1 tiles** -- the launcher must be built right
   next to enemy infrastructure (conveyors/roads) for valid landing targets.
2. **The pioneer builder must walk 15-30 tiles** through no-man's land (building
   roads the whole way at 1 Ti each) to reach the enemy base perimeter.
3. **By the time the pioneer arrives (if ever), it's round 600+** and the game
   is decided by economy.
4. **Target must be passable** (conveyor, road, allied core). Enemy walls and
   empty tiles are NOT passable. Landing requires enemy conveyors, which are
   only near their core area.

## Why the Bot Still Wins

The launcher_drop bot's economy is actually better than buzzing's because:
- More aggressive builder spawning after round 300 (up to 12 builders)
- Extra builders find more ore and build more harvesters
- The wins are purely from better eco, NOT from launcher mechanics

## Losses Analyzed

- **default_small1**: Devastating loss (9326 vs 22470 Ti). Small map = fewer ore tiles,
  extra builders are wasted wandering. Buzzing's sentinel defense is more valuable here.
- **arena/galaxy**: Close losses. Buzzing's sentinels and barriers provide slight edge
  on open maps.

## Strategic Assessment

### Launcher drops are NOT viable as a primary strategy because:

1. **Range too short**: 5.1 tiles is insufficient to throw from a safe position
2. **Pioneer logistics**: Building a road network to enemy base costs ~30+ Ti and
   300+ rounds of builder time
3. **Landing problem**: Target must be passable. Can only land on enemy conveyors/roads,
   which are concentrated near their core -- exactly where defenses are strongest
4. **Resource waste**: 20 Ti for launcher + 30 Ti per builder thrown + roads = 100+ Ti
   for a single attack that does 2 damage/turn
5. **Sentinel hard-counter**: A single sentinel near the landing zone kills the thrown
   builder (18 damage vs 30 HP) before it does meaningful damage

### Potential niche uses:

- **Very small maps (20x20)** where cores are ~12 tiles apart -- launcher at midpoint
  could reach enemy conveyors. But these maps also have few resources.
- **Walled/fragmented maps** where traditional rushers can't path through. The throw
  goes OVER walls. This is the launcher's unique strength but requires the launcher
  to still be within 5 tiles of a landing spot.
- **Late-game harass** after establishing economic dominance -- throw disposable
  builders to distract enemy and force defensive spending.

## Recommendation

**Do NOT invest in launcher drops for the main bot.** The 5-tile throw range makes
it impractical on most competitive maps. Instead:

1. The extra builder spawning (cap 8-12 vs cap 5-7) from this bot IS valuable --
   consider integrating higher builder caps into buzzing.
2. Offensive pressure should come from traditional builder rushers (walking through
   own conveyor network) rather than launcher throws.
3. If launchers are used at all, they should be defensive -- throwing builders to
   repair/reinforce own positions, not offensive.

## Bot Location

`bots/launcher_drop/main.py`
