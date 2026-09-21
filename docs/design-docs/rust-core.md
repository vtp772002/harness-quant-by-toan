# Rust Core Design (system of record)

## Architecture: hybrid, not a rewrite

Python keeps orchestration (gate, selection, DSR, universe, and telemetry),
where agents do most research work. Rust (`crates/quant-core`) ports only the
`panel_backtest` daily hot loop, where execution speed matters.

The boundary is CSV (`panel.csv`, `members.csv` -> `equity.csv` plus stdout
metadata). It is boring, inspectable, and readable without specialized tooling.
The core has zero dependencies and uses only the Rust standard library: no
Serde and no Tokio.

## Why CSV instead of PyO3?

- Agents can inspect and debug the boundary without understanding FFI.
- Cross-language determinism can be checked by diffing files.
- The target environment needs only a separate Cargo build and a drop-in
  binary, not a complex Python extension toolchain.
- The tradeoff is a CSV dump and process spawn. The current benchmark amortizes
  one dump over multiple candidate configurations.

## Current benchmark (2026-09-21, seed 42, 756 days × 4 symbols)
| lookback | python | rust | speedup | maxdiff equity |
|---|---|---|---|---|
| 5 | 168ms | 18ms | 9.2x | 2.328e-10 |
| 10 | 154ms | 13ms | 11.4x | 2.328e-10 |
| 20 | 142ms | 11ms | 13.2x | 2.328e-10 |

The maximum difference is `2.328e-10` on equity around `1e6`, approximately
`2e-16` relative error. This is a last-ULP difference between standard floating
point operation order and pandas. The conformance test is locked at `rtol=1e-9`.

## Promotion status

Rust is now the preferred backend for the CLI gate when its release binary is
available. Python remains the permanent reference and fallback.

1. `run-eval.py --backend rust` requires the release binary and reports the
   selected backend in JSON.
2. `--backend auto` selects Rust when available and falls back to Python.
3. Conformance compares Rust and Python equity, fills, turnover, and gate
   metrics; the Python implementation is not deleted.
