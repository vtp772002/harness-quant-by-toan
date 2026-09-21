"""Pure point-in-time alpha service using only a trailing window."""
from __future__ import annotations
import pandas as pd
from src.domains.alpha.config import AlphaConfigModel


def momentum_signal(bars_asof: pd.DataFrame, cfg: AlphaConfigModel) -> float:
    """`bars_asof` is filtered to `ts<=t` by the repository."""
    if len(bars_asof) < cfg.lookback + 1:
        return 0.0
    window = bars_asof.tail(cfg.lookback + 1)
    past = window["close"].iloc[0]
    last = window["close"].iloc[-1]
    if past == 0:
        return 0.0
    ret = (last - past) / past
    return float(max(-1.0, min(1.0, ret * 10)))
