"""Synthetic market — deterministic, co survivorship-stress + 1 split.
Chi dung cho harness smoke / eval dev. PASS o day = plumbing dung, khong phai alpha that.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import pandas as pd
from src.domains.data.types import Listing, SplitAction
from src.utils.rng_logging import seeded_rng


@dataclass
class SyntheticMarket:
    panel: pd.DataFrame
    listings: list[Listing]
    splits: list[SplitAction]


def make_synthetic_market(seed: int = 42, n_days: int = 756) -> SyntheticMarket:
    rng = seeded_rng(seed)
    dates = [datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(days=i) for i in range(n_days)]
    specs = [("AAA", 0, None), ("BBB", 30, None), ("CCC", 60, 200), ("DDD", 0, None)]
    rows: list[dict] = []
    listings: list[Listing] = []
    for sym, start, end in specs:
        last = n_days if end is None else end
        px, prev_r = 100.0, 0.0
        for i in range(start, last):
            eps = float(rng.normal())
            r = 0.0012 + 0.3 * prev_r + 0.01 * eps
            prev_r = r
            px = px * (1 + r)
            raw = px * (2.0 if (sym == "AAA" and i < 150) else 1.0)
            vol = int(100_000 * (1 + 5 * abs(eps)) + int(rng.integers(0, 5000)))
            rows.append({"symbol": sym, "ts": dates[i], "open": raw, "high": raw * 1.002,
                         "low": raw * 0.998, "close": raw, "volume": vol})
        listings.append(Listing(symbol=sym, list_ts=dates[start],
                                delist_ts=dates[end] if end is not None else None))
    panel = pd.DataFrame(rows).sort_values(["ts", "symbol"]).reset_index(drop=True)
    return SyntheticMarket(panel=panel, listings=listings,
                           splits=[SplitAction(symbol="AAA", ts=dates[150], ratio=2.0)])
