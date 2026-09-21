# ARCHITECTURE.md — Layered Domain Architecture for the Quant Harness

This architecture applies the OpenAI Harness Engineering lesson that strict
boundaries and predictable structure are prerequisites for agent speed without
decay.

## 1. Overview

`src/wiring.py` is the single composition root.

Every domain (`data`, `alpha`, `backtest`, `risk`, `portfolio`) follows:

```text
Types → Config → Repo → Service → Runtime → Reports
```

Providers are the only interface for cross-cutting capabilities:

```text
data_vendor | exchange_sim | telemetry | clock | feature_flags | llm
```

Utilities in `src/utils/` sit outside the domain boundary and feed provider or
service code through explicit interfaces.

## 2. Layer contract

| Layer | Contains | Quant example |
|---|---|---|
| `types.py` | Pydantic models, no business logic | `Bar`, `Signal`, `Fill`, `Position` |
| `config.py` | Dataclass/config models, environment parsing, no I/O | `BacktestConfig(seed, fee_bps, slippage_bps)` |
| `repo.py` | Parquet/DuckDB I/O and point-in-time queries | `ParquetBarRepo.get_asof(symbol, t)` |
| `service.py` | Pure, deterministic, seeded domain logic | `MomentumSignal.compute(bars_asof)` |
| `runtime.py` | Orchestration, event loop, telemetry emission | `BacktestRuntime.run()` |
| `reports.py` | Read-only metrics and rendering | `summarize(fills)` |

The dependency rule is forward-only:

```text
types ← config ← repo ← service ← runtime ← reports
```

Services must not import runtime. Repositories must not import services.
Cross-domain access goes through public service APIs. Cross-cutting access goes
through `src/providers/*`.

## 3. Why rigid boundaries?

Agents reproduce existing patterns, including bad ones. Rigid layers plus a
linter stop drift at PR time instead of waiting for a periodic cleanup.

Prefer boring dependencies: the standard library, NumPy, pandas, Pydantic, and
DuckDB. Do not add a library for a helper already provided by
`src/utils/concurrency.py`, which has full test coverage.

## 4. Mechanical enforcement

- `linters/layering.py` parses the import AST and reports remediation.
- `linters/no_lookahead.py` rejects `.shift(-N)`, `future`, `lead(`, and joins
  without an as-of rule.
- `linters/determinism.py` rejects `random.random()`, `time.time()`, and
  `datetime.now()` outside `providers/clock.py`.
- `linters/taste.py` checks file/function size, structured logging, and secrets.
- `tests/test_structure.py` mirrors the structural checks in pytest.

## 5. Merge philosophy

Blocking gates are minimal and deterministic: layering, no lookahead,
determinism, and the smoke backtest. Full walk-forward and slippage stress can
run as non-blocking nightly or `full-eval` checks.

Keep PRs short-lived and preferably below 400 changed lines. Corrections are
cheap when evidence is local and boundaries are explicit.
