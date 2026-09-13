"""Map-with-concurrency — ban boring thay p-limit, instrumented, 100% tested."""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def map_with_concurrency(
    fn: Callable[[T], R],
    items: Iterable[T],
    *,
    max_workers: int = 8,
    span_name: str = "map_with_concurrency",
    telemetry=None,
) -> list[R]:
    items = list(items)
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        out = list(ex.map(fn, items))
    dt_ms = (time.perf_counter() - t0) * 1000
    if telemetry is not None:
        telemetry.emit_span(span_name, duration_ms=dt_ms, n=len(items))
    return out
