# Skill: reproduce-backtest

When a user reports that strategy X is wrong or Sharpe looks unusual:

1. Run `bash scripts/worktree-boot.sh`.
2. Run `python scripts/run-backtest.py --seed 42` and record the metrics.
3. Query errors with `python scripts/query-logs.py --filter level=ERROR` and
   Sharpe with `python scripts/query-metrics.py --metric sharpe`.
4. Add numeric evidence to the PR: equity head/tail and fills.
5. Fix the issue, rerun with the same seed, diff the metrics, and open the PR.

Do not guess. Every claim must include the relevant `metrics.jsonl` evidence.
