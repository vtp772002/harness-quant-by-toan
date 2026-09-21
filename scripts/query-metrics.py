"""Query metrics using a boring PromQL-like interface."""
from __future__ import annotations
import argparse, json, os
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--metric", default="sharpe")
p.add_argument("--run", default=os.environ.get("QUANT_RUN_ID", "local"))
a = p.parse_args()
fp = Path("runs") / a.run / "metrics.jsonl"
if not fp.exists():
    print(f"no metrics at {fp}"); raise SystemExit(0)
for line in fp.read_text().splitlines():
    o = json.loads(line)
    if o.get("metric") == a.metric:
        print(json.dumps(o))
