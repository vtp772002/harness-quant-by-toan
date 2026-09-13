"""Telemetry legible cho agent: append-only JSONL per-worktree."""
from __future__ import annotations

import json
import os
from pathlib import Path


def _run_dir() -> Path:
    run_id = os.environ.get("QUANT_RUN_ID", "local")
    p = Path("runs") / run_id
    p.mkdir(parents=True, exist_ok=True)
    return p


class Telemetry:
    def __init__(self, run_dir: Path | None = None):
        self.run_dir = run_dir or _run_dir()

    @staticmethod
    def noop() -> "Telemetry":
        import tempfile
        return Telemetry(Path(tempfile.mkdtemp()))

    def _append(self, fname: str, payload: dict) -> None:
        with open(self.run_dir / fname, "a") as f:
            f.write(json.dumps(payload, default=str) + "\n")

    def log(self, level: str, event: str, **fields) -> None:
        self._append("logs.jsonl", {"level": level, "event": event, **fields})

    def metric(self, name: str, value: float, **labels) -> None:
        self._append("metrics.jsonl", {"metric": name, "value": value, **labels})

    def emit_span(self, name: str, duration_ms: float, **fields) -> None:
        self._append("traces.jsonl", {"span": name, "duration_ms": duration_ms, **fields})
