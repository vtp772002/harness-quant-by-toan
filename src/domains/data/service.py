"""Validate the boundary and normalize OHLCV data deterministically."""
from __future__ import annotations
import pandas as pd
from src.domains.data.types import SplitAction


def normalize_bars(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("ts").reset_index(drop=True)
    assert (df["high"] >= df["low"]).all(), "high<low: corrupt bars"
    return df


def apply_splits(panel: pd.DataFrame, actions: list[SplitAction]) -> pd.DataFrame:
    """Back-adjust OHLC before splits using only timestamps."""
    df = panel.copy()
    for a in actions:
        mask = (df["symbol"] == a.symbol) & (df["ts"] < a.ts)
        for col in ("open", "high", "low", "close"):
            df.loc[mask, col] = df.loc[mask, col] / a.ratio
    return df


def trailing_vol(bars_asof: pd.DataFrame, window: int = 20) -> float:
    """Estimate the historical volatility regime, excluding the current bar."""
    hist = bars_asof.iloc[:-1]
    if len(hist) < 5:
        return 0.01
    r = hist["close"].pct_change().dropna().tail(window)
    return float(r.std()) if len(r) > 1 else 0.01
