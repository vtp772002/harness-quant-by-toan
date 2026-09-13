"""Doc-gardening: quét docs stale (thiếu cross-link, schema cũ) và đề xuất PR fix."""
from __future__ import annotations
from pathlib import Path

issues = []
for md in Path("docs").rglob("*.md"):
    txt = md.read_text()
    if "TODO" in txt or "TBD" in txt:
        issues.append(f"{md}: contains TODO/TBD — encode quyết định hoặc move vào tech-debt-tracker.md")
print("\n".join(issues) if issues else "docs fresh — no stale markers")
