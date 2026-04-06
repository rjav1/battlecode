# Match Analysis — April 6 PM Session

**Session record:** 7W-3L (70%) across 10 matches  
**Bot version used:** v40 (most matches), v38 (Ash Hit 14:47 loss)

---

## Summary Table

| Time  | Opponent        | Result | Score | Our Version |
|-------|----------------|--------|-------|-------------|
| 15:46 | Polska Gurom   | LOSS   | 2-3   | v40 |
| 15:35 | MergeConflict  | LOSS   | 1-4   | v40 |
| 15:26 | Warwick CodeSoc | WIN   | 3-2   | v40 |
| 15:16 | O_O            | WIN    | 5-0   | v40 |
| 15:06 | Chameleon      | WIN    | 3-2   | v40 |
| 14:55 | Some People    | WIN    | 3-2   | v40 |
| 14:47 | Ash Hit        | LOSS   | 2-3   | v38 |
| 14:36 | eidooheerfmaet | WIN    | 4-1   | v40 |
| 14:26 | Fake Analysis  | WIN    | 3-2   | v40 |
| 14:15 | EEZ            | WIN    | 4-1   | v40 |

---

## Loss Breakdown

### Loss 1: Polska Gurom — 2-3 (15:46, v40)
**Elo context:** Polska ~1490 (2641 matches played), Us ~1493 before match. Nearly equal Elo — this is a true nemesis.

| Game | Map              | Winner      | Win Condition | Turns |
|------|-----------------|-------------|---------------|-------|
| 1    | mandelbrot       | Polska Gurom | resources    | 2000  |
| 2    | binary_tree      | Polska Gurom | core_destroyed | 1300 |
| 3    | hooks            | buzzing bees | resources    | 2000  |
| 4    | default_medium1  | buzzing bees | resources    | 2000  |
| 5    | wasteland_oasis  | Polska Gurom | resources    | 2000  |

**Key finding:** Game 2 on `binary_tree` — Polska destroyed our core at round 1300. This is a rush or fast kill strategy. We've now lost to Polska 3-0 lifetime (all 3-2 scorelines) with core destroyed on binary_tree in two of the three encounters (see Polska history section below).

---

### Loss 2: MergeConflict — 1-4 (15:35, v40)
**Elo context:** MergeConflict ~1513 (1446 matches, novice bracket), Us ~1503 before match. They're rated higher despite being novice bracket.

| Game | Map              | Winner        | Win Condition | Turns |
|------|-----------------|---------------|---------------|-------|
| 1    | socket           | MergeConflict | resources    | 2000  |
| 2    | hooks            | MergeConflict | resources    | 2000  |
| 3    | wasteland_oasis  | MergeConflict | resources    | 2000  |
| 4    | face             | MergeConflict | resources    | 2000  |
| 5    | hourglass        | buzzing bees  | resources    | 2000  |

**Key finding:** No core destroys — pure economy loss on 4 of 5 maps. MergeConflict out-economied us consistently. The only map we won was `hourglass`. This suggests a systemic economy efficiency gap, not a map-specific issue. MergeConflict also beat Ash Hit 3-2 (note: Ash Hit beat us), suggesting they're legitimately strong.

---

### Loss 3: Ash Hit — 2-3 (14:47, v38)
**Note:** This was v38, not v40. v40 was deployed after this match.  
**Elo context:** Ash Hit ~1508, Us ~1479 before match (they were rated higher).

| Game | Map         | Winner      | Win Condition | Turns |
|------|------------|-------------|---------------|-------|
| 1    | corridors   | Ash Hit     | resources    | 2000  |
| 2    | butterfly   | Ash Hit     | resources    | 2000  |
| 3    | tree_of_life | buzzing bees | resources   | 2000  |
| 4    | landscape   | Ash Hit     | resources    | 2000  |
| 5    | bar_chart   | buzzing bees | resources   | 2000  |

**Key finding:** Economy losses on corridors, butterfly, landscape. We won tree_of_life and bar_chart. This loss was with v38 — v40 later beat O_O who had beaten us, so v40 is likely stronger. Worth noting we beat Ash Hit earlier in the day too (v38 era), so there's map-specific variance.

---

## Polska Gurom — Nemesis Analysis (0-3 lifetime)

All three matches ended 3-2. Polska has beaten us on every single encounter.

### Match 1 (04:14 AM, early bot)
| Game | Map              | Winner | Condition        | Turns |
|------|-----------------|--------|-----------------|-------|
| 1    | face             | Polska | core_destroyed  | 319   |
| 2    | hooks            | Us     | resources       | 2000  |
| 3    | binary_tree      | Us     | resources       | 2000  |
| 4    | landscape        | Polska | resources       | 2000  |
| 5    | wasteland        | Polska | resources       | 2000  |

### Match 2 (09:27 AM)
| Game | Map                  | Winner | Condition  | Turns |
|------|---------------------|--------|-----------|-------|
| 1    | cinnamon_roll        | Polska | resources | 2000  |
| 2    | pls_buy_cucats_merch | Polska | resources | 2000  |
| 3    | battlebot            | Us     | resources | 2000  |
| 4    | tree_of_life         | Polska | resources | 2000  |
| 5    | tiles                | Us     | resources | 2000  |

### Match 3 (15:46 PM, v40)
| Game | Map             | Winner | Condition        | Turns |
|------|----------------|--------|-----------------|-------|
| 1    | mandelbrot      | Polska | resources       | 2000  |
| 2    | binary_tree     | Polska | core_destroyed  | 1300  |
| 3    | hooks           | Us     | resources       | 2000  |
| 4    | default_medium1 | Us     | resources       | 2000  |
| 5    | wasteland_oasis | Polska | resources       | 2000  |

**Polska pattern across all 15 games:**
- Polska wins: face (rush, 319 turns), binary_tree (rush, 1300 turns), mandelbrot, landscape, wasteland/wasteland_oasis (x2), cinnamon_roll, pls_buy_cucats_merch, tree_of_life
- We win: hooks (x2), binary_tree (once, early bot), battlebot, tiles, default_medium1

**Critical insight:** Polska runs a fast rush on `face` and `binary_tree`. Their core kill on `face` was in 319 turns — an extreme early rush. On `binary_tree` they killed us at round 1300. These are maps with narrow corridors or constrained access paths that favor rush bots. We win consistently on `hooks` and `default_medium1` — likely open maps where economy scales better.

**Maps to watch out for vs Polska:**
- `face` — extreme rush risk (round 319 kill)
- `binary_tree` — rush kill at 1300 (happened twice in 3 matches)
- `wasteland`/`wasteland_oasis` — consistent economy loss
- `mandelbrot` — economy loss

---

## Cross-Match Patterns

### Maps we lost on (losses only):
| Map              | Times Lost | Opponent         | Loss Type      |
|-----------------|------------|-----------------|----------------|
| binary_tree      | 2          | Polska (x2)     | core_destroyed |
| wasteland/oasis  | 2          | Polska, MergeC  | resources      |
| mandelbrot       | 1          | Polska          | resources      |
| socket           | 1          | MergeConflict   | resources      |
| hooks            | 1          | MergeConflict   | resources      |
| face             | 1          | MergeConflict   | resources      |
| corridors        | 1          | Ash Hit         | resources      |
| butterfly        | 1          | Ash Hit         | resources      |
| landscape        | 2          | Polska, Ash Hit | resources      |
| cinnamon_roll    | 1          | Polska          | resources      |
| tree_of_life     | 1          | Polska          | resources      |
| pls_buy_cucats_merch | 1    | Polska          | resources      |
| tiles            | 1          | Polska          | resources      |

### Maps we won on (from loss matches only):
- hooks (x2), binary_tree (once), battlebot, tiles, default_medium1, tree_of_life, bar_chart, hourglass

### Win/loss by condition:
- **Core destroyed against us:** 2 games (both by Polska Gurom on binary_tree, face)
- **Economy losses:** All other losses — we are losing the resource race

---

## Root Cause Analysis

### 1. Economy efficiency gap (primary issue)
The vast majority of losses are resource tiebreakers at round 2000. MergeConflict beat us 4-1 on pure economy without a single core destroy. This means stronger teams are simply generating more resources per round than us, across diverse map types. This is a systemic bot efficiency problem.

### 2. Rush vulnerability on constrained maps (secondary issue)
Polska destroyed our core twice — round 319 on `face` and round 1300 on `binary_tree`. These are maps with narrow approaches to the core. We have no rush defense: no sentinels, no gunners covering choke points, no early turret placements. A fast-rushing opponent can walk to our core before we have defenses up.

### 3. Wasteland maps specifically weak
We've lost on wasteland/wasteland_oasis 3 times (all Polska or MergeConflict). This map type may have a layout that disadvantages our expansion logic — possibly sparse ore fields requiring longer conveyor chains or unusual symmetry.

### 4. The Ash Hit loss was v38 (partially resolved)
We beat O_O 5-0 at 15:16 after they beat us 4-1 earlier — strong evidence v40 is a significant improvement. The Ash Hit loss at 14:47 was v38 and may not be fully representative of current bot strength.

---

## Elo Context

| Team           | Elo   | Matches | Category |
|---------------|-------|---------|----------|
| MergeConflict  | ~1513 | 1446    | novice   |
| Ash Hit        | ~1508 | 2641    | main     |
| Polska Gurom   | ~1490 | 2641    | main     |
| buzzing bees   | ~1490 | 82      | main     |

We are closely matched in Elo against all three loss opponents. MergeConflict is slightly above us and is novice bracket — they are a legitimate threat in any bracket.

---

## Actionable Recommendations

### Priority 1 — Rush defense (affects Polska Gurom specifically)
- Build 1-2 gunners or sentinels near the core entrance early on constrained maps (`face`, `binary_tree`)
- Detect when an enemy builder is close to our core and trigger defensive build
- A sentinel placed at the core perimeter in rounds 50-100 would have stopped the round 319 core kill
- Maps to test this on: `face`, `binary_tree`, `corridors` (Ash Hit also won on corridors)

### Priority 2 — Economy throughput audit
- MergeConflict beat us purely on resources 4/5 games. Something fundamental is slower: fewer harvesters? slower conveyor chains? more wasted Ti?
- Run local benchmark: our bot vs itself, measure resources delivered at rounds 500/1000/1500/2000
- Check whether we're hitting the 50 unit cap and stalling expansion
- Check foundry utilization — are we refining axionite efficiently?

### Priority 3 — Wasteland/Wasteland_oasis specific fix
- 3 losses on this map variant. Download and analyze the map layout
- Run `cambc run <bot> <bot> wasteland_oasis` to see our bot behavior on this specific map

### Priority 4 — Prepare for Polska rematch
- Polska is our only team to beat us 3 consecutive times
- Their pattern: rush early on face/binary_tree, outperform on wasteland, landscape
- We beat them consistently on hooks, default_medium1 — these are our "home" maps
- Strategy: survive the early rush (defensive sentinel), then win the economy on open maps
- Consider: can we match-queue dodge? No — ladder is automatic. Need to improve the bot.

### Priority 5 — Study MergeConflict
- They're novice bracket, 1513 Elo, and dominated us 4-1 on pure economy
- Download one of their replays to see what they're doing differently
- Command: `./cambc.bat match replay 4017ade0-25f1-435f-98a0-bc172ff5062b --game 1`
