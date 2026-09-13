from __future__ import annotations
from pydantic import BaseModel


class DataConfigModel(BaseModel):
    root: str = "data/parquet"
