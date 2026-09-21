# EVALUATION — Strategy Evaluation After Costs

1. Run in-sample fit, then walk-forward evaluation with at least three folds and
   purged K-Fold logic in `evals/`. Do not skip a stage.
2. Track Sharpe after costs, maximum drawdown, turnover, IC, and Deflated
   Sharpe. The baseline thresholds are OOS Sharpe `> 0.5` and max drawdown
   `> -15%`.
3. Apply slippage stress ×2 as a blocking check with Sharpe `> 0`. Treat ×5 as
   informational and block only when it is below `-1.0`; a 2026-09-13 run
   showed that hard-blocking ×5 rejected otherwise credible strategies.
4. A fold failure receives a follow-up run and does not automatically block the
   harness merge. A strategy is promoted only when all three folds pass.
5. Every evaluation writes `metrics.jsonl`, queryable with
   `query-metrics.py --metric sharpe`.
6. The standard gate is:
   `PYTHONPATH=. python scripts/run-eval.py --seed 42 --backend auto`.
   It passes when OOS Sharpe `> 0.5`, DSR `> 0.95` (`K` equals the number of
   configurations tried), stress ×2 `> 0`, stress ×5 `> -1.0`, and max drawdown
   `> -15%`.
   `auto` prefers Rust when the release binary exists; `--backend python` keeps
   the reference path and `--backend rust` fails closed if Rust is unavailable.
   DSR uses the observation frequency (daily); do not mix annualized and daily
   units. `K` includes agent proposals through
   `Proposal.candidate_lookbacks`, so proposing more alternatives increases the
   penalty.
7. A synthetic PASS means that the plumbing works. It is not evidence of a
   real alpha; real verdicts require real, governed data.
