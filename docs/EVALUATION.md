# EVALUATION — cach danh gia chien luoc (sau costs)

1. In-sample fit -> Walk-forward (3+ folds) -> Purged K-Fold (`evals/`). Khong skip buoc.
2. Metrics: Sharpe (sau costs), maxDD, turnover, IC, Deflated Sharpe. Nguong: OOS Sharpe>0.5, maxDD>-15%.
3. Stress: slippage x2 block (Sharpe>0); x5 informational, chi block khi < -1.0 (fragile ve co cau).
   Ly do hieu chinh 2026-09-13: strategy Sharpe 2.08 van rot x5 — x5 blocking se giet hau het moi thu that.
4. Flake policy: fail 1 fold -> rerun follow-up, khong block merge harness; strategy chi promote khi 3 folds xanh.
5. Moi eval ghi `metrics.jsonl` de agent query (`query-metrics.py --metric sharpe`).
6. Gate chuan: `PYTHONPATH=. python scripts/run-eval.py --seed 42` → PASS khi
   OOS Sharpe>0.5, DSR>0.95 (K=so config da thu), x2>0, x5>-1.0, maxDD>-15%.
   DSR tinh o tan suat quan sat (daily) — cam tron don vi annualized/daily.
   K bao gom ca proposal tu agents (Proposal.candidate_lookbacks) — de xuat cang nhieu, phat cang nang.
7. Synthetic PASS = plumbing dung, KHONG phai alpha that. Verdict that doi data that.
