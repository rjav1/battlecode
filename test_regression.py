#!/usr/bin/env python3
"""
Battlecode Regression Testing Suite
====================================
Runs a standardized battery of tests and produces a PASS/FAIL verdict.

Usage:
    python test_regression.py                     # Full regression suite
    python test_regression.py --compare buzzing_prev  # Compare two bots head-to-head
    python test_regression.py --quick             # Just core regression (faster)

Exit code 0 = PASS, 1 = FAIL
Detailed results written to research/regression_results.md
"""

import argparse
import io
import os
import sys
import time
import contextlib
import datetime
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

# ── Configuration ──────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent
BOTS_DIR = PROJECT_ROOT / "bots"
MAPS_DIR = PROJECT_ROOT / "maps"
ENGINE_ROOT = str(PROJECT_ROOT)
RESULTS_DIR = PROJECT_ROOT / "research"

PRIMARY_BOT = "buzzing"
PREVIOUS_BOT = "buzzing_prev"

# Core regression maps (must win 3/5 vs previous)
CORE_MAPS = ["default_medium1", "cold", "face", "settlement", "galaxy"]

# Opponent gauntlet: (opponent, [maps])
GAUNTLET_OPPONENTS = [
    ("balanced",       ["cold", "galaxy"]),
    ("barrier_wall",   ["face", "settlement"]),
    ("sentinel_spam",  ["default_medium1", "cold"]),
    ("rusher",         ["face", "default_medium1"]),
    ("ladder_eco",     ["galaxy", "settlement"]),
    ("ladder_rush",    ["cold", "face"]),
    ("ladder_bridge",  ["settlement", "galaxy"]),
]

# Self-play stability map
SELFPLAY_MAP = "default_medium1"

# Seeds for reproducibility (different seeds per match slot)
SEEDS = [1, 42, 137, 256, 999]


# ── Engine wrapper ─────────────────────────────────────────────────────────

def resolve_bot(name):
    """Return absolute path to bot's main.py."""
    p = BOTS_DIR / name / "main.py"
    if not p.exists():
        raise FileNotFoundError(f"Bot not found: {p}")
    return str(p.resolve())


def resolve_map(name):
    """Return absolute path to map file."""
    p = MAPS_DIR / f"{name}.map26"
    if not p.exists():
        raise FileNotFoundError(f"Map not found: {p}")
    return str(p.resolve())


def run_single_match(bot_a_name, bot_b_name, map_name, seed=1):
    """
    Run a single match and return result dict.
    Runs in a subprocess to avoid engine state leakage.
    Returns dict with: winner_name, win_condition, turns, and resource stats.
    """
    try:
        from cambc.cambc_engine import run_game
        player_a = resolve_bot(bot_a_name)
        player_b = resolve_bot(bot_b_name)
        map_path = resolve_map(map_name)
        # Use a unique replay path to avoid conflicts
        replay_path = str(PROJECT_ROOT / f"_test_replay_{os.getpid()}.replay26")
        # Suppress engine stdout ("Completed turn ...") at fd level
        old_fd = os.dup(1)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 1)
        os.close(devnull)
        try:
            result = run_game(player_a, player_b, ENGINE_ROOT, map_path, replay_path, seed, 0)
        finally:
            os.dup2(old_fd, 1)
            os.close(old_fd)
            # Clean up replay file
            try:
                rp = PROJECT_ROOT / f"_test_replay_{os.getpid()}.replay26"
                if rp.exists():
                    rp.unlink()
            except:
                pass

        winner_name = bot_a_name if result["winner"] == "A" else (bot_b_name if result["winner"] == "B" else "draw")
        return {
            "bot_a": bot_a_name,
            "bot_b": bot_b_name,
            "map": map_name,
            "seed": seed,
            "winner": winner_name,
            "win_condition": result["win_condition"],
            "turns": result["turns"],
            "a_ti_mined": result["a_titanium_collected"],
            "b_ti_mined": result["b_titanium_collected"],
            "a_ti_total": result["a_titanium"],
            "b_ti_total": result["b_titanium"],
            "a_ax_mined": result["a_axionite_collected"],
            "b_ax_mined": result["b_axionite_collected"],
            "a_units": result["a_units"],
            "b_units": result["b_units"],
            "a_buildings": result["a_buildings"],
            "b_buildings": result["b_buildings"],
            "error": None,
        }
    except Exception as e:
        return {
            "bot_a": bot_a_name,
            "bot_b": bot_b_name,
            "map": map_name,
            "seed": seed,
            "winner": "error",
            "win_condition": "error",
            "turns": 0,
            "a_ti_mined": 0, "b_ti_mined": 0,
            "a_ti_total": 0, "b_ti_total": 0,
            "a_ax_mined": 0, "b_ax_mined": 0,
            "a_units": 0, "b_units": 0,
            "a_buildings": 0, "b_buildings": 0,
            "error": str(e),
        }


def _worker(args):
    """Process pool worker — runs a single match in isolation."""
    bot_a, bot_b, map_name, seed = args
    return run_single_match(bot_a, bot_b, map_name, seed)


# ── Test Suites ────────────────────────────────────────────────────────────

def run_core_regression(bot=PRIMARY_BOT, opponent=PREVIOUS_BOT):
    """Core regression: bot vs previous on 5 maps. Must win >= 3/5."""
    print(f"\n{'='*60}")
    print(f"  CORE REGRESSION: {bot} vs {opponent}")
    print(f"{'='*60}")

    if not (BOTS_DIR / opponent / "main.py").exists():
        print(f"  WARNING: {opponent} bot not found, skipping core regression")
        return [], True  # Pass vacuously if no previous bot

    results = []
    for i, map_name in enumerate(CORE_MAPS):
        seed = SEEDS[i % len(SEEDS)]
        print(f"  [{i+1}/{len(CORE_MAPS)}] {map_name} (seed={seed})...", end=" ", flush=True)
        t0 = time.time()
        r = run_single_match(bot, opponent, map_name, seed)
        elapsed = time.time() - t0
        results.append(r)

        if r["error"]:
            print(f"ERROR ({elapsed:.1f}s): {r['error']}")
        else:
            marker = "WIN" if r["winner"] == bot else ("LOSS" if r["winner"] == opponent else "DRAW")
            print(f"{marker} - {r['win_condition']} t{r['turns']} "
                  f"(Ti: {r['a_ti_mined']} vs {r['b_ti_mined']}) [{elapsed:.1f}s]")

    wins = sum(1 for r in results if r["winner"] == bot)
    losses = sum(1 for r in results if r["winner"] == opponent)
    errors = sum(1 for r in results if r["error"])

    print(f"\n  Result: {wins}W-{losses}L-{errors}E out of {len(CORE_MAPS)}")

    # Check pass criteria
    passed = True
    fail_reasons = []

    if wins < 3:
        passed = False
        fail_reasons.append(f"Won only {wins}/5 (need 3+)")

    for r in results:
        if r["error"]:
            continue
        # Check for 0 Ti mined
        if r["a_ti_mined"] == 0:
            passed = False
            fail_reasons.append(f"Mined 0 Ti on {r['map']}")
        # Check for core destroyed (we lost by core_destroyed)
        if r["winner"] == opponent and r["win_condition"] == "core_destroyed":
            passed = False
            fail_reasons.append(f"Core destroyed on {r['map']}")

    if passed:
        print("  VERDICT: PASS")
    else:
        print(f"  VERDICT: FAIL - {'; '.join(fail_reasons)}")

    return results, passed


def run_gauntlet(bot=PRIMARY_BOT):
    """Opponent gauntlet: informational win rate tracking."""
    print(f"\n{'='*60}")
    print(f"  OPPONENT GAUNTLET: {bot} vs field")
    print(f"{'='*60}")

    all_results = []
    opponent_summary = []

    for opp, maps in GAUNTLET_OPPONENTS:
        if not (BOTS_DIR / opp / "main.py").exists():
            print(f"  Skipping {opp} (bot not found)")
            continue

        opp_results = []
        for j, map_name in enumerate(maps):
            seed = SEEDS[j % len(SEEDS)]
            print(f"  {bot} vs {opp} on {map_name} (seed={seed})...", end=" ", flush=True)
            t0 = time.time()
            r = run_single_match(bot, opp, map_name, seed)
            elapsed = time.time() - t0
            opp_results.append(r)
            all_results.append(r)

            if r["error"]:
                print(f"ERROR [{elapsed:.1f}s]")
            else:
                marker = "WIN" if r["winner"] == bot else ("LOSS" if r["winner"] == opp else "DRAW")
                print(f"{marker} [{elapsed:.1f}s]")

        wins = sum(1 for r in opp_results if r["winner"] == bot)
        total = len(opp_results)
        opponent_summary.append((opp, wins, total))

    # Overall stats
    total_wins = sum(1 for r in all_results if r["winner"] == bot)
    total_played = len([r for r in all_results if not r["error"]])
    win_rate = (total_wins / total_played * 100) if total_played > 0 else 0

    print(f"\n  Gauntlet Summary:")
    for opp, wins, total in opponent_summary:
        print(f"    vs {opp}: {wins}/{total}")
    print(f"  Overall: {total_wins}/{total_played} ({win_rate:.0f}% win rate)")
    target_met = win_rate >= 50
    print(f"  Target (50%+): {'MET' if target_met else 'NOT MET'}")

    return all_results, win_rate, target_met


def run_selfplay(bot=PRIMARY_BOT):
    """Self-play stability: must not crash."""
    print(f"\n{'='*60}")
    print(f"  SELF-PLAY STABILITY: {bot} vs {bot}")
    print(f"{'='*60}")

    print(f"  {bot} vs {bot} on {SELFPLAY_MAP}...", end=" ", flush=True)
    t0 = time.time()
    r = run_single_match(bot, bot, SELFPLAY_MAP, seed=1)
    elapsed = time.time() - t0

    if r["error"]:
        print(f"ERROR [{elapsed:.1f}s]: {r['error']}")
        passed = False
    else:
        print(f"OK - {r['win_condition']} t{r['turns']} [{elapsed:.1f}s]")
        passed = True

    return r, passed


# ── Comparison Mode ────────────────────────────────────────────────────────

def run_comparison(bot_a, bot_b):
    """Run both bots on the same maps and report paired differences."""
    print(f"\n{'='*60}")
    print(f"  COMPARISON: {bot_a} vs {bot_b}")
    print(f"{'='*60}")

    comparison_maps = CORE_MAPS + ["arena", "corridors", "hourglass"]
    results_a = []  # bot_a as player A
    results_b = []  # bot_b as player A (swapped sides)

    for map_name in comparison_maps:
        if not (MAPS_DIR / f"{map_name}.map26").exists():
            print(f"  Skipping {map_name} (map not found)")
            continue

        seed = SEEDS[comparison_maps.index(map_name) % len(SEEDS)]

        # Game 1: bot_a as A, bot_b as B
        print(f"  {map_name} (seed={seed}): {bot_a} vs {bot_b}...", end=" ", flush=True)
        r1 = run_single_match(bot_a, bot_b, map_name, seed)
        results_a.append(r1)
        m1 = "W" if r1["winner"] == bot_a else "L"
        print(f"{m1}", end="  ")

        # Game 2: bot_b as A, bot_a as B (swap sides)
        print(f"{bot_b} vs {bot_a}...", end=" ", flush=True)
        r2 = run_single_match(bot_b, bot_a, map_name, seed)
        results_b.append(r2)
        m2 = "W" if r2["winner"] == bot_a else "L"
        print(f"{m2}")

    # Tally
    a_wins = sum(1 for r in results_a if r["winner"] == bot_a) + sum(1 for r in results_b if r["winner"] == bot_a)
    b_wins = sum(1 for r in results_a if r["winner"] == bot_b) + sum(1 for r in results_b if r["winner"] == bot_b)
    total = len(results_a) + len(results_b)

    print(f"\n  {bot_a}: {a_wins}/{total} wins")
    print(f"  {bot_b}: {b_wins}/{total} wins")

    return results_a, results_b


# ── Report Generation ──────────────────────────────────────────────────────

def generate_report(core_results, core_passed, gauntlet_results, gauntlet_wr,
                    gauntlet_target, selfplay_result, selfplay_passed,
                    overall_pass, elapsed_total, output_path):
    """Write detailed results to markdown file."""
    lines = []
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append(f"# Regression Test Results")
    lines.append(f"")
    lines.append(f"**Date:** {timestamp}")
    lines.append(f"**Bot:** {PRIMARY_BOT}")
    lines.append(f"**Duration:** {elapsed_total:.0f}s")
    lines.append(f"**Verdict:** {'PASS' if overall_pass else 'FAIL'}")
    lines.append(f"")

    # Summary table
    lines.append(f"## Summary")
    lines.append(f"")
    lines.append(f"| Suite | Result | Details |")
    lines.append(f"|-------|--------|---------|")

    core_wins = sum(1 for r in core_results if r["winner"] == PRIMARY_BOT) if core_results else 0
    core_total = len(core_results) if core_results else 0
    lines.append(f"| Core Regression | {'PASS' if core_passed else 'FAIL'} | {core_wins}/{core_total} vs {PREVIOUS_BOT} |")

    gauntlet_played = len([r for r in gauntlet_results if not r["error"]]) if gauntlet_results else 0
    gauntlet_wins = sum(1 for r in gauntlet_results if r["winner"] == PRIMARY_BOT) if gauntlet_results else 0
    lines.append(f"| Opponent Gauntlet | {'MET' if gauntlet_target else 'NOT MET'} | {gauntlet_wins}/{gauntlet_played} ({gauntlet_wr:.0f}%) |")

    lines.append(f"| Self-Play | {'PASS' if selfplay_passed else 'FAIL'} | {'No crash' if selfplay_passed else 'CRASH'} |")
    lines.append(f"")

    # Core regression detail
    if core_results:
        lines.append(f"## Core Regression: {PRIMARY_BOT} vs {PREVIOUS_BOT}")
        lines.append(f"")
        lines.append(f"| Map | Result | Condition | Turns | Our Ti | Their Ti | Our Ax | Their Ax |")
        lines.append(f"|-----|--------|-----------|-------|--------|----------|--------|----------|")
        for r in core_results:
            if r["error"]:
                lines.append(f"| {r['map']} | ERROR | {r['error'][:30]} | - | - | - | - | - |")
            else:
                result = "WIN" if r["winner"] == PRIMARY_BOT else "LOSS"
                lines.append(f"| {r['map']} | {result} | {r['win_condition']} | {r['turns']} | "
                           f"{r['a_ti_mined']} | {r['b_ti_mined']} | {r['a_ax_mined']} | {r['b_ax_mined']} |")
        lines.append(f"")

    # Gauntlet detail
    if gauntlet_results:
        lines.append(f"## Opponent Gauntlet")
        lines.append(f"")
        lines.append(f"| Opponent | Map | Result | Condition | Turns | Our Ti | Their Ti |")
        lines.append(f"|----------|-----|--------|-----------|-------|--------|----------|")
        for r in gauntlet_results:
            if r["error"]:
                lines.append(f"| {r['bot_b']} | {r['map']} | ERROR | {r['error'][:30]} | - | - | - |")
            else:
                result = "WIN" if r["winner"] == PRIMARY_BOT else "LOSS"
                lines.append(f"| {r['bot_b']} | {r['map']} | {result} | {r['win_condition']} | "
                           f"{r['turns']} | {r['a_ti_mined']} | {r['b_ti_mined']} |")
        lines.append(f"")

    # Self-play detail
    lines.append(f"## Self-Play Stability")
    lines.append(f"")
    if selfplay_result:
        r = selfplay_result
        if r["error"]:
            lines.append(f"- **Result:** CRASH - {r['error']}")
        else:
            lines.append(f"- **Result:** OK ({r['win_condition']}, turn {r['turns']})")
            lines.append(f"- **A Ti:** {r['a_ti_mined']}, **B Ti:** {r['b_ti_mined']}")
    lines.append(f"")

    report = "\n".join(lines)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return report


def generate_comparison_report(bot_a, bot_b, results_a, results_b, output_path):
    """Write comparison results to markdown."""
    lines = []
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append(f"# Comparison: {bot_a} vs {bot_b}")
    lines.append(f"")
    lines.append(f"**Date:** {timestamp}")
    lines.append(f"")

    lines.append(f"| Map | {bot_a} as A | {bot_b} as A | Net |")
    lines.append(f"|-----|-------------|-------------|-----|")

    a_total_wins = 0
    b_total_wins = 0

    for r1, r2 in zip(results_a, results_b):
        g1 = "W" if r1["winner"] == bot_a else "L"
        g2 = "W" if r2["winner"] == bot_a else "L"
        if r1["winner"] == bot_a:
            a_total_wins += 1
        else:
            b_total_wins += 1
        if r2["winner"] == bot_a:
            a_total_wins += 1
        else:
            b_total_wins += 1
        net = ("+" if g1 == "W" and g2 == "W" else
               "-" if g1 == "L" and g2 == "L" else "=")
        lines.append(f"| {r1['map']} | {g1} ({r1['win_condition'][:3]}) | {g2} ({r2['win_condition'][:3]}) | {net} |")

    lines.append(f"")
    total = len(results_a) + len(results_b)
    lines.append(f"**{bot_a}:** {a_total_wins}/{total} wins")
    lines.append(f"**{bot_b}:** {b_total_wins}/{total} wins")

    report = "\n".join(lines)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return report


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Battlecode Regression Testing Suite")
    parser.add_argument("--compare", metavar="BOT", help="Run comparison mode against specified bot")
    parser.add_argument("--quick", action="store_true", help="Run only core regression (faster)")
    parser.add_argument("--bot", default=PRIMARY_BOT, help=f"Bot to test (default: {PRIMARY_BOT})")
    parser.add_argument("--output", default=None, help="Output file path (default: research/regression_results.md)")
    args = parser.parse_args()

    t_start = time.time()

    # Comparison mode
    if args.compare:
        output = Path(args.output) if args.output else RESULTS_DIR / "regression_results.md"
        results_a, results_b = run_comparison(args.bot, args.compare)
        report = generate_comparison_report(args.bot, args.compare, results_a, results_b, output)
        print(f"\nDetailed results: {output}")
        return

    # Full or quick regression
    bot = args.bot
    output = Path(args.output) if args.output else RESULTS_DIR / "regression_results.md"

    # 1. Core regression (must pass)
    core_results, core_passed = run_core_regression(bot)

    # 2. Opponent gauntlet (informational)
    if not args.quick:
        gauntlet_results, gauntlet_wr, gauntlet_target = run_gauntlet(bot)
    else:
        gauntlet_results, gauntlet_wr, gauntlet_target = [], 0, True

    # 3. Self-play stability
    selfplay_result, selfplay_passed = run_selfplay(bot)

    elapsed = time.time() - t_start

    # Overall verdict
    overall_pass = core_passed and selfplay_passed

    # Generate report
    generate_report(core_results, core_passed, gauntlet_results, gauntlet_wr,
                    gauntlet_target, selfplay_result, selfplay_passed,
                    overall_pass, elapsed, output)

    # Final summary
    print(f"\n{'='*60}")
    print(f"  FINAL VERDICT: {'PASS' if overall_pass else 'FAIL'}")
    print(f"  Duration: {elapsed:.0f}s")
    print(f"  Detailed results: {output}")
    print(f"{'='*60}")

    sys.exit(0 if overall_pass else 1)


if __name__ == "__main__":
    main()
