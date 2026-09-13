# ARCHITECTURE.md — Layered Domain Architecture cho Quant Harness

Ap dung bai hoc OpenAI Harness Engineering: strict boundaries + predictable
structure la prerequisite cho agent speed without decay.

## 1. Tong quan

App Wiring (src/wiring.py) la composition root duy nhat.

Moi domain (data, alpha, backtest, risk, portfolio) tuan thu:
  Types -> Config -> Repo -> Service -> Runtime -> Reports

Providers la interface duy nhat cho cross-cutting:
  data_vendor | exchange_sim | telemetry | clock | feature_flags

Utils (src/utils/) nam ngoai boundary, feed vao Providers.

## 2. Layer contract

| Layer | Chua gi | Vi du quant |
|---|---|---|
| types.py | Pydantic models, khong logic | Bar, Signal, Fill, Position |
| config.py | Dataclass config, parse env, khong I/O | BacktestConfig(seed, fee_bps, slippage_bps) |
| repo.py | Doc/ghi Parquet/DuckDB, point-in-time queries | ParquetBarRepo.get_asof(symbol, t) |
| service.py | Logic thuan, deterministic, seeded | MomentumSignal.compute(bars_asof) |
| runtime.py | Orchestration, event loop, telemetry emit | BacktestRuntime.run() |
| reports.py | Metrics (sharpe, maxDD, turnover, IC), read-only | summarize(fills) |

Quy tac forward-only: types <- config <- repo <- service <- runtime <- reports.
service khong import runtime. repo khong import service.
Cross-domain: chi qua service public API.
Cross-cutting: chi qua src/providers/*.

## 3. Vi sao rigid?
Agent replicate pattern hien co — ke ca pattern xau. Rigid layers + linter =
drift bi chan ngay luc PR, khong doi Friday cleanup.

Boring deps: stdlib + numpy + pandas + pydantic + duckdb. Khong pull lib la —
dung src/utils/concurrency.py (map-with-concurrency, 100% coverage).

## 4. Enforce bang linter
- linters/layering.py — parse import AST, fail kem remediation message.
- linters/no_lookahead.py — cam .shift(-N), future, lead(, join khong asof.
- linters/determinism.py — cam random.random(), time.time(), datetime.now() ngoai providers/clock.py.
- linters/taste.py — file <=500 lines, func <=50, structured logging, no hardcoded secrets.
- tests/test_structure.py — mirror bang pytest de fail nhanh local.

## 5. Merge philosophy
Minimal blocking gates: layering + no_lookahead + determinism + smoke-backtest.
Full walk-forward + stress-slippage chay non-blocking (nightly / label full-eval).
PRs short-lived (<400 lines). Corrections cheap, waiting expensive.
