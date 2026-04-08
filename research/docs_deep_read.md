# Deep Read: Competition Docs vs CLAUDE.md vs Engine

## Date: 2026-04-08
## Method: Fetched all spec pages from docs.battlecode.cam, cross-referenced against CLAUDE.md and cambc/_types.py (engine constants), ran empirical tests.

---

## DISCREPANCY 1: Foundry Scale — Docs Say +50%, Engine Says +100%

**docs.battlecode.cam/spec/harvester-and-foundry:** "Scaling: +50%"
**docs.battlecode.cam/spec/resources (reference table):** "+50%"
**CLAUDE.md:** "+100%"
**Empirical test (scale_test bot):** FOUNDRY delta = **100.00%** (141% -> 241%)

**VERDICT: CLAUDE.md is CORRECT. Docs are WRONG.** Foundry adds +100% to scale, not +50%. This is important — it means foundries are even more expensive than the docs suggest. Our decision to avoid foundries is correct.

However, this also means opponents reading the docs might think foundries are cheaper than they are and build them more freely, which would inflate THEIR costs.

## DISCREPANCY 2: Builder Bot HP — Docs Say 40, Engine Says 30

**docs.battlecode.cam/spec/reference:** "Builder bot: 40 HP"
**docs.battlecode.cam/spec/builder-bot:** "HP: 40"
**CLAUDE.md:** "HP: 30"
**cambc/_types.py line 101:** `BUILDER_BOT_MAX_HP = 30`

**VERDICT: CLAUDE.md is CORRECT. Docs are WRONG** (or WebFetch misread). Builder bots have 30 HP. This means they're squishier than the docs claim — enemy turrets kill them faster.

## DISCREPANCY 3: Gunner Ax Damage — Docs Say 40, Engine Says 30

**docs.battlecode.cam/spec/reference:** "10 (40 with Ax)"
**docs.battlecode.cam/spec/turrets:** "10 standard; 40 with refined axionite"
**CLAUDE.md:** "10 (30 w/ Ax)"
**cambc/_types.py line 115:** `GUNNER_AXIONITE_DAMAGE = 30`
**Changelog (March 30):** "Gunners: axionite ammo now deals 30 damage (was 20)"

**VERDICT: CLAUDE.md is CORRECT. Docs are WRONG.** Gunners deal 30 with Ax, not 40. The docs may not have been updated after the March 30 balance patch.

## DISCREPANCY 4: Breach Vision/Attack r^2 — Docs Confused

**docs.battlecode.cam/spec/turrets (WebFetch):** "√2 vision range; √13 attack range"
**CLAUDE.md:** "13 (atk r^2=5)"
**cambc/_types.py line 72:** `BREACH_VISION_RADIUS_SQ = 13`
**cambc/_types.py line 128:** `BREACH_ATTACK_RADIUS_SQ = 5`

**VERDICT: CLAUDE.md is CORRECT.** Breach has vision r^2=13, attack r^2=5. The WebFetch summary may have swapped values.

---

## VERIFIED CORRECT IN CLAUDE.md

| Stat | CLAUDE.md | Engine | Status |
|------|-----------|--------|--------|
| Builder HP | 30 | 30 | CORRECT |
| Builder cost | 30 Ti | 30 Ti | CORRECT |
| Gunner Ax damage | 30 | 30 | CORRECT |
| Gunner base damage | 10 | 10 | CORRECT |
| Sentinel damage | 18 | 18 | CORRECT |
| Sentinel reload | 3 rounds | 3 | CORRECT |
| Sentinel stun | +5 cooldown | +5 | CORRECT |
| Breach damage | 40 + 20 splash | 40 + 20 | CORRECT |
| Breach attack r^2 | 5 | 5 | CORRECT |
| Foundry scale | +100% | +100% | CORRECT |
| Foundry cost | 40 Ti | 40 Ti | CORRECT |
| Harvester cost | 20 Ti | 20 Ti | CORRECT |
| Harvester scale | +5% | +5% | CORRECT |
| Bridge scale | +10% | +10% | CORRECT |
| Road HP | 5 | 5 | CORRECT |
| Starting Ti | 500 | 500 | CORRECT |
| Passive Ti | 10 every 4 rounds | 10/4 | CORRECT |
| Core HP | 500 | 500 | CORRECT |
| Max units | 50 | 50 | CORRECT |

---

## CHANGELOG: KEY BALANCE CHANGES (chronological)

### 2026-03-23: First Balance Patch
- Builder cost: 10 -> 50 Ti (massive increase)
- Builder/sentinel scale: +10% -> +20%
- Bridge: +1% -> +5% scale, 10 -> 20 Ti cost
- Builder self-destruct: damage removed (was dealing damage)
- Builder attack: 2 Ti for 2 damage on standing tile
- Builder heal: 1 Ti for 4 HP (was free 10 HP)
- Unit cap: 50 per team
- Raw Ax destroyed at core/turrets
- Sentinel: reload 2 rounds, 10 damage, 5 ammo

### 2026-03-30: Major Balance Patch
- Builder cost: 50 -> 30 Ti
- Harvester cost: 80 -> 20 Ti, scale +10% -> +5%
- Foundry cost: 120 -> 40 Ti
- Breach cost: 30 -> 15 Ti
- Armoured conveyor cost: 10 -> 5 Ti
- Starting Ti: 1000 -> 500
- Passive Ti: 10 every 4 rounds (unchanged?)
- Sentinel: reload 2 -> 3 rounds
- Gunner Ax damage: 20 -> 30
- Core convert added: 1 refined Ax = 4 Ti
- Bridge scale: +5% -> +10%

### 2026-03-31: Gunner Rotation Fix
- Gunners can now rotate to ANY direction in one action (was adjacent only)

**No balance changes after March 31.** The game has been stable for 8 days.

---

## MECHANICS WE MIGHT HAVE WRONG

### 1. Harvester Output Priority — CONFIRMED
"Prioritises outputting in directions used least recently." This means if a harvester has 2 adjacent conveyors, it alternates between them ~50/50 over time. We tested this in the sentinel auto-split prototype and it works as documented.

### 2. Foundry Accepts/Outputs ANY Side — CONFIRMED
"Accepts input and produces output from any side." This means you can feed Ti from one side and raw Ax from another. Output goes to any adjacent building. No directional preference.

### 3. Splitter Accepts ONLY From Behind — CONFIRMED
"Only accepts input from the back." Splitter has 1 input direction (opposite of facing), 3 output directions (facing + both perpendicular). Alternates between outputs, "prioritises directions used least recently."

### 4. Bridge Bypasses Direction Restrictions — CONFIRMED
"Bridges bypass directional restrictions — they can feed any building that accepts resources." This means a bridge can feed INTO a conveyor from the output side, or feed a turret from any direction. Powerful for connecting chains that don't align directionally.

### 5. Builder Can Walk on Enemy Conveyors/Roads — CONFIRMED
"Conveyors, splitters, armoured conveyors, and bridges (any direction, either team); Roads (either team)." This enables offensive builder rushes on enemy infrastructure.

### 6. Armoured Conveyors IMMUNE to Builder Attack — CONFIRMED
"Armoured conveyors are immune." Builder `fire()` on own tile does 0 damage to armoured conveyors. This makes them useful for defensive chains near enemy bases.

### 7. Turret Ammo: Only Accept When Empty — CONFIRMED
"Turrets only accept resources when completely empty." This means a turret with 1 remaining ammo won't accept new ammo until it fires. This creates throughput bottlenecks -- you can't pre-load turrets.

---

## STRATEGIC IMPLICATIONS

### 1. Docs Errors Help Us
Teams reading the docs might think:
- Builder bots have 40 HP (actual: 30) — they'll underestimate how quickly turrets kill builders
- Gunners do 40 Ax damage (actual: 30) — they'll overvalue gunners vs sentinels
- Foundries cost +50% scale (actual: +100%) — they'll build foundries more aggressively and get punished by scale inflation

### 2. No Recent Balance Changes
Game has been stable since March 31. No surprises. Our CLAUDE.md is accurate for the current meta.

### 3. Core Convert is Underexplored
Added March 30. Core can convert refined Ax to Ti at 1:4. If we ever build a foundry (late game), converting refined Ax immediately gives 40 Ti per stack (10 Ax * 4). This could fund sentinel placement.

### 4. Gunner Rotation Now Allows Any Direction
Since March 31, gunners can rotate to ANY direction in one action (10 Ti, 1 cooldown). Previously limited to adjacent 45-degree turns. This makes gunners more flexible but still expensive to rotate.

---

## CONCLUSION

CLAUDE.md is accurate on all key mechanics. The online docs have at least 3 factual errors (builder HP, gunner Ax damage, foundry scale). No balance changes since March 31. No new mechanics to exploit beyond what we've already analyzed.
