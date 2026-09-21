"""Risk belongs in code, not docs; limits must raise."""
from __future__ import annotations

MAX_POSITION = 1000.0


class RiskBreach(Exception):
    pass


def check_limits(pos: float, target: float, cash: float) -> None:
    if abs(target) > MAX_POSITION:
        raise RiskBreach(f"position {target} > MAX_POSITION {MAX_POSITION}")
    if cash <= 0:
        raise RiskBreach("cash depleted")
