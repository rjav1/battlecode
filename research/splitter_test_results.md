# Splitter -> Sentinel Ammo Delivery Test Results

## Verdict: CONFIRMED WORKING

Splitter-based ammo delivery to sentinels works reliably. Tested on 2 maps with different seeds.

## Test Setup

Bot: `bots/splitter_test/main.py`
Layout built by a single builder bot:

```
Harvester (on Ti ore)
    |
  Conv1 (facing chain_dir, picks up Ti from harvester)
    |
  Splitter (facing chain_dir, accepts from behind=conv1)
   / |
Branch (facing branch_dir, perpendicular to chain)
  |
Sentinel (facing branch_dir, accepts ammo from non-facing sides)
```

Key: the splitter alternates output between its 3 forward directions (forward, forward-left, forward-right). The branch conveyor sits on one of these output sides and feeds into the sentinel.

## Test Results

### Test 1: default_medium1, seed 1

```
Round 8: Built HARVESTER at Position(x=14, y=14)
Round 9: Built CONV1 at Position(x=13, y=14) facing Direction.WEST
Round 11: Built SPLITTER at Position(x=12, y=14) facing Direction.WEST
Round 12: Built BRANCH at Position(x=12, y=13) facing Direction.NORTH
Round 14: Built SENTINEL at Position(x=12, y=12) facing Direction.NORTH
Round 15: SENTINEL ammo=10 type=ResourceType.TITANIUM  <-- SUCCESS
```

- Infrastructure complete by round 14
- Sentinel loaded with 10 Ti ammo by round 15 (1 round after placement!)
- Ammo stayed at 10 throughout (no enemy targets to fire at)
- Splitter and branch conveyor both showed stored Ti in buffer, confirming flow
- Chain direction: WEST, Branch direction: NORTH (perpendicular)

### Test 2: default_medium2, seed 5

```
Round 50: Built HARVESTER at Position(x=27, y=19)
Round 51: Built CONV1 at Position(x=28, y=19) facing Direction.EAST
Round 53: Built SPLITTER at Position(x=29, y=19) facing Direction.EAST
Round 54: Built BRANCH at Position(x=29, y=18) facing Direction.NORTH
Round 56: Built SENTINEL at Position(x=29, y=17) facing Direction.NORTH
Round 57: SENTINEL ammo=10 type=ResourceType.TITANIUM  <-- SUCCESS
```

- Different map, different positions, different chain direction (EAST)
- Same result: sentinel loaded with ammo 1 round after placement
- Confirmed reproducible across maps

## Proven Pattern

```
Harvester -> Conveyor(chain_dir) -> Splitter(chain_dir) -> [branch Conveyor(perp_dir)] -> Sentinel(perp_dir)
```

### Rules:
1. **Splitter facing**: Must face the chain direction (same as conveyors in the main chain). It accepts from behind (where conv1 is).
2. **Branch conveyor**: Place on one of the splitter's 3 forward output tiles (forward, forward-left, forward-right). Face it perpendicular to the chain (away from splitter).
3. **Sentinel facing**: Face it in the SAME direction as the branch conveyor (away from where ammo enters). This ensures the ammo-entry side is NOT the sentinel's facing direction, so it accepts the ammo.
4. **Perpendicular branch**: Using `chain_dir.rotate_left().rotate_left()` or `chain_dir.rotate_right().rotate_right()` gives a clean 90-degree branch.

### What NOT to do:
- Do NOT face the sentinel toward the branch conveyor (facing `branch_dir.opposite()`) -- this would mean the sentinel's facing direction matches the ammo entry side, blocking delivery.

## Resource Flow Observation

Every 4 rounds (harvester output interval), a Ti stack flows:
1. Harvester produces Ti stack
2. Conv1 carries it to splitter
3. Splitter alternates between its 3 outputs -- approximately 1/3 of stacks go to the branch
4. Branch conveyor carries Ti to sentinel
5. Sentinel accepts when empty (ammo=0), fills to 10

The splitter continuously alternates, so roughly every 3rd harvester output reaches the sentinel. With multiple harvesters or faster production, this rate increases.

## Costs

For a single sentinel ammo branch:
- Harvester: 20 Ti
- Conv1: 3 Ti
- Splitter: 6 Ti
- Branch conveyor: 3 Ti
- Sentinel: 30 Ti
- **Total: 62 Ti** for a self-loading sentinel

## Integration Notes

For the main bot:
1. Can share a harvester/chain with the core economy -- just insert a splitter anywhere in an existing conveyor chain
2. The splitter replaces one conveyor in the chain (destroy old conveyor, build splitter facing same direction)
3. Branch off the splitter to feed sentinels while the main chain continues to deliver to core
4. Multiple branches possible from one splitter (all 3 forward outputs can be used)
5. Cost scaling: splitter adds +1% (same as conveyor), sentinel adds +20%
