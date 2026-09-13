# Skill: reproduce-backtest
Khi user báo "strategy X sai / Sharpe lạ":
1. `bash scripts/worktree-boot.sh`
2. `python scripts/run-backtest.py --seed 42` ghi lại metrics.
3. `python scripts/query-logs.py --filter level=ERROR`, `query-metrics.py --metric sharpe`.
4. Ghi video-bằng-số: dump equity head/tail + fills vào PR body.
5. Fix → rerun cùng seed → diff metrics → PR.
Không đoán — mọi claim phải có metrics.jsonl đính kèm.
