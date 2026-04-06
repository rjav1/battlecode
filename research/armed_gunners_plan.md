# Armed Sentinels Integration Plan (Splitter + Sentinel Ammo)

## Summary

Integrate the proven splitter→branch conveyor→sentinel ammo delivery pattern from `bots/splitter_test/main.py` into the main `bots/buzzing/main.py` bot (v35, 837 lines). The pattern costs 62 Ti total per setup (harvester 20 + conv 3 + splitter 6 + branch 3 + sentinel 30) and delivers ammo within 1 round of splitter receiving a stack.

---

## 1. Proven Pattern (from splitter_test)

The exact working layout:
```
[Harvester] → [Conveyor facing chain_dir] → [Splitter facing chain_dir] → continues to core
                                                     ↓ (perpendicular branch)
                                              [Branch Conv facing branch_dir] → [Sentinel facing branch_dir]
```

Key details:
- **Splitter** faces `chain_dir` (same direction as main conveyor chain). Accepts from behind (opposite of chain_dir), outputs alternating between 3 forward directions.
- **Branch conveyor** is perpendicular: `chain_dir.rotate_left().rotate_left()` or `chain_dir.rotate_right().rotate_right()`.
- **Sentinel faces** `branch_dir` (same as branch conveyor direction). Ammo enters from `branch_dir.opposite()` which is NOT the facing side, so it's accepted.
- Sentinel must NOT face `branch_dir.opposite()` (that would be the ammo input side, blocking delivery).

---

## 2. Current Architecture Analysis

### Builder flow (main.py lines 147-383):
1. **Early barriers** (lines 222-264): rounds ≤30, near core
2. **Attacker assignment** (lines 267-273): round >500, id%6==5
3. **Gunner builder** (lines 276-284): id%5==1, round >150-200, harvesters≥3
4. **Barrier placement** (lines 287-294): round ≥80, near core, Ti≥50
5. **Chain-fix mode** (lines 296-298)
6. **Build harvester on adjacent ore** (lines 300-327)
7. **Pick ore target + navigate** (lines 329-382)

### Gunner placement (`_place_gunner`, lines 506-546):
- Finds empty tile near current position facing enemy
- No ammo delivery — gunner relies on conveyors that happen to pass resources
- Cap of 3 gunners, checks nearby gunner count each call
- Cost: 10 Ti + 10% scale per gunner

### Existing sentinel handler (lines 127-138):
- Already fires at enemies when ammo≥10 and cooldown==0
- Works correctly — no changes needed

### Existing gunner handler (lines 140-145):
- Fires at gunner_target when ammo≥2
- Works correctly — no changes needed

---

## 3. WHERE to Insert: New Method `_place_armed_sentinel`

**Insert a new method after `_place_gunner` (after line 546)**. This keeps gunner logic separate and avoids disrupting existing code.

The new method `_place_armed_sentinel(self, c, pos)` will:
1. Find an existing conveyor chain tile near the builder (within action radius)
2. Plan the splitter→branch→sentinel layout off that chain tile
3. Build the components in sequence across multiple rounds (stateful, like `_build_chain` in splitter_test)

### Call site: Replace or supplement gunner builder logic

**Modify lines 276-284** (gunner builder section) to add sentinel placement as an alternative:

```python
# Current (lines 276-284):
if (map_mode != "tight"
        and (self.my_id or 0) % 5 == 1 and rnd > gunner_round
        and self.harvesters_built >= 3 and self.core_pos
        and self.gunner_placed < 3
        and c.get_global_resources()[0] >= 20):
    if self._place_gunner(c, pos):
        return

# Proposed addition AFTER the gunner block (insert at line 285):
if (not self.is_attacker
        and rnd >= 1000
        and self.harvesters_built >= 5
        and not hasattr(self, '_sentinel_complete')
        and self.core_pos
        and c.get_global_resources()[0] >= 70):
    if self._place_armed_sentinel(c, pos):
        return
```

---

## 4. WHEN to Trigger

Based on memory: "Sentinel timing MUST be late (round 1000+) — earlier drops Ti 30-50%"

### Trigger conditions:
| Condition | Value | Rationale |
|-----------|-------|-----------|
| Round | ≥ 1000 | Memory says earlier = 30-50% Ti regression |
| Harvesters built | ≥ 5 | Ensure strong economy before 62 Ti + 21% scale spend |
| Ti available | ≥ 70 | Need 62 Ti for full setup + buffer |
| Sentinel complete | False | Only build ONE sentinel setup (cap at 1) |
| Map mode | Any except tight | Tight maps (≤25x25) don't benefit — too cramped |
| Not attacker | True | Attackers should attack, not build defenses |

### Why round 1000+:
- By round 1000, economy is mature (5+ harvesters producing ~12.5 Ti/round)
- Cost scaling from 62 Ti setup won't crater income
- Late-game defense matters more (enemy attackers arrive round 500+)
- Games end at round 2000, so sentinel has 1000 rounds to contribute

---

## 5. Integration Approach

### Phase 1: Add state variables to `__init__` (line 31-50)

Add after `self._marker_placed = False` (line 50):
```python
self._sentinel_step = 0        # 0=inactive, 1=find_chain, 2=build_splitter, 3=build_branch, 4=build_sentinel, 5=done
self._sentinel_positions = {}  # planned positions for splitter, branch, sentinel
self._sentinel_chain_dir = None
self._sentinel_branch_dir = None
```

### Phase 2: New method `_place_armed_sentinel` (insert after line 546)

```python
def _place_armed_sentinel(self, c, pos):
    """Build splitter+branch+sentinel off an existing conveyor chain."""
    if self._sentinel_step == 0:
        # Find a conveyor within action radius that's part of our chain
        # Prefer conveyors close to core (more resource flow)
        ...find chain tile, plan layout, set step=1...
    elif self._sentinel_step == 1:
        # Replace the found conveyor with a splitter (same facing)
        ...destroy conveyor, build splitter, set step=2...
    elif self._sentinel_step == 2:
        # Build branch conveyor perpendicular to chain
        ...build branch conv, set step=3...
    elif self._sentinel_step == 3:
        # Build sentinel at end of branch
        ...build sentinel, set step=4, mark _sentinel_complete=True...
    return self._sentinel_step > 0  # True if actively building
```

### Phase 3: Integration into builder flow (lines 276-285)

Add the trigger condition block after gunner placement.

### Phase 4: Handle the `run()` dispatch (line 58-61)

The sentinel handler at lines 127-138 already works. No changes needed.

---

## 6. Critical Implementation Details

### Finding a chain tile to splice into:
The bot builds conveyors with `d.opposite()` facing as breadcrumb trails. To find a good splice point:
1. Scan `c.get_nearby_buildings()` for allied conveyors
2. Prefer conveyors close to core (they carry more resource stacks)
3. The conveyor's `c.get_direction(eid)` tells us the chain direction (but it's stored as opposite — the conveyor faces TOWARD the harvester, resources flow toward core)
4. The actual resource flow direction is `c.get_direction(eid).opposite()`

**IMPORTANT: chain_dir for the splitter = the conveyor's facing direction** (d.opposite() in the original build). The splitter replaces the conveyor and must face the same way to maintain chain continuity.

### Layout planning:
```python
chain_dir = c.get_direction(conv_id)  # conveyor's facing direction
splitter_pos = c.get_position(conv_id)
# Try both perpendicular directions
for branch_dir in [perp_left(chain_dir), perp_right(chain_dir)]:
    branch_pos = splitter_pos.add(branch_dir)
    sentinel_pos = branch_pos.add(branch_dir)
    # Check both positions are empty and in bounds
    if (c.is_tile_empty(branch_pos) and c.is_tile_empty(sentinel_pos)
            and c.get_tile_env(branch_pos) != Environment.WALL
            and c.get_tile_env(sentinel_pos) != Environment.WALL):
        # Valid layout found
        break
```

### Splitter replacement:
1. Destroy the existing conveyor: `c.destroy(splitter_pos)`
2. Build splitter with SAME facing: `c.build_splitter(splitter_pos, chain_dir)`
3. Splitter accepts from behind (chain_dir.opposite()) — same input as the original conveyor
4. Splitter outputs to chain_dir (continuing the main chain) AND to perpendicular (branch)

### Sentinel facing:
- Face `branch_dir` (same as branch conveyor output direction)
- This means ammo enters from `branch_dir.opposite()` which is a non-facing side → accepted
- The sentinel's forward firing line is along `branch_dir` — perpendicular to the main chain

---

## 7. Economy Impact Analysis

### Cost breakdown:
| Component | Ti | Scale | Notes |
|-----------|-----|-------|-------|
| Splitter | 6 | +1% | Replaces conveyor (refunds 3 Ti cost, +1% scale) — net +3 Ti, 0% extra scale |
| Branch conveyor | 3 | +1% | New |
| Sentinel | 30 | +20% | New |
| **Net new cost** | **~36 Ti** | **+21%** | After accounting for replaced conveyor |

Actually: destroying the old conveyor reverses its +1% scale, then the splitter adds +1%. So net scale from the swap is 0%. Total new scale = branch (+1%) + sentinel (+20%) = **+21%**.

### Risk mitigation:
1. **Round 1000+ gate**: Economy is mature, 36 Ti is ~3 rounds of income from 5 harvesters
2. **Ti ≥ 70 gate**: Ensures we have buffer after building
3. **Cap at 1 sentinel**: Limits total scale impact to +21% (vs potentially unlimited)
4. **Harvester ≥ 5 gate**: Ensures enough income to absorb cost

### Expected benefit:
- Armed sentinel has 18 damage, r²=32 vision, hits in a wide line
- At round 1000+, enemy attackers and stray builders are the main threat
- One armed sentinel can deny an entire corridor
- With refined Ax ammo: +5 action AND move cooldown stun (but we don't refine Ax, so Ti ammo only)

### Comparison vs current gunners:
| | Gunner | Armed Sentinel |
|--|--------|---------------|
| Cost | 10 Ti | 36 Ti (net) |
| Scale | +10% | +21% |
| Damage | 10 (30 w/ Ax) | 18 |
| Vision r² | 13 | 32 |
| Ammo/shot | 2 | 10 |
| Reload | 1 round | 3 rounds |
| Coverage | Forward ray only | Wide line within 1 Chebyshev |

Sentinel is better for area denial. Gunner is better for economy (cheaper). **Keep both**: gunners for early defense (round 150-200), sentinel for late-game area denial (round 1000+).

---

## 8. Potential Conflicts

### 1. Builder walking to chain tile
The builder needs to be within action radius (r²≤2) of the target conveyor to destroy and rebuild it. If no conveyors are nearby, builder must walk toward core to find one. This could conflict with ore-seeking behavior.

**Mitigation**: Only start sentinel building when builder is already near a conveyor (within vision). Set `self._sentinel_step = 1` and treat it like `fixing_chain` — a temporary mode that overrides ore-seeking until complete.

### 2. Destroying a conveyor breaks the chain temporarily
Between destroying the conveyor and building the splitter, there's a gap. If the builder's action cooldown prevents immediate splitter build, resources may back up for 1 round.

**Mitigation**: Check `c.get_action_cooldown() == 0` before destroying. Destroy + build in same turn (destroy has no cooldown cost per CLAUDE.md: "Remove allied building within action radius (no cooldown cost, repeatable)").

### 3. Ore claiming markers
Builder might have an active ore target when sentinel building triggers. Need to clear target state.

**Mitigation**: When entering sentinel build mode, set `self.target = None` and clear marker state.

### 4. Map mode "tight"
Tight maps (≤25x25) have limited space. Sentinel + branch + splitter might collide with existing infrastructure.

**Mitigation**: Skip sentinel on tight maps entirely (already in trigger conditions).

### 5. Scale impact on other buildings
+21% scale affects ALL future builds. At round 1000 this is less impactful since most building is done.

**Mitigation**: Already handled by round 1000+ gate.

---

## 9. Step-by-Step Implementation

### Step 1: Add state variables
- File: `bots/buzzing/main.py`
- Location: `__init__` method, after line 50
- Add: `_sentinel_step`, `_sentinel_positions`, `_sentinel_chain_dir`, `_sentinel_branch_dir`

### Step 2: Add helper functions
- Location: Top of file, after DIRS definition (line 28)
- Add `perp_left(d)` and `perp_right(d)` helper functions (from splitter_test)

### Step 3: Add `_place_armed_sentinel` method
- Location: After `_place_gunner` method (after line 546)
- Multi-step stateful method:
  - Step 0: Scan nearby conveyors, pick best one, plan layout
  - Step 1: Walk to target conveyor if not in range
  - Step 2: Destroy conveyor + build splitter (same turn, destroy has no cooldown)
  - Step 3: Walk to branch position + build branch conveyor
  - Step 4: Walk to sentinel position + build sentinel
  - Step 5: Mark complete, return to normal behavior

### Step 4: Add trigger in builder flow
- Location: After gunner builder block (line 284)
- Conditions: round ≥1000, harvesters≥5, Ti≥70, not tight, not complete, not attacker

### Step 5: Update version docstring
- Increment to v36

---

## 10. Testing Plan

### Test 1: Ammo delivery verification
```bash
cambc run buzzing starter --watch --seed 42
```
Watch replay to verify:
- Splitter gets built around round 1000
- Branch conveyor + sentinel get built shortly after
- Sentinel receives ammo (check ammo count in replay)
- Main chain still delivers Ti to core (no break)

### Test 2: Economy regression check
```bash
# Run on 3 key maps, compare Ti mined
cambc run buzzing buzzing_prev default_medium1 --seed 1
cambc run buzzing buzzing_prev settlement --seed 1
cambc run buzzing buzzing_prev galaxy --seed 1
```
- Ti mined should NOT decrease by more than 5%
- If regression >10%, increase round gate to 1200 or 1500

### Test 3: Paired test suite
```bash
python test_suite.py --paired buzzing_prev
```
- Must maintain >50% win rate
- Watch for regressions on auto-loss maps (galaxy, face, arena)

### Test 4: Sentinel combat effectiveness
```bash
cambc run buzzing starter face --watch
```
- Observe sentinel firing at approaching enemies
- Verify it doesn't fire at friendlies (no friendly fire for sentinel, unlike breach)

### Test 5: Edge cases
- Test on tight map (should skip sentinel entirely)
- Test on map where all perpendicular positions are walls (should gracefully fail)
- Test with <70 Ti at round 1000 (should defer until Ti sufficient)

---

## 11. Risks and Mitigations Summary

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Economy regression | Medium | High | Round 1000+ gate, Ti≥70, cap at 1 |
| Chain break during splice | Low | Medium | Destroy+build same turn (no cooldown) |
| No suitable conveyor nearby | Medium | Low | Gracefully skip if no chain tile found |
| Layout blocked by walls | Medium | Low | Try both perpendicular dirs, skip if both blocked |
| Scale impact too high | Low | Medium | +21% at round 1000 is marginal |
| Builder stuck walking to chain | Low | Low | Timeout after 20 rounds stuck, abandon |

---

## 12. Decision: Should We Do This?

### Arguments FOR:
- Proven pattern (splitter_test verified ammo delivery)
- Late-game defense currently absent (gunners rarely get ammo)
- Top teams use 20 sentinels — we use 0
- 36 Ti net cost at round 1000 is affordable

### Arguments AGAINST:
- +21% scale is permanent — every future build is more expensive
- We're at 1488 Elo — economy improvements may matter more than defense
- Gunners already provide some defense at lower cost
- Complexity risk: more code = more bugs

### Recommendation:
**Implement conservatively** — round 1000+, cap at 1 sentinel, skip on tight maps. This gives us a taste of armed defense without economy risk. If it works, we can add a second sentinel or lower the round gate in future versions.

The biggest risk is NOT the sentinel itself but rather the implementation introducing bugs in existing logic. Keep changes surgical: new method + small trigger block. Don't modify existing methods.
