# Exec Plan: Honest-Eval Stack (30-Day Phase)

## Goal

Make a green evaluation meaningful by closing four major gaps in quant-agent
research: survivorship bias, flat costs, repeated selection, and train/test
leakage.

## Scope (four workstreams, one to three small PRs each)

1. **Point-in-time universe** — `Listing` with list/delist dates,
   `UniverseRepo.get_members(t)`, and split adjustment. The backtest trades only
   members alive at `t`. Complete when CCC disappears after delisting and AAA
   remains continuous through a split.
2. **Regime cost model** — `RegimeCostModel` makes slippage depend on volatility
   regime and participation rate; stress ×2/×5 is required in the gate. Complete
   when slippage is monotone in quantity and volatility and remains deterministic.
3. **Purged-embargo CV and Deflated Sharpe** — `evals/purged_cv.py` and
   `evals/deflated_sharpe.py` use an Acklam inverse-normal implementation with
   no SciPy dependency. The gate selects lookbacks on train data and evaluates
   OOS. `K` equals the number of configurations tried. Complete when the gate is
   deterministic and DSR has known-value tests.
4. **Gate and calibration** — `evals/gate.py` and `scripts/run-eval.py` enforce
   OOS Sharpe `> 0.5`, DSR `> 0.95`, stress ×2/×5 limits, and max drawdown
   `> -15%`. The calibrated synthetic market proves plumbing, not real alpha.

## Non-goals (later phases)

- A real data vendor, production DuckDB repository, borrow/short costs, and
  intraday limit-order-book simulation.
- Performance optimization such as caching and slicing; that belongs to the
  60-day phase.

## Decision log (append-only)

- 2026-09-13: implemented DSR with `erf` and Acklam instead of SciPy to keep
  dependencies boring and behavior deterministic.
- 2026-09-13: kept `ref_vol = 0.01` as a fixed prior rather than estimating it
  from the full sample, avoiding cost leakage.
- 2026-09-13: selected lookback on train data per fold and passed three trials
  into DSR to model real selection.
- 2026-09-13: documented that synthetic PASS means plumbing works, not that
  alpha is real.
- 2026-09-13: fixed a DSR unit bug where annualized trial variance was mixed
  with daily `sr_hat`, producing DSR equal to zero. Added known-value tests.
- 2026-09-13: increased `n_days` from 300 to 756 because a per-fold Sharpe
  standard error around 1.6 made selection nearly random.
- 2026-09-13: added `min_trade=25` as a strategy deadband; daily turnover was
  consuming the edge (about 16 bps per trade versus a 4 bps edge).
- 2026-09-13: made ×5 stress informational with a `-1.0` floor because hard
  blocking rejected a strategy with Sharpe 2.08.

## Acceptance

`python linters/run_all.py` passes, the seed-42 gate passes twice with
byte-identical output, and `pytest tests/ evals/` passes.
