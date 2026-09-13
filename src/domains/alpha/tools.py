"""Deterministic indicator + structure tools. Pure, PIT-safe: chi nhan bars_asof (ts<=t).
Khong TA-Lib — pandas-only de giu boring deps. Moi ham dung trailing data, khong bao gio
nhin qua bar cuoi cua input.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    d = close.diff()
    up = d.clip(lower=0.0)
    dn = -d.clip(upper=0.0)
    ru = up.ewm(alpha=1.0 / window, min_periods=window, adjust=False).mean()
    rd = dn.ewm(alpha=1.0 / window, min_periods=window, adjust=False).mean()
    rs = ru / rd.replace(0.0, np.nan)
    return (100.0 - 100.0 / (1.0 + rs)).fillna(50.0)


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    f = close.ewm(span=fast, adjust=False).mean()
    s = close.ewm(span=slow, adjust=False).mean()
    m = f - s
    sig = m.ewm(span=signal, adjust=False).mean()
    return pd.DataFrame({"macd": m, "signal": sig, "hist": m - sig})


def stoch(df: pd.DataFrame, window: int = 14, smooth: int = 3) -> pd.DataFrame:
    lo = df["low"].rolling(window).min()
    hi = df["high"].rolling(window).max()
    denom = (hi - lo).replace(0.0, np.nan)
    k = (100.0 * (df["close"] - lo) / denom).fillna(50.0)
    return pd.DataFrame({"k": k, "d": k.rolling(smooth).mean().fillna(50.0)})


def roc(close: pd.Series, window: int = 10) -> pd.Series:
    return (100.0 * (close / close.shift(window) - 1.0)).fillna(0.0)


def willr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    hi = df["high"].rolling(window).max()
    lo = df["low"].rolling(window).min()
    denom = (hi - lo).replace(0.0, np.nan)
    return (-100.0 * (hi - df["close"]) / denom).fillna(-50.0)


def atr(df: pd.DataFrame, window: int = 14) -> pd.Series:
    pc = df["close"].shift(1)
    tr = pd.concat([(df["high"] - df["low"]).abs(),
                    (df["high"] - pc).abs(),
                    (df["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(window).mean()


def range_position(bars_asof: pd.DataFrame, window: int = 20) -> float:
    """Vi tri close hien tai trong range trailing (loai bar hien tai khoi range). 0..1."""
    hist = bars_asof.iloc[:-1].tail(window)
    if len(hist) < 2:
        return 0.5
    lo, hi = float(hist["low"].min()), float(hist["high"].max())
    if hi <= lo:
        return 0.5
    c = float(bars_asof.iloc[-1]["close"])
    return float(max(0.0, min(1.0, (c - lo) / (hi - lo))))


def breakout(bars_asof: pd.DataFrame, window: int = 20) -> str:
    """Close hien tai vuot range trailing (loai bar hien tai) → up/down/none."""
    hist = bars_asof.iloc[:-1].tail(window)
    if len(hist) < 2:
        return "none"
    c = float(bars_asof.iloc[-1]["close"])
    if c > float(hist["high"].max()):
        return "up"
    if c < float(hist["low"].min()):
        return "down"
    return "none"


def engulfing(bars_asof: pd.DataFrame) -> str:
    """Nen nhan chim 2-bar cuoi: bull/bear/none."""
    if len(bars_asof) < 2:
        return "none"
    p, c = bars_asof.iloc[-2], bars_asof.iloc[-1]
    bull = c["close"] > c["open"] and p["close"] < p["open"] and c["open"] <= p["close"] and c["close"] >= p["open"]
    if bull:
        return "bull"
    bear = c["close"] < c["open"] and p["close"] > p["open"] and c["open"] >= p["close"] and c["close"] <= p["open"]
    return "bear" if bear else "none"


def trend_slope(bars_asof: pd.DataFrame, window: int = 30) -> tuple[float, float]:
    """Slope (bps/bar) + R2 cua fit tuyen tinh tren log close trailing. Chi dung qua khu."""
    hist = bars_asof.tail(window + 1)
    if len(hist) < 5:
        return (0.0, 0.0)
    y = np.log(hist["close"].to_numpy(dtype=float))
    x = np.arange(len(y), dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    pred = slope * x + intercept
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float(((y - pred) ** 2).sum()) / ss_tot if ss_tot > 0 else 0.0
    return (float(slope * 10_000.0), float(r2))
