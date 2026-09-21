# 0005 — Promote Rust for CLI backtest evaluation

- Ngay: 2026-09-21. Trang thai: accepted.

## Context

`crates/quant-core` already mirrors `evals.gate.panel_backtest`, with a measured
5.4–5.9x speedup and maximum equity difference of 2.328e-10. It was previously
dev/bench/conformance-only, so the normal CLI gate still paid the Python panel
loop cost for every candidate and stress multiplier.

## Decision

1. Keep Python `panel_backtest` as the reference implementation.
2. Add an explicit backend contract: `python`, `rust`, or `auto`.
3. `run-eval.py` defaults to `auto`; it prefers Rust when the release binary is
   present and falls back to Python when unavailable.
4. Explicit `rust` is fail-closed when the binary is missing.
5. Conformance and scorecard remain blocking evidence; no Python reference is
   deleted.

## Consequences

- Normal CLI evaluation gains the Rust hot-loop path without changing strategy
  semantics or the Python research surface.
- CI must build the Rust quant core before running the blocking gate.
- CSV process-boundary cost remains; PyO3 is deferred until a real workload
  shows that boundary is material.
