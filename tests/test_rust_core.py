"""Rust core must match the Python reference within equity and metadata tolerances.

Skip when the binary is not built; the Python reference remains the gate source
of truth.
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
        pytest.skip("quant-core binary is not built")
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


def test_rust_gate_matches_python_reference():
    import math
    from evals.gate import run_gate
    _require_bin()
    py = run_gate(42, backend="python")
    rs = run_gate(42, backend="rust")
    assert rs["backend"] == "rust"
    assert rs["verdict"] == py["verdict"] == "PASS"
    assert rs["picks"] == py["picks"]
    for key in ("sharpe_oos", "dsr", "stress_x2", "stress_x5", "max_dd"):
        assert math.isclose(rs[key], py[key], rel_tol=1e-9, abs_tol=1e-9), key


def test_auto_fallback_and_explicit_rust_fail_closed(monkeypatch):
    import evals.rust_core as rust_core
    from evals.gate import _resolve_backend
    monkeypatch.setattr(rust_core, "binary_path", lambda: None)
    assert _resolve_backend("auto") == "python"
    with pytest.raises(FileNotFoundError):
        _resolve_backend("rust")
