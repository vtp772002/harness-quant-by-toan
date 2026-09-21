# Honest-Eval Design (System of Record for the 30-Day Phase)

## Why these four gaps?

High-throughput agents can turn a small evaluation optimism problem into
hundreds of false strategies. Prioritize the most common sources of hidden
optimism:

1. **Survivorship** — a current universe silently removes securities that have
   already died. Fix: membership is a function of `t` (`get_members`), and
   delisting is a first-class event.
2. **Flat costs** — a fixed fee can turn a high-turnover strategy into a fake
   star. Fix: slippage uses base spread, volatility regime, and square-root
   participation impact, with ×2/×5 stress.
3. **Multiple testing** — try 500 variants, report the best, and forget the
   other 499 failures. Fix: include `K` in Deflated Sharpe and select
   hyperparameters inside each fold.
4. **Train/test leakage** — a trailing window crosses a fold boundary. Fix:
   purged and embargoed splits with purge at least `max_lookback + 1`.

## Accepted assumptions (may be wrong; keep them visible)

- Trades execute at the close and the current bar volume is considered known;
  this is acceptable for the daily example.
- `ref_vol = 0.01` is a prior, not a full-sample estimate. Recalibrate it when
  the real market regime changes.
- Gate v1 has no borrow cost or short constraint; track this as technical debt.
- The synthetic market contains momentum (AR(1) plus drift) so the gate can
  PASS. This tests plumbing, not profitability. Real verdicts require real data.

## Gate thresholds (after costs, OOS)

Annualized Sharpe `> 0.5`, DSR `> 0.95`, stress ×2 `> 0` (blocking), stress ×5
`> -1.0` (informational), and max drawdown `> -15%`. The final holdout must not
be touched; enforce that in a later phase with a hash and ledger.

## Multi-seed calibration (2026-09-13, executed)

| seed | verdict | Sharpe | DSR | x2 | x5 |
|---|---|---|---|---|---|
| 1 | PASS | 2.13 | 0.997 | 1.47 | 0.28 |
| 2 | FAIL | 0.96 | 0.776 | 1.10 | 1.18 |
| 3 | PASS | 2.08 | 1.000 | 1.99 | -0.22 |
| 7 | PASS | 2.91 | 1.000 | 1.49 | 1.06 |
| 42 (CI lock) | PASS | 2.25 | 1.000 | 2.09 | 1.62 |
| 99 | PASS | 2.19 | 0.999 | 1.46 | 0.81 |
| 123 | FAIL | 1.05 | 0.841 | 0.71 | 0.21 |

Five of seven seeds PASS. The two failures are genuinely marginal (Sharpe
around 1.0 and DSR below 0.9), so the gate rejects them as intended. Seed 42 is
the CI lock with a wide margin. Selection instability remains 60-day-phase
technical debt.
