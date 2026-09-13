from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


class Fill(BaseModel):
    symbol: str
    ts: datetime
    qty: float
    price: float
    fee_bps: float = Field(ge=0)
    slippage_bps: float = Field(ge=0)


class BacktestConfig(BaseModel):
    seed: int = 42
    fee_bps: float = 2.0
    slippage_bps: float = 5.0
    initial_cash: float = 1_000_000.0
