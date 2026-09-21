"""Honest-eval gate with PIT universe, costs, purged folds, DSR, and stress.

Lookback selection happens on train data in every fold, and K trials enter DSR.
The result is deterministic for a given seed.
"""
from __future__ import annotations

import math
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from src.domains.alpha.config import AlphaConfigModel
from src.domains.alpha.service import momentum_signal
from src.domains.data.repo import UniverseRepo
from src.domains.data.service import apply_splits, trailing_vol
from src.domains.data.synthetic import make_synthetic_market
from src.domains.risk.service import check_limits
from src.providers.market import RegimeCostModel
from src.providers.telemetry import Telemetry
from evals.purged_cv import purged_embargo_splits
from evals.deflated_sharpe import deflated_sharpe, return_moments

CANDIDATE_LOOKBACKS = [5, 10, 20]
BACKENDS = ("python", "rust", "auto")
SHARPE_MIN, DSR_MIN, STRESS_MIN, DD_MAX = 0.5, 0.95, 0.0, -0.15
STRESS_X5_FLOOR = -1.0  # informational: block only below the fragile floor


def panel_backtest(panel, universe, lookback, cost, stress_m=1.0, initial_cash=1_000_000.0, ref_vol=0.01,
                   min_trade=25.0):
    dates = sorted(panel["ts"].unique())
    syms = sorted(panel["symbol"].unique())
    frames = {s: panel[panel["symbol"] == s].sort_values("ts").reset_index(drop=True) for s in syms}
    at = {s: {t: i for i, t in enumerate(frames[s]["ts"])} for s in syms}
    cfg = AlphaConfigModel(lookback=lookback)
    cash, pos, curve, fills, turnover = initial_cash, {s: 0.0 for s in syms}, [], 0, 0.0
    for t in dates:
        members = universe.get_members(t)
        px_today = {}
        for s in syms:
            if s not in members or t not in at[s]:
                continue
            df, i = frames[s], at[s][t]
            bars_asof = df.iloc[: i + 1]
            target = 100.0 * momentum_signal(bars_asof, cfg)
            check_limits(pos[s], target, cash)
            delta = target - pos[s]
            px = float(df.loc[i, "close"])
            if abs(delta) > min_trade:  # deadband: trade only for material moves
                slip, fee = cost.total_bps(float(df.loc[i, "volume"]), trailing_vol(bars_asof) / ref_vol, delta, stress_m)
                adj = px * (1 + (slip + fee) / 1e4) if delta > 0 else px * (1 - (slip + fee) / 1e4)
                cash -= delta * adj
                pos[s] = target
                fills += 1
                turnover += abs(delta) * adj
            px_today[s] = px
        curve.append((t, cash + sum(pos[s] * px_today.get(s, 0.0) for s in syms)))
    return pd.DataFrame(curve, columns=["ts", "equity"]), {"fills": fills, "turnover": turnover}


def _sharpe_d(rets) -> float:
    """Daily Sharpe; DSR uses the observation frequency consistently."""
    import numpy as np
    r = np.asarray(list(rets), dtype=float)
    return float(r.mean() / (r.std() + 1e-12)) if len(r) > 1 else 0.0


def _sharpe_ann(rets) -> float:
    return _sharpe_d(rets) * math.sqrt(252)


def _max_dd(rets) -> float:
    import numpy as np
    eq = np.cumprod([1 + x for x in list(rets)])
    return float(((eq / np.maximum.accumulate(eq)) - 1).min()) if len(eq) else 0.0


def _resolve_backend(backend: str) -> str:
    if backend not in BACKENDS:
        raise ValueError(f"backend must be one of {BACKENDS}, got {backend!r}")
    if backend == "auto":
        from evals.rust_core import binary_path
        return "rust" if binary_path() else "python"
    if backend == "rust":
        from evals.rust_core import binary_path
        if binary_path() is None:
            raise FileNotFoundError("Rust backend missing; build crates/quant-core in release mode")
    return backend


def _backend_equity(panel, universe, lookback, cost, stress_m, backend, work):
    if backend == "python":
        return panel_backtest(panel, universe, lookback, cost, stress_m)[0]
    from evals.rust_core import run_rust_backtest
    return run_rust_backtest(panel, universe, lookback, cost, stress_m, d=work)[0]


def _oos_for_stress(panel, universe, cost, stress_m, dates, splits, cands,
                    backend="python") -> tuple[list, list, list]:
    work = None
    if backend == "rust":
        work = Path(tempfile.mkdtemp(prefix="quant-rust-gate-"))
    eq_by_lb = {lb: _backend_equity(panel, universe, lb, cost, stress_m, backend, work)
                for lb in cands}
    rets_by_lb = {lb: eq_by_lb[lb]["equity"].pct_change().fillna(0).tolist() for lb in cands}
    oos, picks, trial_vars = [], [], []
    for train, test in splits:
        d_train = {lb: _sharpe_d([rets_by_lb[lb][i] for i in train]) for lb in cands}
        best = max(cands, key=lambda lb: (d_train[lb], -lb))
        picks.append(best)
        oos.extend(rets_by_lb[best][i] for i in test)
        trial_vars.append(float(np.var(list(d_train.values()))))
    return oos, picks, trial_vars


def run_gate(seed: int = 42, telemetry: Telemetry | None = None,
             candidate_lookbacks: list[int] | None = None, backend: str = "python") -> dict:
    """Run the gate; more proposed candidates increase the DSR penalty."""
    tel = telemetry or Telemetry()
    selected_backend = _resolve_backend(backend)
    tel.log("INFO", "gate.backend", backend=selected_backend)
    cands = list(candidate_lookbacks) if candidate_lookbacks else list(CANDIDATE_LOOKBACKS)
    mkt = make_synthetic_market(seed)
    panel = apply_splits(mkt.panel, mkt.splits)
    universe = UniverseRepo(mkt.listings)
    cost = RegimeCostModel()
    dates = sorted(panel["ts"].unique())
    splits = purged_embargo_splits(len(dates), 3, max(cands) + 1, 5)
    oos, picks, trial_vars = _oos_for_stress(
        panel, universe, cost, 1.0, dates, splits, cands, selected_backend)
    sharpe = _sharpe_ann(oos)
    max_dd = _max_dd(oos)
    sr_d, skew, kurt = return_moments(oos)
    trial_var = float(np.mean(trial_vars))
    dsr = deflated_sharpe(sr_d, len(oos), skew, kurt, trial_var, len(cands))
    stress = {m: _sharpe_ann(_oos_for_stress(
        panel, universe, cost, float(m), dates, splits, cands, selected_backend)[0]) for m in (2, 5)}
    verdict = "PASS" if (sharpe > SHARPE_MIN and dsr > DSR_MIN and stress[2] > STRESS_MIN
                         and stress[5] > STRESS_X5_FLOOR and max_dd > DD_MAX) else "FAIL"
    out = {"verdict": verdict, "backend": selected_backend, "seed": seed,
           "sharpe_oos": sharpe, "dsr": dsr,
           "stress_x2": stress[2], "stress_x5": stress[5], "max_dd": max_dd,
           "n_oos": len(oos), "picks": picks, "candidates": cands}
    for k, v in out.items():
        if isinstance(v, float):
            tel.metric(f"gate.{k}", v, seed=str(seed))
    tel.log("INFO" if verdict == "PASS" else "ERROR", "gate.done", **{k: v for k, v in out.items() if k != "picks"})
    return out
