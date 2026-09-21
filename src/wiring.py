"""Single composition root for wiring providers and domains."""
from __future__ import annotations
import pandas as pd
from src.domains.data.config import DataConfigModel
from src.domains.data.repo import ParquetBarRepo
from src.domains.alpha.config import AlphaConfigModel
from src.domains.backtest.types import BacktestConfig
from src.domains.backtest.runtime import run_backtest
from src.providers.telemetry import Telemetry


def build_demo_run(seed: int = 42) -> dict:
    import numpy as np
    from datetime import datetime, timezone, timedelta
    rng = np.random.default_rng(seed)
    n = 252
    px = 100 + rng.normal(0, 1, n).cumsum()
    ts = [datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(days=i) for i in range(n)]
    df = pd.DataFrame({
        "symbol": "DEMO", "ts": ts,
        "open": px, "high": px + 0.5, "low": px - 0.5,
        "close": px, "volume": 1_000,
    })
    repo = ParquetBarRepo(DataConfigModel(), df)
    tel = Telemetry()
    return run_backtest(repo, "DEMO", BacktestConfig(seed=seed), AlphaConfigModel(), tel)
