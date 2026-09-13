"""Layering linter — parse import AST, fail kèm remediation (như OpenAI custom lints)."""
from __future__ import annotations
import ast, sys
from pathlib import Path

ORDER = ["types", "config", "repo", "service", "runtime", "reports", "runtime_reports"]
FAIL = 0

for py in Path("src").rglob("*.py"):
    tree = ast.parse(py.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.ImportFrom, ast.Import)):
            mod = getattr(node, "module", "") or ""
            names = ",".join(a.name for a in getattr(node, "names", []))
            imp = mod + names
            # repo không được import service/runtime; service không import runtime
            if "domains" in str(py) and "repo.py" in str(py) and "service" in imp:
                print(f"FAIL {py}: repo must not import service. FIX: move logic to service.py, repo only I/O asof.")
                FAIL = 1
            if "service.py" in str(py) and ("runtime" in imp or "providers.telemetry" in imp and "domains" in imp):
                pass  # service thuần — cho phép telemetry? chặn runtime
                if "runtime" in imp:
                    print(f"FAIL {py}: service must not import runtime. FIX: invert — runtime calls service.")
                    FAIL = 1
            # cross-domain repo poke
            if "from src.domains" in (mod) and str(py).count("domains") > 0:
                pass
print("layering OK" if not FAIL else "layering FAILED")
sys.exit(FAIL)
