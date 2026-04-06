# Harvester Throughput Analysis: Why 2-10 vs Opponents' 19-40

Date: 2026-04-06

## Summary

Our bot builds 2-10 harvesters per game while top opponents (The Defect) build 19-40. This is the single biggest cause of economic losses. The root causes are: (1) too few builders spending too little time mining, (2) overly conservative builder spawning caps, and (3) excessive Ti spent on non-harvester infrastructure.

---

## Root Cause #1: Builder Role Dilution (CRITICAL)

### Data
- The Defect: 6 bots total, ALL 5 builders mine full-time = 3-7 harvesters per builder
- buzzing: 8-15 bots, but multiple builders diverted to non-mining roles = 0.1-1.0 harvesters per builder

### Code Analysis

**Builder role assignments steal miners from the economy:**

1. **Gunner builder** (`main.py:369-374`): `id%5==1` switches at round 30-150 depending on map mode, requiring only 1-3 harvesters first. This pulls 20% of builders off mining when the economy barely has any harvesters.

2. **Attacker** (`main.py:357-363`): `id%6==5` after round 500 with 4+ harvesters. Another 17% of builders permanently lost to raiding.

3. **Sentinel splice** (`main.py:377-385`): Round 500+, 5+ harvesters, non-tight maps. Multi-round stateful build that takes a builder offline for 10-20 rounds.

4. **Ax tiebreaker** (`main.py:387-394`): `id%6==2` at round 1800+. Wanders for up to 100 rounds looking for Ax ore, often getting stuck oscillating between two tiles (documented bug in local_bot_losses_debug.md).

5. **Early barrier builder** (`main.py:246-288`): Second+ builder places barriers as first action on tight maps — delays their first harvester.

6. **Barrier walls** (`main.py:397-402`): Round 80+ near core with 50+ Ti — another interruption from mining.

7. **Spend-down gunner** (`main.py:347-354`): Round 300+ with 300+ Ti and 3+ harvesters — further builder distraction.

### Impact Calculation

With 10 builders and these role splits:
- 2 builders (id%5==1) → gunner duty at round 30-150
- 1 builder (id%6==5) → attacker at round 500
- 1 builder → sentinel splice at round 500
- 1 builder (id%6==2) → Ax tiebreaker at round 1800
- Remaining 5 builders → actual miners, but interrupted by barriers and spend-down gunners

Effective mining builders: ~5 out of 10, and those 5 still get interrupted. The Defect gets 5 out of 5 builders mining with zero interruptions.

### Specific Code Changes

**`main.py:369-374` (gunner builder):**
```python
# CURRENT:
gunner_round = 30 if map_mode == "tight" else (120 if map_mode == "balanced" else 150)
harv_req = 1 if map_mode == "tight" else 3

# PROPOSED:
gunner_round = 60 if map_mode == "tight" else (250 if map_mode == "balanced" else 400)
harv_req = 3 if map_mode == "tight" else 6
```

**`main.py:357-363` (attacker):**
```python
# CURRENT:
if (not self.is_attacker and rnd > 500
        and self.harvesters_built >= 4
        and (self.my_id or 0) % 6 == 5):

# PROPOSED:
if (not self.is_attacker and rnd > 800
        and self.harvesters_built >= 8
        and (self.my_id or 0) % 6 == 5):
```

**`main.py:377-385` (sentinel splice):**
```python
# CURRENT:
if (... and rnd >= 500 and self.harvesters_built >= 5 ...):

# PROPOSED:
if (... and rnd >= 1000 and self.harvesters_built >= 10 ...):
```

---

## Root Cause #2: Conservative Builder Spawning Caps (HIGH)

### Data
- The Defect: 6 total units by round 50 (5 builders), all mining immediately
- ladder_bridge: caps 5/10/15/20 builders at rounds 1/20/60/150
- buzzing: caps 3/5/8 on expand maps at rounds 1/30/150

### Code Analysis (`main.py:96-126`)

The core spawn logic has two throttles stacked on top of each other:

**Throttle 1 — Hard caps (line 98-103):**
```python
if self.map_mode == "tight":
    cap = 3 if rnd <= 20 else (5 if rnd <= 100 else 8)
elif self.map_mode == "expand":
    cap = 3 if rnd <= 30 else (5 if rnd <= 150 else (8 if rnd <= 400 else 12))
else:  # balanced
    cap = 3 if rnd <= 25 else (4 if rnd <= 100 else (6 if rnd <= 300 else 8))
```

On expand maps, we only have 3 builders for the first 30 rounds, then 5 until round 150. The Defect has 5 builders by round ~15.

**Throttle 2 — econ_cap (line 113-121):**
```python
econ_cap = max(time_floor, vis_harv * 3 + 4)
cap = min(cap, econ_cap)
```
`vis_harv * 3 + 4` means: 0 visible harvesters = cap 4, 1 harvester = cap 7, 2 harvesters = cap 10. This throttle actually prevents over-spawning when economy is bad, but it further restricts early spawning when combined with the hard caps.

**Throttle 3 — Ti reserve (line 124-125):**
```python
if ti < cost + 2:
    return
```
This is fine — minimal reserve.

### Specific Code Changes

**`main.py:98-103` (hard caps):**
```python
# PROPOSED:
if self.map_mode == "tight":
    cap = 3 if rnd <= 15 else (5 if rnd <= 60 else 8)
elif self.map_mode == "expand":
    cap = 5 if rnd <= 20 else (8 if rnd <= 100 else (12 if rnd <= 300 else 16))
else:  # balanced
    cap = 4 if rnd <= 20 else (6 if rnd <= 80 else (8 if rnd <= 200 else 12))
```

---

## Root Cause #3: Ti Wasted on Non-Harvester Infrastructure (HIGH)

### Data (from replay analysis)

| Resource | buzzing (per game) | The Defect (per game) |
|----------|-------------------|-----------------------|
| Ti on conveyors | 600-1350 Ti (200-450 at 3 Ti) | 27-96 Ti (9-32 at 3 Ti) |
| Ti on roads | 0-12 Ti | 178-341 Ti |
| Ti on bridges | 0-160 Ti | 0 Ti |
| Ti on barriers | 9-45 Ti | 0 Ti |
| Ti on gunners | 10-50 Ti | 0 Ti |
| Ti on builders | 300-450 Ti (10-15 at 30+ Ti) | 150-180 Ti (5 at 30 Ti) |

buzzing spends 600-1350 Ti on conveyors alone. At 20 Ti per harvester (base cost), that's 30-67 harvesters worth of Ti going to conveyors instead. Even accounting for necessary transport conveyors, the excess is enormous because:

1. `_nav` builds a conveyor on EVERY tile the builder walks over (line 510-527)
2. `_explore` also calls `_nav` which builds conveyors while exploring (line 616)
3. Conveyors cost 3 Ti each and +1% scale — a conveyor chain of 15 tiles costs 45 Ti + 15% scale increase

The Defect uses roads (1 Ti, +0.5% scale) for builder movement and only uses conveyors for the actual resource transport chain from harvester to core.

### Specific Code Changes

See conveyor_waste_analysis.md for detailed conveyor-specific fixes. The key change for harvester throughput: **stop building conveyors during exploration** and use roads instead.

---

## Root Cause #4: Ore Selection Converges All Builders on Same Cluster (MEDIUM)

### Code Analysis (`main.py:444-472`)

The ore scoring formula:
```python
if use_nearest:
    score = builder_dist
else:
    core_dist = t.distance_squared(self.core_pos) if self.core_pos else 0
    score = builder_dist + core_dist * 2
```

All builders use the same deterministic scoring — they all converge on the closest cluster of ore near the core. The marker claiming system (line 485-490) tries to prevent duplication, but markers are limited:
- Only placed when `distance_squared > 2` (not adjacent)
- Only penalized by +10000, which doesn't prevent convergence when all ore scores are similar
- Markers block harvester build if the builder that placed them arrives first

The Defect likely uses randomization or builder-ID-based sector assignment to spread builders across different ore patches.

### Specific Code Change

**`main.py:444-472` (ore scoring):**
Add builder-ID-based spread factor:
```python
# After computing score, add ID-based diversity bonus
# Builders with different IDs prefer different ore clusters
id_hash = ((self.my_id or 0) * 2654435761) & 0xFFFFFFFF
tile_hash = (t.x * 73856093 + t.y * 19349663) & 0xFFFFFFFF
diversity = ((id_hash ^ tile_hash) % 100) * 5  # 0-495 random per builder-tile pair
score += diversity
```

---

## Projected Impact

| Fix | Harvesters gained | Ti/game gained |
|-----|-------------------|----------------|
| Delay role splits (RC#1) | +3-5 per game | +2000-4000 |
| Raise builder caps (RC#2) | +2-4 per game | +1500-3000 |
| Reduce conveyor waste (RC#3) | +2-3 per game (from saved Ti) | +1000-2000 |
| Spread ore selection (RC#4) | +1-2 per game | +500-1000 |
| **Combined** | **+8-14 per game** | **+5000-10000** |

Current average: ~6 harvesters/game. Target: 14-20 harvesters/game.
Current average Ti collected: ~10000/game. Target: 15000-20000/game.
