"""No-lookahead linter (BLOCKING)."""
from __future__ import annotations
import re, sys
from pathlib import Path

PATS = [r"\.shift\(-", r"(?<![\w_])future(?![\w_])", r"(?<![\w_.])lead\(", r"bfill", r"close\[.*\+1\]"]
FAIL = 0
for py in list(Path("src/domains/alpha").rglob("*.py")) + list(Path("src/domains/backtest").rglob("*.py")):
    lines = [ln for ln in py.read_text().splitlines() if "__future__" not in ln]
    txt = "\n".join(lines)
    for pat in PATS:
        if re.search(pat, txt):
            print(f"FAIL {py}: matched `{pat}` — possible lookahead. FIX: use bars_asof (ts<=t) + trailing window only. See docs/NO_LOOKAHEAD.md")
            FAIL = 1
print("no_lookahead OK" if not FAIL else "no_lookahead FAILED")
sys.exit(FAIL)
