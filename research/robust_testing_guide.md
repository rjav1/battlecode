# Robust Statistical Testing Guide for Battlecode

## 1. The Variance Problem

A single best-of-5 match on random maps is a **terrible** signal. Here's why:

### Binomial model for a single match

If our bot has true win probability `p` per game, the probability of winning a best-of-5 match (winning 3+ games) is:

```
P(match win) = C(5,3)*p^3*(1-p)^2 + C(5,4)*p^4*(1-p) + C(5,5)*p^5
             = 10*p^3*(1-p)^2 + 5*p^4*(1-p) + p^5
```

| True game win rate (p) | P(win match) | P(0-5 loss) | P(5-0 sweep) |
|------------------------|-------------|-------------|--------------|
| 40% | 31.7% | 7.8% | 1.0% |
| 45% | 40.7% | 5.0% | 1.8% |
| 50% | 50.0% | 3.1% | 3.1% |
| 55% | 59.3% | 1.8% | 5.0% |
| 60% | 68.3% | 1.0% | 7.8% |
| 65% | 76.5% | 0.5% | 11.6% |

**Key insight:** A bot with true 55% game win rate has a **40.7% chance of LOSING** any given match. A 1-4 result (which looks catastrophic) happens with P = C(5,1)*0.55*(0.45)^4 + (0.45)^5 = **12.8%**. That's roughly 1 in 8 matches -- it WILL happen regularly.

### What our v4 0-5 loss actually tells us

P(0-5 | p=0.50) = 3.1%. Looks bad, but:
- We played different opponents than v2 did
- We played different maps
- A single 0-5 is a sample of ONE match

With a single match, the 95% confidence interval on our true match win rate is essentially [0%, 100%]. **One match tells us almost nothing.**

---

## 2. Sample Size Requirements

### How many matches to detect a real improvement?

We want to distinguish between two hypotheses:
- H0: new version has same win rate as old (p = p0)
- H1: new version is better (p = p0 + delta)

Using a one-sided binomial test at alpha=0.05, power=0.80:

| Baseline (p0) | Effect size (delta) | Matches needed | Games needed |
|---------------|--------------------|--------------------|--------------|
| 50% | +10% (to 60%) | ~39 matches | ~195 games |
| 50% | +15% (to 65%) | ~19 matches | ~95 games |
| 50% | +20% (to 70%) | ~12 matches | ~60 games |
| 40% | +15% (to 55%) | ~22 matches | ~110 games |
| 40% | +20% (to 60%) | ~13 matches | ~65 games |

**Bottom line:** To be 95% confident that a version is at least 10 percentage points better, you need ~40 matches. For a 20pp improvement, ~12 matches.

### Practical minimum for local testing

With 6 opponent bots and 6 maps = 36 matchups per seed, running 3 seeds = 108 games (21.6 matches equivalent). This gives us power to detect a ~15pp improvement -- good enough for development.

**Recommendation: Run the full 6x6x3 = 108 game suite before shipping.**

---

## 3. Paired Comparison Design (RECOMMENDED)

### Why paired comparisons?

Map variance is HUGE. Some maps we always win (git_branches: 3-0), some we always lose (cold: 0-3). If version A gets tested on git_branches and version B on cold, we'll draw wrong conclusions.

**Fix:** Run BOTH versions on the SAME (map, opponent, seed) triples and compare directly.

### Method: Paired sign test

For each (opponent, map, seed) triple:
1. Run version A. Record: win/loss + titanium mined.
2. Run version B with same parameters. Record: win/loss + titanium mined.
3. Compare: did version B do better, worse, or tie?

Test statistic: count of (B wins where A lost) vs (A wins where B lost). Ignore ties. Use the sign test (binomial with p=0.5 under null).

### Example

Run 36 matchups (6 opponents x 6 maps) with seed=1:

| Result | Count |
|--------|-------|
| Both win | 15 |
| Both lose | 8 |
| A wins, B loses | 3 |
| B wins, A loses | 10 |

Discordant pairs: 13. B better in 10/13 = 76.9%.
P-value (binomial, H0: p=0.5): P(X >= 10 | n=13, p=0.5) = 0.046 < 0.05.
**Conclusion: B is significantly better.**

### Continuous metric: paired t-test on titanium mined

Even more powerful: for each (opponent, map, seed), compute:

```
diff_i = Ti_mined_B_i - Ti_mined_A_i
```

Then run a one-sample t-test on the diffs (H0: mean diff = 0).

**Advantages:**
- Uses continuous data, not just win/loss -- much more statistical power
- A game where B mines 20000 Ti and A mines 19500 Ti is a "tie" in win/loss but informative for titanium
- Can detect smaller improvements with fewer games

**This is the recommended primary metric.**

---

## 4. Multi-Seed Testing Protocol

### Why multiple seeds?

Same map + same bot + different seed = different resource placement timing, different random tiebreakers. A bot might win on seed 1 but lose on seed 2 on the same map.

### Recommended protocol

- **3 seeds per (opponent, map) pair**: seeds 1, 2, 3
- Total per version: 6 opponents x 6 maps x 3 seeds = **108 games**
- At ~2-5 seconds per local game, this takes ~4-9 minutes
- **Fix seeds across version comparisons** -- always compare A vs B on the exact same (map, opponent, seed) triple

### Why 3 seeds?

- 1 seed: too noisy, single outlier dominates
- 3 seeds: reduces seed variance by ~58% (stdev / sqrt(3))
- 5+ seeds: diminishing returns relative to adding more maps/opponents
- 3 is the sweet spot for development iteration speed

---

## 5. Interpreting Ladder Results

### Confidence intervals for ladder win rate

With N matches, observed win rate w, the 95% Wilson confidence interval is:

```
w_hat +/- z * sqrt(w_hat * (1 - w_hat) / N + z^2 / (4*N^2)) / (1 + z^2/N)
```

where z = 1.96.

Simplified table:

| Matches (N) | Observed 60% | 95% CI | Observed 50% | 95% CI |
|-------------|-------------|---------|-------------|---------|
| 2 | 1W-1L | [9%, 91%] | 1W-1L | [9%, 91%] |
| 5 | 3W-2L | [23%, 88%] | - | - |
| 10 | 6W-4L | [31%, 83%] | 5W-5L | [24%, 76%] |
| 20 | 12W-8L | [39%, 78%] | 10W-10L | [30%, 70%] |
| 50 | 30W-20L | [46%, 72%] | 25W-25L | [36%, 64%] |
| 100 | 60W-40L | [50%, 69%] | 50W-50L | [40%, 60%] |

**Our situation:** v2 went 1-1 (2 matches). The 95% CI on true win rate is [9%, 91%]. We literally cannot say anything. v4 went 0-2. CI: [0%, 66%]. Still too few.

### When to revert

**DO NOT revert after a single match loss.** Use this rule:

```
REVERT only if: cumulative ladder record with new version shows
  P(true win rate >= old version's rate) < 10%
```

In practice, this means:
- After 1 match loss: DO NOT revert (could easily be variance)
- After 2 match losses: probably don't revert yet (P(0-2 | p=0.5) = 25%)
- After 3+ match losses with 0 wins: consider reverting (P(0-3 | p=0.5) = 12.5%)
- After 5+ match losses with 0 wins: revert (P(0-5 | p=0.5) = 3.1%)

**But always cross-reference with local test suite results.** If local testing showed the version is better across 108 games, a couple ladder losses are expected variance. Trust the larger sample.

### Ladder matches per day

~1 match every 10 minutes = ~144 matches/day. After 1 day, the 95% CI width is ~16pp (at 50% observed). After 3 days (~430 matches), CI width is ~10pp. **Meaningful ladder data requires 2-3 days of matches.**

---

## 6. Decision Rules for Shipping

### Gate 1: Local regression suite (REQUIRED)

Run the full paired comparison suite (108 games x 2 versions = 216 games):

**Ship if ALL of these hold:**
1. Paired sign test p-value < 0.10 (B better than A on discordant pairs)
2. Mean titanium mined difference > 0 (B mines more on average)
3. No map regression > 2 standard deviations (B doesn't catastrophically fail any map that A won)
4. Win rate >= 60% against the test suite (absolute floor)

### Gate 2: Smoke test (REQUIRED)

- Run 3 matches against `starter` bot. Must win all 3 (sanity check -- not crashing).
- Run 1 match against current live version. Must not 0-5 (sanity check).

### Gate 3: Ladder monitoring (POST-SHIP)

After submitting:
- **Do not revert for 5 matches** unless the bot is crashing (0 Ti mined = crash signal)
- After 5 matches, compute running win rate
- Revert only if: 5+ matches played AND win rate < 30% AND local retesting confirms regression

### What v4 should have looked like

If we had this framework:
1. Local suite: Would have caught the regression (aggressive builder scaling losing Ti race)
2. After 0-5 ladder loss: "Wait for more data" (could be unlucky maps)
3. After 1-9 game record: "P(0-2 matches | p >= 0.5) = 25%. Still not conclusive, but local suite already flagged this. Revert."

---

## 7. Quick Reference Card

```
BEFORE SHIPPING:
  1. Run: python test_suite.py  (108 games, ~5 min)
  2. Check: win rate >= 60%? Ti mined improved?
  3. Run paired comparison vs current live version
  4. Ship only if paired sign test favors new version

AFTER SHIPPING:
  1. DO NOT TOUCH for 5 matches (~50 min)
  2. Check running win rate
  3. Revert only if: 5+ matches AND win rate < 30%

NEVER DO:
  - Revert after 1 match loss
  - Celebrate after 1 match win
  - Treat 3-2 as meaningfully different from 2-3
  - Compare versions tested against different opponents
```

---

## 8. Statistical Functions (Python)

For quick calculations in the REPL:

```python
from math import comb, sqrt

def match_win_prob(p):
    """P(win best-of-5) given game win probability p."""
    return sum(comb(5, k) * p**k * (1-p)**(5-k) for k in range(3, 6))

def binomial_pvalue(successes, trials, p0=0.5):
    """One-sided P(X >= successes | n=trials, p=p0)."""
    return sum(comb(trials, k) * p0**k * (1-p0)**(trials-k)
               for k in range(successes, trials+1))

def wilson_ci(wins, n, z=1.96):
    """95% Wilson confidence interval for proportion."""
    p_hat = wins / n
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2*n)) / denom
    margin = z * sqrt(p_hat*(1-p_hat)/n + z**2/(4*n**2)) / denom
    return max(0, center - margin), min(1, center + margin)

def sample_size_binomial(p0, p1, alpha=0.05, power=0.80):
    """Approximate sample size for one-sided binomial test."""
    from scipy.stats import norm
    z_a = norm.ppf(1 - alpha)
    z_b = norm.ppf(power)
    n = ((z_a * sqrt(p0*(1-p0)) + z_b * sqrt(p1*(1-p1))) / (p1 - p0))**2
    return int(n) + 1

# Examples:
# match_win_prob(0.55)  -> 0.593 (55% game rate -> 59% match rate)
# binomial_pvalue(0, 2, 0.5)  -> 0.25 (0-2 not significant)
# wilson_ci(3, 5)  -> (0.19, 0.88) (3-2 record is very uncertain)
```
