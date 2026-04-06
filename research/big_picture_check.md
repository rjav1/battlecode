# Big Picture Check: Brutally Honest Strategic Review
## Date: April 4, 2026 | Big Picture Advisor | buzzing bees

---

## 1. What's the Single Biggest Risk We're NOT Addressing?

**We are drowning in analysis paralysis and research documents while our Elo is in freefall.**

The hard numbers: We have produced 10+ research documents totaling thousands of lines. Our bot is ~590 lines. Our Elo trajectory is: 1500 -> 1490 -> 1487 -> 1490 -> 1474 -> 1464. That is a DOWNWARD slope. We are now 36 Elo below where we started.

But the biggest unaddressed risk is not research volume -- it is **regression management**. v4 was a catastrophic regression from v2 (game win rate dropped from 50% to 10%). We deployed it, lost two matches, shed 26 Elo, and the damage is done. The strategic assessment from April 4 literally says "STOP PLANNING. START BUILDING. SHIP DAILY." And then we... produced more research documents.

The risk nobody is talking about: **every submission that regresses costs us double** -- we lose Elo AND waste matchmaking rounds that could have been climbing. With only ~14 days left, every match at 1464 is a match not played at 1700. The ladder runs matches every 10 minutes. At 144 matches per day, a bad submission active for even 6 hours means 36 lost matches. That is 36 chances to climb, wasted.

The real biggest risk: **we ship a broken v-next, it plays 20 matches before we notice, and we drop to 1400.** There is no mention anywhere of a pre-submission testing protocol that prevents regressions.

---

## 2. Are We Building the Right Features in the Right Order?

**The roadmap order (economy -> barriers -> bridges -> offense -> adaptation) is approximately correct but irrelevant if we keep regressing.**

The roadmap says Phase 8 (economy) should take Days 1-2. It is now functionally Day 0 still -- v4 regressed, v5 may or may not have been deployed, and our best performing version (v2, 50% win rate) had a fundamentally broken economy (conveyors in wrong directions, exploration waste). We are re-doing Phase 8 work that should have been done on April 5-6.

The order itself is defensible. The diamond tier analysis proves it: bots at 1899 Elo (dzwiek) have 0 Ti collected. Having ANY working economy beats them. Economy is the right first priority.

**But here is what is wrong with the roadmap:** it treats each phase as a sequential waterfall with gate criteria. The real world does not work that way. The v4 regression proves it -- we "completed" Phase 6 tasks (splitter sentinels, barriers, etc.) but the resulting bot was WORSE than the simpler v2. Adding features on top of a broken foundation just creates a more complex broken bot.

**What should change:** Before ANY new feature, the bot must pass a regression test: beat v2 (our best performing version) at least 3-2 in local testing on 5+ maps. If it cannot beat v2, the new feature is not an improvement regardless of how correct the code looks.

---

## 3. What Would a COMPLETELY DIFFERENT Approach Look Like?

Three alternative philosophies:

### Alternative A: The "Starter Bot Plus" Strategy
Instead of a 590-line bot with 8 features half-working, write a 150-line bot that does exactly ONE thing well: build harvesters and connect them to core with directed conveyors. No sentinels, no barriers, no attackers, no bridges, no splitters. Just economy.

**Why it might work:** The diamond tier analysis shows dzwiek at 1899 Elo with 0 Ti collected. A bot that reliably collects even 5000 Ti would beat every bot below 1800 that has a broken or nonexistent economy. Simplicity means fewer bugs, no regressions, no CPU timeouts.

**Why it might not:** It caps at ~1800. No defense means any bot with basic sentinels can eventually destroy us on narrow maps.

**Verdict: This is probably what we should have done on Day 1.** It is not too late. Strip the bot down to economy-only, get to 1700, THEN layer features.

### Alternative B: The "Rush" Strategy  
Forget economy entirely. Spawn builders, build roads toward enemy core, attack it. Win by Core Destroyed before round 500. Ignore Resource Victory.

**Why it might work:** Core Destroyed wins happen as early as turn 66 (face map) at diamond tier. If we can reliably rush on small/narrow maps, we win 2-3 games per match on favorable maps.

**Why it might not:** On large maps (which are ~50% of the map pool), a rush bot has zero chance of reaching the enemy core before round 2000. We would go 2-3 or 1-4 in every match depending on map draws. Elo would stagnate around 1500.

**Verdict: Not viable as a primary strategy.** But rushing on detected-small-maps is worth ~200 Elo as an addition to a working economy bot.

### Alternative C: The "Copy Blue Dragon" Strategy
Literally reverse-engineer what Blue Dragon does from replays and try to implement the same approach: massive conveyor networks, roads for mobility, bridges for terrain crossing, sentinels for defense.

**Why it might work:** We know exactly what they do. The replay data is comprehensive. If we execute even 30% of their strategy correctly, we beat everything below 2000.

**Why it might not:** We do not know HOW they do it. We know they build 308 conveyors, but we do not know the algorithm that decides where each one goes. Their coordination logic is invisible in replays. Copying outputs without understanding the process produces a cargo-cult bot.

**Verdict: Aspire to their strategy but implement it incrementally.** Economy first (their foundation), then bridges (their expansion), then sentinels (their defense). Do NOT try to replicate their 308-conveyor network directly.

---

## 4. What Are We Over-Investing in vs Under-Investing In?

### OVER-INVESTING:

**Research and analysis.** We have strategic_assessment.md, top3_scouting.md, diamond_tier_analysis.md, economy_debug.md, splitter_integration_analysis.md, barrier_strategy.md, ladder_status_v3.md, roadmap_to_2000.md, and now this document. That is 9 research documents. Our actual bot is 1 file. The research-to-code ratio is absurd.

**Sentinel infrastructure.** The splitter-sentinel integration analysis is 540 lines of careful engineering for a feature that (a) only activates after round 200, (b) requires a working economy to function, and (c) we do not have a working economy. The sentinel builder state machine is the most complex subsystem in our bot and it has never successfully armed a sentinel in a real match. We are optimizing a feature that cannot fire.

**Barriers.** The barrier strategy document is 400 lines. Barriers are 3 Ti each. The correct barrier strategy at 1464 Elo is: "build some barriers near core after harvesters work." That is one sentence, not 400 lines.

### UNDER-INVESTING:

**Testing and regression prevention.** There is NO systematic testing protocol. v4 shipped with a regression that dropped us 26 Elo. There is no before/after comparison, no win-rate threshold for deployment, no automated test suite.

**Core economy logic.** The SINGLE most important function in our bot -- the logic that builds a conveyor chain from harvester to core -- is tangled into `_nav()`, a general navigation function. There is no dedicated "build_chain(harvester_pos, core_pos)" function. The economy is an accidental byproduct of navigation, not a deliberate system.

**Submission frequency.** The roadmap says "NEVER go more than 24 hours without submitting." But the submission cadence suggests long gaps between versions. We should be submitting every 2-3 hours during active development.

**Bridge building.** The roadmap defers bridges to Phase 10 (Days 5-7). But the strategic assessment identifies bridges as "the single most underinvested capability." Blue Dragon builds 33. We build 0-2. Bridges should be Phase 8.5, not Phase 10. On maps with walls between ore and core, no bridges = no economy = guaranteed loss.

---

## 5. Time Check: Will We Make It?

**Today is April 4. International qualifier is April 20. That is 16 days. We are at 1464 Elo. We need ~2000+.**

### Required climb: 536 Elo in 16 days = 33.5 Elo per day.

### Historical climb rates at this level:
- v2 (our best): +3.6 Elo per match win (vs 1495 opponent). To gain 33.5 Elo/day, we need ~9 net match wins per day.
- At 6 matches per hour (every 10 minutes), that is 144 matches/day.
- A 55% match win rate yields ~14 net wins per day --> ~50 Elo/day. This would reach 2000 in ~11 days.
- A 50% match win rate yields ~0 Elo/day. We stay at 1464 forever.
- A 45% match win rate yields ~-14 net wins/day --> lose ~50 Elo/day.

### The cold math:
To reach 2000 from 1464, we need a SUSTAINED 55%+ match win rate. But that win rate has to be against progressively stronger opponents as our Elo rises. At 1464, a 55% win rate climbs us. At 1800, we need to beat 1800-level bots 55% of the time. At 1900, we need to beat 1900-level bots. The climb gets harder as we go up.

### Realistic projection:

| Phase | Days | Starting Elo | Ending Elo | Requires |
|-------|------|-------------|------------|----------|
| Fix regression, deploy working economy | 1-2 | 1464 | 1550 | Working conveyor chains |
| Scale economy, add bridges | 3-5 | 1550 | 1700 | 4+ harvesters, bridges for walls |
| Armed sentinels, barriers | 6-8 | 1700 | 1850 | Splitter ammo, barrier ring |
| Bridge expansion, more harvesters | 9-11 | 1850 | 1950 | 8+ harvesters, 5+ bridges |
| Map adaptation, offense | 12-14 | 1950 | 2050 | Narrow-map rush, launcher |
| Polish | 15-16 | 2050 | 2100? | Bug fixes, tuning |

**Probability of reaching 2000 by April 20: 15-25%.** This is LOWER than the strategic assessment's estimate of 20-30% because:
1. We have lost 2 days to regression and research instead of building
2. v4 regression shows we can easily ship bad code
3. We have not yet demonstrated we can build a working economy

**Probability of reaching 1800 by April 20: 45-55%.** Achievable if we fix economy in the next 2 days and stop regressing.

**What would need to change to hit 2000:**
1. Ship a working economy bot TODAY (not tomorrow, TODAY)
2. Zero regressions from this point forward
3. Add exactly one major feature every 2 days (bridges, sentinels, barriers, offense)
4. Test locally against previous version before every submission
5. Analyze losses from ladder matches and fix the #1 failure mode each day

---

## 6. What Would I Do in the Next 24 Hours If I Were in Charge?

**Hour 0-2: Strip the bot down to economy-only.**

Delete the sentinel builder, delete the attacker, delete the barrier builder. Keep: core spawning, builder navigation, harvester building, conveyor chain building. Make the conveyor chain logic correct: after building a harvester, walk toward core, build conveyors facing `pos.direction_to(core_pos)` at each step.

Test this stripped-down bot against v2 on 5 maps. It MUST win 3-2 or better. If it does not, the economy logic is still broken and nothing else matters.

**Hour 2-4: Add bridges.**

When a builder is walking toward core to build a conveyor chain and hits a wall, build a bridge. This is 20 lines of code. Test on pls_buy_cucats_merch, wasteland, butterfly -- maps where walls block ore access. The bot should collect >0 Ti on every map.

**Hour 4-5: Submit to ladder.**

Submit the stripped-down economy + bridges bot. Monitor first 5 matches. It should win at least 2 out of 5. If it does not, there is a fundamental bug. If it does, let it run overnight.

**Hour 5-8: While matches run, add barriers and sentinel ammo.**

Layer back barriers (simplified: build 6 barriers near core after round 120 and 2+ harvesters). Layer back sentinel ammo (simplified: find a conveyor in an active chain, splice in a splitter, build one sentinel). Test against the stripped-down version -- must not regress.

**Hour 8-10: Submit v2 of the day.**

Second submission with barriers + sentinels added on top of working economy. Monitor matches.

**24-hour target: 1500-1550 Elo with a bot that has working economy + bridges + basic defense.**

---

## 7. What's the ONE Thing That Would Double Our Elo Gain Rate?

**A 5-minute regression test run before every submission.**

Right now, the biggest Elo destroyer is shipping regressions. v4 cost us 26 Elo and probably 4+ hours of ladder time. A simple test:

```bash
cambc run buzzing buzzing_prev default_medium1
cambc run buzzing buzzing_prev hourglass
cambc run buzzing buzzing_prev landscape
cambc run buzzing buzzing_prev corridors  
cambc run buzzing buzzing_prev pls_buy_cucats_merch
```

If the new version loses 3+ games, DO NOT SUBMIT. This takes 5 minutes and prevents catastrophic regressions.

This is not glamorous. It is not a feature. It is not a research document. But it is the one process improvement that would most accelerate our climb. Every regression costs us 20-30 Elo and 6+ hours of wasted matches. Preventing ONE regression is worth more than any single feature addition.

---

## EXECUTIVE SUMMARY: Top 5 Insights

1. **WE ARE GOING BACKWARDS.** 1500 -> 1464 in 5 matches. v4 is a confirmed regression. The strategic assessment said "stop planning, start building" on April 4. It is now April 4 and we have produced MORE plans instead of a better bot.

2. **STRIP DOWN, THEN BUILD UP.** The current 590-line bot has too many half-working features. Delete sentinels, attackers, barriers. Get economy working correctly in isolation. Then layer features back one at a time, testing after each addition.

3. **BRIDGES ARE BEING DEFERRED TOO LONG.** The roadmap puts bridges in Phase 10 (Days 5-7). They should be Phase 8.5 (Day 2). On maps with walls, no bridges = no economy = guaranteed loss. This is the single highest-leverage feature we are not building.

4. **TEST BEFORE SHIPPING.** 5-map regression test before every submission. This would have prevented the v4 catastrophe. Process discipline beats feature complexity.

5. **THE CLOCK IS TICKING AND WE ARE STANDING STILL.** 16 days to April 20. Probability of 2000: 15-25%. Probability of 1800: 45-55%. We need to ship working code TODAY, not tomorrow.

---

*Big Picture Advisor. First review. Waiting for follow-up questions or next review cycle.*
