from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class Signal(BaseModel):
    symbol: str
    ts: datetime
    asof: datetime
    value: float
