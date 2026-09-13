"""Backtest runtime — event loop deterministic, costs always modeled."""
from __future__ import annotations
import time
import pandas as pd
from src.domains.backtest.types import BacktestConfig
from src.domains.data.repo import ParquetBarRepo
from src.domains.alpha.config import AlphaConfigModel
from src.domains.alpha.service import momentum_signal
from src.domains.risk.service import check_limits
from src.providers.market import SimpleExchangeSim
from src.providers.telemetry import Telemetry
from src.utils.rng_logging import seeded_rng


def run_backtest(
    repo: ParquetBarRepo,
    symbol: str,
    bt_cfg: BacktestConfig,
    alpha_cfg: AlphaConfigModel,
    telemetry: Telemetry,
) -> dict:
    t0 = time.perf_counter()
    rng = seeded_rng(bt_cfg.seed)
    _ = rng
    bars = repo.load(symbol)
    ex = SimpleExchangeSim()
    cash = bt_cfg.initial_cash
    pos = 0.0
    equity = []
    fills = []
    for i in range(len(bars)):
        row = bars.iloc[i]
        bars_asof = bars.iloc[: i + 1]
        sig = momentum_signal(bars_asof, alpha_cfg)
        target = 100.0 * sig
        check_limits(pos, target, cash)
        delta = target - pos
        if abs(delta) > 1e-9:
            px = ex.apply_costs(float(row["close"]), delta, bt_cfg.fee_bps, bt_cfg.slippage_bps)
            cash -= delta * px
            pos = target
            fills.append({"ts": row["ts"], "qty": delta, "price": px})
        equity.append({"ts": row["ts"], "equity": cash + pos * float(row["close"])})
    eq = pd.DataFrame(equity)
    rets = eq["equity"].pct_change().fillna(0)
    sharpe = float(rets.mean() / (rets.std() + 1e-12) * (252 ** 0.5)) if len(rets) > 1 else 0.0
    max_dd = float(((eq["equity"] / eq["equity"].cummax()) - 1).min()) if len(eq) else 0.0
    dt_ms = (time.perf_counter() - t0) * 1000
    telemetry.emit_span("backtest.run", duration_ms=dt_ms, n=len(bars))
    telemetry.metric("sharpe", sharpe, symbol=symbol)
    telemetry.metric("max_drawdown", max_dd, symbol=symbol)
    telemetry.log("INFO", "backtest.done", sharpe=sharpe, max_dd=max_dd, fills=len(fills))
    return {"sharpe": sharpe, "max_drawdown": max_dd, "fills": fills, "equity": eq}
