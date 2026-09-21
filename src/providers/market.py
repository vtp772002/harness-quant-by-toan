"""DataVendor and ExchangeSim protocols; parse at the boundary with Pydantic."""
from __future__ import annotations

import math
from typing import Protocol
from pydantic import BaseModel
import pandas as pd


class DataVendor(Protocol):
    def load_bars(self, symbol: str) -> pd.DataFrame: ...


class ExchangeSim(Protocol):
    def apply_costs(self, price: float, qty: float, fee_bps: float, slippage_bps: float) -> float: ...


class SimpleExchangeSim:
    def apply_costs(self, price: float, qty: float, fee_bps: float, slippage_bps: float) -> float:
        cost_rate = (fee_bps + slippage_bps) / 10_000.0
        if qty > 0:
            return price * (1 + cost_rate)
        return price * (1 - cost_rate)


class RegimeCostConfig(BaseModel):
    fee_bps: float = 2.0
    base_spread_bps: float = 5.0
    impact_k: float = 50.0


class RegimeCostModel:
    """Slip phu thuoc vol-regime + participation. Thuan, deterministic."""

    def __init__(self, cfg: RegimeCostConfig | None = None):
        self.cfg = cfg or RegimeCostConfig()

    def total_bps(self, volume: float, vol_ratio: float, qty: float, stress_m: float = 1.0) -> tuple[float, float]:
        part = abs(qty) / max(volume, 1e-9)
        vr = min(max(vol_ratio, 0.0), 4.0)
        slip = (self.cfg.base_spread_bps * (1 + 2 * vr) + self.cfg.impact_k * math.sqrt(part)) * stress_m
        return (float(slip), float(self.cfg.fee_bps))
