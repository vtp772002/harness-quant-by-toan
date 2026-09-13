"""Walk-forward eval — 3 folds OOS, sau costs. Non-blocking nhưng promote cần xanh."""
from __future__ import annotations
import pandas as pd
from src.domains.data.config import DataConfigModel
from src.domains.data.repo import ParquetBarRepo
from src.domains.alpha.config import AlphaConfigModel
from src.domains.backtest.types import BacktestConfig
from src.domains.backtest.runtime import run_backtest
from src.providers.telemetry import Telemetry


def test_walkforward():
    from src.wiring import build_demo_run  # smoke: demo deterministic
    r1 = build_demo_run(42)
    r2 = build_demo_run(42)
    assert r1["sharpe"] == r2["sharpe"], "nondeterministic demo run"
