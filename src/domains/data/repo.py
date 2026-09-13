"""Repo: chi doc point-in-time. Khong tinh toan o day."""
from __future__ import annotations
from datetime import datetime
import pandas as pd
from src.domains.data.config import DataConfigModel
from src.domains.data.types import Listing


class ParquetBarRepo:
    def __init__(self, cfg: DataConfigModel, df: pd.DataFrame | None = None):
        self.cfg = cfg
        self._df = df

    def load(self, symbol: str) -> pd.DataFrame:
        if self._df is not None:
            df = self._df
        else:
            df = pd.read_parquet(f"{self.cfg.root}/{symbol}.parquet")
        df = df.sort_values("ts").reset_index(drop=True)
        return df

    def get_asof(self, symbol: str, t: datetime) -> pd.DataFrame:
        """Chi tra rows co ts <= t. Day la bien no-lookahead."""
        df = self.load(symbol)
        return df[df["ts"] <= t].copy()


class UniverseRepo:
    """Universe la ham cua t. Delist la exclusive: t < delist_ts."""

    def __init__(self, listings: list[Listing]):
        self._listings = listings

    def get_members(self, t: datetime) -> list[str]:
        out = [l.symbol for l in self._listings if l.list_ts <= t and (l.delist_ts is None or t < l.delist_ts)]
        return sorted(out)
