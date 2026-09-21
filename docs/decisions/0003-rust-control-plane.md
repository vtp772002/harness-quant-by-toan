# 0003 — Rust Control Plane with Thin Shell Adapters

- Date: 2026-09-21. Status: accepted.
- Context: the harness had quant logic and a scorecard, but no cross-platform
  entrypoint for booting, producing evidence, and running one validation
  contract. README and shell scripts described many separate commands.

## Decision

1. Rust is a small standard-library-only control plane with `doctor`, `boot`,
   and `check`.
2. Bash and PowerShell only forward commands; they do not duplicate policy or
   quant logic.
3. Python remains the reference implementation for pandas/Pydantic, evaluation,
   and the scorecard. Rust does not replace it without conformance proof.
4. `check` sets `PYTHONPATH=.` and disables auto-loaded pytest plugins so results
   do not depend on global plugins in an agent machine.

## Consequences

- Agents have one discoverable, inspectable contract instead of many scattered
  commands.
- Rust adds a small build surface but provides a clear manifest/evidence and
  failure boundary.
- Live data, brokers, LLMs, and deployment remain product-owned decisions; the
  harness does not infer them or provision credentials.

## Alternatives rejected

- A new Python CLI: duplicates orchestration and blurs the "less Python on the
  control path" boundary.
- Shell-only orchestration: lacks a typed, portable contract good enough for
  PowerShell.
- Rust replacing the entire backtest: violates the Python reference and
  conformance principle.
