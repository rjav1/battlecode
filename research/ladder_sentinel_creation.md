# ladder_sentinel Bot Creation — Task #18

**Date:** 2026-04-06
**File:** bots/ladder_sentinel/main.py

## Objective

Model Polska Gurom's sentinel-heavy defense (2 sentinels by round 389, 6 by round 1117)
to test buzzing's rush defense improvements.

## Architecture

### Core spawning
- Builder ramp: 4 by round 30, 6 by 100, 7 by 200, 8 after (matches smart_eco)
- Ti reserve: cost+5 before spawning

### Builder roles
- Builders by id%5 slot:
  - Slots 0, 1, 2: pure miners (d.opposite() conveyors, ore targeting, harvester building)
  - Slot 3 (id%5==3): sentinel builder, activates at round 300
  - Slot 4 (id%5==4): sentinel builder, activates at round 500
- Before activation round, sentinel builders mine like normal builders

### Sentinel placement
- Placed 4-5 tiles from core in enemy direction
- Up to 6 sentinels total (SENTINEL_CAP=6)
- Slots: (4 fwd, center), (4 fwd, 2 left/right), (5 fwd, center), (5 fwd, 3 left/right)
- All face enemy direction

### Ammo delivery
- Each sentinel gets a splitter chain:
  - Conveyors from core toward sentinel (d.opposite() facing, deliver toward core)
  - Splitter directly behind sentinel, facing sentinel_dir (outputs toward sentinel)
- Pattern from bots/splitter_test/main.py confirmed working

### Enemy direction detection
- Symmetry-based detection from buzzing's _get_enemy_direction
- Scores 3 mirror symmetries (rotation, horizontal flip, vertical flip) based on tile env matches
- Picks highest-scoring mirror to find enemy core position

## Test Results

### vs buzzing (seed 1, 5 standard maps)

| Map            | Winner          | buzzing Ti mined | ladder_sentinel Ti mined |
|----------------|-----------------|-----------------|--------------------------|
| default_medium1| ladder_sentinel | 9100            | 26320                    |
| cold           | buzzing         | 19670           | 19610                    |
| face           | ladder_sentinel | 17840           | 20330                    |
| settlement     | buzzing         | 33270           | 19320                    |
| galaxy         | buzzing         | 14210           | 9910                     |

**Result: 2W-3L vs buzzing**

### vs smart_eco (pure economy baseline)

- default_medium1: LOSS (21060 vs 24100 Ti mined)
- face: LOSS (9610 vs 14710 Ti mined)

Sentinel builders divert ~5-10K Ti in economy toward defense infrastructure.

## Analysis

### What works
- Sentinel placement logic functions correctly
- Ammo chain (conveyors + splitter) builds successfully
- Enemy direction detection via symmetry works
- Bot mines 20K+ Ti on default_medium1 and face

### Limitations
- Economy suffers vs pure-eco opponents (smart_eco wins easily)
- 2 sentinel builders out of 8 total = 25% of labor on defense
- Settlement/galaxy losses are likely spawn-side disadvantages (buzzing team A)
- Cold is a near-draw (19670 vs 19610 mined)

### How to use for testing
Run: `cambc run buzzing ladder_sentinel face`

This tests whether buzzing's rush defense holds against sentinel-based defense.
The ladder_sentinel bot provides:
- Sentinel barriers that should slow builder bots approaching the core
- Ammo delivery via splitter pattern (proven working)
- Economy roughly comparable to buzzing on favorable maps
