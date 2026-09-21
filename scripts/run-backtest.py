"""Run the demo backtest with agent-readable output."""
from __future__ import annotations
import argparse, json
from src.wiring import build_demo_run
from src.domains.backtest.reports import summarize

p = argparse.ArgumentParser()
p.add_argument("--seed", type=int, default=42)
a = p.parse_args()
res = build_demo_run(seed=a.seed)
print(json.dumps(summarize(res), indent=2, default=str))
