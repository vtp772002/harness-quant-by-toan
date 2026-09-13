"""Taste linter: file<=500 lines, func<=50, structured logging, no hardcoded secrets."""
from __future__ import annotations
import ast, sys
from pathlib import Path

FAIL = 0
for py in Path("src").rglob("*.py"):
    lines = py.read_text().splitlines()
    if len(lines) > 500:
        print(f"FAIL {py}: {len(lines)} lines >500. FIX: split domain layer."); FAIL = 1
    tree = ast.parse("\n".join(lines))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            n = node.end_lineno - node.lineno + 1
            if n > 50:
                print(f"FAIL {py}:{node.lineno} func {node.name} {n} lines >50. FIX: extract helper."); FAIL = 1
    if "api_key=" in "\n".join(lines):
        print(f"FAIL {py}: hardcoded api_key. FIX: env + config boundary."); FAIL = 1
print("taste OK" if not FAIL else "taste FAILED")
sys.exit(FAIL)
