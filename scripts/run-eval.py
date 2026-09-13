"""CLI gate trung thuc: python scripts/run-eval.py --seed 42 (can PYTHONPATH=.)"""
from __future__ import annotations
import argparse, json
from evals.gate import run_gate

p = argparse.ArgumentParser()
p.add_argument("--seed", type=int, default=42)
a = p.parse_args()
print(json.dumps(run_gate(seed=a.seed), indent=2, default=str))
