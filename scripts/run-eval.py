"""Honest-eval CLI. Rust is preferred when its release binary is available."""
from __future__ import annotations
import argparse, json
from evals.gate import BACKENDS, run_gate

p = argparse.ArgumentParser()
p.add_argument("--seed", type=int, default=42)
p.add_argument("--backend", choices=BACKENDS, default="auto")
a = p.parse_args()
print(json.dumps(run_gate(seed=a.seed, backend=a.backend), indent=2, default=str))
