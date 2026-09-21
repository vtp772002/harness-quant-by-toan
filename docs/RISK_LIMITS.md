# RISK_LIMITS — Enforced in Code

The checks in `src/domains/risk/service.py` raise exceptions. They do not merely
emit warnings.

| Limit | Value | Enforce |
|---|---|---|
| MAX_POSITION (per symbol) | 1000 shr | `check_limits` raise `RiskBreach` |
| MAX_NOTIONAL_PCT cash | 20% | runtime check |
| MAX_DD kill-switch | -15% | eval fail, archive strategy |
| Min fee+slippage | fee>=1bps, slip>=2bps | BacktestConfig validate |
| Turnover cap | 5x equity/day | reports warn -> evaluation fails when exceeded |

Exceeding a limit raises an exception and marks the run `INVALID`. The system
does not warn and continue past a hard limit.
