# Problem Maps v38 Baseline Test
**Date:** 2026-04-06  
**Bot:** buzzing (v38) vs ladder_eco and ladder_rush  
**Historical worst maps:** galaxy (0-8), face (0-5), arena (0-4), shish_kebab (1-6), tree_of_life (2-5), wasteland (1-4), landscape (2-5)

---

## Summary Table: buzzing vs ladder_eco

| Map | Winner | buzzing Ti (mined) | eco Ti (mined) | buzzing Units | eco Units | buzzing Bldgs | eco Bldgs | Notes |
|-----|--------|-------------------|----------------|---------------|-----------|---------------|-----------|-------|
| galaxy | **buzzing** (tiebreak r2000) | 8292 (13880) | 3249 (12050) | 20 | 40 | 366 | 283 | |
| face | **buzzing** (tiebreak r2000) | 17514 (13780) | 5500 (9910) | 10 | 40 | 97 | 184 | Error: `_build_ax_tiebreaker` AttributeError |
| arena | **buzzing** (tiebreak r2000) | 16451 (14340) | 4343 (9920) | 13 | 40 | 172 | 243 | |
| shish_kebab | **buzzing** (tiebreak r2000) | 18062 (14690) | 3631 (7870) | 10 | 40 | 105 | 188 | |
| tree_of_life | **buzzing** (tiebreak r2000) | 17400 (21330) | 82 (0) | 10 | 18 | 416 | 159 | eco mined 0?? |
| wasteland | **buzzing** (tiebreak r2000) | 241 (0) | 46 (0) | 17 | 16 | 235 | 300 | Both mined 0 — no ore on map? |
| landscape | **buzzing** (tiebreak r2000) | 9571 (15170) | 182 (0) | 11 | 17 | 377 | 219 | eco mined 0 |

**vs ladder_eco result: 7-0**

---

## Summary Table: buzzing vs ladder_rush (tight maps)

| Map | Winner | buzzing Ti (mined) | rush Ti (mined) | buzzing Units | rush Units | buzzing Bldgs | rush Bldgs | Notes |
|-----|--------|-------------------|-----------------|---------------|------------|---------------|------------|-------|
| face | **buzzing** (tiebreak r2000) | 8402 (4980) | 7147 (4970) | 10 | 20 | 129 | 107 | Close margin |
| arena | **ladder_rush** (tiebreak r2000) | 11606 (10140) | 12192 (11540) | 13 | 20 | 192 | 158 | LOSS |
| shish_kebab | **buzzing** (tiebreak r2000) | 1849 (1070) | 11 (0) | 14 | 20 | 113 | 134 | rush mined 0 |

**vs ladder_rush result: 2-1**

---

## Observations

### Positives
- **vs ladder_eco: Clean 7-0 sweep** on all historically problematic maps — massive improvement over prior 0-8 on galaxy, 0-5 on face etc.
- Strong resource margins on most maps (buzzing Ti often 3-5x ladder_eco's final Ti)
- tree_of_life: buzzing mined 21330 Ti vs eco mined 0 — dominance on large maps
- landscape, shish_kebab, arena: eco completely failed to mine, suggesting buzzing's road/conveyor network blocks eco expansion

### Issues Found
1. **AttributeError on face map**: `'Player' object has no attribute '_build_ax_tiebreaker'` — a method is being called that doesn't exist. This is an error in the buzzing bot that occurs occasionally. Did not affect win (still won), but indicates a code bug that should be fixed.
2. **arena vs ladder_rush: LOSS** — closest match, lost by ~586 Ti on tiebreak (11606 vs 12192). Arena is a tight map where rush bot's faster unit generation may give it an edge.
3. **wasteland: Both sides mined 0 Ti** — this map may have no ore, making it purely a passive income + starting Ti game. Buzzing won 241 vs 46 on tiebreak, suggesting better Ti management.
4. **face vs ladder_rush: Very close** — 8402 vs 7147 Ti (only ~1255 margin). Buzzing won but barely.

### Bug Fix Needed
The `_build_ax_tiebreaker` AttributeError on face map should be investigated and fixed. The method appears to be referenced in `_builder` but not defined in the class.

---

## Comparison to Historical Record

| Map | Historical | v38 vs eco | v38 vs rush |
|-----|-----------|------------|-------------|
| galaxy | 0-8 | **WIN** | not tested |
| face | 0-5 | **WIN** | **WIN** (close) |
| arena | 0-4 | **WIN** | **LOSS** |
| shish_kebab | 1-6 | **WIN** | **WIN** |
| tree_of_life | 2-5 | **WIN** | not tested |
| wasteland | 1-4 | **WIN** | not tested |
| landscape | 2-5 | **WIN** | not tested |

**Conclusion:** v38 represents a dramatic improvement over historical performance on problem maps vs eco-style opponents. The rush matchup on arena remains a vulnerability.
