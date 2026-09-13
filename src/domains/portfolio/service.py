"""Portfolio — target sizing boring, deterministic."""
from __future__ import annotations


def size_target(signal_value: float, base_qty: float = 100.0) -> float:
    v = max(-1.0, min(1.0, signal_value))
    return v * base_qty
