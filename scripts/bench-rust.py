"""Benchmark Python versus the Rust core for conformance and speedup.

Inputs are dumped once and reused across configurations for a fair comparison.
Rust is skipped automatically when the release binary has not been built.
"""
from __future__ import annotations
import tempfile
import time
from pathlib import Path
import numpy as np
from src.domains.data.service import apply_splits
from src.domains.data.synthetic import make_synthetic_market
from src.domains.data.repo import UniverseRepo
from src.providers.market import RegimeCostModel
from evals.gate import panel_backtest, CANDIDATE_LOOKBACKS

mkt = make_synthetic_market(42)
panel = apply_splits(mkt.panel, mkt.splits)
universe = UniverseRepo(mkt.listings)
cost = RegimeCostModel()

from evals.rust_core import binary_path, dump_inputs, run_rust_backtest
has_rust = binary_path() is not None
print(f"rust backend: {'FOUND ' + str(binary_path()) if has_rust else 'MISSING (cargo build --release -p quant-core)'}")
shared = Path(tempfile.mkdtemp())
if has_rust:
    t0 = time.perf_counter()
    dump_inputs(panel, universe, shared)
    print(f"csv dump once: {(time.perf_counter() - t0) * 1000:.0f} ms")
for lb in CANDIDATE_LOOKBACKS:
    t0 = time.perf_counter()
    eq_py, _ = panel_backtest(panel, universe, lb, cost, 1.0)
    dt_py = time.perf_counter() - t0
    if has_rust:
        t0 = time.perf_counter()
        eq_rs, _ = run_rust_backtest(panel, universe, lb, cost, 1.0, d=shared)
        dt_rs = time.perf_counter() - t0
        diff = float(np.abs(eq_py["equity"].to_numpy() - eq_rs["equity"].to_numpy()).max())
        print(f"lb={lb}: python={dt_py*1000:.0f}ms rust={dt_rs*1000:.0f}ms "
              f"speedup={dt_py/max(dt_rs,1e-9):.1f}x maxdiff={diff:.3e}")
    else:
        print(f"lb={lb}: python={dt_py*1000:.0f}ms rust=SKIP")
