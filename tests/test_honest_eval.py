"""Tests cho honest-eval stack: PIT universe, splits, purged gaps, DSR, costs, gate."""
from __future__ import annotations

from datetime import datetime, timezone


def _market(seed=42):
    from src.domains.data.synthetic import make_synthetic_market
    return make_synthetic_market(seed)


def test_universe_pit():
    from src.domains.data.repo import UniverseRepo
    m = _market()
    u = UniverseRepo(m.listings)
    d0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    d100 = datetime(2024, 4, 10, tzinfo=timezone.utc)
    d250 = datetime(2024, 9, 7, tzinfo=timezone.utc)
    assert "BBB" not in u.get_members(d0) and "AAA" in u.get_members(d0)
    assert "CCC" in u.get_members(d100) and "CCC" not in u.get_members(d250)


def test_split_adjustment_continuity():
    from src.domains.data.service import apply_splits
    m = _market()
    adj = apply_splits(m.panel, m.splits)
    a = adj[adj.symbol == "AAA"].sort_values("ts").reset_index(drop=True)
    before = a.loc[149, "close"] / a.loc[150, "close"]
    raw = m.panel[m.panel.symbol == "AAA"].sort_values("ts").reset_index(drop=True)
    assert abs(before - 1.0) < 0.05  # lien tuc qua split (sai so 1 ngay return)
    assert abs(raw.loc[149, "close"] / raw.loc[150, "close"] - 2.0) < 0.05  # raw gap 2:1


def test_purged_gaps():
    from evals.purged_cv import purged_embargo_splits
    for train, test in purged_embargo_splits(756, 3, 21, 5):
        a, b = min(test), max(test)
        assert all(i < a - 21 or i > b + 5 for i in train)
        assert len(train) > 0 and len(test) == 756 // 3


def test_phi_inv_roundtrip():
    from evals.deflated_sharpe import phi, phi_inv
    for p in (0.025, 0.5, 0.975, 0.999):
        assert abs(phi(phi_inv(p)) - p) < 1e-9


def test_dsr_known_values():
    from evals.deflated_sharpe import deflated_sharpe
    strong = deflated_sharpe(0.12, 500, 0.0, 3.0, 0.0004, 3)
    assert strong > 0.95
    zero = deflated_sharpe(0.0, 500, 0.0, 3.0, 0.0004, 3)
    assert zero < 0.5


def test_cost_monotonic_and_deterministic():
    from src.providers.market import RegimeCostModel
    c = RegimeCostModel()
    s1, _ = c.total_bps(100_000, 1.0, 10.0)
    s2, _ = c.total_bps(100_000, 1.0, 1000.0)
    s3, _ = c.total_bps(100_000, 3.0, 10.0)
    assert s2 > s1 and s3 > s1
    assert c.total_bps(100_000, 1.0, 10.0) == c.total_bps(100_000, 1.0, 10.0)


def test_gate_deterministic_and_passes():
    from evals.gate import run_gate
    from src.providers.telemetry import Telemetry
    import tempfile
    from pathlib import Path
    r1 = run_gate(42, Telemetry(Path(tempfile.mkdtemp())))
    r2 = run_gate(42, Telemetry(Path(tempfile.mkdtemp())))
    assert r1 == r2
    assert r1["verdict"] == "PASS", r1


def test_gate_stress_ordering():
    from evals.gate import run_gate
    from src.providers.telemetry import Telemetry
    import tempfile
    from pathlib import Path
    r = run_gate(42, Telemetry(Path(tempfile.mkdtemp())))
    assert r["sharpe_oos"] >= r["stress_x2"] >= r["stress_x5"]
