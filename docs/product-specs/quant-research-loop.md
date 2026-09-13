# Quant Research Loop — spec chuan cho moi strategy

1. Hypothesis (1 cau, falsifiable).
2. Universe + horizon + rebalance freq.
3. Features: point-in-time definition, asof rule.
4. Costs: fee_bps + slippage_bps, stress x2/x5.
5. Risk: max position, max DD kill-switch, turnover cap.
6. Eval: walk-forward + purged CV + Deflated Sharpe, min 3 folds OOS.
7. Kill criteria so hoa (vd: OOS Sharpe<0.3 sau 2 folds -> archive).
