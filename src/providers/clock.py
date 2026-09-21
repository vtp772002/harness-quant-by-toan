"""Clock provider — the only place allowed to read the wall clock."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class SimulatedClock:
    def __init__(self, start: datetime):
        self._t = start

    def now(self) -> datetime:
        return self._t

    def advance(self, t: datetime) -> None:
        self._t = t
