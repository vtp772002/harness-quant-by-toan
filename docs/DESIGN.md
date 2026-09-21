# DESIGN — Boring Stack Decision

Use Python, Pydantic, pandas, DuckDB, and Parquet by default. Do not add
Polars or ClickHouse until an agent-backed experiment proves that the current
stack is the bottleneck.

The rationale is legibility, stable APIs, and mature examples that agents can
reason about reliably.
