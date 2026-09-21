"""Agent-layer schemas.

Every agent output is validated by Pydantic before it moves forward. Numeric
values come from deterministic tools; the LLM may add narrative and confidence
but must not change the numbers.
"""
from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class IndicatorValues(BaseModel):
    rsi: float = Field(ge=0, le=100)
    macd: float
    macd_signal: float
    macd_hist: float
    stoch_k: float = Field(ge=0, le=100)
    stoch_d: float = Field(ge=0, le=100)
    roc: float
    willr: float = Field(ge=-100, le=0)
    atr: float = Field(ge=0)


class IndicatorReport(BaseModel):
    symbol: str
    ts: datetime
    asof: datetime
    values: IndicatorValues


class PatternReport(BaseModel):
    symbol: str
    ts: datetime
    asof: datetime
    breakout: Literal["up", "down", "none"]
    engulfing: Literal["bull", "bear", "none"]
    range_position: float = Field(ge=0, le=1)


class TrendReport(BaseModel):
    symbol: str
    ts: datetime
    asof: datetime
    slope_bps: float
    r_squared: float = Field(ge=0, le=1)
    channel_position: float = Field(ge=0, le=1)
    regime: Literal["up", "down", "range"]


class Proposal(BaseModel):
    """The only agent proposal; the gate decides success or failure."""
    symbol: str
    ts: datetime
    asof: datetime
    direction: Literal["long", "short", "flat"]
    confidence: float = Field(ge=0, le=1)
    candidate_lookbacks: list[int] = Field(min_length=1)
    rationale: str
    model: str


class ProposalContext(BaseModel):
    symbol: str
    ts: datetime
    asof: datetime
    indicator: IndicatorReport
    pattern: PatternReport
    trend: TrendReport
    instruction: str = ""
