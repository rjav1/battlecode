# Strategy Research: Map-Adaptive Bot

## Hypothesis

Detecting map size on round 1 and switching between rush/balanced/expand strategies
should outperform a one-size-fits-all approach by tailoring behavior to map characteristics.

## Classification Logic

```
area = width * height
if area <= 625:   strategy = "rush"      (25x25 or smaller)
elif area >= 1600: strategy = "expand"   (40x40 or larger)
else:              strategy = "balanced"  (medium maps)
```

Map classifications from the 38-map pool:
- **Rush** (8 maps): arena (25x25), face (20x20), default_small1 (20x20), default_small2 (21x21), shish_kebab (20x20), battlebot (21x29), thread_of_connection (20x20), gaussian (35x20=700 -> balanced)
- **Balanced** (14 maps): default_medium1 (30x30=900), default_medium2 (30x30), corridors (31x31=961), butterfly (31x31), cinnamon_roll (30x30), hooks (31x31), minimaze (25x25=625 -> rush), dna (21x50=1050), etc.
- **Expand** (16 maps): cubes (50x50), settlement (50x38), cold (37x37), default_large1 (40x40), default_large2 (50x30), galaxy (40x40), etc.

## Strategy Details

### Rush Mode (small maps)
- 5 builders spawned immediately (low reserve)
- Economy: only 2 harvesters, then switch to attack
- Early builders (born round <=5) do economy; rest become attackers
- Up to 2 gunners built facing enemy direction
- Attackers rush toward enemy core, destroying conveyors/harvesters along the way

### Expand Mode (large maps)
- Conservative start: 3 builders, scaling to 12 by late game
- Maximum harvester count
- d.opposite() conveyors for resource transport
- Bridge fallback for distant ore
- Barriers (up to 8) after round 200
- Sentinels (up to 3) after round 300

### Balanced Mode (medium maps)
- 4 initial builders, scaling to 11
- 4+ harvesters
- 4 barriers after round 150
- 2 sentinels after round 200
- 1 attacker after round 500

## Test Results

### vs starter (baseline opponent)

| Map | Size | Strategy | Winner | Adaptive Ti | Starter Ti | Margin |
|-----|------|----------|--------|-------------|------------|--------|
| face | 20x20 | rush | **adaptive** | 4,322 (4,980 mined) | 3,640 (0 mined) | +682 |
| arena | 25x25 | rush | **adaptive** | 7,771 (9,490 mined) | 3,521 (0 mined) | +4,250 |
| default_medium1 | 30x30 | balanced | **adaptive** | 7,125 (4,820 mined) | 3,200 (0 mined) | +3,925 |
| corridors | 31x31 | balanced | **adaptive** | 19,059 (14,650 mined) | 3,482 (0 mined) | +15,577 |
| settlement | 50x38 | expand | **adaptive** | 20,147 (24,240 mined) | 248 (0 mined) | +19,899 |
| cubes | 50x50 | expand | **adaptive** | 3,938 (19,580 mined) | 580 (0 mined) | +3,358 |

**vs starter: 6-0 (all wins)**

### vs buzzing (our strongest bot, one-size-fits-all)

| Map | Size | Strategy | Winner | Adaptive Ti | Buzzing Ti | Notes |
|-----|------|----------|--------|-------------|------------|-------|
| face | 20x20 | rush | **buzzing** | 11,079 (6,590) | 24,536 (20,580) | Rush mode mined less |
| arena | 25x25 | rush | **buzzing** | 6,322 (5,000) | 17,696 (15,630) | Buzzing eco dominates |
| default_medium1 | 30x30 | balanced | **adaptive** | 36,054 (35,160) | 9,173 (5,520) | Balanced mode strong |
| corridors | 31x31 | balanced | **adaptive** | 19,059 (14,650) | 15,039 (9,930) | Balanced wins |
| settlement | 50x38 | expand | **adaptive** | 17,047 (19,400) | 21,083 (17,910) | Won despite lower Ti total |
| cubes | 50x50 | expand | **adaptive** | 272 (19,580) | 22,375 (19,060) | Adaptive won (delivered more) |

**vs buzzing: 4-2 (adaptive wins on medium + large, loses on small)**

### Comparison: buzzing vs starter

| Map | Size | Winner | Buzzing Ti | Starter Ti |
|-----|------|--------|------------|------------|
| face | 20x20 | **buzzing** | 19,077 (14,770) | 4,707 (0) |
| default_medium1 | 30x30 | **buzzing** | 27,252 (26,410) | 3,070 (0) |
| settlement | 50x38 | **buzzing** | 36,129 (39,030) | 12 (0) |

## Analysis

### What worked

1. **Balanced mode is excellent on medium maps.** The adaptive bot beat buzzing 36,054 to 9,173 on default_medium1 -- a huge margin. The 4-builder start with moderate harvester targets was the sweet spot.

2. **Expand mode wins on large maps.** Won both settlement and cubes vs buzzing. On cubes, despite only having 272 Ti remaining vs buzzing's 22,375, the adaptive bot won because it *delivered* more refined resources to core (tiebreak is delivered, not stored).

3. **Strategy switching itself works.** The classification logic correctly identifies map types and triggers appropriate behaviors. Builders read strategy from map dimensions directly (marker-based communication was unreliable).

### What failed

1. **Rush mode on small maps loses to buzzing.** On face (20x20) and arena (25x25), the rush strategy mined only 5,000-6,590 Ti vs buzzing's 15,630-20,580. The problem: rushing with builders (2 damage, costs 2 Ti) is extremely resource-inefficient. Buzzing's pure economy approach vastly outproduces the rush on small maps.

2. **Small map problem diagnosis:** With only 8-10 Ti ore tiles on face/arena, economy is limited. But buzzing still mines 3-4x more because it:
   - Spawns economically-focused builders
   - Has efficient d.opposite() conveyor chains
   - Doesn't waste builders on attacking
   The rush builders burning 2 Ti per attack while earning nothing is a net negative.

### Key Insight

**Rush mode should not rush.** On small maps with scarce resources, pure economy is still optimal because:
- Builder attacks cost 2 Ti for 2 damage (terrible efficiency)
- Enemy core has 500 HP (250 attacks = 500 Ti just in attack costs)
- Lost builders cost 30+ Ti each to replace
- Small maps have fewer ore tiles, so every Ti matters more

**The real adaptation should be:**
- Small maps: tight economy, minimal builders, no military waste
- Medium maps: balanced approach (current balanced mode works great)
- Large maps: aggressive expansion with late defenses

## Verdict

**Map-adaptive strategy switching outperforms one-size-fits-all (4-2 vs buzzing)**, but the rush strategy specifically needs rethinking. The balanced and expand modes are strong. The ideal adaptive bot would:

1. Replace rush mode with a "tight economy" mode (fewer builders, maximum harvester efficiency)
2. Keep balanced mode as-is (strongest performance)
3. Keep expand mode as-is (wins on large maps)

## Recommended Next Steps

- Rework rush mode to be "economy-tight" instead of actual rushing
- Test the corrected adaptive bot across all 38 maps
- Consider additional classification signals: wall density, core distance, ore count
- Merge the strongest aspects into buzzing for the next submission
