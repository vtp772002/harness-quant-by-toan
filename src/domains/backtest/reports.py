"""Read-only backtest reports with Sharpe after costs and turnover."""
from __future__ import annotations


def summarize(result: dict) -> dict:
    eq = result["equity"]
    turnover = sum(abs(f["qty"] * f["price"]) for f in result["fills"])
    return {
        "sharpe": result["sharpe"],
        "max_drawdown": result["max_drawdown"],
        "turnover": float(turnover),
        "n_fills": len(result["fills"]),
        "final_equity": float(eq["equity"].iloc[-1]) if len(eq) else 0.0,
    }
