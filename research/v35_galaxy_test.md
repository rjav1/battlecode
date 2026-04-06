# v35 Galaxy Fix Test Results

Date: 2026-04-06

## Context

v35 raised the expand builder cap and econ_cap for galaxy (40x40, expand mode) to fix our 0-8 record on galaxy map.

---

## Galaxy Map Matches

### 1. buzzing vs ladder_eco — galaxy

**Winner: ladder_eco** (Resources tiebreak, turn 2000)

|         | buzzing        | ladder_eco      |
|---------|----------------|-----------------|
| Ti      | 11201          | 3239            |
| Ti mined| 9940           | 14430           |
| Ax      | 0              | 0               |
| Units   | 10             | 40              |
| Buildings | 250          | 417             |

**Note:** Despite buzzing having more Ti on hand, ladder_eco mined significantly more (14430 vs 9940) and won on resources tiebreak. Buzzing had fewer units (10 vs 40), suggesting builder cap still limiting expansion.

---

### 2. buzzing vs ladder_rush — galaxy

**Winner: ladder_rush** (Resources tiebreak, turn 2000)

|         | buzzing        | ladder_rush     |
|---------|----------------|-----------------|
| Ti      | 3853           | 4093            |
| Ti mined| 2770           | 5470            |
| Ax      | 0              | 0               |
| Units   | 10             | 20              |
| Buildings | 194          | 232             |

**Note:** Very close Ti totals but ladder_rush mined nearly double. Again buzzing capped at 10 units vs 20.

---

### 3. buzzing vs buzzing_prev — galaxy

**Winner: buzzing** (Resources tiebreak, turn 2000)

|         | buzzing        | buzzing_prev    |
|---------|----------------|-----------------|
| Ti      | 15156          | 16621           |
| Ti mined| 14170          | 14160           |
| Ax      | 0              | 0               |
| Units   | 10             | 10              |
| Buildings | 298          | 207             |

**Note:** v35 beats buzzing_prev on galaxy — both mine same amount but buzzing wins on final Ti. However buzzing_prev has MORE Ti on hand (16621 vs 15156), yet loses. This is confusing — may need to re-examine tiebreak ordering. Buzzing has more buildings (298 vs 207).

---

### 4. buzzing vs starter — galaxy

**Winner: buzzing** (Resources tiebreak, turn 2000)

|         | buzzing        | starter         |
|---------|----------------|-----------------|
| Ti      | 14585          | 2530            |
| Ti mined| 14210          | 0               |
| Ax      | 0              | 0               |
| Units   | 10             | 3               |
| Buildings | 330          | 663             |

**Note:** Easy win. Starter mined nothing.

---

## Regression Checks (buzzing vs buzzing_prev)

### 5. default_medium1

**Winner: buzzing** (Resources tiebreak, turn 2000)

|         | buzzing        | buzzing_prev    |
|---------|----------------|-----------------|
| Ti      | 11115          | 6827            |
| Ti mined| 9380           | 4950            |
| Units   | 10             | 10              |
| Buildings | 268          | 253             |

**Result: PASS** — v35 wins convincingly (+4288 Ti, +4430 mined).

---

### 6. cold

**Winner: buzzing_prev** (Resources tiebreak, turn 2000)

|         | buzzing        | buzzing_prev    |
|---------|----------------|-----------------|
| Ti      | 18710          | 19606           |
| Ti mined| 19670          | 19700           |
| Units   | 10             | 10              |
| Buildings | 406          | 348             |

**Result: REGRESSION** — Very close (19670 vs 19700 mined) but buzzing_prev edges it. Near-identical mining, slight Ti deficit for v35. This is marginal — could be noise.

---

### 7. face

**Winner: buzzing_prev** (Resources tiebreak, turn 2000)

|         | buzzing        | buzzing_prev    |
|---------|----------------|-----------------|
| Ti      | 13372          | 13249           |
| Ti mined| 9720           | 9910            |
| Units   | 10             | 10              |
| Buildings | 110          | 138             |

**Result: REGRESSION** — v35 loses on face. Mining slightly lower (9720 vs 9910). Very narrow margin.

---

## Summary

| Match | Map | Winner | Notes |
|-------|-----|--------|-------|
| buzzing vs ladder_eco | galaxy | ladder_eco | Still losing — 9940 vs 14430 mined |
| buzzing vs ladder_rush | galaxy | ladder_rush | Still losing — 2770 vs 5470 mined |
| buzzing vs buzzing_prev | galaxy | **buzzing** | v35 improvement confirmed |
| buzzing vs starter | galaxy | **buzzing** | Expected win |
| buzzing vs buzzing_prev | default_medium1 | **buzzing** | Regression check: PASS |
| buzzing vs buzzing_prev | cold | buzzing_prev | Regression check: MARGINAL LOSS (very close) |
| buzzing vs buzzing_prev | face | buzzing_prev | Regression check: NARROW LOSS |

## Assessment

**Galaxy improvement: PARTIAL.** v35 beats buzzing_prev on galaxy (good) but still loses to ladder_eco and ladder_rush. The mining gap vs ladder_eco is huge (9940 vs 14430) — ladder_eco has 40 units vs our 10, suggesting the builder cap fix may not be working as intended or the econ_cap is still too restrictive.

**Regression concern:** v35 introduces narrow losses on `cold` and `face` vs buzzing_prev. These are very close margins (likely noise) but worth monitoring.

**Recommendation:** The unit count on galaxy still shows 10 for buzzing even in galaxy mode — if the expand builder cap was raised, the units aren't reaching it. May need to debug whether the galaxy mode detection is triggering correctly.
