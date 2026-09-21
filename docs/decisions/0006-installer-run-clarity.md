# 0006 — Make Installer and Run Evidence Explicit

- Date: 2026-09-21. Status: accepted.
- Context: installation itself passed, but the user-facing flow was ambiguous.
  Merge mode printed many `preserve` lines without explaining that the target
  already contained the managed files. Dry-run reported an install even when a
  binary would be preserved. Direct checks also wrote metrics to `runs/local`,
  mixing evidence from unrelated runs.

## Baseline

- Linters: PASS.
- Python tests: 27 passed.
- Seed-42 gate: PASS on Rust with Sharpe `2.2509292543797406`, DSR
  `0.9999942897035148`, and stress ×2 `2.093507369754939`.
- Scorecard: PASS (`quant-scorecard-v1`).

## Decision

1. Reject obvious ref placeholders such as `COMMIT_SHA_OR_TAG` before network
   access, with an actionable error.
2. Make installer dry-run output distinguish preserving an existing executable
   from installing a new one.
3. Propagate `--run-id` from the Rust control plane to every Python validation
   stage so logs and metrics stay attached to the requested run.
4. Document that smoke backtests and promotion gates use different datasets and
   answer different questions. Query commands must name the run when history is
   present.

## Consequences

- Copy-pasted placeholder commands fail locally with a clear message instead of
  a raw GitHub 404.
- A `boot --run-id X` followed by `check --run-id X` produces coherent evidence.
- The quant calculation and gate thresholds remain unchanged.
