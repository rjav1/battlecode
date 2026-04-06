# v35 Galaxy Investigation Report

## Map Properties
- galaxy: 40x40, rotational, 16 Ti + 8 Ax ore, path=34/68
- Cores: (4,35) and (35,4)
- Classification: "expand" (area=1600)
- Spiral arm pattern with 8.4% walls

## Diagnostic Results (v34)

### vs ladder_eco (5 seeds)
- **3-2 win**: Seeds 2,3,5 win; seeds 1,4 lose
- Win seeds: both mine 9950 Ti, we store more (13051 vs 1037)
- Loss seeds: we mine 9950, they mine **14420** — they claim contested center ore
- We build only **5 harvesters** total (3 by r34, 2 at r823-827)

### vs ladder_rush: WIN (12702 stored, 9940 mined)
### vs starter: WIN (13737 stored, 13670 mined)
### vs ladder_eco vs starter: ladder_eco wins

## Root Cause Analysis

### 1. Builder Cap Bottleneck (econ_cap)
The core tracks `vis_harv` (harvesters visible from core, r^2=36).
On galaxy, only **1 harvester** is ever visible (nearest ore at dist 4).
The other 4 harvesters are built at distances 6-23 tiles from core, beyond vision.

**econ_cap = max(time_floor, vis_harv*3+4)** with vis_harv=1:
- r100: econ_cap = max(6, 7) = 7
- r200: econ_cap = max(7, 7) = 7
- r500: econ_cap = max(8, 7) = 8
- r1000: econ_cap = max(10, 7) = 10

**Effective cap = min(expand_cap, econ_cap):**
- r150-400: min(9, 7-8) = **7-8 builders**
- r400+: min(12, 8-10) = **8-10 builders**

We max out at **10 units** (9 builders + core) for the entire late game.

### 2. Attempts to Raise Builder Count FAILED
Every attempt to increase builders on expand maps caused regressions:
- More builders = more cost scaling (+20% per builder)
- More builders drain Ti faster, leaving less for harvesters
- On galaxy with only 16 Ti ore, more builders don't find more ore
- The 5 harvesters we build cover the reachable ore; the remaining 3 are on enemy side

### 3. The Real Galaxy Problem
With 16 Ti ore total on a rotational map, ore near the center is CONTESTED.
Whichever team's builders reach center ore first claims it.
- On seeds 1,4: ladder_eco's 40 builders claim 7-8 of 16 ore, mining 14420
- On seeds 2,3,5: both claim ~8 each, mining 9940-9950

**0-8 on ladder** against real opponents is NOT reproducible vs our test bots.
The issue is likely systemic, not galaxy-specific:
1. Opponents may deliver refined axionite (tiebreak #1), which we never do
2. Opponents may have better military pressure (sentinels, launchers)
3. Opponents may use foundries for Ax->Ti conversion (1:4 ratio)

### 4. Explore Pattern Changes Hurt
- Faster sector rotation (200r -> 100r): builders zigzag, don't commit
- Enemy-biased explore: builders skip nearby ore to rush toward enemy
- Lower explore Ti reserve: builders burn all Ti on conveyors, can't afford harvesters
- All variants regressed vs ladder_rush

## Changes Attempted (all reverted)
1. Expand cap 9->12->15: more builders but less Ti mined (cost scaling)
2. Skip econ_cap on expand maps: too many builders, Ti drained
3. econ_cap time_floor boost: same regression
4. Spawn reserve increase: no improvement, same econ_cap bottleneck
5. Faster sector rotation (200r -> 100r): zigzag, less ore found
6. Enemy-biased explore: skips nearby ore
7. Lower explore reserve: catastrophic Ti drain

## Conclusions

Galaxy is inherently coin-flippy on contested ore. Our 3-2 vs ladder_eco is
reasonable. The 0-8 on ladder likely stems from:

1. **No refined axionite** — opponents win tiebreak #1 with any Ax delivery
2. **Weak military** — galaxy's long path discourages rush, but mid-game
   sentinels/launchers can deny our ore
3. **No Ax economy** — 8 Ax ore tiles unused (we harvest but raw Ax destroyed at core)

### Recommended Next Steps (not implemented — require major features)
1. **Build foundry + refine Ax**: Even 1 refined Ax delivered wins tiebreak #1
2. **Sentinel defense**: Protect near-core harvesters from builder raids
3. **Launcher offense**: Throw builders at enemy harvesters on contested ore
4. These are not galaxy-specific fixes but general competitive improvements

## Final State
Code reverted to v34 (only docstring changed). No code changes deployed.
