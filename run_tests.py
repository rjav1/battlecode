"""Run v28 test suite and print results."""
import subprocess
import sys

PYTHON = r"C:\Users\rahil\AppData\Local\Programs\Python\Python313\python.exe"
TESTS = [
    ("buzzing", "buzzing_prev", "galaxy"),
    ("buzzing_prev", "buzzing", "galaxy"),
    ("buzzing", "buzzing_prev", "arena"),
    ("buzzing_prev", "buzzing", "arena"),
    ("buzzing", "buzzing_prev", "default_medium1"),
    ("buzzing_prev", "buzzing", "default_medium1"),
]

results = []
for p1, p2, mapname in TESTS:
    print(f"\n--- {p1} vs {p2} on {mapname} ---", flush=True)
    result = subprocess.run(
        [PYTHON, "-c", "from cambc.cli import main; main()", "run", p1, p2, mapname],
        capture_output=True,
        cwd=r"C:\Users\rahil\downloads\battlecode",
    )
    raw = result.stdout + result.stderr
    # Try multiple encodings
    for enc in ("utf-8", "utf-16-le", "cp1252", "latin-1"):
        try:
            output = raw.decode(enc)
            break
        except Exception:
            continue
    else:
        output = raw.decode("latin-1")
    print(output, flush=True)
    results.append((p1, p2, mapname, output))

print("\n\n=== SUMMARY ===")
wins = 0
for p1, p2, mapname, output in results:
    winner_line = [l for l in output.splitlines() if "Winner" in l]
    if winner_line:
        print(f"{p1} vs {p2} on {mapname}: {winner_line[0].strip()}")
        if "buzzing" in winner_line[0] and "buzzing_prev" not in winner_line[0].split("Winner")[1].split("(")[0]:
            wins += 1
    else:
        print(f"{p1} vs {p2} on {mapname}: NO WINNER LINE FOUND")
        print("  Raw:", repr(output[:200]))

print(f"\nTotal wins for buzzing (new): {wins}/6")
