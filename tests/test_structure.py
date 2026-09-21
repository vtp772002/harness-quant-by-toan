"""Structural tests that mirror linters for fast local failure."""
from __future__ import annotations
import subprocess, sys


def test_linters_pass():
    r = subprocess.run([sys.executable, "linters/run_all.py"])
    assert r.returncode == 0, "linters failed"


def test_determinism():
    from src.wiring import build_demo_run
    a = build_demo_run(7)["equity"]["equity"].tolist()
    b = build_demo_run(7)["equity"]["equity"].tolist()
    assert a == b


def test_no_lookahead_spot():
    import pandas as pd
    from datetime import datetime, timezone
    from src.domains.data.config import DataConfigModel
    from src.domains.data.repo import ParquetBarRepo
    df = pd.DataFrame({
        "symbol": ["A"] * 5,
        "ts": [datetime(2024, 1, i + 1, tzinfo=timezone.utc) for i in range(5)],
        "open": [1, 2, 3, 4, 5], "high": [1, 2, 3, 4, 5],
        "low": [1, 2, 3, 4, 5], "close": [1, 2, 3, 4, 5], "volume": [1] * 5,
    })
    repo = ParquetBarRepo(DataConfigModel(), df)
    asof = repo.get_asof("A", datetime(2024, 1, 3, tzinfo=timezone.utc))
    assert len(asof) == 3 and (asof["ts"] <= datetime(2024, 1, 3, tzinfo=timezone.utc)).all()
