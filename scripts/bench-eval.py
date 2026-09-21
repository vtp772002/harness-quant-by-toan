"""Benchmark the baseline and separate stages to size the hot loop.

Run with: PYTHONPATH=. python scripts/bench-eval.py [--seed 42]
"""
from __future__ import annotations
import argparse, time
from src.domains.data.service import apply_splits
from src.domains.data.synthetic import make_synthetic_market
from src.domains.data.repo import UniverseRepo
from src.providers.market import RegimeCostModel
from evals.gate import panel_backtest, CANDIDATE_LOOKBACKS

p = argparse.ArgumentParser()
p.add_argument("--seed", type=int, default=42)
a = p.parse_args()

t0 = time.perf_counter()
mkt = make_synthetic_market(a.seed)
t_gen = time.perf_counter() - t0

t0 = time.perf_counter()
panel = apply_splits(mkt.panel, mkt.splits)
universe = UniverseRepo(mkt.listings)
cost = RegimeCostModel()
t_prep = time.perf_counter() - t0

loop_total = 0.0
for lb in CANDIDATE_LOOKBACKS:
    t0 = time.perf_counter()
    panel_backtest(panel, universe, lb, cost, 1.0)
    dt = time.perf_counter() - t0
    loop_total += dt
    print(f"panel_backtest lookback={lb}: {dt * 1000:.0f} ms")
print(f"synthetic gen: {t_gen * 1000:.0f} ms")
print(f"prep (splits+universe): {t_prep * 1000:.0f} ms")
print(f"panel loop total (3 lbs): {loop_total * 1000:.0f} ms")
print(f"gate full ~ x{1 + 2} (m=1 + stress x2/x5): ~{loop_total * 3 * 1000:.0f} ms + selection")
