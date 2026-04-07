"""Run buzzing against varied opponents on varied maps with varied seeds.
Usage: python test_varied.py [--count N] [--opponent BOT]
"""
import subprocess
import random
import sys
import os

PYTHON = r"C:\Users\rahil\AppData\Local\Programs\Python\Python313\python.exe"
CAMBC_CMD = [PYTHON, "-c", "from cambc.cli import main; main()"]
BATTLECODE_DIR = r"C:\Users\rahil\downloads\battlecode"

# All available test bots
BOTS = ['ladder_eco', 'ladder_rush', 'smart_eco', 'smart_defense',
        'balanced', 'sentinel_spam', 'rusher', 'fast_expand', 'adaptive',
        'barrier_wall', 'turtle',
        'ladder_mergeconflict', 'ladder_fast_rush', 'ladder_hybrid_defense']

# Maps categorized by type
TIGHT_MAPS = ['face', 'arena', 'shish_kebab', 'default_small1', 'default_small2']
BALANCED_MAPS = ['default_medium1', 'cold', 'corridors', 'hourglass', 'butterfly',
                 'binary_tree', 'dna', 'gaussian', 'mandelbrot']
EXPAND_MAPS = ['galaxy', 'settlement', 'landscape', 'wasteland', 'tree_of_life',
               'default_large1', 'default_large2', 'pixel_forest']
# All 38 maps from maps/ directory (includes uncategorized ladder maps)
ALL_MAPS = [
    'arena', 'bar_chart', 'battlebot', 'binary_tree', 'butterfly',
    'chemistry_class', 'cinnamon_roll', 'cold', 'corridors', 'cubes',
    'default_large1', 'default_large2', 'default_medium1', 'default_medium2',
    'default_small1', 'default_small2', 'dna', 'face', 'galaxy', 'gaussian',
    'git_branches', 'hooks', 'hourglass', 'landscape', 'mandelbrot',
    'minimaze', 'pixel_forest', 'pls_buy_cucats_merch', 'settlement',
    'shish_kebab', 'sierpinski_evil', 'socket', 'starry_night',
    'thread_of_connection', 'tiles', 'tree_of_life', 'wasteland',
    'wasteland_oasis',
]

def run_match(bot_a, bot_b, map_name, seed=None):
    cmd = CAMBC_CMD + ['run', bot_a, bot_b, map_name]
    if seed:
        cmd += ['--seed', str(seed)]
    result = subprocess.run(cmd, capture_output=True, timeout=120, cwd=BATTLECODE_DIR)
    raw = result.stdout + result.stderr
    for enc in ('utf-8', 'utf-16-le', 'cp1252', 'latin-1'):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode('utf-8', errors='replace')

def main():
    count = int(sys.argv[sys.argv.index('--count') + 1]) if '--count' in sys.argv else 20
    fixed_opponent = sys.argv[sys.argv.index('--opponent') + 1] if '--opponent' in sys.argv else None
    wins, losses, draws = 0, 0, 0
    results = []

    for i in range(count):
        opponent = fixed_opponent if fixed_opponent else random.choice(BOTS)
        map_name = random.choice(ALL_MAPS)
        seed = random.randint(1, 10000)

        print(f"Match {i+1}/{count}: buzzing vs {opponent} on {map_name} (seed {seed})")
        try:
            output = run_match('buzzing', opponent, map_name, seed)
        except subprocess.TimeoutExpired:
            print(f"  -> TIMEOUT")
            draws += 1
            results.append((opponent, map_name, seed, 'TIMEOUT'))
            continue

        # Parse winner - check for 'buzzing' win vs buzzing_prev confusion
        winner_line = ''
        for line in output.splitlines():
            if 'Winner:' in line:
                winner_line = line
                break

        if 'Winner: buzzing' in winner_line and 'buzzing_prev' not in winner_line and 'buzzing_v' not in winner_line:
            wins += 1
            result = 'WIN'
        elif 'Winner:' in winner_line and winner_line.strip() != '':
            losses += 1
            result = 'LOSS'
        else:
            draws += 1
            result = 'DRAW'

        results.append((opponent, map_name, seed, result))
        print(f"  -> {result} ({wins}W-{losses}L)")

    total_decided = wins + losses
    win_rate_str = f"{wins/total_decided*100:.0f}%" if total_decided > 0 else "N/A"
    print(f"\nFinal: {wins}W-{losses}L-{draws}D ({win_rate_str} win rate)")

    # Write results
    os.makedirs('research', exist_ok=True)
    with open('research/varied_test_results.md', 'w') as f:
        f.write(f"# Varied Test Results\n")
        f.write(f"Record: {wins}W-{losses}L-{draws}D ({win_rate_str})\n\n")
        f.write("| # | Opponent | Map | Seed | Result |\n")
        f.write("|---|----------|-----|------|--------|\n")
        for i, (opp, m, s, r) in enumerate(results):
            f.write(f"| {i+1} | {opp} | {m} | {s} | {r} |\n")

if __name__ == '__main__':
    main()
