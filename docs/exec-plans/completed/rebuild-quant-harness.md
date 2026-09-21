# Exec plan — rebuild quantitative research harness

## Objective

Provide one cross-platform, agent-legible control plane for quantitative
research while preserving the existing Python reference implementation.

## Scope

- Rust CLI owns repository discovery, doctor checks, run manifests, and the
  validation contract.
- Bash and PowerShell are thin adapters with the same commands.
- Python remains the smallest possible layer for pandas/Pydantic research
  logic, evaluation, and scorecard calculations.
- No live trading, broker credentials, LLM orchestration, or data-vendor
  policy is introduced.

## Acceptance criteria

- `scripts/quant-harness.sh doctor` and the PowerShell equivalent validate the
  required repository contract.
- `boot` records run id, seed, git SHA, and harness version in a manifest.
- `check --seed 42` runs lint, tests, honest-eval, and scorecard with the
  Python plugin environment made explicit.
- A failed stage stops the pipeline and reports a machine-readable status.
- Rust unit tests include positive and negative contract proofs.
- Existing Python gate results remain unchanged for seed 42.

## Progress (completed 2026-09-21)

- [x] Record baseline and inspect authoritative docs.
- [x] Add Rust control plane and cross-platform adapters.
- [x] Add contract tests and decision record.
- [x] Rerun full validation and update docs/tech debt.
- [x] Add curl bootstrap installer with merge/dry-run/override boundaries.
