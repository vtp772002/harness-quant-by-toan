# QUALITY_SCORE — Grades Per Domain and Layer

Grades are evidence-backed snapshots and should be refreshed as the harness
changes. Known gaps are tracked explicitly rather than hidden behind a grade.

| Domain | Grade | Gap |
|---|---|---|
| data | B+ | production DuckDB repository is still missing |
| alpha | A- | tools, reports, and proposals are complete; live LLM validation remains |
| backtest | A- | regime costs are complete; stochastic slippage remains |
| evals | A- | seed 42 has a wide PASS margin; multi-seed result is 5/7 — see `honest-eval.md` |
| risk | A | enforced exceptions |
| portfolio | C+ | position sizing is still naive |

The `quality-grade` agent scans deviations and opens small refactoring PRs that
should take less than one minute to review.
