"""Alpha repo/runtime/reports: signal loop point-in-time."""
from __future__ import annotations
import pandas as pd
from src.domains.alpha.config import AlphaConfigModel
from src.domains.alpha.service import momentum_signal
from src.domains.data.repo import ParquetBarRepo


def compute_signals(repo: ParquetBarRepo, symbol: str, cfg: AlphaConfigModel) -> pd.DataFrame:
    bars = repo.load(symbol)
    vals = []
    for i in range(len(bars)):
        t = bars.loc[i, "ts"]
        bars_asof = bars.iloc[: i + 1]
        v = momentum_signal(bars_asof, cfg)
        vals.append({"symbol": symbol, "ts": t, "asof": t, "value": v})
    return pd.DataFrame(vals)
