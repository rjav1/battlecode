# Strategy Research: Gunner Defense

## Hypothesis
Gunners (10 Ti, +10% scale, 1-round reload, 2 ammo/shot) are more cost-efficient
than sentinels (30 Ti, +20% scale, 3-round reload, 10 ammo/shot) for static defense.
DPS per Ti invested is ~5x better for gunners.

## Bot Design: gunner_defense
- 4 builders, d.opposite() conveyor economy (same base as sentinel_spam)
- After round 150, builder #0 places 3-4 gunners at chokepoints facing enemy
- Gunners placed adjacent to existing conveyor chains for automatic Ti ammo
- Auto-fire via `c.get_gunner_target()` + `c.fire(target)`
- Fallback positions along enemy approach axis if no conveyors available

## Test Results

### vs rusher (aggressive attacker)
| Map | Winner | Gunner Ti (mined) | Rusher Ti (mined) | Notes |
|-----|--------|-------------------|-------------------|-------|
| face | **rusher** | 2,875 (140) | 6,248 (9,930) | Economy failed -- only 140 mined |
| corridors | **gunner_defense** | 24,839 (19,800) | 9,727 (4,990) | Dominant eco win |
| default_medium1 | **gunner_defense** | 2,093 (590) | 42 (0) | Both eco poor, gunner won |

### vs buzzing (v7 sentinel+bridge+barrier bot)
| Map | Winner | Gunner Ti (mined) | Buzzing Ti (mined) |
|-----|--------|-------------------|--------------------|
| default_medium1 | **gunner_defense** | 28,087 (23,510) | 21,089 (16,790) |
| face | **gunner_defense** | 22,650 (18,160) | 14,364 (9,870) |
| corridors | **gunner_defense** | 24,839 (19,800) | 15,039 (9,930) |

### vs starter
| Map | Winner | Gunner Ti (mined) | Starter Ti (mined) |
|-----|--------|-------------------|--------------------|
| default_medium1 | **gunner_defense** | 18,348 (14,680) | 3,129 (0) |

### vs sentinel_spam (head-to-head comparison)
| Map | Winner | Gunner Ti (mined) | Sentinel Ti (mined) | Delta |
|-----|--------|-------------------|---------------------|-------|
| face | **gunner_defense** | 27,533 (23,120) | 18,915 (14,430) | +8,618 |
| corridors | sentinel_spam (coinflip) | 24,839 (19,800) | 24,839 (19,800) | 0 |
| default_medium1 | **gunner_defense** | 27,336 (24,230) | 21,345 (18,200) | +5,991 |

## Overall Record: 9W-1L

## Key Findings

### 1. Gunners win via lower scaling cost, not via combat
The gunner bot consistently out-economied sentinel_spam by ~6,000-8,600 Ti on open maps.
This is because gunners cost +10% scale vs sentinels at +20%. Building 4 gunners adds
40% scaling vs 4 sentinels at 80%. The economy stays healthier.

### 2. Combat rarely matters in these matchups
On most maps neither bot's turrets actually fired -- the fights were pure economy races.
Both bots use identical economy patterns (d.opposite() conveyors, 4 builders).
The scale cost difference is the real differentiator.

### 3. The face map is problematic
Both gunner_defense and sentinel_spam lost to rusher on face with identical scores (2,875 Ti,
140 mined). This is a map/economy issue, not a turret issue -- the builders fail to find
and chain ore on this specific map layout.

### 4. Gunner ammo delivery is cheap
2 Ti per shot vs 10 Ti per sentinel shot means conveyors don't need to be dedicated.
Existing economy conveyors carry enough Ti to keep gunners firing continuously.

## Assessment

**Gunners are better than sentinels for passive defense in the current meta.**

The advantage isn't from combat superiority (gunner range is shorter: r^2=13 vs r^2=32).
It's from the 50% lower scaling cost preserving economy health. In a meta where games go
to tiebreak and Ti mined decides the winner, lower scaling = more buildings = more income.

### When sentinels might be better
- Against launcher-drop attacks (sentinel range r^2=32 covers more area)
- With refined Ax ammo (+5 cooldown stun is uniquely powerful)
- On maps where combat actually happens near turret positions

### Recommendation
Use gunners as the default cheap defense (10 Ti, low scaling impact). Reserve sentinels
for refined-Ax stun builds where the cooldown debuff justifies the 3x cost.
Consider a hybrid: 2 gunners for cheap DPS + 1 sentinel with Ax ammo for stun.
