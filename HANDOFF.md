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
- Bot: v43, ~1360 lines, Version 45 on ladder
- Elo: volatile but climbing — V45 is 3W-0L (best streak)
- Local baseline: 50% (was 44% pre-session). Rusher 75% (was 25%), sentinel_spam 75% (was 20%)
- Beat The Defect 4-1 (nemesis, was 0-3 lifetime!)
- Sprint 4 deadline: April 11

## WHAT'S LIVE ON LADDER:
- v43 as Version 45: conservative caps + defense improvements + armed sentinel + attacker infra + bridge
- GitHub: github.com/rjav1/battlecode — fully pushed

## WHAT JUST HAPPENED (this session):
- v36: Fixed econ_cap ceiling (was max 10, now expand=20, balanced=15, tight=12)
  - Galaxy went from 10 → 20 units. Builder cap no longer bottlenecks.
- v36: Enabled gunners on tight maps (round 60) — was COMPLETELY BLOCKED before
  - Face/shish_kebab core destructions were caused by zero gunners on tight maps
- v36: Enabled mid-game barriers on tight maps
- Research completed: BFS strategies, ladder analysis, armed gunners plan, spend-down, Ax tiebreaker
- Key finding: spend-down is cap-driven not threshold-driven (econ_cap fix IS the spend-down fix)
- Key finding: we mine 0 Ax → any opponent with 1 refined Ax auto-wins TB#1

## AUTO-LOSS MAP STATUS (ALL ADDRESSED):
- face: 0-5 → FIXED (v32 early barriers, 1.8K→13.8K Ti)
- cold: 0-4 → FIXED (v33 exploration diversity, 9.7K→19.7K Ti)
- galaxy: 0-8 → IMPROVED (v31 earlier gunner, marginal gains)
- arena: 0-4 → FIXED (v34 builder cap 7→15, now 2/4 wins)

## KEY ARCHITECTURE:
- d.opposite() conveyors = ONLY working approach. Roads-first FAILED 3 TIMES. NEVER attempt again.
- Conveyors can only face cardinal directions (N/S/E/W). Diagonal movement creates gaps but fixing it is WORSE (speed loss > gap cost).
- Chain connectivity is NOT the primary bottleneck (proven by v32 investigation).

## KEY RESEARCH (April 6 session):
- research/bfs_strategies_apr6.md — 7 ranked strategies (Chain Census #1)
- research/ladder_analysis_apr6.md — full ladder intel + non-obvious mechanics
- research/armed_gunners_plan.md — complete splitter→sentinel integration plan
- research/spend_down_analysis.md — hoard is cap-driven, thresholds are fine
- research/gunner_timing_analysis.md — tight maps had ZERO gunners
- research/v36_econ_cap_test.md — unit cap fix verified (10→20 units)

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

## NEXT PRIORITIES (from data, April 6):
1. Monitor v36 ladder performance (econ_cap fix + tight gunners)
2. Armed gunners v37 (splitter ammo pattern — plan ready at research/armed_gunners_plan.md)
3. Ax tiebreaker — late-game foundry for TB#1 wins (research in progress)
4. Chain census via markers — detect/repair broken conveyor chains (highest BFS ceiling)
5. Attacker targets infrastructure not core (conveyors 20HP vs core 500HP)
6. Bridge-first expansion (Blue Dragon uses 33 bridges, we use 0-2)
7. Earlier gunner timing on balanced maps (120 vs 200)
8. Study actual ladder replays (need Chrome connected)

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
