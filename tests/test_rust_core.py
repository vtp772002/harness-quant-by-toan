"""Conformance: Rust core phai khop Python reference (equity 1e-9, fills/turnover).
Skip neu binary chua build — Python reference van la source of truth cho gate.
"""
from __future__ import annotations

from pathlib import Path
import pytest


def _inputs(lb=20):
    from src.domains.data.service import apply_splits
    from src.domains.data.synthetic import make_synthetic_market
    from src.domains.data.repo import UniverseRepo
    from src.providers.market import RegimeCostModel
    mkt = make_synthetic_market(42)
    panel = apply_splits(mkt.panel, mkt.splits)
    return panel, UniverseRepo(mkt.listings), RegimeCostModel(), lb


def _require_bin():
    from evals.rust_core import binary_path
    b = binary_path()
    if b is None:
        pytest.skip("quant-core binary chua build")
    return b


def test_conformance_equity_and_meta():
    import numpy as np
    from evals.gate import panel_backtest
    from evals.rust_core import run_rust_backtest
    _require_bin()
    for lb in (5, 10, 20):
        panel, universe, cost, _ = _inputs(lb)
        eq_py, meta_py = panel_backtest(panel, universe, lb, cost, 1.0)
        eq_rs, meta_rs = run_rust_backtest(panel, universe, lb, cost, 1.0)
        assert np.allclose(eq_py["equity"].to_numpy(), eq_rs["equity"].to_numpy(),
                           rtol=1e-9, atol=1e-9)
        assert meta_rs["fills"] == meta_py["fills"]
        assert abs(meta_rs["turnover"] - meta_py["turnover"]) / max(meta_py["turnover"], 1) < 1e-9


def test_conformance_stress():
    import numpy as np
    from evals.gate import panel_backtest
    from evals.rust_core import run_rust_backtest
    _require_bin()
    panel, universe, cost, _ = _inputs()
    eq_py, _ = panel_backtest(panel, universe, 10, cost, 5.0)
    eq_rs, _ = run_rust_backtest(panel, universe, 10, cost, 5.0)
    assert np.allclose(eq_py["equity"].to_numpy(), eq_rs["equity"].to_numpy(), rtol=1e-9, atol=1e-9)


def test_rust_binary_path_documented():
    assert Path("crates/quant-core/Cargo.toml").exists()
