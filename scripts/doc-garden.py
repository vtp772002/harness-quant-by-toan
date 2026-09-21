"""Doc gardening: find stale markers and propose documentation fixes."""
from __future__ import annotations
from pathlib import Path

issues = []
for md in Path("docs").rglob("*.md"):
    txt = md.read_text()
    if "TODO" in txt or "TBD" in txt:
        issues.append(f"{md}: contains TODO/TBD — encode the decision or move it to tech-debt-tracker.md")
print("\n".join(issues) if issues else "docs fresh — no stale markers")
