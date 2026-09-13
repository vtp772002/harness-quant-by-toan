# RISK_LIMITS — enforced in code (`src/domains/risk/service.py` raise, khong warn)

| Limit | Value | Enforce |
|---|---|---|
| MAX_POSITION (per symbol) | 1000 shr | `check_limits` raise `RiskBreach` |
| MAX_NOTIONAL_PCT cash | 20% | runtime check |
| MAX_DD kill-switch | -15% | eval fail, archive strategy |
| Min fee+slippage | fee>=1bps, slip>=2bps | BacktestConfig validate |
| Turnover cap | 5x equity/day | reports warn -> eval fail neu vuot |

Vuot limit = exception + run marked INVALID. Khong warn-cho-qua.
