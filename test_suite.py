"""
Battlecode Local Test Suite (v2 - statistically robust)
Run: python test_suite.py [--paired OLD_BOT]
Runs buzzing bot against curated opponents across multiple maps and seeds.
Produces win rate summary table with confidence intervals.

Key fix from v1: calls run_game engine directly instead of parsing CLI output.
"""

import sys
import time
import argparse
from pathlib import Path
from math import comb, sqrt
from collections import defaultdict

CWD = Path(r"C:\Users\rahil\downloads\battlecode")
BOTS_DIR = CWD / "bots"
MAPS_DIR = CWD / "maps"
ENGINE_ROOT = str((CWD / "cambc").resolve().parent)

BUZZING = "buzzing"
OPPONENTS = ["eco_opponent", "sentinel_spam", "fast_expand", "balanced", "barrier_wall", "rusher"]
MAPS = ["default_medium1", "cold", "face", "settlement", "corridors", "shish_kebab"]
SEEDS = [1, 2, 3]

# Replay path (overwritten each game, not important for testing)
REPLAY_PATH = str(CWD / "test_replay.replay26")


def resolve_bot(name):
    """Resolve bot name to main.py path."""
    p = BOTS_DIR / name / "main.py"
    if p.exists():
        return str(p.resolve())
    raise FileNotFoundError(f"Bot not found: {p}")


def resolve_map(name):
    """Resolve map name to .map26 path."""
    p = MAPS_DIR / (name + ".map26")
    if p.exists():
        return str(p.resolve())
    raise FileNotFoundError(f"Map not found: {p}")


def run_match(bot_name, opponent, map_name, seed=1):
    """Run a single game using the engine directly. Returns result dict."""
    from cambc.cambc_engine import run_game

    player_a = resolve_bot(bot_name)
    player_b = resolve_bot(opponent)
    map_path = resolve_map(map_name)

    try:
        result = run_game(player_a, player_b, ENGINE_ROOT, map_path, REPLAY_PATH, seed, 0)
    except Exception as e:
        return {
            "opponent": opponent, "map": map_name, "seed": seed,
            "winner": "ERROR", "win_condition": str(e), "turn": 0,
            "buzzing_ti": 0, "opp_ti": 0, "buzzing_ax": 0, "opp_ax": 0,
            "buzzing_ti_mined": 0, "opp_ti_mined": 0,
            "buzzing_units": 0, "opp_units": 0,
            "buzzing_buildings": 0, "opp_buildings": 0,
        }

    # Map engine result keys to our format
    # Engine returns: winner ("A"/"B"/"Draw"), win_condition, turns,
    #   a_titanium, a_titanium_collected, a_axionite, a_axionite_collected,
    #   b_titanium, b_titanium_collected, b_axionite, b_axionite_collected,
    #   a_units, b_units, a_buildings, b_buildings

    winner_raw = result.get("winner", "Draw")
    if winner_raw == "A":
        winner = bot_name
    elif winner_raw == "B":
        winner = opponent
    else:
        winner = "Draw"

    condition = result.get("win_condition", "")
    if condition == "core_destroyed":
        condition = "Core destroyed"
    elif condition == "resources":
        condition = "Resources (tiebreak)"

    return {
        "opponent": opponent, "map": map_name, "seed": seed,
        "winner": winner,
        "win_condition": condition,
        "turn": result.get("turns", 0),
        "buzzing_ti": result.get("a_titanium", 0),
        "buzzing_ti_mined": result.get("a_titanium_collected", 0),
        "opp_ti": result.get("b_titanium", 0),
        "opp_ti_mined": result.get("b_titanium_collected", 0),
        "buzzing_ax": result.get("a_axionite", 0),
        "opp_ax": result.get("b_axionite", 0),
        "buzzing_units": result.get("a_units", 0),
        "opp_units": result.get("b_units", 0),
        "buzzing_buildings": result.get("a_buildings", 0),
        "opp_buildings": result.get("b_buildings", 0),
    }


def wilson_ci(wins, n, z=1.96):
    """95% Wilson confidence interval for a proportion."""
    if n == 0:
        return 0.0, 1.0
    p_hat = wins / n
    denom = 1 + z ** 2 / n
    center = (p_hat + z ** 2 / (2 * n)) / denom
    margin = z * sqrt(p_hat * (1 - p_hat) / n + z ** 2 / (4 * n ** 2)) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def binomial_pvalue(successes, trials, p0=0.5):
    """One-sided P(X >= successes | n=trials, p=p0)."""
    return sum(comb(trials, k) * p0 ** k * (1 - p0) ** (trials - k)
               for k in range(successes, trials + 1))


def print_results(results, bot_name):
    """Print summary tables with confidence intervals."""
    total = len(results)
    wins = sum(1 for r in results if r["winner"] == bot_name)
    lo, hi = wilson_ci(wins, total)

    print("\n" + "=" * 70)
    print(f"  TEST SUITE RESULTS: {bot_name}")
    print(f"  Overall: {wins}W - {total - wins}L  ({100 * wins / total:.0f}% win rate)")
    print(f"  95% CI: [{100 * lo:.0f}%, {100 * hi:.0f}%]")
    print("=" * 70)

    # Heatmap: opponent x map (aggregated across seeds)
    print(f"\n{'Opponent':<16}", end="")
    for m in MAPS:
        print(f" {m[:10]:>10}", end="")
    print(f" {'W-L':>6}  {'Rate':>5}")
    print("-" * (16 + 11 * len(MAPS) + 14))

    for opp in OPPONENTS:
        opp_results = [r for r in results if r["opponent"] == opp]
        opp_wins = sum(1 for r in opp_results if r["winner"] == bot_name)
        print(f"{opp:<16}", end="")
        for m in MAPS:
            map_results = [r for r in opp_results if r["map"] == m]
            map_wins = sum(1 for r in map_results if r["winner"] == bot_name)
            total_map = len(map_results)
            if total_map > 0:
                print(f" {map_wins}/{total_map:>8}", end="")
            else:
                print(f" {'?':>10}", end="")
        rate = 100 * opp_wins / len(opp_results) if opp_results else 0
        print(f" {opp_wins}-{len(opp_results) - opp_wins:>1}  {rate:>4.0f}%")

    # Per-map summary
    print(f"\n{'Map':<16} {'W-L':>6}  {'Rate':>5}  {'95% CI':>14}")
    print("-" * 48)
    for m in MAPS:
        map_results = [r for r in results if r["map"] == m]
        map_wins = sum(1 for r in map_results if r["winner"] == bot_name)
        n = len(map_results)
        rate = 100 * map_wins / n if n else 0
        lo_m, hi_m = wilson_ci(map_wins, n)
        print(f"{m:<16} {map_wins}-{n - map_wins:>1}  {rate:>4.0f}%  [{100 * lo_m:.0f}%, {100 * hi_m:.0f}%]")

    # Economy comparison
    print(f"\n{'Opponent':<16} {'Avg Ti Mined':>12} {'Opp Ti Mined':>12} {'Ti Ratio':>8}")
    print("-" * 52)
    for opp in OPPONENTS:
        opp_results = [r for r in results if r["opponent"] == opp]
        avg_ti = sum(r["buzzing_ti_mined"] for r in opp_results) / len(opp_results) if opp_results else 0
        avg_opp_ti = sum(r["opp_ti_mined"] for r in opp_results) / len(opp_results) if opp_results else 0
        ratio = avg_ti / avg_opp_ti if avg_opp_ti > 0 else float('inf')
        print(f"{opp:<16} {avg_ti:>12.0f} {avg_opp_ti:>12.0f} {ratio:>7.1f}x")

    # Losses detail
    loss_results = [r for r in results if r["winner"] != bot_name]
    if loss_results:
        print(f"\nLOSSES DETAIL:")
        print(f"{'Opponent':<16} {'Map':<16} {'Seed':>4} {'Condition':<24} {'Turn':>5} {'Our Ti':>7} {'Their Ti':>9}")
        print("-" * 85)
        for r in loss_results:
            print(f"{r['opponent']:<16} {r['map']:<16} {r['seed']:>4} {r['win_condition']:<24} {r['turn']:>5} "
                  f"{r['buzzing_ti_mined']:>7} {r['opp_ti_mined']:>9}")

    return wins, total


def print_paired_comparison(results_new, results_old, name_new, name_old):
    """Paired sign test comparing two versions on the same (opponent, map, seed) triples."""
    print("\n" + "=" * 70)
    print(f"  PAIRED COMPARISON: {name_new} vs {name_old}")
    print("=" * 70)

    new_better = 0
    old_better = 0
    ties = 0
    ti_diffs = []

    for r_new in results_new:
        key = (r_new["opponent"], r_new["map"], r_new["seed"])
        r_old = next((r for r in results_old
                      if (r["opponent"], r["map"], r["seed"]) == key), None)
        if r_old is None:
            continue

        new_won = r_new["winner"] == name_new
        old_won = r_old["winner"] == name_old

        if new_won and not old_won:
            new_better += 1
        elif old_won and not new_won:
            old_better += 1
        else:
            ties += 1

        ti_diff = r_new["buzzing_ti_mined"] - r_old["buzzing_ti_mined"]
        ti_diffs.append(ti_diff)

    discordant = new_better + old_better
    print(f"\n  New wins where old lost: {new_better}")
    print(f"  Old wins where new lost: {old_better}")
    print(f"  Concordant (both same):  {ties}")

    if discordant > 0:
        pval = binomial_pvalue(new_better, discordant, 0.5)
        print(f"\n  Sign test p-value (new > old): {pval:.4f}", end="")
        if pval < 0.05:
            print("  ** SIGNIFICANT at 5% **")
        elif pval < 0.10:
            print("  * marginal at 10% *")
        else:
            print("  (not significant)")
    else:
        print("\n  No discordant pairs -- cannot test.")

    if ti_diffs:
        mean_diff = sum(ti_diffs) / len(ti_diffs)
        var_diff = sum((d - mean_diff) ** 2 for d in ti_diffs) / (len(ti_diffs) - 1) if len(ti_diffs) > 1 else 0
        se_diff = sqrt(var_diff / len(ti_diffs)) if var_diff > 0 else 0
        t_stat = mean_diff / se_diff if se_diff > 0 else 0

        print(f"\n  Titanium mined difference (new - old):")
        print(f"    Mean: {mean_diff:+.0f} Ti")
        print(f"    Std:  {sqrt(var_diff):.0f} Ti")
        print(f"    t-stat: {t_stat:.2f} (df={len(ti_diffs) - 1})")
        if abs(t_stat) > 2.0:
            direction = "NEW BETTER" if t_stat > 0 else "OLD BETTER"
            print(f"    ** {direction} (|t| > 2) **")

    return new_better, old_better, ties


def run_suite(bot_name):
    """Run full test suite for a bot. Returns list of result dicts."""
    total_games = len(OPPONENTS) * len(MAPS) * len(SEEDS)
    print(f"Running {total_games} games: {bot_name} vs {len(OPPONENTS)} opponents x {len(MAPS)} maps x {len(SEEDS)} seeds")
    print()

    results = []
    game_num = 0

    for opp in OPPONENTS:
        for map_name in MAPS:
            for seed in SEEDS:
                game_num += 1
                sys.stdout.write(f"  [{game_num}/{total_games}] {bot_name} vs {opp} on {map_name} (seed {seed})... ")
                sys.stdout.flush()

                t0 = time.time()
                result = run_match(bot_name, opp, map_name, seed)
                dt = time.time() - t0

                w = "WIN" if result["winner"] == bot_name else "LOSS"
                ti = result["buzzing_ti_mined"]
                print(f"{w} (Ti:{ti}, {result['win_condition']}, turn {result['turn']}) [{dt:.1f}s]")

                results.append(result)

    return results


def write_results_md(results, bot_name, elapsed, paired_info=None):
    """Write results to markdown file."""
    total = len(results)
    wins = sum(1 for r in results if r["winner"] == bot_name)
    lo, hi = wilson_ci(wins, total)

    lines = []
    lines.append("# Test Suite Results\n")
    lines.append(f"**Date:** {time.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Bot:** {bot_name}")
    lines.append(f"**Elapsed:** {elapsed:.0f}s")
    lines.append(f"**Games:** {total} ({len(OPPONENTS)} opponents x {len(MAPS)} maps x {len(SEEDS)} seeds)")
    lines.append(f"**Overall:** {wins}W - {total - wins}L ({100 * wins / total:.0f}% win rate)")
    lines.append(f"**95% CI:** [{100 * lo:.0f}%, {100 * hi:.0f}%]\n")

    # Heatmap table
    lines.append("## Win/Loss Heatmap (wins/total per cell)\n")
    header = "| Opponent |"
    sep = "|----------|"
    for m in MAPS:
        header += f" {m} |"
        sep += "--------|"
    header += " W-L | Rate |"
    sep += "-----|------|"
    lines.append(header)
    lines.append(sep)

    for opp in OPPONENTS:
        opp_results = [r for r in results if r["opponent"] == opp]
        opp_wins = sum(1 for r in opp_results if r["winner"] == bot_name)
        row = f"| {opp} |"
        for m in MAPS:
            map_results = [r for r in opp_results if r["map"] == m]
            map_wins = sum(1 for r in map_results if r["winner"] == bot_name)
            n = len(map_results)
            row += f" {map_wins}/{n} |"
        rate = 100 * opp_wins / len(opp_results) if opp_results else 0
        row += f" {opp_wins}-{len(opp_results) - opp_wins} | {rate:.0f}% |"
        lines.append(row)

    # Per-map
    lines.append("\n## Per-Map Win Rate\n")
    lines.append("| Map | W-L | Rate | 95% CI |")
    lines.append("|-----|-----|------|--------|")
    for m in MAPS:
        map_results = [r for r in results if r["map"] == m]
        map_wins = sum(1 for r in map_results if r["winner"] == bot_name)
        n = len(map_results)
        rate = 100 * map_wins / n if n else 0
        lo_m, hi_m = wilson_ci(map_wins, n)
        lines.append(f"| {m} | {map_wins}-{n - map_wins} | {rate:.0f}% | [{100 * lo_m:.0f}%, {100 * hi_m:.0f}%] |")

    # Economy
    lines.append("\n## Economy Comparison\n")
    lines.append("| Opponent | Avg Ti Mined | Opp Ti Mined | Ratio |")
    lines.append("|----------|-------------|-------------|-------|")
    for opp in OPPONENTS:
        opp_results = [r for r in results if r["opponent"] == opp]
        avg_ti = sum(r["buzzing_ti_mined"] for r in opp_results) / len(opp_results) if opp_results else 0
        avg_opp_ti = sum(r["opp_ti_mined"] for r in opp_results) / len(opp_results) if opp_results else 0
        ratio = avg_ti / avg_opp_ti if avg_opp_ti > 0 else float('inf')
        lines.append(f"| {opp} | {avg_ti:.0f} | {avg_opp_ti:.0f} | {ratio:.1f}x |")

    # Losses
    loss_results = [r for r in results if r["winner"] != bot_name]
    if loss_results:
        lines.append("\n## Losses Detail\n")
        lines.append("| Opponent | Map | Seed | Condition | Turn | Our Ti | Their Ti |")
        lines.append("|----------|-----|------|-----------|------|--------|----------|")
        for r in loss_results:
            lines.append(f"| {r['opponent']} | {r['map']} | {r['seed']} | {r['win_condition']} | {r['turn']} | "
                         f"{r['buzzing_ti_mined']} | {r['opp_ti_mined']} |")

    if paired_info:
        lines.append("\n## Paired Comparison\n")
        lines.append(f"New wins where old lost: {paired_info[0]}")
        lines.append(f"Old wins where new lost: {paired_info[1]}")
        lines.append(f"Concordant: {paired_info[2]}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Battlecode test suite")
    parser.add_argument("--bot", default=BUZZING, help="Bot to test (default: buzzing)")
    parser.add_argument("--paired", default=None, help="Old bot name for paired comparison")
    parser.add_argument("--seeds", type=int, default=3, help="Number of seeds (default: 3)")
    args = parser.parse_args()

    global SEEDS
    SEEDS = list(range(1, args.seeds + 1))

    start = time.time()

    # Run main bot suite
    results = run_suite(args.bot)
    elapsed = time.time() - start
    total_games = len(results)

    print(f"\nAll {total_games} games completed in {elapsed:.0f}s")
    wins, total = print_results(results, args.bot)

    # Paired comparison if requested
    paired_info = None
    if args.paired:
        print(f"\nRunning paired comparison: {args.paired}")
        results_old = run_suite(args.paired)
        elapsed = time.time() - start
        paired_info = print_paired_comparison(results, results_old, args.bot, args.paired)

    # Write markdown results
    md = write_results_md(results, args.bot, elapsed, paired_info)
    md_path = str(CWD / "research" / "test_suite_results.md")
    with open(md_path, "w") as f:
        f.write(md)
    print(f"\nResults written to {md_path}")

    # Exit code: 0 if >= 60% win rate, 1 otherwise
    rate = 100 * wins / total
    lo, hi = wilson_ci(wins, total)
    if rate >= 60:
        print(f"\nPASS: {rate:.0f}% win rate [CI: {100 * lo:.0f}%-{100 * hi:.0f}%] (target: >=60%)")
        sys.exit(0)
    else:
        print(f"\nFAIL: {rate:.0f}% win rate [CI: {100 * lo:.0f}%-{100 * hi:.0f}%] (target: >=60%)")
        sys.exit(1)


if __name__ == "__main__":
    main()
