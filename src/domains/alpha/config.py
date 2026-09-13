from __future__ import annotations
from pydantic import BaseModel


class AlphaConfigModel(BaseModel):
    lookback: int = 20
    seed: int = 42
