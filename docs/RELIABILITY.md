# RELIABILITY — backtest span budget, per-worktree isolation
- No backtest span >2s cho 252 bars demo; prod fold >30s → trace + split.
- Mỗi worktree isolated runs/<id>/, teardown sau task (xem worktree-boot.sh).
- Flake → follow-up run gắn label, không block merge harness.
