"""Garbage collection: quét hand-rolled helpers trùng utils + YOLO probing."""
from __future__ import annotations
import re
from pathlib import Path

hits = []
for py in Path("src").rglob("*.py"):
    if "utils/" in str(py):
        continue
    txt = py.read_text()
    if re.search(r"ThreadPoolExecutor|multiprocessing\.Pool", txt):
        hits.append(f"{py}: hand-rolled concurrency — dùng src/utils/concurrency.map_with_concurrency")
    if re.search(r"requests\.get\(.*\.json\(\)\[", txt):
        hits.append(f"{py}: YOLO probing shape — parse at boundary bằng Pydantic")
print("\n".join(hits) if hits else "gc clean")
