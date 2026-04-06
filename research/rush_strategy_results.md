# Rush Strategy Bot Results

## Bot: `bots/rusher/main.py`
## Date: April 4, 2026

## Strategy Summary

The rusher bot uses a split strategy:
- **2 economy builders** (spawned rounds 1-2): find Ti ore, build harvester, lay conveyor chain to core
- **2+ attackers** (spawned round 3+): rush toward enemy base via roads, walk on enemy conveyors/roads and destroy them
- **Core**: spawns 4 builders in first 8 rounds, then continues spawning with Ti reserve

Key findings during development:
- **Builders CANNOT walk on enemy core** (only allied core). Only conveyors and roads are walkable by either team.
- **Builder fire() only damages the building the builder is standing ON**. So the only enemy buildings attackers can damage are conveyors and roads.
- The rush component is primarily about **economic sabotage** (destroying enemy conveyors) rather than core destruction.
- **Core destruction requires turrets** (gunners, sentinels, breach) -- builders alone cannot damage the enemy core.
- The rusher's economy is surprisingly effective on its own -- it consistently mines 5000-15000 Ti.

## Results vs Starter Bot

All games with seed=42, decided by Resources tiebreak at turn 2000.

| Map | Result | Rusher Ti (Mined) | Starter Ti (Mined) |
|-----|--------|-------------------|-------------------|
| face (20x20, path=9) | **WIN** | 12,083 (9,940) | 4,998 (0) |
| arena (25x25, path=8) | LOSS | 25 (0) | 2,789 (0) |
| corridors (31x31, path=42) | **WIN** | 9,761 (4,990) | 2,971 (0) |
| default_medium1 (30x30, path=9) | **WIN** | 6,995 (9,830) | 3,361 (0) |
| default_small1 (20x20, path=19) | **WIN** | 12,421 (9,930) | 4,918 (0) |
| landscape (30x30, path=25) | **WIN** | 122 (4,940) | 1,559 (0) |
| starry_night (50x41, path=9) | **WIN** | 32 (4,950) | 25 (0) |
| cold (37x37, path=12) | **WIN** | 53 (4,960) | 34 (0) |
| binary_tree (41x30, path=20) | **WIN** | 13,337 (14,870) | 2,153 (0) |
| hourglass (27x45, path=42) | **WIN** | 2,217 (4,940) | 3,469 (0) |
| default_large1 (40x40, path=17) | **WIN** | 11,134 (14,760) | 1,292 (0) |

**Record vs starter: 10W-1L** (only loss: arena)

## Results vs Buzzing Bot (our main economy bot)

| Map | Result | Rusher Ti (Mined) | Buzzing Ti (Mined) |
|-----|--------|-------------------|-------------------|
| face (20x20, path=9) | **WIN** | 7,681 (9,920) | 2,804 (250) |
| arena (25x25, path=8) | LOSS | 16 (0) | 7,476 (6,200) |
| corridors (31x31, path=42) | LOSS | 9,764 (4,990) | 14,879 (9,930) |
| default_medium1 (30x30, path=9) | **WIN** | 1,036 (4,920) | 317 (1,010) |
| default_small1 (20x20, path=19) | **WIN** | 16,379 (14,830) | 4,441 (390) |
| landscape (30x30, path=25) | **WIN** | 21 (4,940) | 1,522 (2,950) |
| starry_night (50x41, path=9) | LOSS | 26 (4,950) | 27 (6,250) |
| cold (37x37, path=12) | **WIN** | 1,238 (4,960) | 23 (2,430) |
| binary_tree (41x30, path=20) | **WIN** | 14,096 (14,870) | 2,631 (830) |
| hourglass (27x45, path=42) | **WIN** | 15,482 (14,800) | 2,859 (610) |
| default_large1 (40x40, path=17) | **WIN** | 14,250 (14,740) | 2,135 (570) |

**Record vs buzzing: 8W-3L**

## Analysis

### Where Rusher Wins
- **Most maps**: The rusher's economy is actually stronger than buzzing's because the conveyor chain logic is cleaner and more efficient.
- The rusher mines 5000-15000 Ti consistently, outperforming buzzing (which often mines 200-2000 Ti).
- This is primarily an **economy win**, not a rush win. The attackers don't significantly damage the enemy.

### Where Rusher Loses
- **arena**: Ore is 6+ BFS steps from core, beyond builder starting vision (r^2=20, ~4.5 tiles). Economy builders never find ore. All Ti is spent on attacker roads.
- **corridors vs buzzing**: Buzzing mines 9930 vs rusher's 4990. On this long map, buzzing's economy is more mature. The rusher only connects 1-2 harvesters while buzzing connects more.
- **starry_night vs buzzing**: Very close (4950 vs 6250 mined). Buzzing's extra harvesters win marginal advantage.

### Key Takeaway
**The rush component (attacking enemy infrastructure) had minimal impact.** The wins come from the rusher having a cleaner economy than its opponents. The attackers mostly wander around building roads toward the enemy but rarely find enemy conveyors to destroy (the starter doesn't build them, and buzzing's conveyors are near its own core, far from our attackers).

### Potential Improvements
1. **Better ore exploration**: The arena loss is purely due to not finding ore. A smarter BFS-based exploration could fix this.
2. **Turret-based offense**: Build gunners or sentinels near enemy core instead of relying on builder fire(). Gunners deal 10 damage at range.
3. **Launcher drops**: Build a launcher and throw attackers directly into enemy territory, bypassing the long road walk.
4. **Adaptive strategy**: Detect map size/distance at game start. Rush on short maps, economy on long maps.
5. **Sentinel defense**: Build sentinels along the approach path to protect economy from enemy rushers.

### Data for Adaptive Bot Design
Maps where rusher economy excels (mines 10000+ Ti):
- face, default_small1, binary_tree, hourglass, default_large1

Maps where rusher economy struggles (mines 0-5000 Ti):
- arena (0), landscape (~5000), corridors (~5000), starry_night (~5000)

The difference is primarily ore proximity to core and map connectivity.
