"""Rust acceleration backend for the panel backtest.

Python remains the reference implementation; this module owns the typed CSV
boundary and subprocess contract for the Rust numerical engine.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
import pandas as pd

BIN = Path("crates/quant-core/target/release/quant-core")


def binary_path() -> Path | None:
    return BIN if BIN.exists() else None


def dump_inputs(panel: pd.DataFrame, universe, d: Path) -> None:
    panel.sort_values(["ts", "symbol"]).to_csv(
        d / "panel.csv", columns=["symbol", "ts", "close", "volume"], index=False)
    rows = [(t, s) for t in sorted(panel["ts"].unique()) for s in universe.get_members(t)]
    pd.DataFrame(rows, columns=["ts", "symbol"]).to_csv(d / "members.csv", index=False)


def run_rust_backtest(panel, universe, lookback: int, cost, stress_m: float = 1.0,
                      initial_cash: float = 1_000_000.0, ref_vol: float = 0.01,
                      min_trade: float = 25.0, d: Path | None = None) -> tuple[pd.DataFrame, dict]:
    import tempfile
    binp = binary_path()
    if binp is None:
        raise FileNotFoundError("quant-core binary chua build: cargo build --release -p quant-core")
    work = d or Path(tempfile.mkdtemp())
    work.mkdir(parents=True, exist_ok=True)
    if not (work / "panel.csv").exists() or not (work / "members.csv").exists():
        dump_inputs(panel, universe, work)
    r = subprocess.run(
        [str(binp), "--panel", str(work / "panel.csv"), "--members", str(work / "members.csv"),
         "--lookback", str(lookback), "--fee", str(cost.cfg.fee_bps),
         "--spread", str(cost.cfg.base_spread_bps), "--impact", str(cost.cfg.impact_k),
         "--stress", str(stress_m), "--cash", str(initial_cash),
         "--ref-vol", str(ref_vol), "--min-trade", str(min_trade),
         "--out", str(work / "equity.csv")],
        capture_output=True, text=True, check=True)
    meta = {}
    for tok in r.stdout.strip().split():
        k, _, v = tok.partition("=")
        meta[k] = float(v)
    eq = pd.read_csv(work / "equity.csv", parse_dates=["ts"])
    return eq, {"fills": int(meta["fills"]), "turnover": meta["turnover"]}
