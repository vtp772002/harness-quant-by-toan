"""Runtime + Reports data: ingest job phat telemetry, schema report."""
from __future__ import annotations
import pandas as pd
from src.providers.telemetry import Telemetry


def ingest_runtime(df: pd.DataFrame, telemetry: Telemetry) -> pd.DataFrame:
    telemetry.log("INFO", "ingest", n=len(df))
    return df


def schema_report(df: pd.DataFrame) -> str:
    lines = ["# db-schema (generated) — KHONG sua tay", ""]
    for c, d in zip(df.columns, df.dtypes):
        lines.append(f"- {c}: {d}")
    return "\n".join(lines) + "\n"
