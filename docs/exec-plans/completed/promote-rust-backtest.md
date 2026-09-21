# Exec plan — promote Rust backtest backend

## Objective

Use the existing Rust hot loop for CLI evaluation while preserving Python as
the reference oracle and deterministic fallback.

## Baseline

- Python panel loop: 145–171 ms per candidate on the synthetic panel.
- Rust panel loop: 25–32 ms per candidate.
- Existing conformance max equity difference: 2.328e-10.
- Python gate result for seed 42: PASS, OOS Sharpe 2.250929254379804.

## Scope

- Add explicit `python`, `rust`, and `auto` backend selection.
- Make `scripts/run-eval.py` use `auto`, preferring Rust when the release
  binary exists and falling back to Python when it does not.
- Keep direct `evals.gate.run_gate()` Python-default for reference tests.
- Reuse one CSV input dump per stress run rather than dumping for every
  candidate lookback.
- Add backend identity and Rust-vs-Python proof to the blocking scorecard.

## Non-goals

- No LLM, pandas/Pydantic boundary, or report rewrite.
- No PyO3 dependency before process-boundary overhead is shown to matter.
- No removal of Python reference code.

## Acceptance criteria

- `run-eval.py --backend rust` passes and reports `backend: rust`.
- Rust and Python gate outputs pass conformance within the existing tolerance.
- Missing Rust binary makes `auto` fall back to Python but explicit `rust` fail
  clearly.
- Seed 42 gate remains PASS and all baseline tests remain green.

## Status

Completed 2026-09-21; move this plan to `docs/exec-plans/completed/` after the
final validation run.
