"""Blocking determinism linter for raw clocks and randomness."""
from __future__ import annotations
import re, sys
from pathlib import Path

PATS = [r"random\.random", r"time\.time\(\)", r"datetime\.now\("]
ALLOW = ["providers/clock.py", "utils/rng_logging.py", "linters/"]
FAIL = 0
for py in Path("src").rglob("*.py"):
    if any(a in str(py) for a in ALLOW):
        continue
    txt = py.read_text()
    for pat in PATS:
        if re.search(pat, txt):
            print(f"FAIL {py}: `{pat}` — nondeterminism. FIX: SimulatedClock.now() or seeded_rng(seed). See docs/REPRODUCIBILITY.md")
            FAIL = 1
print("determinism OK" if not FAIL else "determinism FAILED")
sys.exit(FAIL)
