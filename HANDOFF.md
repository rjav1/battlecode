# PLANNER HANDOFF — Read This to Resume Operations

## YOU ARE the planner/manager for Cambridge Battlecode 2026 bot development.
## Team: buzzing bees | Elo: ~1488 | Rank: #134/573 | Qualifier: April 20

## CRITICAL RULES (from user):
- NEVER do work yourself. ALWAYS delegate to agents.
- Use Opus for creative/complex tasks, Sonnet for execution, Haiku for simple ops.
- ONE small change per agent. Test. Regress. Deploy. Next.
- Fresh agents > context-rotted ones. Kill agents after their task.
- BFS strategies — explore multiple approaches, let data decide.
- Never wait for user input. Always have wheels turning.
- PhD/quant rigor. Measure everything. No assumptions.

## CURRENT STATE:
- Bot: v33, 832 lines, Version 35 on ladder
- Elo: ~1488, flat at this level despite 22 deployed versions
- Ladder record: 24W-30L across 54 matches (44% match win rate)
- Local win rate vs realistic opponents: was 33%, v32-v33 fixes should improve

## WHAT'S LIVE ON LADDER:
- v33: sector exploration diversity + early barriers on tight maps
- GitHub: github.com/rjav1/battlecode — all pushed

## WHAT JUST HAPPENED:
- v32: Fixed face auto-loss (0-5 → WIN via early barriers against rush)
- v33: Fixed cold auto-loss (9.7K → 19.7K Ti via prime-multiplier exploration diversity)
- A final-benchmark agent is currently running v33 vs ladder_eco + ladder_rush on 10 maps

## AUTO-LOSS MAP STATUS:
- face: 0-5 → FIXED (v32 early barriers)
- cold: 0-4 → FIXED (v33 exploration diversity, 2x improvement)
- galaxy: 0-8 → minor improvement (earlier gunner), still problematic
- arena: 0-4 → improved but still losing on tiebreaks

## KEY ARCHITECTURE:
- d.opposite() conveyors = ONLY working approach. Roads-first FAILED 3 TIMES. NEVER attempt again.
- Conveyors can only face cardinal directions (N/S/E/W). Diagonal movement creates gaps but fixing it is WORSE (speed loss > gap cost).
- Chain connectivity is NOT the primary bottleneck (proven by v32 investigation).

## DEAD ENDS (proven, never retry):
- Roads-first navigation (3 failures)
- 40+ builder scaling (v4 0-5 disaster, scale cost kills economy)
- More builders without better exploration (they cluster on same ore)
- Axionite economy, launcher drops, attacker removal
- Diagonal gap fix (speed loss outweighs gap cost)
- Spending hypothesis (bank balance IS part of Ti collected)

## WHAT WORKS:
- d.opposite() conveyor economy
- Sector-based exploration with prime multiplier (v23+v33 breakthrough)
- Wall-density + ore-density adaptive scoring
- Map-size adaptation (tight/balanced/expand)
- Early barriers on tight maps (v32 anti-rush)
- Marker-based ore claiming
- Gunner defense (simplified, no chain destruction)
- Bridge fallback
- Distance-based explore reserve
- econ_cap ramping

## KEY FILES:
- bots/buzzing/main.py — THE bot (832 lines)
- bots/buzzing_prev/main.py — previous version for regression testing
- CLAUDE.md — full game rules + API reference
- DEPLOY_CHECKLIST.md — mandatory before every submission
- SESSION_LOG.md — comprehensive session log
- research/ladder_deep_review.md — 54-match ladder analysis (CRITICAL)
- research/nemesis_analysis.md — 4 teams we never beat
- research/realistic_opponents.md — ladder_eco + ladder_rush test bots
- research/chain_connectivity_truth.md — diagonal gap investigation
- memory/battlecode_learnings.md — all empirical learnings

## TEST OPPONENTS (in bots/ directory):
- ladder_eco — 40-bot pure economy (models real 1500 Elo opponents) 
- ladder_rush — rush+eco hybrid (models core-destroyed scenarios)
- smart_eco, smart_defense, smart_hybrid — intermediate opponents
- sentinel_spam, balanced, barrier_wall, fast_expand, rusher, turtle, etc.

## NEXT PRIORITIES (from data):
1. Check final-benchmark results (agent running now)
2. Galaxy (0-8) still unsolved — needs investigation  
3. Arena (0-4) close losses — needs tiebreaker edge
4. Study actual ladder replays (need Chrome connected)
5. Armed gunners (splitter ammo pattern proven but never properly integrated)
6. Consider completely different architecture if current one hits ceiling

## LADDER NEMESES (0-14 combined):
- The Defect (1521 Elo): broadly superior on all maps
- One More Time (1523 Elo): pure economy, 40+ bots
- KCPC-B (1472 Elo): lower rated but beats us 100%
- Polska Gurom (1476 Elo): rush + economy dual competency

## MANAGEMENT INFRASTRUCTURE:
- TeamCreate "battlecode-dev" team exists
- Agents spawn with team_name="battlecode-dev"
- Use SendMessage for agent comms (but subagents can't reply)
- DEPLOY_CHECKLIST.md: save prev, test 5 maps both positions, self-play, then submit
- test_suite.py exists but may need fixes
- Statistical guide: need 12+ matches for 20pp detection, never revert after 1 match
