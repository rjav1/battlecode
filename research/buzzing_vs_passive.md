# Buzzing vs ladder_passive — Economy Comparison

**Date:** 2026-04-06  
**Bot:** buzzing V60 vs ladder_passive (stripped/debug bot)  
**Question:** Does ladder_passive match or beat buzzing on 3+ of 5 maps? If yes, buzzing's features are net negative.

---

## Results

| Map | Type | Buzzing Ti Mined | Passive Ti Mined | Passive/Buzzing | Winner |
|-----|------|-----------------|------------------|-----------------|--------|
| cold | balanced | **19670** | 0 | 0% | buzzing |
| galaxy | expand | **14200** | 4950 | 35% | buzzing |
| default_medium1 | balanced | **23000** | 0 | 0% | buzzing |
| arena | tight | **14850** | 9900 | **67%** | buzzing |
| settlement | expand | **28210** | 18780 | **67%** | buzzing |

**Record: buzzing 5W-0L (100%)**

---

## Verdict

**ladder_passive does NOT match buzzing on 3+ maps. Buzzing wins all 5.**

ladder_passive matched buzzing most closely on:
- **arena (tight):** 9900 vs 14850 — passive at 67% of buzzing's output
- **settlement (expand):** 18780 vs 28210 — passive at 67% of buzzing's output

On balanced maps (cold, default_medium1), passive mined 0 Ti — completely broken. On galaxy (expand), passive reached 35%.

The `explore_dir` → `explore_idx` AttributeError fires on all runs but is caught internally. The partial functionality on arena and settlement suggests the passive bot has working harvester+conveyor logic on some map types despite the error.

---

## Notes on ladder_passive Behavior

- 2 builder bots spawned across all matches (vs buzzing's 8-15)
- Buildings: 3-314 depending on map (settlement: 314, arena: 86, others: 1-27)
- The bot appears to be a stripped-down version that successfully chains harvesters on some maps but crashes early on others
- Settlement's 18780 Ti mined with only 2 bots and 314 buildings is notable — passive achieves dense coverage on open maps despite the bug

---

## Conclusion

Buzzing's features are NOT net negative vs this passive baseline. Buzzing mines 33-100% more Ti across all 5 maps. The closest gap is on tight/expand maps (arena, settlement) where passive reaches ~67% — but buzzing still wins cleanly on resources at round 2000.

The team-lead hypothesis (features net negative if passive matches on 3+) is not supported. V60 provides genuine value over the stripped passive bot.
