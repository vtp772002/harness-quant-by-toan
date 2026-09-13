# DESIGN — quyết định boring-stack
Python + pydantic + pandas + duckdb + parquet. Không polars/clickhouse cho tới khi agent chứng minh cần.
Lý do: legible, stable API, training-set dày → agent model được.
