"""Run a single match and show full output."""
import subprocess
import sys

PYTHON = r"C:\Users\rahil\AppData\Local\Programs\Python\Python313\python.exe"
p1 = sys.argv[1] if len(sys.argv) > 1 else "buzzing"
p2 = sys.argv[2] if len(sys.argv) > 2 else "buzzing_prev"
mapname = sys.argv[3] if len(sys.argv) > 3 else "default_medium1"

result = subprocess.run(
    [PYTHON, "-c", "from cambc.cli import main; main()", "run", p1, p2, mapname],
    capture_output=True,
    cwd=r"C:\Users\rahil\downloads\battlecode",
)
raw = result.stdout + result.stderr
for enc in ("utf-8", "cp1252", "latin-1"):
    try:
        print(raw.decode(enc))
        break
    except Exception:
        continue
