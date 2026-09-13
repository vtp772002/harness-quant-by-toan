"""Query logs kiểu LogQL-boring: python scripts/query-logs.py --filter level=ERROR"""
from __future__ import annotations
import argparse, json, os
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--filter", default="")
p.add_argument("--run", default=os.environ.get("QUANT_RUN_ID", "local"))
a = p.parse_args()
fp = Path("runs") / a.run / "logs.jsonl"
if not fp.exists():
    print(f"no logs at {fp}"); raise SystemExit(0)
k, _, v = a.filter.partition("=") if "=" in a.filter else ("", "", "")
for line in fp.read_text().splitlines():
    o = json.loads(line)
    if not a.filter or str(o.get(k)) == v:
        print(json.dumps(o))
