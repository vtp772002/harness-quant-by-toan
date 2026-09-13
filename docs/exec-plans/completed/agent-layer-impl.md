# Exec Plan: agent-layer slice 1 (pipeline deterministic + LLM provider seam)

## Goal
Agents propose (hypothesis/params), gate disposes (verdict). Slice 1 chay offline hoan toan.

## Scope (lam xong)
- `alpha/tools.py`: RSI/MACD/Stoch/ROC/WillR/ATR + breakout/engulfing/range/trend_slope (pandas, PIT).
- `alpha/schemas.py`: Indicator/Pattern/TrendReport + Proposal + ProposalContext (Pydantic).
- `providers/llm.py`: LLMProvider protocol + ReplayLLM (test) + LiveLLM (can key, stdlib HTTPS).
- `alpha/agents.py`: pipeline 4 buoc + rules-v1 fallback + provider path (validate + asof<=ts assert).
- `evals/gate.py`: nhan candidate_lookbacks tu Proposal; K = len(candidates).

## Khong lam (deferred, can human — decision 0001)
Provider that, secrets policy, token budget, LangGraph, live-fire validation.

## Acceptance
linters xanh + pytest (10 tests agent-layer) xanh + gate seed 42 PASS byte-identical +
scorecard PASS. → DAT → move sang completed/.
