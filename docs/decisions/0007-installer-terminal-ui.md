# 0007 — Add TTY-Aware Installer Progress UI

- Date: 2026-09-22. Status: accepted.
- Context: the curl bootstrap worked, but a user could not tell whether the
  installer was downloading, compiling, or waiting during a longer step.

## Baseline

- Linters: PASS.
- Python tests: 27 passed.
- Seed-42 Rust gate: PASS with Sharpe `2.2509292543797406`.
- Scorecard: PASS (`quant-scorecard-v1`).

## Decision

1. Add a small four-stage installer UI with ANSI color, check marks, and a
   spinner for network and Cargo steps.
2. Enable it automatically only when stdout and stderr are TTYs and the
   terminal is not `dumb`.
3. Keep plain output as the default for CI and redirected logs.
4. Support `NO_COLOR=1`, `HARNESS_INSTALLER_UI=never`, and an explicit
   `HARNESS_INSTALLER_UI=always` override.
5. Keep the installer dependency-free: the UI uses Bash built-ins and standard
   shell utilities already required by the installer.

## Consequences

- Interactive curl installs are easier to understand without changing the
  managed payload or validation contract.
- Failed download/build output is retained and printed after the spinner stops.
- ANSI output is not emitted by default in CI or when output is redirected.
