# RELIABILITY — backtest span budget, per-worktree isolation
- No demo backtest over 252 bars should exceed two seconds; a production fold
  over 30 seconds must be traced and split.
- Every worktree has an isolated `runs/<id>/` stack, which is torn down after
  the task. See `scripts/worktree-boot.sh`.
- A flaky result gets a labeled follow-up run; it does not silently block a
  harness merge.
