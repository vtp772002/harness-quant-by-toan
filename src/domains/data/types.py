from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


class Bar(BaseModel):
    symbol: str
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = Field(ge=0)


class Listing(BaseModel):
    """Thanh vien universe la ham cua t — chong survivorship bias."""
    symbol: str
    list_ts: datetime
    delist_ts: datetime | None = None


class SplitAction(BaseModel):
    symbol: str
    ts: datetime
    ratio: float = Field(gt=0)
