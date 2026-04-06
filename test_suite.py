"""
Battlecode Local Test Suite
Run: python test_suite.py
Runs buzzing bot against curated opponents across multiple maps.
Produces win rate summary table.
"""

import subprocess
import re
import sys
import time
from collections import defaultdict

BUZZING = "buzzing"
OPPONENTS = ["eco_opponent", "sentinel_spam", "fast_expand", "balanced", "barrier_wall", "rusher"]
MAPS = ["default_medium1", "cold", "face", "settlement", "corridors", "shish_kebab"]

CWD = r"C:\Users\rahil\downloads\battlecode"
PYTHON = r"C:\Users\rahil\AppData\Local\Programs\Python\Python313\python.exe"


def run_match(opponent, map_name, seed=1):
    """Run a single match and return parsed results."""
    cmd = [PYTHON, "-c", "from cambc.cli import main; main()",
           "run", BUZZING, opponent, map_name, "--seed", str(seed)]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            cwd=CWD, timeout=120
        )
        output = proc.stdout
    except subprocess.TimeoutExpired:
        return {"opponent": opponent, "map": map_name, "winner": "TIMEOUT",
                "buzzing_ti": 0, "opp_ti": 0, "buzzing_ax": 0, "opp_ax": 0,
                "buzzing_ti_mined": 0, "opp_ti_mined": 0,
                "buzzing_units": 0, "opp_units": 0,
                "buzzing_buildings": 0, "opp_buildings": 0,
                "win_condition": "TIMEOUT", "turn": 0}

    result = {
        "opponent": opponent, "map": map_name, "winner": "UNKNOWN",
        "buzzing_ti": 0, "opp_ti": 0, "buzzing_ax": 0, "opp_ax": 0,
        "buzzing_ti_mined": 0, "opp_ti_mined": 0,
        "buzzing_units": 0, "opp_units": 0,
        "buzzing_buildings": 0, "opp_buildings": 0,
        "win_condition": "", "turn": 0
    }

    # Parse winner line:  "  Winner: buzzing  (Resources (tiebreak), turn 2000)"
    winner_match = re.search(
        r'Winner:\s+(\S+)\s+\(([^,]+),\s*turn\s+(\d+)\)', output
    )
    if winner_match:
        result["winner"] = winner_match.group(1)
        result["win_condition"] = winner_match.group(2)
        result["turn"] = int(winner_match.group(3))

    # Parse titanium line:  "  Titanium     23638 (20660 mined)    3203 (0 mined)"
    ti_match = re.search(
        r'Titanium\s+(\d+)\s+\((\d+)\s+mined\)\s+(\d+)\s+\((\d+)\s+mined\)', output
    )
    if ti_match:
        result["buzzing_ti"] = int(ti_match.group(1))
        result["buzzing_ti_mined"] = int(ti_match.group(2))
        result["opp_ti"] = int(ti_match.group(3))
        result["opp_ti_mined"] = int(ti_match.group(4))

    # Parse axionite line
    ax_match = re.search(
        r'Axionite\s+(\d+)\s+\((\d+)\s+mined\)\s+(\d+)\s+\((\d+)\s+mined\)', output
    )
    if ax_match:
        result["buzzing_ax"] = int(ax_match.group(1))
        result["opp_ax"] = int(ax_match.group(3))

    # Parse units line:  "  Units                          5                 3"
    units_match = re.search(r'Units\s+(\d+)\s+(\d+)', output)
    if units_match:
        result["buzzing_units"] = int(units_match.group(1))
        result["opp_units"] = int(units_match.group(2))

    # Parse buildings line
    bldg_match = re.search(r'Buildings\s+(\d+)\s+(\d+)', output)
    if bldg_match:
        result["buzzing_buildings"] = int(bldg_match.group(1))
        result["opp_buildings"] = int(bldg_match.group(2))

    return result


def print_results(results):
    """Print summary tables."""
    total = len(results)
    wins = sum(1 for r in results if r["winner"] == BUZZING)
    losses = sum(1 for r in results if r["winner"] != BUZZING and r["winner"] != "UNKNOWN")

    print("\n" + "=" * 70)
    print(f"  BUZZING TEST SUITE RESULTS")
    print(f"  Overall: {wins}W - {total - wins}L  ({100*wins/total:.0f}% win rate)")
    print("=" * 70)

    # Heatmap table: opponent x map
    print(f"\n{'Opponent':<16}", end="")
    for m in MAPS:
        print(f" {m[:10]:>10}", end="")
    print(f" {'W-L':>6}  {'Rate':>5}")
    print("-" * (16 + 11 * len(MAPS) + 14))

    for opp in OPPONENTS:
        opp_results = [r for r in results if r["opponent"] == opp]
        opp_wins = sum(1 for r in opp_results if r["winner"] == BUZZING)
        print(f"{opp:<16}", end="")
        for m in MAPS:
            match = next((r for r in opp_results if r["map"] == m), None)
            if match:
                marker = "  W" if match["winner"] == BUZZING else "  L"
                if match["win_condition"] == "Core destroyed":
                    marker += "!"  # core kill
                print(f" {marker:>10}", end="")
            else:
                print(f" {'?':>10}", end="")
        rate = 100 * opp_wins / len(opp_results) if opp_results else 0
        print(f" {opp_wins}-{len(opp_results)-opp_wins:>1}  {rate:>4.0f}%")

    # Per-map summary
    print(f"\n{'Map':<16} {'W-L':>6}  {'Rate':>5}")
    print("-" * 30)
    for m in MAPS:
        map_results = [r for r in results if r["map"] == m]
        map_wins = sum(1 for r in map_results if r["winner"] == BUZZING)
        rate = 100 * map_wins / len(map_results) if map_results else 0
        print(f"{m:<16} {map_wins}-{len(map_results)-map_wins:>1}  {rate:>4.0f}%")

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
    loss_results = [r for r in results if r["winner"] != BUZZING]
    if loss_results:
        print(f"\nLOSSES DETAIL:")
        print(f"{'Opponent':<16} {'Map':<16} {'Condition':<24} {'Turn':>5} {'Our Ti':>7} {'Their Ti':>9}")
        print("-" * 80)
        for r in loss_results:
            print(f"{r['opponent']:<16} {r['map']:<16} {r['win_condition']:<24} {r['turn']:>5} "
                  f"{r['buzzing_ti_mined']:>7} {r['opp_ti_mined']:>9}")

    return wins, total


def write_results_md(results, elapsed):
    """Write results to markdown file."""
    total = len(results)
    wins = sum(1 for r in results if r["winner"] == BUZZING)

    lines = []
    lines.append("# Test Suite Results\n")
    lines.append(f"**Date:** {time.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Bot:** {BUZZING}")
    lines.append(f"**Elapsed:** {elapsed:.0f}s")
    lines.append(f"**Overall:** {wins}W - {total-wins}L ({100*wins/total:.0f}% win rate)\n")

    # Heatmap table
    lines.append("## Win/Loss Heatmap\n")
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
        opp_wins = sum(1 for r in opp_results if r["winner"] == BUZZING)
        row = f"| {opp} |"
        for m in MAPS:
            match = next((r for r in opp_results if r["map"] == m), None)
            if match:
                if match["winner"] == BUZZING:
                    cell = "W"
                    if match["win_condition"] == "Core destroyed":
                        cell = "W!"
                else:
                    cell = "**L**"
                    if match["win_condition"] == "Core destroyed":
                        cell = "**L!**"
                row += f" {cell} |"
            else:
                row += " ? |"
        rate = 100 * opp_wins / len(opp_results) if opp_results else 0
        row += f" {opp_wins}-{len(opp_results)-opp_wins} | {rate:.0f}% |"
        lines.append(row)

    # Per-map
    lines.append("\n## Per-Map Win Rate\n")
    lines.append("| Map | W-L | Rate |")
    lines.append("|-----|-----|------|")
    for m in MAPS:
        map_results = [r for r in results if r["map"] == m]
        map_wins = sum(1 for r in map_results if r["winner"] == BUZZING)
        rate = 100 * map_wins / len(map_results) if map_results else 0
        lines.append(f"| {m} | {map_wins}-{len(map_results)-map_wins} | {rate:.0f}% |")

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
    loss_results = [r for r in results if r["winner"] != BUZZING]
    if loss_results:
        lines.append("\n## Losses Detail\n")
        lines.append("| Opponent | Map | Condition | Turn | Our Ti | Their Ti |")
        lines.append("|----------|-----|-----------|------|--------|----------|")
        for r in loss_results:
            lines.append(f"| {r['opponent']} | {r['map']} | {r['win_condition']} | {r['turn']} | "
                         f"{r['buzzing_ti_mined']} | {r['opp_ti_mined']} |")

    return "\n".join(lines)


def main():
    total_matches = len(OPPONENTS) * len(MAPS)
    print(f"Running {total_matches} matches: {BUZZING} vs {len(OPPONENTS)} opponents x {len(MAPS)} maps")
    print()

    results = []
    start = time.time()
    match_num = 0

    for opp in OPPONENTS:
        for map_name in MAPS:
            match_num += 1
            sys.stdout.write(f"  [{match_num}/{total_matches}] {BUZZING} vs {opp} on {map_name}... ")
            sys.stdout.flush()

            t0 = time.time()
            result = run_match(opp, map_name)
            dt = time.time() - t0

            w = "WIN" if result["winner"] == BUZZING else "LOSS"
            cond = result["win_condition"]
            print(f"{w} ({cond}, turn {result['turn']}) [{dt:.1f}s]")

            results.append(result)

    elapsed = time.time() - start
    print(f"\nAll {total_matches} matches completed in {elapsed:.0f}s")

    wins, total = print_results(results)

    # Write markdown results
    md = write_results_md(results, elapsed)
    md_path = CWD + "/research/test_suite_results.md"
    with open(md_path, "w") as f:
        f.write(md)
    print(f"\nResults written to {md_path}")

    # Exit code: 0 if >70% win rate, 1 otherwise
    rate = 100 * wins / total
    if rate >= 70:
        print(f"\nPASS: {rate:.0f}% win rate (target: >70%)")
        sys.exit(0)
    else:
        print(f"\nFAIL: {rate:.0f}% win rate (target: >70%)")
        sys.exit(1)


if __name__ == "__main__":
    main()
